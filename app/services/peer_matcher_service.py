import os
import json
import traceback

from app.models.peer_matcher import find_closest_peers, prepare_vectors
from app.models.dcf_generator import run_dcf_from_inputs
from app.utils.valuation import combine_valuations, estimate_peer_valuation
from app.utils.helpers import validate_vector
from app.models.dcf_generator import run_sensitivity_analysis
from app.models.three_statement_model import forecast_3_statement
from app.models.dcf_generator import generate_dcf

def run_peer_match_pipeline(
    company_name,
    wacc=0.10,
    terminal_growth=0.03,
    dcf_weight=0.5,
    top_n_peers=5,
    min_similarity=0.0,
    wacc_range=None,
    terminal_growth_range=None,
    verbose=False,
    output_json=False,
    output_path="results/output_summary.json",
    multiple_type="ev_ebitda",  # ✅ Add this line
    export_peers=False

):

    # 1. Load target vector and peer data
    target_vector, peer_data = prepare_vectors(company_name)

    if verbose:
        print(f"✅ Loaded {len(peer_data)} entries.")
        for i, peer in enumerate(peer_data):
            print(f"{i}: {peer.get('name')} | Vector valid: {validate_vector(peer.get('vector'))}")

    # 2. Identify the target company
    target_peer = next(
        (peer for peer in peer_data
         if peer.get("name", "").strip().lower() == company_name.strip().lower()),
        None
    )
    if not target_peer:
        raise ValueError(f"Target company '{company_name}' not found in peer data.")

    # 3. Match similar peers
    top_peers = find_closest_peers(
        target_vector,
        peer_data,
        top_k=top_n_peers,
        target_name=company_name,
        min_similarity=min_similarity
    )

    if not top_peers:
        raise ValueError("No similar peers found above min_similarity threshold.")

    if verbose:
        print(f"🧠 Top match: {top_peers[0][0].get('name')} | Similarity: {top_peers[0][1]:.4f}")

    # 4. Estimate peer-based valuation
    peer_result = estimate_peer_valuation(
        [p for p, _ in top_peers],
        target_peer,
        multiple_type=multiple_type
    )

    # 5. Run DCF if not available

    dcf_raw = target_peer.get("dcf_value")
    forecast = None

    if not dcf_raw:
        try:
            # Generate full 3-statement forecast
            required_keys = [
                'revenue_base',
                'revenue_growth',
                'ebitda_margin',
                'capex_pct',
                'depreciation_pct',
                'nwc_pct',
                'tax_rate'
            ]
            target_inputs = {k: target_peer[k] for k in required_keys if
                             k in target_peer}
            forecast = forecast_3_statement(**target_inputs)

            dcf_result = generate_dcf(forecast, wacc=wacc,
                                      terminal_growth=terminal_growth)
            dcf_value = dcf_result["value"]
            target_peer["dcf_value"] = dcf_value
        except Exception as e:
            if verbose:
                print(f"⚠️ DCF generation failed: {e}")
            dcf_value = 0.0
    else:
        dcf_value = float(dcf_raw[0]) if isinstance(dcf_raw, list) else float(dcf_raw)

    # ✅ Sensitivity logic goes here, outside both try and else
    sensitivity_output = None
    if forecast and wacc_range and terminal_growth_range:
        try:
            sensitivity_output = run_sensitivity_analysis(
                forecast,
                wacc_range=wacc_range,
                terminal_growth_range=terminal_growth_range
            )
        except Exception as e:
            sensitivity_output = {"error": str(e)}
            if verbose:
                print(f"⚠️ Sensitivity analysis failed: {e}")



    # 6. Combine DCF + peer valuations
    combined_valuation = combine_valuations(
        dcf_value=dcf_value,
        peer_value=peer_result,
        dcf_weight=dcf_weight
    )


    # 7. Return results
    result_data = {
        "company_name": company_name,
        "dcf_value": round(dcf_value, 2),
        "peer_value": (
            round(peer_result.get("implied_value"), 2)
            if isinstance(peer_result, dict)
            else round(peer_result, 2)
        ),

        "combined_valuation": round(combined_valuation,
                                    2) if combined_valuation is not None else None,
        "top_peers": [
            {
                "peer_name": peer.get("name"),
                "similarity": round(score, 4),
                "ev_ebitda": round(peer.get("ev_ebitda"), 2) if peer.get(
                    "ev_ebitda") else None,
                "pe_ratio": round(peer.get("pe_ratio"), 2) if peer.get(
                    "pe_ratio") else None,

            }
            for peer, score in top_peers
        ],
        "sensitivity_analysis": sensitivity_output if wacc_range and terminal_growth_range else None,
    }

    if output_json:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        try:
            with open(output_path, "w") as f:
                json.dump(result_data, f, indent=2)
            if verbose:
                print(f"📝 Results saved to {output_path}")
        except (TypeError, ValueError) as e:
            print(f"❌ Error saving JSON to {output_path}: {e}")
            if verbose:
                traceback.print_exc()

    if export_peers:
        peer_table_path = "results/peer_similarity_table.csv"
        os.makedirs("results", exist_ok=True)

        import pandas as pd
        df = pd.DataFrame([
            {
                "peer_name": peer.get("name"),
                "similarity": round(score, 4),
                "ev_ebitda": peer.get("ev_ebitda"),
                "pe_ratio": peer.get("pe_ratio"),
                "description": peer.get("description", "")[:100]  # truncated
            }
            for peer, score in top_peers
        ])
        df.to_csv(peer_table_path, index=False)
        if verbose:
            print(f"📤 Exported peer similarity table to {peer_table_path}")

    # Optional: Export sensitivity matrix to CSV
    if sensitivity_output and isinstance(sensitivity_output, dict):
        try:
            import pandas as pd

            waccs = sensitivity_output["wacc_values"]
            tgrs = sensitivity_output["terminal_growth_values"]
            matrix = sensitivity_output["valuation_matrix"]

            df = pd.DataFrame(
                matrix,
                index=[f"WACC: {w:.2%}" for w in waccs],
                columns=[f"TGR: {g:.2%}" for g in tgrs]
            )
            os.makedirs("results", exist_ok=True)
            df.to_csv("results/sensitivity_matrix.csv")
            if verbose:
                print("📊 Exported sensitivity matrix to results/sensitivity_matrix.csv")
        except Exception as e:
            if verbose:
                print(f"⚠️ Failed to export sensitivity matrix: {e}")

    # Optional: Print pretty console table
    if sensitivity_output and isinstance(sensitivity_output, dict) and verbose:
        print("\n📉 Sensitivity Matrix (WACC ↓ vs TGR →):\n")

        header = "WACC \\ TGR | " + " | ".join([f"{tg:.2%}".rjust(8) for tg in tgrs])
        print(header)
        print("-" * len(header))

        for i, w in enumerate(waccs):
            row = f"{w:.2%}".rjust(11) + " | " + " | ".join([
                f"{val:8,.0f}" if val is not None else "   N/A" for val in matrix[i]
            ])
            print(row)

    return result_data

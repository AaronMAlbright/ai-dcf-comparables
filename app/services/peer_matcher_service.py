import os
import json
import traceback

from app.models.peer_matcher import find_closest_peers, prepare_vectors
from app.models.dcf_generator import run_dcf_from_inputs
from app.utils.valuation import combine_valuations, estimate_peer_valuation
from app.utils.helpers import validate_vector


def run_peer_match_pipeline(
    company_name,
    wacc=0.10,
    terminal_growth=0.03,
    dcf_weight=0.5,
    top_n_peers=5,
    min_similarity=0.0,
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
    if not dcf_raw:
        try:
            dcf_value = run_dcf_from_inputs(
                target_peer, wacc=wacc, terminal_growth=terminal_growth
            )
            target_peer["dcf_value"] = dcf_value
        except Exception as e:
            if verbose:
                print(f"⚠️ DCF generation failed: {e}")

            dcf_value = 0.0
    else:
        dcf_value = float(dcf_raw[0]) if isinstance(dcf_raw, list) else float(dcf_raw)

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
        ]
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


    return result_data

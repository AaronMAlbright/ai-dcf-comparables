import os
import json
from dcf_app.models.peer_matcher import prepare_vectors, find_closest_peers, apply_peer_multiples
from dcf_app.models.dcf_generator import run_dcf_from_inputs, generate_forecasted_fcfs
from dcf_app.utils.valuation import combine_valuations


def run_peer_match_pipeline(
    company_name,
    wacc=0.10,
    terminal_growth=0.03,
    dcf_weight=0.5,
    top_n_peers=5,
    min_similarity=0.0,
    verbose=False,
    multiple_type="ev_ebitda",
    fallback_description=None,
    fallback_revenue=None,
    fallback_ebitda_margin=None,
    desc_weight=0.85,
    exit_multiple=None,
):
    print("🚀 RUN_PEER_MATCH_PIPELINE STARTED")

    # Load target company and peer data (with optional fallback)
    target_vector, peer_data = prepare_vectors(
        company_name,
        fallback_description=fallback_description,
        fallback_revenue=fallback_revenue,
        fallback_ebitda_margin=fallback_ebitda_margin,
        desc_weight=desc_weight
    )

    target_company = next(
        (p for p in peer_data if
         p.get("name", "").strip().lower() == company_name.strip().lower()),
        None
    )

    if not target_company:
        print(f"❌ Target company '{company_name}' not found in peer data, and no fallback provided.")
        return None

    if verbose:
        print(f"🧠 Target company: {target_company}")
        print(f"🧑‍🤝‍🧑 Peer count: {len(peer_data)}")

    # Find closest peers
    top_peers = find_closest_peers(
        target_vector,
        peer_data,
        top_k=top_n_peers,
        target_name=company_name,
        min_similarity=min_similarity
    )

    if not top_peers:
        print("❌ No similar peers found.")
        return None

    peer_companies = [peer for peer, _ in top_peers]

    # DCF valuation
    inputs = {
        "revenue_base": target_company.get("revenue_base"),
        "revenue_growth": target_company.get("revenue_growth"),
        "ebitda_margin": target_company.get("ebitda_margin"),
        "capex_pct": target_company.get("capex_pct"),
        "nwc_pct": target_company.get("nwc_pct"),
        "depreciation_pct": target_company.get("depreciation_pct"),
        "tax_rate": target_company.get("tax_rate")
    }

    # DCF valuation (with terminal value unpacking)
    value, terminal_info = run_dcf_from_inputs(
        inputs,
        wacc=wacc,
        terminal_growth=terminal_growth,
        exit_multiple=exit_multiple
    )

    fcf_forecast = {
        "valuation": value,
        "fcfs": generate_forecasted_fcfs(inputs)
    }
    dcf_value = fcf_forecast["valuation"]

    # ✅ Compute terminal value via Exit Multiple
    exit_terminal_value = None
    if exit_multiple is not None:
        final_fcf = fcf_forecast["fcfs"][-1]
        try:
            ebitda_margin = inputs["ebitda_margin"]
            terminal_ebitda = final_fcf / ebitda_margin
            exit_terminal_value = terminal_ebitda * exit_multiple
        except Exception as e:
            print(f"❌ Error computing exit-based terminal value: {e}")

    # Peer-based valuation
    peer_result = apply_peer_multiples(target_company, peer_companies, multiple_type=multiple_type)
    peer_value = peer_result.get("implied_value")

    # Combine valuations
    final_value = combine_valuations(dcf_value, peer_value, dcf_weight)

    return {
        "company_name": company_name,
        "dcf_value": dcf_value,
        "peer_value": peer_value,
        "combined_valuation": final_value,
        "exit_terminal_value": round(exit_terminal_value,
                                     2) if exit_terminal_value else None,
        "terminal_info": terminal_info,
        "peer_result": peer_result,
        "top_peers": [
            {
                "name": peer.get("name"),
                "similarity": round(score, 4),
                "ev_ebitda": peer.get("ev_ebitda"),
                "pe_ratio": peer.get("pe_ratio")
            }
            for peer, score in top_peers
        ]
    }




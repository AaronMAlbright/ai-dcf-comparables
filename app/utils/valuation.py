import numpy as np

def combine_valuations(
    dcf_value: float,
    peer_value: float,
    dcf_weight: float = 0.5
) -> float:
    """
    Combines DCF and peer-based valuation with adjustable weights.
    Returns None if both values are invalid.
    """

    if dcf_value is None and peer_value is None:
        return None
    elif dcf_value is None:
        return peer_value
    elif peer_value is None:
        return dcf_value

    # ✅ Handle dict inputs
    if isinstance(dcf_value, dict):
        dcf_value = dcf_value.get("valuation")

    if isinstance(peer_value, dict):
        # fallback logic for either "implied_value" or "valuation"
        peer_value = peer_value.get("implied_value") or peer_value.get("valuation")

    # ✅ Final guard: make sure both are valid numbers
    if not isinstance(dcf_value, (int, float)) or not isinstance(peer_value, (int, float)):
        print(f"❌ Invalid valuation types — dcf: {dcf_value}, peer: {peer_value}")
        return None

    peer_weight = 1 - dcf_weight

    print(f"⚠️ Types — dcf_value: {type(dcf_value)}, peer_value: {type(peer_value)}")

    return round(
        float(dcf_value) * float(dcf_weight) +
        float(peer_value) * float(peer_weight),
        2
    )


def estimate_peer_valuation(peers, target_company, multiple_type="ev_ebitda"):
    """
    Estimate the target company's value using peer multiples.
    Supports EV/EBITDA and P/E ratio.
    """
    metric = "ebitda" if multiple_type == "ev_ebitda" else "earnings"
    multiple_key = "ev_ebitda" if multiple_type == "ev_ebitda" else "pe_ratio"

    target_metric = target_company.get(metric)
    if target_metric is None:
        print(f"❌ Missing target metric ({metric}) for {target_company.get('name')}")
        return None

    # Collect valid peer multiples
    multiples = []
    for peer in peers:
        peer_val = peer.get(multiple_key)
        if isinstance(peer_val, (int, float)):
            multiples.append(peer_val)
        else:
            print(f"⚠️ Invalid or missing {multiple_key} for {peer.get('name')}")

    if not multiples:
        print(f"❌ No valid {multiple_type} multiples found in peers.")
        return None

    avg_multiple = sum(multiples) / len(multiples)
    implied_value = avg_multiple * target_metric

    return {
        "valuation_method": multiple_type,
        "implied_value": round(implied_value, 2),
        "target_metric": round(target_metric, 2),
        "avg_multiple": round(avg_multiple, 2),
        "peer_count": len(multiples)
    }


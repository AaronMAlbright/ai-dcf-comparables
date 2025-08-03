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


def estimate_peer_valuation(
    target_company,
    top_peers,
    multiple_type="ev_ebitda"
):
    """
    Estimate valuation based on peer multiples (EV/EBITDA or P/E).
    Returns implied value or None if calculation fails.
    """
    if not top_peers or not target_company:
        print("❌ Missing input: top peers or target company.")
        return None

    target_name = target_company.get("name", "Unknown")
    print(f"📈 Estimating valuation for {target_name} using {multiple_type.upper()}...")

    if multiple_type == "ev_ebitda":
        target_metric = target_company.get("ebitda")
        multiple_field = "ev_ebitda"
    elif multiple_type == "pe_ratio":
        target_metric = target_company.get("net_income")
        multiple_field = "pe_ratio"
    else:
        print(f"❌ Unsupported multiple type: {multiple_type}")
        return None

    if target_metric is None:
        print(f"❌ Missing target metric ({multiple_field}) for {target_name}.")
        return None

    multiples = []
    for peer in top_peers:
        multiple = peer.get(multiple_field)
        if multiple is not None:
            multiples.append(multiple)

    if not multiples:
        print("❌ No valid peer multiples available.")
        return None

    avg_multiple = sum(multiples) / len(multiples)
    implied_value = avg_multiple * target_metric

    print(f"✅ Avg {multiple_field.upper()} from peers: {round(avg_multiple, 2)}")
    print(f"💰 Implied valuation: {round(implied_value, 2)}")

    return implied_value

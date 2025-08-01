def combine_valuations(
    dcf_value: float,
    peer_value: float,
    dcf_weight: float = 0.5
) -> float:
    """
    Combines DCF and peer-based valuation with adjustable weights.

    :param dcf_value: Valuation from discounted cash flow
    :param peer_value: Valuation from comparables
    :param dcf_weight: Weight assigned to DCF (default 0.5)
    :return: Weighted average of both methods
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

    peer_weight = 1 - dcf_weight

    print(f"⚠️ Types — dcf_value: {type(dcf_value)}, peer_value: {type(peer_value)}")

    return round(
        float(dcf_value) * float(dcf_weight) +
        float(peer_value) * float(peer_weight),
        2
    )

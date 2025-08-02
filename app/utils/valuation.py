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
    peers: list,
    target_peer: dict,
    multiple_key: str = "ev_ebitda",
    metric_key: str = "ebitda"
) -> dict:
    print(
        f"🧪 Estimating value from {len(peers)} peers using multiple: {multiple_key}")

    if peers:
        print(f"📌 Sample peer data: {peers[0]}")
    else:
        print("❌ No peers passed into valuation.")
    """
    Estimate peer-based valuation using a median multiple and a target metric.

    Returns a dictionary with keys:
    - median_multiple
    - target_metric
    - implied_value
    """

    valid_multiples = []
    for peer in peers:
        if peer.get("name") == target_peer.get("name"):
            continue

        multiple = peer.get(multiple_key)
        print(f"🧪 {peer['name']} ev/EBITDA: {multiple}")
        if isinstance(multiple, (int, float)):
            valid_multiples.append(multiple)
        else:
            print(f"⚠️ Skipping {peer.get('name')} — missing or invalid {multiple_key}: {multiple}")

    if not valid_multiples:
        print("❌ No valid peer multiples found.")
        return {"median_multiple": None, "target_metric": None, "implied_value": None}

    median_multiple = np.median(valid_multiples)

    target_metric = target_peer.get(metric_key)
    if target_metric is None:
        print(f"⚠️ Target peer is missing '{metric_key}' entirely: {target_peer.get('name')}")

    if not isinstance(target_metric, (int, float)):
        print("❌ Target metric missing or invalid.")
        return {"median_multiple": median_multiple, "target_metric": None, "implied_value": None}

    implied_value = median_multiple * target_metric

    return {
        "median_multiple": median_multiple,
        "target_metric": target_metric,
        "implied_value": implied_value
    }

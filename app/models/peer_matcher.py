from sentence_transformers import SentenceTransformer, util
from app.utils.loader import load_company_data, create_company_vector
import numpy as np
import torch
from app.utils.helpers import validate_vector

# Initialize the transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# 🔧 DEBUG TOGGLE: Force regenerate all vectors regardless of validation
FORCE_REGENERATE_VECTORS = True


def prepare_vectors(company_name, exclude_name=None):
    """
    Loads target and peer data, regenerating vectors if needed.
    Excludes the target company from peer data if exclude_name is provided.
    """
    print(f"\n📥 DEBUG: Calling load_company_data('{company_name}')")
    target_vector, peer_data = load_company_data(company_name)

    print(f"📊 DEBUG: Raw peer_data loaded: {len(peer_data)} items")
    for i, p in enumerate(peer_data[:3]):
        print(f"  peer[{i}]: type={type(p)}, preview={str(p)[:80]}")

    # 🧹 Filter out malformed entries
    cleaned_peers = []
    for i, peer in enumerate(peer_data):
        if isinstance(peer, dict):
            cleaned_peers.append(peer)
        else:
            print(f"❌ Skipping malformed peer at index {i}: {peer} (type: {type(peer)})")
    peer_data = cleaned_peers

    # Remove the target from peer list if specified
    if exclude_name:
        peer_data = [
            peer for peer in peer_data
            if peer.get("name", "").strip().lower() != exclude_name.strip().lower()
        ]

    # Regenerate peer vectors
    for peer in peer_data:
        if FORCE_REGENERATE_VECTORS or not validate_vector(peer.get("vector")):
            print(f"⚠️ Recreating vector for peer: {peer.get('name', 'UNKNOWN')}")
            peer["vector"] = create_company_vector(peer)

    # Regenerate target vector if needed
    if FORCE_REGENERATE_VECTORS or not validate_vector(target_vector):
        print(f"⚠️ Recreating vector for target company: {company_name}")
        target_company = next((p for p in peer_data if p.get("name") == company_name), None)
        if target_company:
            target_vector = create_company_vector(target_company)
        else:
            raise ValueError(f"Target company '{company_name}' not found in peer data.")

    return target_vector, peer_data


def find_closest_peers(target_vector, peer_data, top_k=5, target_name=None):
    similarities = []

    for peer in peer_data:
        if not isinstance(peer, dict):
            print(f"⚠️ Skipping invalid peer (not a dict): {peer}")
            continue

        name = peer.get("name", "UNKNOWN")
        vector = peer.get("vector")
        is_self = (name.strip().lower() == target_name.strip().lower()) if target_name else False
        is_valid_vector = validate_vector(vector)

        print(f"🔍 Peer: {name} | Is self? {is_self} | Vector valid? {is_valid_vector} | Sample vector: {vector[:5] if isinstance(vector, list) else vector}")

        if is_self:
            print(f"🚫 Skipping self-match: {name}")
            continue

        if not is_valid_vector:
            print(f"⚠️ Skipping {name} due to invalid vector.")
            continue

        try:
            similarity = util.cos_sim(
                torch.tensor([target_vector], dtype=torch.float32),
                torch.tensor([vector], dtype=torch.float32)
            )[0][0].item()

            similarities.append((peer, similarity))
            print(f"✅ Similarity with {name}: {similarity:.4f}")
        except Exception as e:
            print(f"❌ Error computing similarity for {name}: {e}")

    if not similarities:
        print("⚠️ No valid similarities found — check vectors or filtering logic.")

    for peer, score in similarities:
        print(f"⭐ {peer.get('name')}: {score:.4f}")

    top_peers = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
    return top_peers


def apply_peer_multiples(target_company: dict, peers: list, multiple_type: str = "ev_ebitda") -> dict:
    """
    Apply a peer multiple to estimate target valuation.
    """
    if multiple_type == "ev_ebitda":
        peer_multiples = [p.get("ev_ebitda") for p in peers if p.get("ev_ebitda") is not None]
        ebitda_margin = target_company.get("ebitda_margin")
        revenue_base = target_company.get("revenue_base")
        target_metric = ebitda_margin * revenue_base if ebitda_margin and revenue_base else None
    elif multiple_type == "pe_ratio":
        peer_multiples = [p.get("pe_ratio") for p in peers if p.get("pe_ratio") is not None]
        target_metric = target_company.get("earnings")
    else:
        raise ValueError("Unsupported multiple type.")

    if not peer_multiples or target_metric is None:
        return {"median_multiple": None, "target_metric": None, "implied_value": None}

    median_multiple = np.median(peer_multiples)
    implied_value = median_multiple * target_metric

    return {
        "median_multiple": round(median_multiple, 2),
        "target_metric": round(target_metric, 2),
        "implied_value": round(implied_value, 2)
    }


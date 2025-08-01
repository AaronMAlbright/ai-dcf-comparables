from sentence_transformers import SentenceTransformer, util
from app.utils.loader import load_company_data
from app.utils.loader import create_company_vector
from app.utils.loader import load_company_data, create_company_vector
import numpy as np


# Initialize the transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def validate_vector(vector):
    """Ensure the vector is a list of floats."""
    return isinstance(vector, list) and all(isinstance(x, float) for x in vector)

def prepare_vectors(company_name):
    """
    Loads target and peer data, regenerating vectors if needed.
    """
    target_vector, peer_data = load_company_data(company_name)

    # Validate and regenerate peer vectors if necessary
    for peer in peer_data:
        if not validate_vector(peer.get("vector", None)):
            print(f"⚠️ Recreating vector for peer: {peer.get('name', 'UNKNOWN')}")
            peer["vector"] = create_company_vector(peer)

    # Validate target vector
    if not validate_vector(target_vector):
        print(f"⚠️ Recreating vector for target company: {company_name}")
        target_company = next((c for c in peer_data if c["name"] == company_name), None)
        if target_company:
            target_vector = create_company_vector(target_company)
        else:
            raise ValueError(f"Target company '{company_name}' not found in peer data.")

    return target_vector, peer_data

import torch
from sentence_transformers import util

def find_closest_peers(target_vector, peer_data, top_k=5):
    similarities = []

    for peer in peer_data:
        vector = peer.get("vector")

        if not isinstance(vector, list) or not all(isinstance(v, (int, float)) for v in vector):
            print(f"⚠️ Skipping {peer.get('name')} due to invalid vector: {vector}")
            continue

        try:
            similarity = util.cos_sim([target_vector], [vector])[0][0].item()
            similarities.append((peer, similarity))
        except Exception as e:
            print(f"❌ Error computing similarity for {peer.get('name')}: {e}")

    top_peers = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
    return top_peers

def apply_peer_multiples(target_company: dict, peers: list, multiple_type: str = "ev_ebitda") -> dict:
    """
    Apply a peer multiple to estimate target valuation.

    Args:
        target_company (dict): The target company dict.
        peers (list): List of peer company dicts.
        multiple_type (str): 'ev_ebitda' or 'pe_ratio'

    Returns:
        dict: { 'median_multiple': x, 'target_metric': y, 'implied_value': z }
    """
    if multiple_type == "ev_ebitda":
        # Get peer EV/EBITDA multiples
        peer_multiples = [p.get("ev_ebitda") for p in peers if p.get("ev_ebitda") is not None]
        # Compute target EBITDA
        ebitda_margin = target_company.get("ebitda_margin")
        revenue_base = target_company.get("revenue_base")
        target_metric = ebitda_margin * revenue_base if ebitda_margin and revenue_base else None
    elif multiple_type == "pe_ratio":
        # Get peer P/E multiples
        peer_multiples = [p.get("pe_ratio") for p in peers if p.get("pe_ratio") is not None]
        # Placeholder: replace with actual earnings if available
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
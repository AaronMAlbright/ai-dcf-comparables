from sentence_transformers import SentenceTransformer, util
from app.utils.loader import load_company_data
from app.utils.loader import create_company_vector



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


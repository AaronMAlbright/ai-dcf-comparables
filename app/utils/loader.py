import os
import json
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd

# Load model once at module level
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_financial_metrics() -> dict:
    df = pd.read_csv("data/company_metrics.csv")
    print("🧮 Loaded financial metrics:\n", df.head())

    return {row["name"]: row.drop("name").to_dict() for _, row in df.iterrows()}

def load_company_data(target_company_name=None):
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'peers.json')

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Peer data file not found: {file_path}")

    with open(file_path, 'r') as f:
        peer_data = json.load(f)

    # Inject real financial metrics if available
    metrics = load_financial_metrics()
    for peer in peer_data:
        if peer.get("name") in metrics:
            peer.update(metrics[peer["name"]])

    print(f"📊 Injected metrics for: {list(metrics.keys())}")



    # 🧼 Filter non-dict entries just in case
    if isinstance(peer_data, list):
        peer_data = [p for p in peer_data if isinstance(p, dict)]

    # 🧠 Log what's loaded
    peer_names = [p.get("name", "UNKNOWN") for p in peer_data]
    print(f"🧠 LOADED NAMES: {peer_names}")

    # 🧠 Lowercase for matching
    normalized_name = target_company_name.strip().lower() if target_company_name else None

    # 🔍 Find the target peer (case-insensitive)
    target_peer = None
    for peer in peer_data:
        if isinstance(peer, dict):
            peer_name = peer.get("name", "").strip().lower()
            if peer_name == normalized_name:
                target_peer = peer
                break

    # 🔁 Regenerate vectors for any missing ones
    for peer in peer_data:
        if "vector" not in peer or not isinstance(peer["vector"], list):
            print(f"⚠️ Recomputing vector for: {peer.get('name')}")
            peer["vector"] = create_company_vector(peer)

    # 🧪 Confirm match status
    if target_peer is None:
        print(f"❌ Target company '{target_company_name}' not matched.")
    else:
        print(f"✅ Target company matched: {target_peer.get('name')}")

    return target_peer["vector"] if target_peer else None, peer_data

def create_company_vector(company: dict, use_numerics: bool = True) -> np.ndarray:
    """
    Create a vector for similarity comparison from description and numeric fields.

    Args:
        company (dict): Dictionary with company 'description' and optional numerics.
        use_numerics (bool): Whether to include numerical metrics like margins.

    Returns:
        np.ndarray: Combined vector.
    """
    description = company.get("description", "")
    desc_vector = model.encode(description)

    if not use_numerics:
        return desc_vector

    # Choose relevant numeric fields
    numeric_keys = ["revenue_growth", "ebitda_margin", "capex_pct"]
    numerics = [company.get(k, 0.0) for k in numeric_keys]

    # Normalize (z-score)
    numerics = np.array(numerics)
    numerics = (numerics - numerics.mean()) / (numerics.std() + 1e-6)

    return np.concatenate([desc_vector, numerics])

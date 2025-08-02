import os
import json
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from app.utils.vector_cache import get_cached_vector, set_cached_vector
from app.utils.helpers import validate_vector

# Load model once at module level
model = SentenceTransformer('all-MiniLM-L6-v2')


def create_company_vector(company: dict, use_numerics: bool = True) -> np.ndarray:
    """
    Create a vector for similarity comparison from description and numeric fields.
    Ensures final vector is valid (no NaNs or None), and caches the result.
    """
    name = company.get("name", "").strip()

    # ✅ Step 1: Try cache
    cached = get_cached_vector(name)
    if cached and validate_vector(cached):
        print(f"🧠 Loaded cached vector for: {name}")
        return np.array(cached)

    print(f"⚙️ Computing new vector for: {name}")

    # ✅ Step 2: Encode description
    description = company.get("description", name)
    try:
        desc_vector = model.encode(description)
    except Exception as e:
        print(f"❌ Failed to encode description for {name}: {e}")
        return None

    if not use_numerics:
        if validate_vector(desc_vector):
            set_cached_vector(name, desc_vector.tolist())
            return desc_vector
        else:
            print(f"❌ Invalid description-only vector for {name}")
            return None

    # ✅ Step 3: Numeric features
    numeric_keys = ["revenue_growth", "ebitda_margin", "capex_pct"]
    try:
        numerics = [float(company.get(k, 0.0)) for k in numeric_keys]
        numerics = np.array(numerics, dtype=np.float32)
        if np.any(np.isnan(numerics)):
            print(f"❌ NaNs in numeric inputs for {name}: {numerics}")
            return None
        numerics = (numerics - numerics.mean()) / (numerics.std() + 1e-6)
    except Exception as e:
        print(f"❌ Error processing numerics for {name}: {e}")
        return None

    # ✅ Step 4: Combine
    try:
        combined = np.concatenate([desc_vector, numerics])
        if not validate_vector(combined):
            print(f"❌ Combined vector is invalid for {name}")
            return None
        set_cached_vector(name, combined.tolist())
        return combined
    except Exception as e:
        print(f"❌ Vector combination error for {name}: {e}")
        return None


def load_financial_metrics() -> dict:
    df = pd.read_csv("data/company_metrics.csv")
    print("🧮 Loaded financial metrics:\n", df.head())
    return {row["name"]: row.drop("name").to_dict() for _, row in df.iterrows()}


def load_company_data(target_company_name=None):
    file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data',
                             'peers.json')

    print(f"📁 DEBUG: Trying to load this file: {os.path.abspath(file_path)}")
    abs_path = os.path.abspath(file_path)
    print(f"📁 ABSOLUTE path being loaded: {abs_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Peer data file not found: {file_path}")

    with open(file_path, 'r') as f:
        peer_data = json.load(f)

    # 🔍 Debugging: Preview first 3 entries
    print(f"✅ Loaded {len(peer_data)} entries from JSON")
    for i, item in enumerate(peer_data[:3]):
        print(f"  [{i}] {item} — type: {type(item)}")

    print("🔍 Checking for invalid entries in peer_data...")
    for i, peer in enumerate(peer_data):
        if not isinstance(peer, dict):
            print(f"❌ Invalid entry at index {i}: {peer} (type: {type(peer)})")

    # 🧪 Remove malformed entries immediately after loading
    peer_data = [peer for peer in peer_data if isinstance(peer, dict)]

    # Inject real financial metrics if available
    metrics = load_financial_metrics()
    for peer in peer_data:
        if peer.get("name") in metrics:
            peer.update(metrics[peer["name"]])

    print(f"📊 Injected metrics for: {list(metrics.keys())}")

    # 🧠 Log what's loaded
    peer_names = [p.get("name", "UNKNOWN") for p in peer_data]
    print(f"🧠 LOADED NAMES: {peer_names}")

    # 🧠 Lowercase for matching
    normalized_name = target_company_name.strip().lower() if target_company_name else None

    # 🔍 Find the target peer (case-insensitive)
    target_peer = None
    for peer in peer_data:
        if peer.get("name", "").strip().lower() == normalized_name:
            target_peer = peer
            break

    # 🔁 Regenerate vectors for any missing or invalid ones, with safe handling
    for peer in peer_data:
        if not validate_vector(peer.get("vector", None)):
            print(f"⚠️ Recomputing vector for: {peer.get('name')}")
            new_vec = create_company_vector(peer)
            if new_vec is None:
                print(f"❌ Failed to create vector for {peer.get('name')}, leaving vector as None")
                peer["vector"] = None
            else:
                peer["vector"] = new_vec

    print("\n🧠 Final peer vectors validation:")
    for peer in peer_data:
        valid = validate_vector(peer.get("vector"))
        print(f"  {peer.get('name')}: Vector valid? {valid}")

    # 🧪 Confirm match status
    if target_peer is None:
        print(f"❌ Target company '{target_company_name}' not matched.")
    else:
        print(f"✅ Target company matched: {target_peer.get('name')}")

    # Optional: final validation printout
    print("\n🧠 Final vector validation:")
    for peer in peer_data:
        print(f"  {peer.get('name')}: Valid Vector? {validate_vector(peer.get('vector'))}")

    return target_peer["vector"] if target_peer else None, peer_data

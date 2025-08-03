from sentence_transformers import SentenceTransformer, util
from dcf_app.utils.loader import load_company_data, create_company_vector
from dcf_app.utils.helpers import validate_vector
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import torch
import os

# Initialize model and cache settings
model = SentenceTransformer('all-MiniLM-L6-v2')
VECTOR_CACHE_DIR = "vector_cache"
FORCE_REGENERATE_VECTORS = True



def prepare_vectors(company_name=None, target_peer=None,
                    fallback_description=None, fallback_revenue=None, fallback_ebitda_margin=None,
                    desc_weight=0.85):  # NEW

    print(f"\n📥 DEBUG: Calling load_company_data('{company_name}')")
    target_vector, peer_data = load_company_data(
        company_name,
        fallback_description=fallback_description,
        fallback_revenue=fallback_revenue,
        fallback_ebitda_margin=fallback_ebitda_margin
    )

    print(f"📊 Loaded {len(peer_data)} peers")

    # ✅ Match by name or ticker
    target_peer = next(
        (p for p in peer_data if
         p.get("name", "").strip().lower() == company_name.strip().lower()
         or p.get("ticker", "").strip().lower() == company_name.strip().lower()),
        None
    )

    if not target_peer:
        raise ValueError(f"Target company '{company_name}' not found and no fallback provided.")

    # ✅ Generate target vector
    # ✅ Generate target vector
    target_vector = create_company_vector(target_peer, desc_weight=desc_weight)

    if not validate_vector(target_vector):
        raise ValueError(f"Generated target vector for '{company_name}' is invalid.")

    # ✅ Define thread-safe vector caching function
    def cache_peer_vector(peer):
        name = peer.get("name", "").strip()
        safe_name = name.replace("/", "_").replace(",", "").replace(":", "").replace("\\", "_").replace("|", "")
        vector_path = os.path.join(VECTOR_CACHE_DIR, f"{safe_name}.npy")

        if os.path.exists(vector_path):
            try:
                peer["vector"] = np.load(vector_path)
            except Exception:
                peer["vector"] = None
        else:
            vector = create_company_vector(peer, desc_weight=desc_weight)

            if validate_vector(vector):
                np.save(vector_path, vector)
                peer["vector"] = vector
            else:
                peer["vector"] = None

    # ✅ Parallel execution
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(cache_peer_vector, peer): peer for peer in peer_data}
        for future in as_completed(futures):
            peer = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"❌ Error caching vector for {peer.get('name')}: {e}")

    return target_vector, peer_data


def find_closest_peers(target_vector, peer_data, top_k=5,
                       target_name=None, min_similarity=0.0):
    similarities = []

    for peer in peer_data:
        name = peer.get("name", "UNKNOWN")
        vector = peer.get("vector")
        is_self = (name.strip().lower() == target_name.strip().lower()) if target_name else False
        is_valid_vector = validate_vector(vector)

        if is_self or not is_valid_vector:
            continue

        try:
            similarity = util.cos_sim(
                torch.tensor([target_vector], dtype=torch.float32),
                torch.tensor([vector], dtype=torch.float32)
            )[0][0].item()

            if similarity >= min_similarity:
                similarities.append((peer, similarity))
        except Exception as e:
            print(f"❌ Error computing similarity for {name}: {e}")

    top_peers = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
    return top_peers


def apply_peer_multiples(target_company: dict, peers: list, multiple_type: str = "ev_ebitda") -> dict:
    def is_valid_multiple(val):
        return isinstance(val, (int, float)) and 3 <= val <= 30

    if multiple_type == "ev_ebitda":
        # Filter peers with valid EV/EBITDA
        peer_multiples = [
            p.get("ev_ebitda") for p in peers if is_valid_multiple(p.get("ev_ebitda"))
        ]
        ebitda_margin = target_company.get("ebitda_margin")
        revenue_base = target_company.get("revenue_base")

        try:
            if ebitda_margin is None or revenue_base is None:
                raise ValueError("Missing target inputs for EV/EBITDA calculation")
            target_metric = ebitda_margin * revenue_base
        except Exception as e:
            print(f"❌ Error computing target_metric: {e}")
            target_metric = None

    elif multiple_type == "pe_ratio":
        # Filter peers with valid P/E
        peer_multiples = [
            p.get("pe_ratio") for p in peers if is_valid_multiple(p.get("pe_ratio"))
        ]
        target_metric = target_company.get("earnings")

    else:
        raise ValueError("Unsupported multiple type.")

    if not peer_multiples or target_metric is None:
        print(f"⚠️ No valid peers or target metric for {multiple_type} valuation.")
        return {
            "median_multiple": None,
            "target_metric": None,
            "implied_value": None
        }

    median_multiple = np.median(peer_multiples)
    implied_value = median_multiple * target_metric

    return {
        "median_multiple": round(median_multiple, 2),
        "target_metric": round(target_metric, 2),
        "implied_value": round(implied_value, 2)
    }


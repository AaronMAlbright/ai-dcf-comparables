import json
import os

CACHE_PATH = "data/vector_cache.json"

def load_vector_cache():
    """Load the vector cache JSON file, or return an empty dict if not found."""
    if not os.path.exists(CACHE_PATH):
        return {}
    with open(CACHE_PATH, "r") as f:
        return json.load(f)

def save_vector_cache(cache):
    """Save the current cache dictionary to file."""
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)

def get_cached_vector(company_name):
    """Return vector from cache if available, else None."""
    cache = load_vector_cache()
    return cache.get(company_name)

def set_cached_vector(company_name, vector):
    cache = load_vector_cache()
    cache[company_name] = vector
    save_vector_cache(cache)
    print(f"💾 Cached vector for: {company_name}")


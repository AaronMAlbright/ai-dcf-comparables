import os
import json
import yfinance as yf
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from dcf_app.utils.vector_cache import get_cached_vector, set_cached_vector
from dcf_app.utils.helpers import validate_vector
PEER_UNIVERSE_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "peer_universe.csv")




# Load model once at module level
model = SentenceTransformer('all-MiniLM-L6-v2')


def create_company_vector(company: dict, use_numerics: bool = True, desc_weight: float = 0.85) -> np.ndarray:
    name = company.get("name", "").strip()

    cached = get_cached_vector(name)
    if cached and validate_vector(cached):
        print(f"🧠 Loaded cached vector for: {name}")
        return np.array(cached)

    print(f"⚙️ Computing new vector for: {name}")
    description = company.get("description", name)
    try:
        desc_vector = model.encode(description)
    except Exception as e:
        print(f"❌ Failed to encode description for {name}: {e}")
        return None

    if not use_numerics:
        if validate_vector(desc_vector):
            set_cached_vector(name, desc_vector.tolist())
            return np.array(desc_vector)
        else:
            print(f"❌ Invalid description-only vector for {name}")
            return None

    numeric_keys = ["revenue_growth", "ebitda_margin", "capex_pct"]
    try:
        numerics = np.array([float(company.get(k, 0.0)) for k in numeric_keys], dtype=np.float32)

        if np.any(np.isnan(numerics)):
            print(f"⚠️ Skipping {name} due to NaNs in numeric inputs: {numerics}")
            return None

        # Normalize numerics (z-score)
        numerics = (numerics - numerics.mean()) / (numerics.std() + 1e-6)
    except Exception as e:
        print(f"❌ Error processing numerics for {name}: {e}")
        return None

    try:
        # Weight and concatenate
        numerics_weight = 1 - desc_weight
        scaled_desc = desc_vector * desc_weight
        scaled_num = numerics * numerics_weight

        combined = np.concatenate([scaled_desc, scaled_num])
        if not validate_vector(combined):
            print(f"❌ Combined vector is invalid for {name}")
            return None

        set_cached_vector(name, combined.tolist())
        return np.array(combined)

    except Exception as e:
        print(f"❌ Vector combination error for {name}: {e}")
        return None

def load_financial_metrics() -> dict:
    path = "data/company_metrics.csv"
    if not os.path.exists(path):
        return {}
    df = pd.read_csv(path)
    return {row["name"]: row.drop("name").to_dict() for _, row in df.iterrows()}


def try_yfinance_scrape(ticker: str) -> dict:
    try:
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        print(f"🌐 Pulled data from yfinance for {ticker}")

        return {
            "name": ticker.upper(),
            "description": info.get("longBusinessSummary", f"{ticker.upper()} business"),
            "revenue_base": info.get("totalRevenue", 0) / 1e6,  # convert to millions
            "revenue_growth": info.get("revenueGrowth", 0.10),
            "ebitda_margin": info.get("ebitdaMargins", 0.25),
            "capex_pct": 0.05,
            "depreciation_pct": 0.06,
            "nwc_pct": 0.04,
            "tax_rate": 0.21
        }
    except Exception as e:
        print(f"❌ Failed to pull yfinance data for {ticker}: {e}")
        return None


def load_company_data(company_name, fallback_description=None, fallback_revenue=None, fallback_ebitda_margin=None):
    # Load static universe
    if not os.path.exists(PEER_UNIVERSE_CSV):
        raise FileNotFoundError(f"Missing file: {PEER_UNIVERSE_CSV}")

    df = pd.read_csv(PEER_UNIVERSE_CSV)
    peers = df.to_dict(orient="records")

    # Try to find target in static universe
    target = next((p for p in peers if p.get("name", "").strip().lower() == company_name.strip().lower()), None)

    # If not found, try using yfinance
    if not target:
        try:
            ticker = yf.Ticker(company_name)
            info = ticker.info
            description = info.get("longBusinessSummary", "")
            revenue = info.get("totalRevenue", fallback_revenue)
            margin = info.get("ebitdaMargins", fallback_ebitda_margin)

            if description and revenue and margin:
                target = {
                    "name": company_name,
                    "description": description,
                    "revenue_base": revenue,
                    "ebitda_margin": margin,
                    "revenue_growth": 0.08,
                    "capex_pct": 0.04,
                    "nwc_pct": 0.03,
                    "depreciation_pct": 0.05,
                    "tax_rate": 0.21,
                    "ev_ebitda": 16.0,
                    "pe_ratio": 22.0
                }
                peers.append(target)
                print(f"✅ Pulled fallback target data from yfinance for {company_name}")
        except Exception as e:
            print(f"❌ yfinance failed: {e}")

    # If still not found, use manual fallback
    if not target and fallback_description and fallback_revenue and fallback_ebitda_margin:
        target = {
            "name": company_name,
            "description": fallback_description,
            "revenue_base": fallback_revenue,
            "ebitda_margin": fallback_ebitda_margin,
            "revenue_growth": 0.08,
            "capex_pct": 0.04,
            "nwc_pct": 0.03,
            "depreciation_pct": 0.05,
            "tax_rate": 0.21,
            "ev_ebitda": 16.0,
            "pe_ratio": 22.0
        }
        peers.append(target)
        print(f"✅ Using manually provided fallback data for {company_name}")

    # Compute target vector if description exists
    if target and "vector" not in target and "description" in target:
        target["vector"] = model.encode(target["description"])

    print(f"🔍 Loading peer universe from: {PEER_UNIVERSE_CSV}")

    return target["vector"], peers




def load_peer_universe(path="data/peer_universe.csv"):
    df = pd.read_csv(path)
    return df.to_dict(orient="records")

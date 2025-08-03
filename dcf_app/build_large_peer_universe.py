import os
import yfinance as yf
import pandas as pd
from tqdm import tqdm
from collections import defaultdict

# === Output Folder and File ===
output_dir = os.path.join("dcf_app", "data")
os.makedirs(output_dir, exist_ok=True)
combined_output_path = os.path.join(output_dir, "peer_universe.csv")

# === Config ===
TICKER_SOURCE = "https://datahub.io/core/nasdaq-listings/r/nasdaq-listed-symbols.csv"
EXCLUDED_SECTORS = {"Biotechnology", "Shell Companies", "SPACs", "Blank Check", None}
MIN_REVENUE = 50_000_000
VALID_MULTIPLE_RANGE = (3, 30)

def get_all_tickers():
    try:
        df = pd.read_csv(TICKER_SOURCE)
        tickers = df['Symbol'].dropna().tolist()
        return [t for t in tickers if t.isalpha() and len(t) <= 5]
    except Exception as e:
        print(f"❌ Failed to fetch tickers: {e}")
        return []

def calculate_revenue_growth(ticker_obj):
    try:
        rev = ticker_obj.quarterly_financials.loc["Total Revenue"]
        if rev.shape[0] < 5:
            return None
        latest = rev.iloc[0:4].sum()
        previous = rev.iloc[4:8].sum()
        if previous == 0:
            return None
        return (latest - previous) / previous
    except:
        return None

def is_valid_company(row):
    try:
        if not all([
            row["name"], row["sector"], row["industry"],
            row["revenue_base"], row["description"]
        ]):
            return False

        if row["sector"] in EXCLUDED_SECTORS:
            return False

        if row["revenue_base"] < MIN_REVENUE:
            return False

        if row["ev_ebitda"] is None or not (VALID_MULTIPLE_RANGE[0] <= row["ev_ebitda"] <= VALID_MULTIPLE_RANGE[1]):
            return False

        return True
    except:
        return False

def build_peer_universe():
    tickers = get_all_tickers()
    print(f"🔍 Found {len(tickers)} tickers to scan...")

    existing_tickers = set()
    if os.path.exists(combined_output_path):
        existing_df = pd.read_csv(combined_output_path)
        existing_tickers = set(existing_df['ticker'].tolist())

    sector_to_rows = defaultdict(list)
    saved, skipped = 0, 0

    for ticker in tqdm(tickers[:2000]):
        if ticker in existing_tickers:
            continue

        try:
            t = yf.Ticker(ticker)
            info = t.info

            row = {
                "ticker": ticker,
                "name": info.get("shortName") or info.get("longName"),
                "description": info.get("longBusinessSummary", "").strip(),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "revenue_base": info.get("totalRevenue"),
                "revenue_growth": calculate_revenue_growth(t),
                "ebitda_margin": info.get("ebitdaMargins"),
                "ev_ebitda": info.get("enterpriseToEbitda"),
                "pe_ratio": info.get("trailingPE"),
            }

            if not is_valid_company(row):
                skipped += 1
                continue

            sector_key = row["sector"].lower().replace(" ", "_")
            sector_to_rows[sector_key].append(row)
            saved += 1

        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")
            skipped += 1
            continue

    # ✅ Save cleaned results
    full_dataset = []
    for sector_key, rows in sector_to_rows.items():
        df_sector = pd.DataFrame(rows)
        path = os.path.join(output_dir, f"peer_universe_{sector_key}.csv")
        df_sector.to_csv(path, index=False)
        print(f"📁 Saved {len(df_sector)} companies → {path}")
        full_dataset.extend(rows)

    pd.DataFrame(full_dataset).to_csv(combined_output_path, index=False)
    print(f"\n📦 Combined peer universe saved → {combined_output_path}")
    print(f"✅ Final stats: {saved} saved, {skipped} skipped")

if __name__ == "__main__":
    build_peer_universe()

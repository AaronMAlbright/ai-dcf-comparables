import os
import time
import yfinance as yf
import pandas as pd

# ✅ High-quality large caps — consistent data
tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "TSLA", "NVDA", "V", "MA", "JPM", "UNH",
    "HD", "DIS", "PEP", "KO", "XOM", "BAC"
]

rows = []
output_path = os.path.join("dcf_app", "data", "peer_universe.csv")

def calculate_revenue_growth(ticker_obj):
    try:
        rev = ticker_obj.quarterly_financials.loc["Total Revenue"]
        if rev.shape[0] < 5:
            return None
        latest = rev.iloc[0:4].sum()
        previous = rev.iloc[4:8].sum()
        if previous == 0:
            return None
        return round((latest - previous) / previous, 4)
    except Exception:
        return None

for i, ticker in enumerate(tickers):
    try:
        t = yf.Ticker(ticker)
        info = t.info

        revenue = info.get("totalRevenue")
        ebitda = info.get("ebitda")
        pe_ratio = info.get("trailingPE")
        ev = info.get("enterpriseValue")

        sector = info.get("sector", "")
        industry = info.get("industry", "")
        name = info.get("longName", ticker)

        # Compute EV/EBITDA
        ev_ebitda = ev / ebitda if ev and ebitda and ebitda != 0 else None

        # Compute EBITDA Margin
        ebitda_margin = ebitda / revenue if ebitda and revenue else None

        # Compute Revenue Growth from quarterly data
        revenue_growth = calculate_revenue_growth(t)

        # Basic filter
        if revenue is None or pe_ratio is None:
            print(f"⏭️ Skipping {ticker}: insufficient data")
            continue

        row = {
            "ticker": ticker,
            "name": name,
            "description": sector,
            "sector": sector,
            "industry": industry,
            "revenue_base": round(revenue / 1e6, 2),
            "revenue_growth": revenue_growth,
            "ebitda_margin": round(ebitda_margin, 4) if ebitda_margin else None,
            "ev_ebitda": round(ev_ebitda, 2) if ev_ebitda else None,
            "pe_ratio": round(pe_ratio, 2),
        }

        rows.append(row)
        print(f"✅ [{i+1}/{len(tickers)}] Added {ticker}")
        time.sleep(1)

    except Exception as e:
        print(f"❌ Error for {ticker}: {e}")

# Save
df = pd.DataFrame(rows)
df.to_csv(output_path, index=False)
print(f"\n📁 Saved {len(df)} valid peer companies to {output_path}")

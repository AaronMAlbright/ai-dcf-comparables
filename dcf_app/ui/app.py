import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json
import os
import io
import yfinance as yf
import sys

# ✅ Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dcf_app.services.peer_matcher_service import run_peer_match_pipeline

# ✅ Paths
RESULTS_PATH = "results/output_summary.json"
SENS_PATH = "results/sensitivity_matrix.csv"

# ✅ UI setup
st.set_page_config(page_title="AI-Powered DCF & Peer Valuation", layout="wide")
st.title("📊 AI-Powered DCF & Peer Valuation Dashboard")

# Sidebar
st.sidebar.header("🔧 Controls")
st.sidebar.markdown("Adjust inputs below or rerun the backend to refresh results.")
ticker_input = st.sidebar.text_input("🔎 Lookup by Ticker (e.g. AAPL)", value="").upper()

# ✅ Clear stale results if no ticker is typed
if not ticker_input:
    result = {}
elif os.path.exists(RESULTS_PATH):
    with open(RESULTS_PATH, "r") as f:
        result = json.load(f)
else:
    result = {}

# ✅ Show company info
if ticker_input:
    try:
        ticker = yf.Ticker(ticker_input)
        info = ticker.info
        st.sidebar.markdown(f"**Company:** {info.get('shortName', 'N/A')}")
        st.sidebar.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
        st.sidebar.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
        st.sidebar.markdown(f"**Description:** {info.get('longBusinessSummary', 'N/A')[:300]}...")
    except Exception as e:
        st.sidebar.error(f"Failed to fetch info for {ticker_input}: {e}")

# ✅ Run pipeline if new ticker
if ticker_input:
    try:
        ticker_obj = yf.Ticker(ticker_input)
        info = ticker_obj.info
        short_name = info.get("shortName", ticker_input)
        description = info.get("longBusinessSummary", "")
        revenue = info.get("totalRevenue")
        ebitda_margin = info.get("ebitdaMargins")

        if short_name and description and revenue and ebitda_margin:
            st.sidebar.success(f"Running valuation for {short_name}...")

            # Only run if not already saved
            if result.get("ticker") != ticker_input:
                run_result = run_peer_match_pipeline(
                    company_name=ticker_input,
                    wacc=0.10,
                    terminal_growth=0.03,
                    dcf_weight=0.5,
                    top_n_peers=5,
                    min_similarity=0.0,
                    verbose=False,
                    multiple_type="ev_ebitda",
                    fallback_description=description,
                    fallback_revenue=revenue / 1e6 if revenue else None,
                    fallback_ebitda_margin=ebitda_margin
                )
                if run_result:
                    run_result["ticker"] = ticker_input  # ✅ Save for comparison
                    print("🪵 Keys in run_result:", run_result.keys())
                    print("🪵 Terminal Value Info Preview:",
                          run_result.get("terminal_value_info"))

                    with open(RESULTS_PATH, "w") as f:
                        print("🪵 Keys in run_result:", run_result.keys())
                        print("🪵 Terminal Value Info Preview:",
                              run_result.get("terminal_value_info"))

                        json.dump(run_result, f, indent=2)
                    st.rerun()
                else:
                    st.sidebar.error("❌ Pipeline failed to produce results.")
        else:
            st.sidebar.warning("⚠️ Missing data for this ticker. Try another.")
    except Exception as e:
        st.sidebar.error(f"Pipeline failed: {e}")

# ✅ Load results for display
company_name = result.get("company_name", "N/A")
dcf_value = result.get("dcf_value", 0)
peer_value = result.get("peer_value", 0)
combined_valuation = result.get("combined_valuation", 0)

# Sliders
wacc_range = st.sidebar.slider("WACC Range", 0.08, 0.12, (0.08, 0.12), step=0.005)
tgr_range = st.sidebar.slider("Terminal Growth Range", 0.02, 0.04, (0.02, 0.04), step=0.002)

# Summary Metrics
col1, col2, col3 = st.columns(3)
col1.metric("🧮 DCF Value", f"${dcf_value:,.0f}")
col2.metric("📊 Peer Value", f"${peer_value:,.0f}")
col3.metric("💰 Combined Valuation", f"${combined_valuation:,.0f}")
# Terminal Value Info (Optional Detail)
if "terminal_info" in result:
    st.subheader("🏁 Terminal Value Details")
    t_info = result["terminal_info"]

    st.markdown(f"""
    - **Method**: {t_info.get("method", "N/A")}
    - **Terminal Value**: ${t_info.get("terminal_value", 0):,.0f}
    - **Exit Multiple Used**: {t_info.get("exit_multiple", "N/A")}
    - **Final FCF Year**: ${t_info.get("final_fcf", 0):,.0f}  # <-- FIXED HERE
    - **Discounted Terminal Value**: ${t_info.get("discounted_terminal_value", 0):,.0f}
    """)



# Peer Table
st.subheader("🔍 Top Peer Matches")
peer_df = pd.DataFrame(result.get("top_peers", []))
if not peer_df.empty:
    peer_df.columns = ["Peer Name", "Similarity", "EV/EBITDA", "P/E"]
    st.dataframe(peer_df, use_container_width=True)
else:
    st.warning("No peer matches found. Try a different ticker.")

# Sensitivity Heatmap
st.subheader("🔥 DCF Sensitivity Heatmap (WACC ↓ vs TGR →)")
if os.path.exists(SENS_PATH):
    sens_df = pd.read_csv(SENS_PATH, index_col=0)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(sens_df, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax)
    st.pyplot(fig)
else:
    st.warning("No sensitivity_matrix.csv found. Run with --wacc_range and --terminal_growth_range.")

# Exports
st.subheader("📥 Export Results")
csv_buffer = io.StringIO()
if not peer_df.empty:
    peer_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download Peers as CSV",
        data=csv_buffer.getvalue(),
        file_name="peer_matches.csv",
        mime="text/csv"
    )

json_data = json.dumps(result, indent=2)
st.download_button(
    label="📥 Download Full Results (JSON)",
    data=json_data,
    file_name="valuation_results.json",
    mime="application/json"
)

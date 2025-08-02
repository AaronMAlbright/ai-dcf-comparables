import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json
import os

st.set_page_config(page_title="AI-Powered DCF & Peer Valuation", layout="wide")
st.title("📊 AI-Powered DCF & Peer Valuation Dashboard")

# Load the latest output JSON
RESULTS_PATH = "results/output_summary.json"
SENS_PATH = "results/sensitivity_matrix.csv"

if not os.path.exists(RESULTS_PATH):
    st.error("No output_summary.json found. Please run the pipeline first.")
    st.stop()

with open(RESULTS_PATH, "r") as f:
    result = json.load(f)

# Sidebar Inputs
st.sidebar.header("🔧 Controls")
st.sidebar.markdown("Adjust inputs below or rerun the backend to refresh results.")

company_name = result.get("company_name", "N/A")
dcf_value = result.get("dcf_value", 0)
peer_value = result.get("peer_value", 0)
combined_valuation = result.get("combined_valuation", 0)

# Sensitivity sliders (placeholder if dynamic range added later)
wacc_range = st.sidebar.slider("WACC Range", 0.08, 0.12, (0.08, 0.12), step=0.005)
tgr_range = st.sidebar.slider("Terminal Growth Range", 0.02, 0.04, (0.02, 0.04), step=0.002)

# Main Summary
col1, col2, col3 = st.columns(3)
col1.metric("🧮 DCF Value", f"${dcf_value:,.0f}")
col2.metric("📊 Peer Value", f"${peer_value:,.0f}")
col3.metric("💰 Combined Valuation", f"${combined_valuation:,.0f}")

# Peer Table
st.subheader("🔍 Top Peer Matches")
peer_df = pd.DataFrame(result["top_peers"])
peer_df.columns = ["Peer Name", "Similarity", "EV/EBITDA", "P/E"]
st.dataframe(peer_df, use_container_width=True)

# Sensitivity Heatmap
st.subheader("🔥 DCF Sensitivity Heatmap (WACC ↓ vs TGR →)")

if os.path.exists(SENS_PATH):
    sens_df = pd.read_csv(SENS_PATH, index_col=0)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(sens_df, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax)
    st.pyplot(fig)
else:
    st.warning("No sensitivity_matrix.csv found. Run with --wacc_range and --terminal_growth_range.")

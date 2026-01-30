![Image 8-2-25 at 12 20 AM](https://github.com/user-attachments/assets/39166ed6-39ad-45e6-8fa0-faa0a8adad8c)
Automated-DCF-Engine-with-NLP-Based-Peer-Matching
Automated DCF Engine with NLP-Based Peer Matching

AI-Powered DCF Valuation & Comparable Company Engine
A Python-based financial valuation platform that automates discounted cash flow (DCF) analysis and intelligently identifies comparable companies using NLP and financial similarity metrics. Incorporates derivative overlays via QuantLib for option-based valuation stress testing.

 Features
 Automated DCF Modeling for public companies
 WACC, Terminal Value, Sensitivity Analysis
 NLP-Based Peer Matching using business descriptions and financial ratios
 QuantLib Integration for derivative pricing overlays (e.g., options, credit models)
 Modular, API-ready architecture with optional Docker/Streamlit deployment
Compatible with AWS/GCP deployment and cron-based automation
Sample Output
Dashboard Screenshot
![Image 8-2-25 at 12 20 AM](https://github.com/user-attachments/assets/39166ed6-39ad-45e6-8fa0-faa0a8adad8c)

Ticker	DCF Value	Current Price	Upside	Top Comparables
AAPL	$195.23	$208.10	-6.2%	MSFT, GOOGL, META
How It Works
Data Collection

Pulls financials from Yahoo Finance or FMP API
Scrapes company descriptions or uses openai for enhanced context
DCF Engine

Forecasts revenue, EBIT, CapEx, D&A, NWC
Calculates FCF, WACC, terminal value
Outputs intrinsic equity value
Comparable Matching

Uses vector embeddings (e.g., Sentence-BERT or OpenAI) for business model similarity
Ranks peer companies by qualitative + financial proximity
Derivatives Integration (Optional)

QuantLib used to price equity options and calculate implied volatility overlays
Can apply Merton model for credit-adjusted valuation
Tech Stack
Python 3.10+
pandas, numpy, yfinance, scikit-learn
QuantLib, sentence-transformers, openai (optional)
FastAPI / Streamlit (frontend or API)
Docker-ready for deployment
PostgreSQL / SQLite (for persistence, optional)
Installation
git clone https://github.com/yourusername/dcf-ai-comparables.git
cd dcf-ai-comparables
pip install -r requirements.txt

from dcf_app.utils.loader import create_company_vector
import numpy as np

def main():
    # Sample company
    sample = {
        "name": "Test Co",
        "description": "A leading provider of cloud analytics and AI-driven business intelligence solutions.",
        "revenue_growth": 0.15,
        "ebitda_margin": 0.25,
        "capex_pct": 0.05
    }

    # Run vector creation
    vector = create_company_vector(sample)

    # Validate output
    if isinstance(vector, np.ndarray):
        print(f"✅ Vector shape: {vector.shape}")
        print(f"🔢 Vector preview: {vector[:10]}")
    else:
        print("❌ Failed to generate valid vector.")

if __name__ == "__main__":
    main()

from app.models.dcf_generator import mock_dcf_valuation

def run_sensitivity_analysis(peer):
    print(f"\n[Sensitivity Analysis] {peer} Valuation Under Varying Growth Rates:")

    # Example range of growth rates to test sensitivity
    growth_rates = [0.01, 0.03, 0.05]

    for growth in growth_rates:
        valuation = mock_dcf_valuation(peer, growth=growth)
        print(f"  Growth: {growth:.0%} → DCF Valuation: ${valuation:.2f}M")

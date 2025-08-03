def forecast_3_statement(
    revenue_base: float,
    revenue_growth: float,
    ebitda_margin: float,
    capex_pct: float,
    depreciation_pct: float,
    nwc_pct: float,
    tax_rate: float,
    interest_expense: float = 0.0,
    debt: float = 0.0,
    years: int = 5
) -> dict:
    """
    Forecasts income statement, balance sheet, and cash flow statement to produce FCF.
    Returns a dictionary of yearly outputs including revenue, EBIT, NOPAT, D&A, CapEx, ∆NWC, and FCF.
    """

    # Defensive defaults in case any critical input is None
    revenue_base = revenue_base or 0.0
    revenue_growth = revenue_growth or 0.0
    ebitda_margin = ebitda_margin or 0.0
    depreciation_pct = depreciation_pct or 0.0
    capex_pct = capex_pct or 0.0
    nwc_pct = nwc_pct or 0.0
    tax_rate = tax_rate or 0.21  # assume standard US corp tax

    results = []
    revenue = revenue_base

    for _ in range(years):
        revenue *= (1 + revenue_growth)
        ebitda = revenue * ebitda_margin
        depreciation = revenue * depreciation_pct
        ebit = ebitda - depreciation
        nopat = ebit * (1 - tax_rate)
        capex = revenue * capex_pct
        change_nwc = revenue * nwc_pct
        fcf = nopat + depreciation - capex - change_nwc

        results.append({
            "revenue": revenue,
            "ebitda": ebitda,
            "depreciation": depreciation,
            "ebit": ebit,
            "nopat": nopat,
            "capex": capex,
            "change_nwc": change_nwc,
            "fcf": fcf
        })

    return results


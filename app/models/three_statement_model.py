def forecast_3_statement(
    revenue_base: float,
    revenue_growth: float,
    ebitda_margin: float,
    capex_pct: float,
    depreciation_pct: float,
    nwc_pct: float,
    tax_rate: float,
    interest_expense: float,
    debt: float,
    years: int = 5
) -> dict:
    """
    Forecasts income statement, balance sheet, and cash flow statement to produce FCF.
    Returns a dictionary of yearly outputs including revenue, EBIT, NOPAT, D&A, CapEx, ∆NWC, and FCF.
    """
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

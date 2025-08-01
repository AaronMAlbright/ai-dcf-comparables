def calculate_dcf(fcf_forecast: list, wacc: float,
                  terminal_growth: float) -> float:
    """
    Discount projected Free Cash Flows to present value using WACC and a terminal growth rate.

    Parameters:
    - fcf_forecast: list of forecasted FCFs per year
    - wacc: Weighted Average Cost of Capital (as a decimal, e.g., 0.09 for 9%)
    - terminal_growth: Terminal growth rate (as a decimal, e.g., 0.02 for 2%)

    Returns:
    - Net Present Value (NPV) of the business
    """
    npv = 0.0
    for t, fcf in enumerate(fcf_forecast, start=1):
        npv += fcf / ((1 + wacc) ** t)

    # Terminal Value using perpetuity growth model
    terminal_value = fcf_forecast[-1] * (1 + terminal_growth) / (
                wacc - terminal_growth)
    terminal_pv = terminal_value / ((1 + wacc) ** len(fcf_forecast))

    return npv + terminal_pv

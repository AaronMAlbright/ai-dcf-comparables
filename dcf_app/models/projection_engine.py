from dcf_app.models.three_statement_model import forecast_3_statement
from dcf_app.models.dcf_model import discounted_cash_flow

def project_valuation(*args, wacc=0.10, terminal_growth=0.03, **kwargs) -> float:
    """
    Full pipeline: generate FCFs from inputs, then run DCF to estimate value.

    Args:
        kwargs: Inputs for 3-statement forecast
        wacc (float): Discount rate
        terminal_growth (float): Terminal value growth assumption

    Returns:
        float: Enterprise value from DCF
    """
    valid_keys = {
        "revenue_base", "revenue_growth", "ebitda_margin",
        "depreciation_pct", "capex_pct", "nwc_pct", "tax_rate",
        "interest_expense", "debt"
    }

    filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_keys}

    forecast = forecast_3_statement(**filtered_kwargs)
    fcfs = [year["fcf"] for year in forecast]

    value = discounted_cash_flow(fcfs, wacc=wacc, terminal_growth=terminal_growth)

    return value

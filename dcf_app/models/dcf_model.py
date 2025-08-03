def discounted_cash_flow(
    fcfs: list[float],
    wacc: float = 0.10,
    terminal_growth: float = 0.03,
    exit_multiple: float = None,
    method: str = "perpetuity"
) -> tuple[float, dict]:
    """
    Performs a mid-year DCF valuation with optional terminal value method.

    Args:
        fcfs: Forecasted Free Cash Flows (in millions)
        wacc: Weighted Average Cost of Capital
        terminal_growth: Growth rate for terminal value
        exit_multiple: Optional exit multiple to override perpetuity method
        method: 'perpetuity' or 'exit'

    Returns:
        Tuple: (enterprise value, terminal value breakdown dict)
    """
    n = len(fcfs)
    discounted_fcfs = []

    for t, fcf in enumerate(fcfs, start=1):
        df = 1 / ((1 + wacc) ** (t - 0.5))  # Mid-year convention
        discounted_fcfs.append(fcf * df)

    # Terminal Value Calculation
    final_fcf = fcfs[-1]
    if method == "exit" and exit_multiple is not None:
        terminal_value = final_fcf * exit_multiple
    else:
        terminal_value = final_fcf * (1 + terminal_growth) / (wacc - terminal_growth)
        method = "perpetuity"  # Force label

    terminal_discounted = terminal_value / ((1 + wacc) ** (n - 0.5))
    npv = sum(discounted_fcfs) + terminal_discounted

    return npv, {
        "final_fcf": fcfs[-1],
        "discounted_terminal_value": terminal_discounted,
        "terminal_value": terminal_value,
        "method": method,
        "exit_multiple": exit_multiple
    }


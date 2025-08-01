def discounted_cash_flow(fcfs: list[float], wacc: float = 0.10, terminal_growth: float = 0.03) -> float:
    """
    Performs a simple mid-year DCF valuation.

    Args:
        fcfs: Forecasted Free Cash Flows (in millions)
        wacc: Weighted Average Cost of Capital
        terminal_growth: Growth rate for terminal value

    Returns:
        Estimated enterprise value (in millions)
    """
    n = len(fcfs)
    discounted_fcfs = []

    for t, fcf in enumerate(fcfs, start=1):
        df = 1 / ((1 + wacc) ** (t - 0.5))  # Mid-year convention
        discounted_fcfs.append(fcf * df)

    terminal_value = fcfs[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    terminal_discounted = terminal_value / ((1 + wacc) ** (n - 0.5))

    return sum(discounted_fcfs) + terminal_discounted

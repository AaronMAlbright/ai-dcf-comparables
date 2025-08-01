def run_sensitivity_analysis(project_fcf_func, calculate_dcf_func, base_wacc=0.09, base_terminal_growth=0.02, **kwargs):
    """
    Runs a basic sensitivity analysis on WACC and terminal growth rate.

    Args:
        project_fcf_func: Function to project FCFs.
        calculate_dcf_func: Function to calculate DCF from projected FCFs.
        base_wacc: Base WACC to center the sensitivity range.
        base_terminal_growth: Base terminal growth rate to center the sensitivity range.
        **kwargs: Additional inputs passed to the FCF projection function.

    Returns:
        A nested dictionary of DCF values indexed by (WACC, Terminal Growth).
    """
    results = {}

    wacc_range = [round(base_wacc + delta, 3) for delta in [-0.01, 0, 0.01]]
    tg_range = [round(base_terminal_growth + delta, 3) for delta in [-0.01, 0, 0.01]]

    for wacc in wacc_range:
        for tg in tg_range:
            fcf_forecast = project_fcf_func(**kwargs)
            dcf_value = calculate_dcf_func(fcf_forecast, wacc=wacc, terminal_growth=tg)
            results[(wacc, tg)] = dcf_value

    return results

import numpy as np

def calculate_dcf(fcf_forecast, discount_rate, terminal_growth_rate):
    """
    Calculate the DCF value from forecasted free cash flows.

    :param fcf_forecast: list of forecasted FCFs for N years
    :param discount_rate: WACC / discount rate as decimal (e.g., 0.10 for 10%)
    :param terminal_growth_rate: terminal growth rate (e.g., 0.02 for 2%)
    :return: intrinsic value (DCF sum)
    """
    dcf_value = 0
    for t, fcf in enumerate(fcf_forecast, start=1):
        dcf_value += fcf / ((1 + discount_rate) ** t)

    # Terminal Value (Gordon Growth)
    terminal_value = fcf_forecast[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
    terminal_discounted = terminal_value / ((1 + discount_rate) ** len(fcf_forecast))

    return dcf_value + terminal_discounted

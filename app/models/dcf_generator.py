import random
from app.models.three_statement_model import forecast_3_statement
from app.models.dcf_model import discounted_cash_flow
import numpy as np

def run_sensitivity_analysis(
    forecast: list[dict],
    wacc_range: tuple,
    terminal_growth_range: tuple,
    step: float = 0.01
) -> dict:
    """
    Builds a sensitivity table of DCF valuations over WACC and terminal growth rate ranges.

    Args:
        forecast (list[dict]): List of forecasted financials per year (must include 'fcf')
        wacc_range (tuple): (min_wacc, max_wacc)
        terminal_growth_range (tuple): (min_tgr, max_tgr)
        step (float): increment for both axes (default 0.01)

    Returns:
        dict: {
            "wacc_values": [...],
            "terminal_growth_values": [...],
            "valuation_matrix": [[...], [...], ...]
        }
    """
    fcfs = [year.get("fcf", 0) for year in forecast]
    if not fcfs:
        raise ValueError("⚠️ No forecasted FCFs found for sensitivity analysis.")

    wacc_values = np.arange(wacc_range[0], wacc_range[1] + step, step)
    tg_values = np.arange(terminal_growth_range[0], terminal_growth_range[1] + step, step)

    matrix = []
    for wacc in wacc_values:
        row = []
        for tg in tg_values:
            try:
                value = discounted_cash_flow(fcfs, wacc=wacc, terminal_growth=tg)
                row.append(round(value, 2))
            except Exception:
                row.append(None)
        matrix.append(row)

    return {
        "wacc_values": wacc_values.tolist(),
        "terminal_growth_values": tg_values.tolist(),
        "valuation_matrix": matrix
    }

def mock_dcf_valuation(company_description: str) -> float:
    """
    Temporary placeholder DCF logic for early UI testing or stubbing.
    """
    base_value = 100  # In millions
    multiplier = random.uniform(0.8, 1.5)
    return base_value * multiplier

def generate_forecasted_fcfs(inputs: dict) -> list:
    """
    Forecast FCFs using the 3-statement model based on input assumptions.

    Args:
        inputs (dict): Model assumptions (e.g., revenue, margins, capex, etc.)

    Returns:
        list: Forecasted Free Cash Flows
    """
    forecast = forecast_3_statement(**inputs)
    fcfs = [year["fcf"] for year in forecast]
    return fcfs


def run_dcf_from_inputs(inputs: dict, wacc: float = 0.10,
                        terminal_growth: float = 0.03) -> float:
    """
    Complete DCF valuation from raw inputs.

    Args:
        inputs (dict): Model assumptions
        wacc (float): Discount rate
        terminal_growth (float): Terminal value growth assumption

    Returns:
        float: Enterprise value from DCF
    """
    required_keys = [
        'revenue_base',
        'revenue_growth',
        'ebitda_margin',
        'capex_pct',
        'depreciation_pct',
        'nwc_pct',
        'tax_rate'
    ]
    filtered_inputs = {k: v for k, v in inputs.items() if k in required_keys}

    missing = [k for k in required_keys if k not in filtered_inputs]
    if missing:
        raise ValueError(f"Missing required inputs for DCF: {missing}")

    fcfs = generate_forecasted_fcfs(filtered_inputs)
    value = discounted_cash_flow(fcfs, wacc=wacc,
                                 terminal_growth=terminal_growth)
    return value


def generate_dcf(forecast: list[dict], wacc: float = 0.10, terminal_growth: float = 0.03) -> dict:
    """
    Compute DCF valuation from a full 3-statement forecast.

    Args:
        forecast (list[dict]): List of forecasted financials per year (must include 'fcf')
        wacc (float): Discount rate
        terminal_growth (float): Terminal growth rate

    Returns:
        dict: Valuation breakdown
    """
    fcfs = [year.get("fcf", 0) for year in forecast]
    if not fcfs:
        raise ValueError("⚠️ Forecasted FCFs not found in input.")

    # Run existing DCF model
    value = discounted_cash_flow(fcfs, wacc=wacc, terminal_growth=terminal_growth)

    return {
        "value": value,
        "fcfs": fcfs,
        "wacc": wacc,
        "terminal_growth": terminal_growth
    }

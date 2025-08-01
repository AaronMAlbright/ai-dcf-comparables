import pytest
from app.models.projection_engine import project_valuation

def test_project_valuation_output():
    inputs = {
        "revenue_base": 150.0,
        "revenue_growth": 0.06,
        "ebitda_margin": 0.30,
        "capex_pct": 0.07,
        "depreciation_pct": 0.05,
        "nwc_pct": 0.04,
        "tax_rate": 0.21,
        "interest_expense": 0.0,  # or a real assumption
        "debt": 0.0               # or a real assumption
    }

    valuation = project_valuation(**inputs)
    assert isinstance(valuation, float)
    assert valuation > 0


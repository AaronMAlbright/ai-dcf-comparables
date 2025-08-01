from app.models.three_statement_model import forecast_3_statement


def project_fcf(*args, **kwargs):
    # Add required FCF drivers
    valid_keys = {
        "revenue_base", "revenue_growth", "ebitda_margin",
        "depreciation_pct", "interest_expense", "debt",
        "capex_pct", "nwc_pct", "tax_rate"
    }
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_keys}

    forecasts = forecast_3_statement(**filtered_kwargs)
    return [year["fcf"] for year in forecasts]

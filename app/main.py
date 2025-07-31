from app.data.loader import get_financials
from app.models.dcf_model import calculate_dcf

# Example
ticker = "MSFT"
financials = get_financials(ticker)

print(f"Loaded financials for {financials['longName']}")

# Dummy FCF forecast (in millions)
fcf_forecast = [20000, 22000, 24000, 26000, 28000]
discount_rate = 0.09
terminal_growth = 0.03

value = calculate_dcf(fcf_forecast, discount_rate, terminal_growth)
print(f"Estimated DCF value: ${round(value, 2)} million")

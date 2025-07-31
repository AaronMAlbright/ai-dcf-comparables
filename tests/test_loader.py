from app.data.loader import get_financials

def test_get_financials_returns_data():
    result = get_financials("AAPL")
    assert "ticker" in result
    assert result["ticker"] == "AAPL"
    assert result["cashflow"] is not None

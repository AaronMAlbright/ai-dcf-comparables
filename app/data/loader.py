import yfinance as yf

def get_financials(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    cashflow = stock.cashflow
    return {
        'ticker': ticker,
        'longName': info.get('longName', ''),
        'marketCap': info.get('marketCap', None),
        'cashflow': cashflow
    }

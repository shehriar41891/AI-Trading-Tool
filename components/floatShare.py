import yfinance as yf

# Replace 'AAPL' with the ticker symbol of the stock you're interested in
ticker = "AAPL"

# Fetch stock data
stock = yf.Ticker(ticker)

# Get float shares
float_shares = stock.info.get("floatShares")

if float_shares:
    print(f"Float shares for {ticker}: {float_shares}")
else:
    print(f"Float shares data is not available for {ticker}.")

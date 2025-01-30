import os
from polygon import RESTClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Polygon API key
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

# Initialize the Polygon API client
client = RESTClient(POLYGON_API_KEY)

def get_weighted_shares_polygon(ticker):
    try:
        # Fetch the ticker details using the Polygon API client
        ticker_details = client.get_ticker_details(ticker)
        
        # Print the available attributes of the response object for debugging
        print("Ticker Details:", dir(ticker_details))
        
        # Access weighted shares outstanding
        if hasattr(ticker_details, 'weighted_shares_outstanding'):
            weighted_shares = ticker_details.weighted_shares_outstanding
            print(f"Weighted shares outstanding for {ticker}: {weighted_shares}")
            return weighted_shares
        else:
            print(f"Weighted shares outstanding data is not available for {ticker}.")
            return None
            
    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return None

# Example Usage
# ticker = "AAPL"  # Replace with your desired stock ticker
# get_weighted_shares_polygon(ticker)

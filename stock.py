import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
from polygon import RESTClient
from dotenv import load_dotenv
import os
from time import sleep

# Load environment variables from .env file
load_dotenv()
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

# Initialize the Polygon API client
client = RESTClient(POLYGON_API_KEY)

# Static list of NASDAQ 100 stocks (add the full list)
nasdaq_100_stocks = ["AMZN"]

def get_stocks(stock):
    retries = 5  # Maximum retry attempts
    delay = 5  # Initial delay (in seconds) between retries
    for attempt in range(retries):
        try:
            # Fetch data using `list_aggs` method for hourly aggregation
            aggs = []
            for a in client.list_aggs(
                ticker=stock,
                multiplier=1,
                timespan="hour",  
                from_="2025-01-24",  # Start date
                to="2025-01-24",  # End date
                limit=50000
            ):
                aggs.append(a)

            if not aggs:
                print(f"No data returned for {stock}")
                return pd.DataFrame()  # Return empty DataFrame if no data

            data = []
            for agg in aggs:
                data.append({
                    'timestamp': pd.to_datetime(agg.timestamp, unit='ms'),
                    'open': agg.open,
                    'high': agg.high,
                    'low': agg.low,
                    'close': agg.close,
                    'volume': agg.volume
                })

            stock_data = pd.DataFrame(data)
            print(f"Fetched data for {stock}: {stock_data.head()}")
            return stock_data
        except Exception as e:
            if '429' in str(e):  # Handle rate-limiting errors
                print(f"Rate-limiting error for {stock}. Retrying in {delay} seconds...")
                sleep(delay)
                delay *= 2  # Exponential backoff
                continue  # Retry the request
            else:
                print(f"Error fetching data for {stock}: {e}")
                return pd.DataFrame()  # Return an empty DataFrame in case of other errors
    return pd.DataFrame()  # Return an empty DataFrame if retries fail

# Create a Dash app
app = dash.Dash(__name__)

# Function to generate a candlestick chart
def create_candlestick_figure(stock_data):
    if stock_data.empty:
        print("No valid stock data to plot")
        return go.Figure()  # Return an empty figure if no data

    fig = go.Figure(data=[go.Candlestick(
        x=stock_data['timestamp'],
        open=stock_data['open'],
        high=stock_data['high'],
        low=stock_data['low'],
        close=stock_data['close']
    )])

    fig.update_layout(
        title="Candlestick Chart",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template="plotly_dark"
    )
    return fig


# Create the layout for the Dash app
app.layout = html.Div([
    html.H1("Stock Price Candlestick Chart"),
    dcc.Dropdown(
        id='stock-dropdown',
        options=[{'label': stock, 'value': stock} for stock in nasdaq_100_stocks],
        value=nasdaq_100_stocks[0]  # Default value
    ),
    dcc.Graph(id='candlestick-chart')
])

@app.callback(
    dash.dependencies.Output('candlestick-chart', 'figure'),
    [dash.dependencies.Input('stock-dropdown', 'value')]
)
def update_candlestick_chart(stock):
    stock_data = get_stocks(stock)  # Fetch the stock data
    if not stock_data.empty:
        return create_candlestick_figure(stock_data)  # Return the candlestick chart
    else:
        return go.Figure()  # Return an empty figure if no data is available

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)


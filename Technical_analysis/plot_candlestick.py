from polygon import RESTClient
import json
from typing import cast
from urllib3 import HTTPResponse
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os
import time
from time import sleep
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Load API key from environment variables
load_dotenv()
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

# Connect to the Polygon API
client = RESTClient(POLYGON_API_KEY)

# List of NASDAQ 100 stocks
nasdaq_100_stocks = [
    "AMZN"  # Example stock, you can add more
]

# Function to fetch stock data
def get_stocks(stock):
    retries = 5  # Maximum retry attempts
    delay = 5  # Initial delay (in seconds) between retries
    for attempt in range(retries):
        try:
            # Fetch data using the `list_aggs` method for hourly aggregation
            aggs = []
            for a in client.list_aggs(
                ticker=stock,
                multiplier=1,
                timespan="hour",
                from_="2025-01-24",
                to="2025-01-24",
                limit=50000
            ):
                aggs.append(a)

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
            return stock_data
        except Exception as e:
            if '429' in str(e):
                print(f"Rate-limiting error for {stock}. Retrying in {delay} seconds...")
                sleep(delay)
                delay *= 2  # Exponential backoff
                continue  # Retry the request
            else:
                print(f"Error fetching data for {stock}: {e}")
                return pd.DataFrame()  # Return an empty DataFrame in case of other errors
    return pd.DataFrame()  # Return an empty DataFrame if retries fail

# Function to plot candlestick chart with a moving average
def plot_candlestick_with_indicators(stock_data, stock_name):
    if stock_data.empty:
        print(f"No data available for {stock_name}.")
        return None

    # Calculate a 10-period moving average
    stock_data['SMA_10'] = stock_data['close'].rolling(window=10).mean()

    # Create a candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=stock_data['timestamp'],
        open=stock_data['open'],
        high=stock_data['high'],
        low=stock_data['low'],
        close=stock_data['close'],
        name='Candlestick'
    )])

    # Add a moving average line to the chart
    fig.add_trace(go.Scatter(
        x=stock_data['timestamp'],
        y=stock_data['SMA_10'],
        mode='lines',
        name='10-Period SMA',
        line=dict(color='orange', width=2)
    ))

    # Customize the layout
    fig.update_layout(
        title=f'Candlestick Chart with Indicators for {stock_name}',
        xaxis_title='Time',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        template='plotly_dark'
    )

    return fig

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout of the Dash app
app.layout = html.Div([
    html.H1("NASDAQ 100 Stock Candlestick Charts with Indicators"),
    dcc.Dropdown(
        id="stock-dropdown",
        options=[{"label": stock, "value": stock} for stock in nasdaq_100_stocks],
        value=nasdaq_100_stocks[0]
    ),
    dcc.Graph(id="stock-candlestick")
])

# Define the callback to update the graph
@app.callback(
    Output("stock-candlestick", "figure"),
    [Input("stock-dropdown", "value")]
)
def update_graph(stock):
    stock_data = get_stocks(stock)
    return plot_candlestick_with_indicators(stock_data, stock)  # Use the updated function

# Run the app on a specific port
if __name__ == "__main__":
    app.run_server(debug=True, port=8050, use_reloader=False)

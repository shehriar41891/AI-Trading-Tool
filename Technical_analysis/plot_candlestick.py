from polygon import RESTClient
import pandas as pd
import os
from time import sleep
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load API key from environment variables
load_dotenv()
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

# Connect to the Polygon API
client = RESTClient(POLYGON_API_KEY)

# List of NASDAQ 100 stocks
nasdaq_100_stocks = ["TSLA"]  # Example stock, add more if needed

def get_stocks(stock):
    retries = 5
    delay = 5
    for attempt in range(retries):
        try:
            aggs = []
            for a in client.list_aggs(
                ticker=stock,
                multiplier=1,
                timespan="minute",
                from_="2025-01-31",
                to="2025-02-01",
                limit=50000
            ):
                aggs.append(a)

            # Check if we received data
            if not aggs:
                print(f"No data received for {stock}.")
                return pd.DataFrame()

            data = []
            for agg in aggs:                
                # Ensure the 'close' field exists before using it
                if hasattr(agg, 'close'):
                    data.append({
                        'timestamp': pd.to_datetime(agg.timestamp, unit='ms'),
                        'open': agg.open,
                        'high': agg.high,
                        'low': agg.low,
                        'close': agg.close,
                        'volume': agg.volume
                    })
                else:
                    print(f"Missing 'close' data for {stock} at {agg.timestamp}.")
            
            # Return data if not empty
            if data:
                stock_data = pd.DataFrame(data)
                print(stock_data.tail())

                # Convert timestamps to Karachi time (UTC+5)
                stock_data['timestamp'] = stock_data['timestamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Karachi')

                # Convert start_time to Karachi timezone as well
                # start_time = pd.to_datetime('2025-01-31 22:00').tz_localize('Asia/Karachi')

                # Ensure data is after the start_time
                # stock_data = stock_data[stock_data['timestamp'] >= start_time]

                # Calculate Technical Indicators
                stock_data['SMA_10'] = stock_data['close'].rolling(window=10).mean()
                stock_data['EMA_10'] = stock_data['close'].ewm(span=10, adjust=False).mean()
                stock_data['SMA_20'] = stock_data['close'].rolling(window=20).mean()
                stock_data['STD_20'] = stock_data['close'].rolling(window=20).std()
                stock_data['Upper_BB'] = stock_data['SMA_20'] + (2 * stock_data['STD_20'])
                stock_data['Lower_BB'] = stock_data['SMA_20'] - (2 * stock_data['STD_20'])

                delta = stock_data['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                stock_data['RSI'] = 100 - (100 / (1 + rs))

                short_ema = stock_data['close'].ewm(span=12, adjust=False).mean()
                long_ema = stock_data['close'].ewm(span=26, adjust=False).mean()
                stock_data['MACD'] = short_ema - long_ema
                stock_data['MACD_Signal'] = stock_data['MACD'].ewm(span=9, adjust=False).mean()

                return stock_data

            print(f"No valid data found for {stock}.")
            return pd.DataFrame()
        
        except Exception as e:
            if '429' in str(e):
                print(f"Rate-limiting error for {stock}. Retrying in {delay} seconds...")
                sleep(delay)
                delay *= 2
                continue
            else:
                print(f"Error fetching data for {stock}: {e}")
                return pd.DataFrame()

    return pd.DataFrame()


def plot_candlestick_with_indicators(stock_data, stock_name):
    if stock_data.empty:
        print(f"No data available for {stock_name}.")
        return None, None, None

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=stock_data['timestamp'],
        open=stock_data['open'],
        high=stock_data['high'],
        low=stock_data['low'],
        close=stock_data['close'],
        name='Candlestick'
    ))

    fig.add_trace(go.Scatter(x=stock_data['timestamp'], y=stock_data['SMA_10'],
                             mode='lines', name='10-Period SMA', line=dict(color='orange', width=2)))
    fig.add_trace(go.Scatter(x=stock_data['timestamp'], y=stock_data['EMA_10'],
                             mode='lines', name='10-Period EMA', line=dict(color='blue', width=1.5)))
    fig.add_trace(go.Scatter(x=stock_data['timestamp'], y=stock_data['Upper_BB'],
                             mode='lines', name='Upper Bollinger Band', line=dict(color='purple', width=1, dash='dot')))
    fig.add_trace(go.Scatter(x=stock_data['timestamp'], y=stock_data['Lower_BB'],
                             mode='lines', name='Lower Bollinger Band', line=dict(color='purple', width=1, dash='dot')))

    macd_fig = go.Figure()
    macd_fig.add_trace(go.Scatter(x=stock_data['timestamp'], y=stock_data['MACD'],
                                  mode='lines', name='MACD', line=dict(color='cyan', width=1.5)))
    macd_fig.add_trace(go.Scatter(x=stock_data['timestamp'], y=stock_data['MACD_Signal'],
                                  mode='lines', name='MACD Signal', line=dict(color='red', width=1.5)))

    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(x=stock_data['timestamp'], y=stock_data['RSI'],
                                 mode='lines', name='RSI', line=dict(color='yellow', width=1.5)))
    rsi_fig.update_layout(title="RSI (14-Period)", yaxis=dict(title="RSI Value", range=[0, 100], showgrid=True),
                          xaxis=dict(title="Time"), template="plotly_dark")

    fig.update_layout(title=f'Candlestick Chart with Indicators for {stock_name}', xaxis_title='Time',
                      yaxis_title='Price', xaxis_rangeslider_visible=False, template='plotly_dark')

    return fig, macd_fig, rsi_fig


def run_dashboard():
    app = dash.Dash(__name__)

    app.layout = html.Div([ 
        html.H1("NASDAQ 100 Stock Candlestick Charts with Indicators"),
        dcc.Dropdown(
            id="stock-dropdown",
            options=[{"label": stock, "value": stock} for stock in nasdaq_100_stocks],
            value=nasdaq_100_stocks[0]
        ),
        dcc.Graph(id="stock-candlestick"),
        dcc.Graph(id="macd-chart"),
        dcc.Graph(id="rsi-chart")
    ])

    @app.callback(
        [Output("stock-candlestick", "figure"),
         Output("macd-chart", "figure"),
         Output("rsi-chart", "figure")],
        [Input("stock-dropdown", "value")]
    )
    def update_graph(stock):
        stock_data = get_stocks(stock)
        candlestick_fig, macd_fig, rsi_fig = plot_candlestick_with_indicators(stock_data, stock)
        return candlestick_fig, macd_fig, rsi_fig

    app.run_server(debug=True)


if __name__ == '__main__':
    run_dashboard()

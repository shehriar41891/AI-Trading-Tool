from polygon import RESTClient
import json
from typing import cast
from urllib3 import HTTPResponse
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os
import time
import concurrent.futures
from time import sleep


load_dotenv()

POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

# Connecting to the Polygon API
client = RESTClient(POLYGON_API_KEY)

# Static list of NASDAQ 100 stocks (add the full list)
nasdaq_100_stocks = [
    "AMZN"
]

# 1. Fetch Stock Data and Calculate Metrics using Polygon API
def calculate_metrics(stock):
    retries = 5  # Maximum retry attempts
    delay = 5  # Initial delay (in seconds) between retries
    for attempt in range(retries):
        try:
            # Fetch data using `list_aggs` method for hourly aggregation
            aggs = []
            for a in client.list_aggs(
                ticker=stock,
                multiplier=5,
                timespan="minute",  
                from_="2025-01-23",  
                to="2025-01-24", 
                limit=50000
            ):
                aggs.append(a)

            data = []
            for agg in aggs:
                data.append({
                    'timestamp': pd.to_datetime(agg.timestamp, unit='ms'),
                    'close': agg.close,
                    'volume': agg.volume
                })
                
            print(F'The data we get is {stock}',data)

            stock_data = pd.DataFrame(data)

            # Calculate the percentage change between the first and last closing price
            first_close = stock_data['close'].iloc[0]
            last_close = stock_data['close'].iloc[-1]
            
            print('the first and last close are',first_close,last_close)

            percentage_change = ((last_close - first_close) / last_close) * 100
            
            print('The percentage change is ',percentage_change)

            # Calculate the relative volume
            current_volume = stock_data['volume'].iloc[-1]
            average_volume = stock_data['volume'].mean()
            relative_volume = current_volume / average_volume

            # Return current stock value (last closing price), percentage change, and relative volume
            return stock, last_close, percentage_change, relative_volume

        except Exception as e:
            if '429' in str(e): 
                print(f"Rate-limiting error for {stock}. Retrying in {delay} seconds...")
                sleep(delay)
                delay *= 2  # Exponential backoff
                continue  # Retry the request
            else:
                print(f"Error fetching data for {stock}: {e}")
                return stock, 0, 0, 0  # Return a default value in case of other errors
    return stock, 0, 0, 0  # Return default values after all retries fail

# 2. Filter Stocks that Meet the Criteria
def filter_popular_stocks(stocks):
    valid_stocks = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(calculate_metrics, stocks)

        for stock, last_close, percentage_change, relative_volume in results:
            print(f"Percentage change is {percentage_change}, Current price is {last_close}, RV is {relative_volume}")
            if percentage_change >= 0 and relative_volume >= 1:
                valid_stocks.append(stock)
                print(f'{stock} meets the criteria: {percentage_change}% increase, RV: {relative_volume}, Current Price: {last_close}')

    return valid_stocks

# # 3. Continuous Monitoring of NASDAQ 100 Stocks
# def monitor_nasdaq_100():
#     valid_stocks = filter_popular_stocks(nasdaq_100_stocks)

#     # Process valid stocks
#     print(f"Valid stocks: {valid_stocks}")

# # 4. Start Monitoring
# monitor_nasdaq_100()

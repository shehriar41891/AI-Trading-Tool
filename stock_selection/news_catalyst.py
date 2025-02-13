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
import requests
from datetime import datetime, timedelta

load_dotenv()

POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

# Connecting to the Polygon API
client = RESTClient(POLYGON_API_KEY)


def fetch_stock_news(stock):
    """
    Fetch recent news for a given stock using the Polygon.io API.
    """
    try:
        url = f"https://api.polygon.io/v2/reference/news?ticker={stock}&limit=5&apiKey={POLYGON_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        news_data = response.json()   
        news = []
        for item in news_data.get("results", []):
            news.append({
                'title': item['title'],
                'published_utc': item['published_utc'],
                'article_url': item['article_url'],
                'summary': item.get('description', 'No summary available'),
            })
        return stock, news

    except Exception as e:
        print(f"Error fetching news for {stock}: {e}")
        return stock, []


def get_news_for_stock(stock: str):
    """
    Fetch news for a single stock ticker.
    """
    stock, news = fetch_stock_news(stock)
    return {stock: news}


# # Example usage:
# valid_stocks = 'MBRX' # Replace with your valid_stocks array
# news_data = get_news_for_stock(valid_stocks)

# # print('The news data is',news_data)

# #filtering out old news 
# time_threshold = datetime.utcnow() - timedelta(hours=48)

# filtered_news = {}

# for stock, articles in news_data.items():
#     filtered_news[stock] = [
#         article
#         for article in articles
#         if datetime.strptime(article["published_utc"], "%Y-%m-%dT%H:%M:%SZ") > time_threshold
#     ]

# print(news_data)

# # Output the filtered news with summaries
# for stock, articles in filtered_news.items():
#     print(f"News for {stock} in the last 24 hours:")
#     for article in articles:
#         title = article.get("title", "No Title")
#         published_date = article.get("published_utc", "Unknown Date")
#         url = article.get("url", "No URL provided")
#         summary = article.get("summary", "No summary available")  # Safely get summary

#         print(f"  - {title} (Published: {published_date})")
#         print(f"    {summary}")
#         print(f"    {url}")
#     if not articles:
#         print(f"  No news in the last 24 hours.\n")
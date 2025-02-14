import os
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
import json

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# Initialize the LLM
llm = OpenAI()

# Define a prompt for structured candlestick chart analysis
prompt = PromptTemplate.from_template(
    """
    You are a professional stock trading analyst. Analyze the given textual description 
    of candlestick chart data, stock details, and news sentiment. Your goal is to 
    provide an updated structured trading recommendation while minimizing risk.  

    **Decision-Making Guidelines:**  
    - **Buying:** If the trend is favorable, buy a maximum of 2 shares, but **do not buy** if current shares are already 10 or more.  
    - **Selling:** If the trend is very bad, sell all current shares to minimize risk.  
    - **Holding:** If the situation is unclear, hold without updating stop-loss or take-profit.  
    - **Stop-Loss & Take-Profit:** Adjust these only if required to minimize risk; otherwise, keep them unchanged.  

    **Structured Recommendation Format:**  

    {{
        "Recommendation": "<Buy | Sell | Hold>",
        "Current Shares": "<Number of shares currently held>",
        "Stop-Loss": "<Revised stop-loss price, if required>",
        "Take-Profit": "<Revised take-profit price, if required>",
        "Shares to Buy": "<Number of shares to buy (max 2, or 0 if current shares >= 10)>",
        "Shares to Sell": "<Number of shares to sell, or 0>"
    }}

    **Stock Details**: {stock_details}  
    **News Sentiment**: {news_sentiment}  
    **Textual Chart Data**: {chart_text}  
    **Current Shares**: {current_shares}  
    **Current Stop-Loss**: {current_stop_loss}  
    **Current Take-Profit**: {current_take_profit}  

    Provide the response strictly in the above JSON format.
    """
)

# Create the chain
chain = prompt | llm

# Function for analyzing candlestick chart textual description
def analyze_candlestick_text(stock_details, news_sentiment, chart_text,current_shares,stop_loss,take_profit):
    response = chain.invoke(
        {
            "stock_details": stock_details,
            "news_sentiment": news_sentiment,
            "chart_text": chart_text,
            "Current Shares": current_shares,
            "current_stop_loss": stop_loss,
            "current_take_profit": take_profit
        }
    ).strip()

    try:
        recommendation = json.loads(response) 
        return recommendation  
    except json.JSONDecodeError:
        return {"Recommendation": "NO RECOMMENDATION"}  

# Example usage:
# result = analyze_candlestick_text(stock_details, news_sentiment, chart_text_description)
# print("Trading Recommendation:")
# print(result)

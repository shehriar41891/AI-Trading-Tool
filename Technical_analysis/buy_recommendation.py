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
    You are a professional stock trading analyst. Analyze the given candlestick chart data, stock details, 
    and news sentiment to determine whether the stock is a **BUY** or **NOT BUY**. 

    **Analysis Criteria:**
    
    1. **Momentum & Trend Confirmation**  
       - Identify if the stock shows a **Bull Flag** or **Flat Top Breakout** pattern.  
       - Verify if it’s **trading above the 9 EMA** (Exponential Moving Average).  
       - Confirm that the **overall trend is upward**.  

    2. **Volume Analysis**  
       - Ensure there is **low volume on red candles (pullbacks)** and **high volume on green candles (buy signals)**.  

    3. **Support & Resistance Levels**  
       - Check if the stock is **near key support levels** (good entry).  
       - Avoid recommending buy if it's near **major resistance**.  

    4. **News Sentiment**  
       - Consider only **positive catalysts** (strong earnings, industry growth, new contracts, etc.).  
       - If the stock has **negative news**, mark it as **NOT BUY**.  

    5. **Position Sizing**  
       - If **BUY**, recommend **≤ 5 shares** only.  
       - If **NOT BUY**, provide reasoning based on technicals or fundamentals.  

    **Structured Recommendation Format (JSON Only):**
    
    {{
        "Recommendation": "<BUY | NOT BUY>",
        "Entry Price": "<Estimated optimal entry price if BUY>",
        "Stop-Loss": "<Recommended stop-loss price if BUY>",
        "Profit Target": "<Expected price level to take profit if BUY>",
        "Shares to Buy": "<Number of shares to buy (≤ 5) if BUY>",
        "Reason": "<Brief reason for decision>"
    }}

    **Stock Details**: {stock_details}  
    **News Sentiment**: {news_sentiment}  
    **Textual Chart Data**: {chart_text}  

    Provide the response strictly in the above JSON format.
    """
)

# Create the chain
chain = prompt | llm

# Function for analyzing candlestick chart textual description
def analyze_candlestick_text(stock_details, news_sentiment, chart_text):
    response = chain.invoke(
        {
            "stock_details": stock_details,
            "news_sentiment": news_sentiment,
            "chart_text": chart_text,
        }
    ).strip()

    try:
        recommendation = json.loads(response) 
        return recommendation  
    except json.JSONDecodeError:
        return {"Recommendation": "NOT BUY"}  

# Example usage:
# result = analyze_candlestick_text(stock_details, news_sentiment, chart_text_description)
# print("Trading Recommendation:")
# print(result)

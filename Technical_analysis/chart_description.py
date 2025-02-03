import os
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate

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
    of candlestick chart data, stock details, and news sentiment, and provide a structured 
    trading recommendation including entry price, stop-loss, profit target, and position sizing.

    **Analysis Steps:**
    
    1. **Momentum**: Identify if the stock shows a Bull Flag or Flat Top Breakout pattern 
       and if it’s trading above the 9 EMA.
    2. **Volume**: Check for low volume on red candles (pullbacks) and high volume on 
       green candles (potential buy signal).
    3. **Support & Resistance**: Consider key support and resistance levels and suggest 
       a stop-loss level.
    4. **Trend Confirmation**: Evaluate the overall trend based on the description.
    5. **Stock Details**: Consider the stock’s market sector, recent performance, and key metrics.
    6. **News Sentiment**: Analyze recent news sentiment related to the stock.

    **Structured Recommendation Format:**
    
    {{
        "Recommendation": "<Buy | Sell | Hold>",
        "Entry Price": "<Estimated optimal entry price>",
        "Stop-Loss": "<Recommended stop-loss price>",
        "Profit Target": "<Expected price level to take profit>",
        "Position Sizing": {{
            "If Buy": "<How many shares to buy>",
            "If Sell": "<How many shares to sell>"
        }},
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
    )
    return response.strip()

# Example usage:
# result = analyze_candlestick_text(stock_details, news_sentiment, chart_text_description)
# print("Trading Recommendation:")
# print(result)

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
    of candlestick chart data, stock details, and news sentiment, and provide a structured 
    trading recommendation including entry price, stop-loss, profit target, and position sizing.

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

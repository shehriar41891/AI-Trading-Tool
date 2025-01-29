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

# Define a prompt for textual candlestick chart analysis
prompt = PromptTemplate.from_template(
    """
    You are a professional stock trading analyst. Analyze the given textual description 
    of candlestick chart data and provide a recommendation: Buy, Sell, or Hold. Follow these steps:

    1. **Momentum**: Identify if the stock shows a Bull Flag or Flat Top Breakout pattern 
       and if it’s trading above the 9 EMA.
    2. **Volume**: Check for low volume on red candles (pullbacks) and high volume on 
       green candles (potential buy signal).
    3. **Support & Resistance**: Consider key support and resistance levels, and suggest 
       a stop-loss level.
    4. **Trend Confirmation**: Evaluate the overall trend based on the description.

    Textual Chart Data: {chart_text}
    Recommendation (Buy, Sell, or Hold) and Reason:
    """
)

# Create the chain
chain = prompt | llm

# Function for analyzing candlestick chart textual description
def analyze_candlestick_text(chart_text):
    response = chain.invoke(
        {
            "chart_text": chart_text,
        }
    )
    return response.strip()

# Example usage
chart_text_description = """
The candlestick chart for AAPL shows an initial uptrend in the morning, 
followed by a peak around midday before experiencing a sharp decline in the afternoon.
The price consistently stays below both the 10-period SMA and EMA after the drop, 
indicating bearish momentum. Bollinger Bands widen during the selloff, 
signaling high volatility, and later contract, suggesting reduced price movement.
The overall trend remains downward, with no strong reversal signals,
implying continued selling pressure.
"""

result = analyze_candlestick_text(chart_text_description)
print("Trading Recommendation:")
print(result)

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

# Define a prompt for sentiment analysis with stock name and short-term context
prompt = PromptTemplate.from_template(
    """
    You are a stock market sentiment analyzer. Analyze the sentiment of the given news or stock-related text, focusing on the short-term outlook for the specified stock.
    Return one of the following:
    - Positive
    - Negative
    - Neutral
    
    Please consider the market news, stock performance, and any external factors that might affect the stock's short-term movement.
    
    Stock Name: {stock_name}
    Input Text: {input_text}
    Sentiment (Short-term outlook): 
    """
)

# Create the chain
chain = prompt | llm

# Function for sentiment analysis with stock name and short-term focus
def analyze_sentiment(stock_name, input_text):
    response = chain.invoke(
        {
            "stock_name": stock_name,
            "input_text": input_text,
        }
    )
    return response.strip()

# Example usage
# Example input text for Nvidia stock
# text_to_analyze = """
# Nvidia's stock price has been impacted by increased export regulations related to their DeepSeek AI technology. This has led to a sell-off, which some experts see as a buying opportunity. However, Nvidia's competitor AMD is also well-positioned in the AI chip market and has upcoming releases that could compete with Nvidia's offerings.
# """
# stock_name = "Nvidia"

# # Get the sentiment for Nvidia stock in the short-term
# result = analyze_sentiment(stock_name, text_to_analyze)
# print(f"Sentiment Analysis Result for {stock_name}:")
# print(result)

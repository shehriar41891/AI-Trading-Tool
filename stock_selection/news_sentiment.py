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

# Define a simplified prompt for sentiment analysis from a stock trading perspective
prompt = PromptTemplate.from_template(
    """
    You are a stock market sentiment analyzer. Analyze the sentiment of the given text 
    related to a company, stock, or market news. Return only one of the following:
    - Positive
    - Negative
    - Neutral

    Input Text: {input_text}
    Sentiment: 
    """
)

# Create the chain
chain = prompt | llm

# Function for sentiment analysis from a stock trading perspective
def analyze_sentiment(input_text):
    response = chain.invoke(
        {
            "input_text": input_text,
        }
    )
    return response.strip()

# # Example usage
# text_to_analyze = """
# Apple Inc. reported its quarterly earnings, with a surprising 10% increase in revenue, 
# and a new product launch is expected next quarter. Analysts are optimistic about future growth.
# """
# result = analyze_sentiment(text_to_analyze)
# print("Sentiment Analysis Result:")
# print(result)

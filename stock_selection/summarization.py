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

# Define a prompt for extracting news related to a certain stock and summarizing it
prompt = PromptTemplate.from_template(
    """
    You are a stock market news extractor and summarizer. Given the stock name and a block of text, extract the most relevant news related to the provided stock and then summarize it into a few key sentences.

    Stock Name: {stock_name}
    Input Text: {input_text}
    Extracted News Summary: 
    """
)

# Create the chain
chain = prompt | llm

# Function for extracting and summarizing stock-related news based on stock name
def extract_and_summarize_stock_news(stock_name, input_text):
    response = chain.invoke(
        {
            "stock_name": stock_name,
            "input_text": input_text,
        }
    )
    return response.strip()

# Example usage
# stock_name = "Apple Inc."
# text_to_process = """
# Apple Inc. has recently launched a new product, with market analysts predicting that it will boost their earnings significantly in the coming quarter. The stock price has already seen a positive reaction.
# Other news mentions companies like Tesla and Microsoft, but the main focus is on Apple.
# """
# result = extract_and_summarize_stock_news(stock_name, text_to_process)
# print("Stock News Extraction & Summarization Result:")
# print(result)

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def visual_to_text(image_path):
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = (
        "Analyze the given candlestick chart with your knowledge. "
        "Identify different patterns in the candlestick formation. "
        "Create a detailed report explaining what exactly happens in the chart "
        "and how these patterns might be used for making buying or selling decisions. "
        "Ensure the report provides insights that can help in deciding stock trading strategies."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a financial analyst with expertise in candlestick pattern recognition."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": image_path}  # Assuming OpenAI's API can handle image input
        ]
    )
    
    # Corrected the access to the response object
    response_dict = response.to_dict()
    final_response = response_dict["choices"][0]["message"]["content"]
    #write final response to a file 
    with open('file.txt','w') as f:
        f.write(final_response)
    
    return final_response

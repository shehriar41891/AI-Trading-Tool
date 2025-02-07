import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def encode_image(image_path):
    """Convert image to Base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def visual_to_text(image_path):
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = (
        "Analyze the given candlestick chart. Identify any candlestick patterns, "
        "trends, and key support/resistance levels. Provide insights for possible "
        "buying or selling decisions based on technical analysis."
    )

    # Convert image to Base64
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a financial analyst with expertise in candlestick pattern recognition."},
            {"role": "user", "content": prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Here is a candlestick chart for analysis."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            }
        ]
    )

    # Extract the response content
    final_response = response.choices[0].message.content

    # Write the response to a file
    with open('file.txt', 'w') as f:
        f.write(final_response)

    return final_response

# Run the function
# res = visual_to_text(image_path="../downloaded_candles/candlestick_chart.png")
# print(res)

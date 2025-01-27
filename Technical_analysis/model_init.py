import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
generation_config = {
  "temperature": 1.05,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
)

response = model.generate_content([
  "input: An image of the candlestick chart: A visual representation of the market for a specific time range.",
  "output: Trend: Market trend (e.g., Bullish, Bearish, Sideways) with identified patterns (e.g., Double Top, Doji).Key Levels: Support and resistance levels with strong buying/selling pressure.Indicators: Moving Averages, RSI, Bollinger Bands (optional).Insights: Buy/Sell/Hold recommendations and risk or stop-loss suggestions.",
  "input: ",
  "output: ",
])

print(response.text)
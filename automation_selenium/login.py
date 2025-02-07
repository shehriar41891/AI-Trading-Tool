from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from automation_selenium.automatino_funcs import search_market, automate_buy, automate_sell, stock_details
from automation_selenium.automatino_funcs import capture_candlestick_chart, connect_paper_trading
from db.db_operations import find_all_stocks
from sell_buy.sell_stock import sell_hold_stock
from sell_buy.buy_stock import buy_stock
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from fastapi.responses import JSONResponse
from win10toast import ToastNotifier

# Load environment variables
load_dotenv()

# Set up FastAPI app
app = FastAPI()

# Allow all origins or set a specific origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust for security
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)
# Set your credentials
email = os.getenv('EMAIL_ADDRESS')
password = os.getenv('PASSWORD')

# Set up the Selenium WebDriver (initiating this once for each action)
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.tradingview.com/")
    time.sleep(3)
    return driver

# Create a model for stock actions input (for ease of extensibility)
class StockActionRequest(BaseModel):
    stocks: list
    action: str  # 'buy' or 'sell'

# Function for signing in
def signin(driver):
    # Open user menu and login
    user_menu_button = driver.find_element(By.CLASS_NAME, "tv-header__user-menu-button")
    user_menu_button.click()
    time.sleep(2)

    sign_in_button = driver.find_element(By.CSS_SELECTOR, "button[data-name='header-user-menu-sign-in']")
    sign_in_button.click()
    time.sleep(2)

    email_button = driver.find_element(By.XPATH, "//button[contains(@name, 'Email')]")
    email_button.click()
    time.sleep(2)

    email_input = driver.find_element(By.NAME, "id_username")
    email_input.send_keys(email)
    time.sleep(1)

    password_input = driver.find_element(By.NAME, "id_password")
    password_input.send_keys(password)
    time.sleep(1)

    sign_in_submit = driver.find_element(By.XPATH, "//button[contains(@class, 'submitButton-LQwxK8Bm')]")
    sign_in_submit.click()
    print("Please solve the CAPTCHA manually...")
    time.sleep(40)  # Wait for CAPTCHA to be solved manually
    print("Continuing after CAPTCHA is solved...")
    sign_in_submit.click()

# Function to instantiate market data and connect
def instantiate(driver, stocks):
    search_market(driver, stocks[0])
    connect_paper_trading(driver)

# Endpoint for sign in
@app.post("/signin/")
def signin_endpoint():
    driver = init_driver()
    try:
        signin(driver)
    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail=f"Failed to sign in: {str(e)}")
    return {"message": "Signed in successfully. Please solve the CAPTCHA manually."}

# Endpoint for initiating stock actions (buy/sell)
@app.post("/instantiate/")
def instantiate_endpoint(stocks: list):
    driver = init_driver()
    try:
        instantiate(driver, stocks)
    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail=f"Failed to instantiate: {str(e)}")
    return {"message": "Stock instantiation complete."}

class StockActionRequest(BaseModel):
    stocks: List[str]
# Endpoint for buying stocks
@app.post("/buy_stock/")
def buy_stock_endpoint(stock_action: StockActionRequest):
    print(stock_action)
    driver = init_driver()
    try:
        signin(driver)  # Ensure user is signed in before taking action
        instantiate(driver, stock_action.stocks)  # Ensure market is instantiated before buying
        # clear the file before doing anything 
        with open('file.txt','w') as f:
            pass
        
        stock_info = stock_details(driver)
        capture_candlestick_chart(driver, "../downloaded_candles")
        print('The stock information in new system is ',stock_info)
        res,summarized_news,sentiment_of_news= buy_stock(stock_info, stock_action.stocks[0])
        print('The result in here is ',res)
        reason = res['Reason']
        recommendation = res['Recommendation']
        print('The recommendation is ',reason)
        if recommendation.lower() == 'buy':
            automate_buy(driver, res)
            return JSONResponse(content={
                "message": f"Buying stock {stock_action.stocks[0]}",
                "stock_info": stock_info,
                "buy_stock_response": res,
                "summarized_news": summarized_news,
                "sentiment_of_news": sentiment_of_news,
                "reason" : reason
            })
        else:
            # toaster = ToastNotifier()
            # toaster.show_toast("Stock Alert", "We are not buying this stock!", duration=5)
            print('We are not buying this stocks')
            return JSONResponse(content={
                "message": f"Buying stock {stock_action.stocks[0]}",
                "stock_info": stock_info,
                "buy_stock_response": res,
                "summarized_news": summarized_news,
                "sentiment_of_news": sentiment_of_news,
                "reason" : reason
            })
    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail=f"Error buying stock: {str(e)}")
    finally:
        driver.quit()

# Endpoint for selling stocks
@app.post("/sell_stock/")
def sell_stock_endpoint(stock_action: StockActionRequest):
    driver = init_driver()
    try:
        signin(driver)  # Ensure user is signed in before taking action
        instantiate(driver, stock_action.stocks)  # Ensure market is instantiated before selling
        for stock in stock_action.stocks:
            stock_info = stock_details(driver)
            res = sell_hold_stock(stock_info, stock)
            if res.lower() == 'sell':
                automate_sell(driver)
                return {"message": f"Selling stock {stock}"}
            elif res.lower() == 'buy':
                automate_buy(driver)
                return {"message": f"Buying stock {stock}"}
            else:
                return {"message": f"Holding stock {stock}"}
    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail=f"Error selling stock: {str(e)}")
    finally:
        driver.quit()

# Run the app with `uvicorn`:
# uvicorn app_name:app --reload

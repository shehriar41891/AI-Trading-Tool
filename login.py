from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from automation_selenium.automatino_funcs import search_market, automate_buy, automate_sell, stock_details
from automation_selenium.automatino_funcs import capture_candlestick_chart, connect_paper_trading,search_remaining
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
from automation_selenium.get_stock_names import extract_stock_data
import os 
from dotenv import load_dotenv
from db.db_operations import find_all_stocks,add_to_db,delete_from_db,get_current_shares
import random

load_dotenv()

WARRIOR_TRADING_URL = os.getenv('WARRIOR_TRADING_URL')

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
    time.sleep(20)  # Wait for CAPTCHA to be solved manually
    print("Continuing after CAPTCHA is solved...")
    if sign_in_submit:
        sign_in_submit.click()
    else:
        print('There is no sign in  button')
    print('We are done with sign in')

# Function to instantiate market data and connect
def instantiate(driver, stock):
    search_market(driver, stock)
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
    stocks_in_db = find_all_stocks()
    if len(stocks_in_db) < 5:
        print('We are inside the if block')
        list_of_stocks = extract_stock_data(WARRIOR_TRADING_URL)
        list_of_stocks_to_buy = []
        print(stock_action)
        driver = init_driver()
        try:
            signin(driver)  # Ensure user is signed in before taking action
            #retrieve all the stocks present in the database
            stocks_in_db = find_all_stocks()
            db_stocks = []
            for db_stock in stocks_in_db:
                db_stocks.append(db_stock['_id'])
            print('We are safe up till here and stocks are',stocks_in_db)
            instantiate(driver, 'TSLA')  # Ensure market is instantiated before buying 
            for stock in list_of_stocks[1:]:
                stock_info = stock
                print('The stock infor is ',stock_info)
                if stock['name'] not in db_stocks:
                    print('The stock at 0 position is ',stock['name'])
                    search_remaining(driver,stock['name'])
                    # stock_info = stock_details(driver)
                    capture_candlestick_chart(driver, "downloaded_candles")
                    print('The stock information in new system is ',stock_info)
                    res,summarized_news,sentiment_of_news= buy_stock(stock_info, stock['name'])
                    print('The result in here is ',res)
                    reason = res['Reason']
                    recommendation = res['Recommendation']
                    print('The recommendation is ',reason)
                    price_int = int(float(stock['Price']))
                    print('The price of the stock is ',price_int)
                    if recommendation.lower() == 'buy' and price_int <=5:
                        shares = res['Shares to Buy']
                        stop_loss = res['Stop-Loss']
                        profit_take = res['Profit Target']
                        add_to_db(stock['name'],shares,stop_loss,profit_take)
                        automate_buy(driver,shares,stop_loss,profit_take)
                        return JSONResponse(content={
                            "message": f"Buying stock {stock['name']}",
                            "stock_info": stock_info,
                            "buy_stock_response": res,
                            "summarized_news": summarized_news,
                            "sentiment_of_news": sentiment_of_news,
                            "reason" : reason
                        })
                        break
                    else:
                        print('We are not buying this stocks')

        except Exception as e:
            driver.quit()
            raise HTTPException(status_code=500, detail=f"Error buying stock: {str(e)}")
        finally:
            driver.quit()
    else:
        return {"message" : f"You already got {len(stocks_in_db)} stocks to play around"}

# Endpoint for selling stocks
@app.post("/sell_stock/")
def sell_stock_endpoint():
    driver = init_driver()
    try:
        signin(driver)  # Ensure user is signed in before taking action
        instantiate(driver,['NVDA'])  # Ensure market is instantiated before selling
        while True:
            stock = find_all_stocks()
            
            print('The stock retrieved is ',stock)
            
            if not stock:
                print("No stocks available for analysis.")
                break  # No stocks left, exit loop
            
            stock = stock[0]
            if int(stock['number_of_shares']) < 10:  # Convert to integer if needed
                stock_info = {
                    "number_of_shares": int(stock['number_of_shares']),  # Convert if necessary
                    "stop loss": float(stock['stop_loss']),
                    "profit take": float(stock['profit_take'])
                }
                stock_name = stock['_id']
                current_shares = int(stock['number_of_shares'])
                search_remaining(driver,stock_name)
                
                capture_candlestick_chart(driver,"downloaded_candles")
                res,summarized_news,sentiment_of_news = sell_hold_stock(stock_info, stock_name)

                print('The response from the ai is ',res)
                
                recommendation = res.get("Recommendation", "").lower()  # Fix: Access dictionary correctly

                if recommendation == 'sell':
                    shares_to_sell = int(res['Shares to Sell'])
                    stop_loss = float(res['Stop-Loss'])
                    profit_take = float(res['Take-Profit'])
                    
                    # Update shares after selling
                    new_shares = max(0, current_shares - shares_to_sell)
                    add_to_db(stock_name, new_shares, stop_loss, profit_take)
                    
                    automate_sell(driver, shares_to_sell, stop_loss, profit_take)
                    print(f"Selling {shares_to_sell} shares of {stock_name}. Remaining: {new_shares}")

                elif recommendation == 'buy':
                    shares_to_buy = int(res['Shares to Buy'])
                    stop_loss = float(res['Stop-Loss'])
                    profit_take = float(res['Take-Profit'])

                    # Update shares after buying
                    new_shares = current_shares + shares_to_buy
                    add_to_db(stock_name, new_shares, stop_loss, profit_take)
                    
                    automate_buy(driver, shares_to_buy, stop_loss, profit_take)
                    print(f"Buying {shares_to_buy} shares of {stock_name}. Total: {new_shares}")

                else:
                    print(f"Holding {stock_name}. Shares remain: {current_shares}")

            else:
                # Stock has no shares left, delete it and exit loop
                delete_from_db(stock['_id'])
                print(f"Stock {stock['_id']} has no shares left. Removing from database.")
                break  # Exit the loop since stock is gone

    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail=f"Error selling stock: {str(e)}")
    finally:
        driver.quit()

# Run the app with `uvicorn`:
# uvicorn app_name:app --reload

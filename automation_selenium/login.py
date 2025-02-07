# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import time
# import os
# from dotenv import load_dotenv
# from automation_selenium.automatino_funcs import search_market, automate_buy, automate_sell, stock_details
# from automation_selenium.automatino_funcs import capture_candlestick_chart, connect_paper_trading
# from db.db_operations import find_all_stocks
# from sell_buy.sell_stock import sell_hold_stock
# import requests
# from bs4 import BeautifulSoup
# from sell_buy.buy_stock import buy_stock
# from automation_selenium.automatino_funcs import automate_buy, search_remaining

# # Load environment variables
# load_dotenv()

# # Set your credentials
# email = os.getenv('EMAIL_ADDRESS')
# password = os.getenv('PASSWORD')

# # Set up the Selenium WebDriver
# options = webdriver.ChromeOptions()
# options.add_argument("--start-maximized")  # Open browser in maximized mode

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# driver.get("https://www.tradingview.com/")

# # Wait for elements to load
# time.sleep(3)

# def signin():
#     # Open user menu
#     user_menu_button = driver.find_element(By.CLASS_NAME, "tv-header__user-menu-button")
#     user_menu_button.click()
#     time.sleep(2)

#     # Click "Sign in"
#     sign_in_button = driver.find_element(By.CSS_SELECTOR, "button[data-name='header-user-menu-sign-in']")
#     sign_in_button.click()
#     time.sleep(2)

#     # Click "Email" sign-in option
#     email_button = driver.find_element(By.XPATH, "//button[contains(@name, 'Email')]")
#     email_button.click()
#     time.sleep(2)

#     # Enter email
#     email_input = driver.find_element(By.NAME, "id_username")
#     email_input.send_keys(email)
#     time.sleep(1)

#     # Enter password
#     password_input = driver.find_element(By.NAME, "id_password")
#     password_input.send_keys(password)
#     time.sleep(1)

#     # Click "Sign in"
#     sign_in_submit = driver.find_element(By.XPATH, "//button[contains(@class, 'submitButton-LQwxK8Bm')]")
#     if sign_in_button:
#         sign_in_submit.click()

#     # Wait for login to complete and CAPTCHA to be solved manually
#     print("Please solve the CAPTCHA manually...")
#     time.sleep(40)  # Wait for manual CAPTCHA solving (adjust the time as needed)

#     # After CAPTCHA is solved, continue with the next steps
#     print("Continuing after CAPTCHA is solved...")
#     if sign_in_button:
#         sign_in_submit.click()
#     else:
#         print('There is no signin button')

#     print('The signin is done')
#     # # Search for NVDA
#     # search_market(driver, "NVDA")

#     # Wait before closing
#     time.sleep(10)

# # Connect to paper trading
# stocks = ['NVDA', 'MSFT']
# def instantiate():
#     search_market(driver, stocks[0])
#     connect_paper_trading(driver)

# # As long as we are in the game, we need to keep playing
# # Let's assume for today we have the following stocks to look at
# def sell():
#     stocks_cons = []
#     for stock in stocks[1:]:
#         #clear the overall file before every new stock
#         with open('file.txt','w') as f:
#             pass
        
#         name = stock
#         search_remaining(driver, name)  # Search and open the stock page
#         stock_info = stock_details(driver)  # Get details from the stock page
#         capture_candlestick_chart(driver, "../downloaded_candles")  # Download image of candlestick
#         print('The stock details are', stock_info)
        
#         min_est_per = 0.1
#         min_est_rv = 0.34
#         max_est_price = 6000
#         max_est_float = 2000000000000
        
#         # Check whether the stock meets client requirements
#         print('Stocks detail', stock_info['shares_float'], stock_info['current_price'])
#         if True:  # If yes, then we buy the stock
#             res = buy_stock(stock_info, name)
#             recommendation = res['Recommendation']
#             print('The result for buy is',recommendation)
#             if recommendation == 'BUY' or recommendation == 'buy':
#                 print('We are buying this stock')
#                 automate_buy(driver,res)
#                 # We will store the stock in database in future

#         # result = sell_hold_stock(stock_info, stock)

# # Retrieved all the stocks we bought from the database
# # Let's assume the following stocks are in the database
# max_checks = 10  # Stop after 100 iterations
# check_count = 0
# stocks_from_db = ['TSLA', 'AAPL']
# while check_count < max_checks:
#     print('We entered in the while loop')
#     for stock in stocks_from_db:
#         print('The stock in sell_buy', stock)
#         search_remaining(driver, stock)
#         stock_info = stock_details(driver)
#         res = sell_hold_stock(stock_info, stock)
#         print('The result for sell is', res)
#         if res.lower() == 'sell':
#             automate_sell(driver)
#         elif res.lower() == 'buy':
#             automate_buy(driver)
#         else:
#             print('Hold for a few more minutes')

#     time.sleep(600)  # Check every 10 minutes
#     check_count += 1

# time.sleep(2400)

# # Close the browser
# driver.quit()



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
        recommendation = res['Recommendation']
        print('The recommendation is ',recommendation)
        if recommendation.lower() == 'buy':
            automate_buy(driver, res)
            return JSONResponse(content={
                "message": f"Buying stock {stock_action.stocks[0]}",
                "stock_info": stock_info,
                "buy_stock_response": res,
                "summarized_news": summarized_news,
                "sentiment_of_news": sentiment_of_news,
            })
        else:
            raise HTTPException(status_code=400, detail=f"Recommendation is not to buy: {recommendation}")
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

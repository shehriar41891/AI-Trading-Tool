from fastapi import FastAPI, Response, Request, Query, HTTPException
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
from automation_selenium.get_stock_names import extract_stock_data
import os 
from dotenv import load_dotenv
from db.db_operations import find_all_stocks,add_to_db,delete_from_db,get_current_shares
import random
from fastapi import FastAPI, Depends, Query, BackgroundTasks
from typing import Optional
import re
import uvicorn
import threading
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from automation_selenium.alert import show_custom_alert,alert_candle,confirm_alert

load_dotenv()

WARRIOR_TRADING_URL = os.getenv('WARRIOR_TRADING_URL')
stop_analysis_flag = threading.Event()

# Load environment variables
load_dotenv()

# Set up FastAPI app
app = FastAPI()

is_running = False

# Allow all origins or set a specific origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Set your credentials
email = os.getenv('EMAIL_ADDRESS')
password = os.getenv('PASSWORD')

def read_cookies(request: Request):
    cookies = request.cookies  
    return {"cookies": cookies}

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
    
    signed_in = True  
    return signed_in

# Function to instantiate market data and connect
def instantiate(driver, stock, trade_option):
    search_market(driver, stock)
    time.sleep(3)
    if trade_option == 'paper_trading':
        connect_paper_trading(driver)
    else:
        print('Please connect with your broker')
        show_custom_alert(driver)
        time.sleep(100)
        
        
HTML_FILE_PATH = "web_page/page.html"

@app.get("/")
def serve_homepage():
    if os.path.exists(HTML_FILE_PATH):
        return FileResponse(HTML_FILE_PATH)
    return {"error": "index.html not found"}

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
@app.get("/buy_stock/")
def buy_stock_endpoint(trade_option: Optional[str] = Query(None)):
    print("Full Query Params:", trade_option)  # Debugging
    print("Received Trade Option:", trade_option if trade_option else "None")
    
    stocks_in_db = find_all_stocks()
    if len(stocks_in_db) == 0:
        print('We are inside the if block')
        list_of_stocks = extract_stock_data(WARRIOR_TRADING_URL)
        list_of_stocks_to_buy = []
        driver = init_driver()
        try:
            signin(driver)  # Ensure user is signed in before taking action
            db_stocks = []
            instantiate(driver, 'TSLA', trade_option)  # Ensure market is instantiated before buying 
            print('We are inside the if condition of stocks_in_db')
            for stock in list_of_stocks[1:]:
                stock_info = stock
                print('The stock infor is ',stock_info)
                search_remaining(driver,stock['name'])
                # stock_info = stock_details(driver)
                user_response = confirm_alert(driver)
                if user_response:
                    print('Users wants adjustment in candlestick charts')
                    time.sleep(10)
                else:
                    time.sleep(10)
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
                        profit_take = res['Take-Profit']
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
                        print('We are not buying this stock at this moment')

        except Exception as e:
            driver.quit()
            raise HTTPException(status_code=500, detail=f"Error buying stock: {str(e)}")
        finally:
            driver.quit()
    else:
        return {"message" : f"You already got {len(stocks_in_db)} stocks to play around"}
    
def clean_text(text):
    clean_text = ''.join(c for c in text if ord(c) < 128)  
    clean_text = re.sub(r'[^\d.]', '', clean_text)  
    return clean_text


def sell_stock_task(trade_option):
    print('The trade option in sell stock_task is ',trade_option)
    global is_running
    driver = init_driver()  # Initialize the web driver
    try:
        signin(driver)  # Ensure user is signed in before taking action
        instantiate(driver, ['NVDA'],trade_option)  # Ensure market is instantiated before selling
        
        while is_running:
            uncleaned_stock = find_all_stocks()
            print('The raw data from database is ', uncleaned_stock)
            stock_name = uncleaned_stock[0]['_id']
            print('The name of stock is ', stock_name)

            # Check if cleaning is needed
            needs_cleaning = any(isinstance(v, str) and '��' in v for item in uncleaned_stock for v in item.values())
            if needs_cleaning:
                print('Need cleaning...')
                stock = [{k: clean_text(v) if isinstance(v, str) else v for k, v in item.items()} for item in uncleaned_stock]
            else:
                print('No cleaning needed...')
                stock = uncleaned_stock  # Use the data as is

            print('Final cleaned stock:', stock)
                        
            if not stock:
                print("No stocks available for analysis.")
                break  # No stocks left, exit loop
            
            stock = stock[0]
            if stock and int(stock['number_of_shares']) >= 1:
                stock_info = {
                    "number_of_shares": int(stock['number_of_shares']),
                    "stop loss": float(stock['stop_loss']),
                    "profit take": float(stock['profit_take'])
                }
                print('The stock under analysis is ', stock_name)
                current_shares = int(stock['number_of_shares'])
                search_remaining(driver, stock_name)
                
                capture_candlestick_chart(driver, "downloaded_candles")
                res, summarized_news, sentiment_of_news = sell_hold_stock(stock_info, stock_name)

                print('The response from the AI is ', res)
                
                recommendation = res.get("Recommendation", "").lower()

                if recommendation == 'sell':
                    shares_to_sell = int(res['Shares to Sell'])
                    stop_loss = float(res['Stop-Loss'].replace('$','').strip())
                    profit_take = float(res['Take-Profit'].replace('$','').strip())
                    
                    new_shares = max(0, current_shares - shares_to_sell)
                    add_to_db(stock_name, new_shares, stop_loss, profit_take)
                    
                    automate_sell(driver, shares_to_sell, stop_loss, profit_take)
                    print(f"Selling {shares_to_sell} shares of {stock_name}. Remaining: {new_shares}")

                elif recommendation == 'buy' and int(stock['number_of_shares']) < 10:
                    shares_to_buy = int(res['Shares to Buy'])
                    stop_loss = float(res['Stop-Loss'])
                    profit_take = float(res['Take-Profit'])

                    new_shares = current_shares + shares_to_buy
                    add_to_db(stock_name, new_shares, stop_loss, profit_take)
                    
                    automate_buy(driver, shares_to_buy, stop_loss, profit_take)
                    print(f"Buying {shares_to_buy} shares of {stock_name}. Total: {new_shares}")

                else:
                    print(f"Holding {stock_name}. Shares remain: {current_shares}")

            elif int(stock['number_of_shares']) == 0:
                delete_from_db(stock['_id'])
                print(f"Stock {stock['_id']} has no shares left. Removing from database.")
                break
            else:
                print(f"The case seems suspicious. Number of shares: {stock['number_of_shares']}")
                break

    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail=f"Error selling stock: {str(e)}")
    finally:
        driver.quit()


@app.get("/sell_stock/")
def sell_stock_endpoint(request: Request, trade_option: str = Query(None)):
    print("Full Query Params:", request.query_params)  # Debugging
    print("Received Trade Option:", trade_option if trade_option else "None")
    
    global is_running
    print("is running :",is_running)
    if not is_running:
        is_running = True
        thread = threading.Thread(target=sell_stock_task,args=(trade_option,), daemon=True)
        thread.start()
        return {"message": "Started selling stock analysis in a separate thread."}
    return {"message": "Analysis is already running."}

@app.get("/stop")
def stop_analysis():
    global is_running
    if is_running:
        print('We entered into is_running condition ',is_running)
        is_running = False  # This will stop the `sell_stock_task` loop
        return {"message": "Analysis stopped."}
    return {"message": "Analysis is not running."}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from dotenv import load_dotenv
from automation_selenium.automatino_funcs import search_market,automate_buy,automate_sell,stock_details
from automation_selenium.automatino_funcs import capture_candlestick_chart,connect_paper_trading
from db.db_operations import find_all_stocks
from sell_buy.sell_stock import sell_hold_stock
import requests
from bs4 import BeautifulSoup
from sell_buy.buy_stock import buy_stock
from automation_selenium.automatino_funcs import automate_buy,search_remaining
# Load environment variables
load_dotenv()

# Set your credentials
email = os.getenv('EMAIL_ADDRESS')
password = os.getenv('PASSWORD')

# Set up the Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Open browser in maximized mode

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.tradingview.com/")

# Wait for elements to load
time.sleep(3)

# Open user menu
user_menu_button = driver.find_element(By.CLASS_NAME, "tv-header__user-menu-button")
user_menu_button.click()
time.sleep(2)

# Click "Sign in"
sign_in_button = driver.find_element(By.CSS_SELECTOR, "button[data-name='header-user-menu-sign-in']")
sign_in_button.click()
time.sleep(2)

# Click "Email" sign-in option
email_button = driver.find_element(By.XPATH, "//button[contains(@name, 'Email')]")
email_button.click()
time.sleep(2)

# Enter email
email_input = driver.find_element(By.NAME, "id_username")
email_input.send_keys(email)
time.sleep(1)

# Enter password
password_input = driver.find_element(By.NAME, "id_password")
password_input.send_keys(password)
time.sleep(1)

# Click "Sign in"
sign_in_submit = driver.find_element(By.XPATH, "//button[contains(@class, 'submitButton-LQwxK8Bm')]")
sign_in_submit.click()

# Wait for login to complete and CAPTCHA to be solved manually
print("Please solve the CAPTCHA manually...")
time.sleep(40)  # Wait for manual CAPTCHA solving (adjust the time as needed)

# After CAPTCHA is solved, continue with the next steps
print("Continuing after CAPTCHA is solved...")
sign_in_submit.click()

# # Search for NVDA
# search_market(driver, "NVDA")

# Wait before closing
time.sleep(10)

#connect to paper trading
stocks = ['NVDA','MSFT']
search_market(driver,stocks[0])
connect_paper_trading(driver)
capture_candlestick_chart(driver, "./download")

#as long as we are in the game we need to keep playing 
#let assume for today we have the following stock to look
stocks_cons = []
for stock in stocks[1:]:
    name = stock
    search_remaining(driver, name)
    stock_info = stock_details(driver)
    print('The stock details is ',stock_info)
    min_est_per = 0.1
    min_est_rv = 0.34
    max_est_price = 6000
    max_est_float = 2000000000000
    
    print('Stocks detail',stock_info['shares_float'],stock_info['current_price'])
    # if stock_info['shares_float'] <= max_est_float and stock_info['current_price'] <= max_est_price and stock_info['relative_volume'] >=min_est_rv and stock_info['percentage_change'] >= min_est_per:
    if True:
        res = buy_stock(stock_info,name)
        print('The res for buy is ',res)
        if True:
            print('We are buying this stock')
            automate_buy(driver)
            #we will store the stock in database in future

    # result = sell_hold_stock(stock_info,stock)

#retrieved all the stocks we bought from database
#let assume the following stocks are in the database
max_checks = 10  # Stop after 100 iterations
check_count = 0
stocks_from_db = ['TSLA','AAPL']
while check_count < max_checks:
    print('We entered in the while loop')
    for stock in stocks_from_db:
        print('The stock in sell_buy ',stock)
        res = sell_hold_stock(stock_info, stock)
        print('The res for sell is ',res)
        if res.lower() == 'sell':
            automate_sell(driver)
        elif res.lower() == 'buy':
            automate_buy(driver)
        else:
            print('Hold for few more minutes')

    time.sleep(600)  # Check every 10 minutes
    check_count += 1

time.sleep(2400)

# Close the browser
driver.quit()

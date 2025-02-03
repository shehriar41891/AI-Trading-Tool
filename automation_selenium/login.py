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
time.sleep(30)  # Wait for manual CAPTCHA solving (adjust the time as needed)

# After CAPTCHA is solved, continue with the next steps
print("Continuing after CAPTCHA is solved...")
sign_in_submit.click()

# # Search for NVDA
# search_market(driver, "NVDA")

# Wait before closing
time.sleep(10)

capture_candlestick_chart(driver, "./download")

#connect to paper trading
connect_paper_trading(driver)

#as long as we are in the game we need to keep playing 
stocks = find_all_stocks()
for stock in stocks:
    name = stock['_id']
    search_market(driver, name)
    stock_info = stock_details(driver)
    print('The stock details is ',stock_info)
    # result = sell_hold_stock(stock_info,stock)

time.sleep(1200)

# Close the browser
driver.quit()

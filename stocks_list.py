from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Set up the Chrome WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Open browser maximized
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the TradingView chart URL
url = "https://www.tradingview.com/chart/OKTGVFqg/?symbol=NASDAQ%3ATSLA"
driver.get(url)

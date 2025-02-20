from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os 
from dotenv import load_dotenv

load_dotenv()

WARRIOR_TRADING_URL = os.getenv('WARRIOR_TRADING_URL')

def extract_stock_names(url):
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no UI)
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("Opening browser in headless mode...")
    driver.get(url)

    try:
        # Wait for the page to load completely
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Click the button if needed
        try:
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Scanner of the Most Active Stocks Today')]"))
            )
            button.click()
        except Exception:
            print("No button found or needed, continuing...")

        # Allow JavaScript to load data
        time.sleep(3)  # Increase if necessary

        # Wait for table rows to be fully visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'grid-cols-9')]/div"))
        )

        # Extract table data
        stock_names = []
        table_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'grid-cols-9')]/div")

        # Extract stock names (Assuming first column contains stock names)
        for i, div in enumerate(table_elements):
            if i % 9 == 0:  # First element in each row contains the stock name (if the table has 9 columns per row)
                stock_names.append(div.text.strip())

    except Exception as e:
        print(f"Error: {e}")
        driver.quit()
        return []

    driver.quit()
    return stock_names
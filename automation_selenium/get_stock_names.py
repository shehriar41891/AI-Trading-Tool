from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def extract_stock_data(url):
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

        # Define column names (modify these based on the actual website layout)
        column_names = [
            "name","Gap (%)", "Price", "Volume", "Relative Volume (Daily Rate)", 
            "Relative Volume (5 min %)", "Change From Close (%)", "Float", "Short Interest"
        ]
        # Extract table data
        stock_data = []
        table_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'grid-cols-9')]/div")

        # Assuming the table has 9 columns per row
        num_cols = len(column_names)
        for i in range(0, len(table_elements), num_cols):
            row_values = [table_elements[j].text.strip() for j in range(i, min(i + num_cols, len(table_elements)))]
            if len(row_values) == num_cols:  # Ensure full rows only
                stock_entry = dict(zip(column_names, row_values))
                stock_data.append(stock_entry)

    except Exception as e:
        print(f"Error: {e}")
        driver.quit()
        return []

    driver.quit()
    return stock_data

# # Test the function
# stocks = extract_stock_data('https://www.warriortrading.com/day-trading-watch-list-top-stocks-to-watch/')
# for stock in stocks:
#     print(stock)

import time 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import shutil
import os 
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests 
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import time

headers = {"User-Agent": "Mozilla/5.0"} 


def search_market(driver, stock_name):
    """
    Searches for a stock (e.g., NVDA) using the provided search button.
    Handles both cases:
    1. When the search bar is directly available.
    2. When "Get started for free" must be clicked first, then "Search markets here".
    3. When search button (`tv-header-search-container`) is used.
    """
    try:
        print('We inside in search market')
        time.sleep(2)  # Ensure page is fully loaded

        # Case 1: Directly find and click the search bar
        try:
            search_button = driver.find_element(By.CLASS_NAME, "searchBar-PCujdK9L")
            search_button.click()
            time.sleep(2)
        except:
            print("Case 1: Direct search bar not found, checking for alternative...")

            # Case 2: Click "Get started for free" first
            try:
                get_started_btn = driver.find_element(By.CLASS_NAME, "children-LHcKxrzD")
                get_started_btn.click()
                time.sleep(2)
                print("Clicked on 'Get started for free'")

                # Now click on "Search markets here"
                search_trigger = driver.find_element(By.CLASS_NAME, "tv-header-search-container")
                search_trigger.click()
                time.sleep(2)

            except:
                print("Required elements not found in Case 2.")

                # Case 3: Check if the button with the specific class is available and click it
                try:
                    search_button = driver.find_element(By.CLASS_NAME, "tv-header-search-container")
                    search_button.click()
                    time.sleep(2)
                    print("Clicked on the search button with class 'tv-header-search-container'")
                except:
                    print("Search button not found. Exiting search.")
                    return

        # Enter stock name
        search_input = driver.switch_to.active_element  # Get the active input field
        search_input.send_keys(stock_name)
        time.sleep(2)

        # Press ENTER to search
        search_input.send_keys(Keys.RETURN)
        time.sleep(5)

        print(f"Successfully searched for {stock_name}")

    except Exception as e:
        print(f"Error searching for {stock_name}: {e}")
        
        
def capture_candlestick_chart(driver, save_directory):
    time.sleep(3)
    print('We are inside the candlestick download function ...')
    """
    Captures and saves a candlestick chart screenshot by clicking the download button from a dropdown.
    """
    try:
        # Wait for the "header-toolbar-screenshot" button to be clickable and click it
        screenshot_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "header-toolbar-screenshot"))  # Target by the button's ID
        )
        ActionChains(driver).move_to_element(screenshot_button).click().perform()

        # Wait for the dropdown to appear and the "Download image" option to be clickable
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-name="save-chart-image"]'))  # Target the download option
        )
        ActionChains(driver).move_to_element(download_button).click().perform()

        # Wait for the download to complete (you can adjust the time as needed)
        time.sleep(5)

        print('Download option clicked, waiting for the chart to be saved...')

        # Ensure the save directory exists
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # If you're capturing a screenshot of the chart itself (assuming the chart is rendered on the page):
        chart_element = driver.find_element(By.CLASS_NAME, "chart-container")  # Adjust selector if necessary
        screenshot_path = "candlestick_chart.png"
        chart_element.screenshot(screenshot_path)

        # Move the screenshot to the desired directory
        final_path = os.path.join(save_directory, "candlestick_chart.png")
        shutil.move(screenshot_path, final_path)

        print(f"Screenshot saved at {final_path}")

    except Exception as e:
        print(f"Error capturing candlestick chart: {e}")
        

def connect_paper_trading(driver):
    """
    Connects to the Paper Trading account by clicking the corresponding button.
    """
    try:
        time.sleep(3)  # Ensure the page is fully loaded

        # Locate the Paper Trading card
        paper_trading_card = driver.find_element(By.CLASS_NAME, "wrapper-UDHP9FaB")
        paper_trading_card.click()
        time.sleep(2)

        # Locate and click the "Connect" button
        connect_button = driver.find_element(By.NAME, "broker-login-submit-button")
        connect_button.click()
        time.sleep(5)

        print("Successfully connected to Paper Trading.")

    except Exception as e:
        print(f"Error connecting to Paper Trading: {e}")

def automate_sell(driver):
    wait = WebDriverWait(driver, 10)

    # Click on the Sell button
    sell_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@data-name="sell-order-button"]')))
    sell_button.click()

    # Enter the number of shares
    quantity_input = wait.until(EC.presence_of_element_located((By.ID, 'quantity-field')))
    quantity_input.clear()
    quantity_input.send_keys("1")

    # Click Take Profit checkbox
    take_profit_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@data-name="order-ticket-profit-checkbox-bracket"]')))
    take_profit_checkbox.click()

    # Click Stop Loss checkbox
    stop_loss_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@data-name="order-ticket-loss-checkbox-bracket"]')))
    stop_loss_checkbox.click()

    # Click on the final Sell button
    final_sell_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-name="place-and-modify-button"]')))
    final_sell_button.click()

def stock_details(driver):
    """
    Extracts stock details such as average volume, shares float, current volume,
    percentage change, and current price using class names.
    """
    try:
        # Click the button first
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "button-vll9ujXF"))
        )
        button.click()
        print("Button clicked successfully!")

        # Wait for data to load
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "title-cXDWtdxq"))
        )

        # Function to convert text to float and handle large numbers like B (billion) and M (million)
        def parse_float(value):
            # value = re.sub(r'[^\d.-]', '', value)
            value = value.strip()
            value = re.sub(r'[^0-9KMBkmb.-]', '', value)
            print('The value here is ',value)
            try:
                # Handling Billion (B), Million (M), and Thousand (K)
                if 'B' in value or 'b' in value:
                    return float(value.replace('B', '').replace('b', '').strip()) * 1e9  
                elif 'M' in value or 'm' in value:
                    return float(value.replace('M', '').replace('m', '').strip()) * 1e6 
                elif 'K' in value or 'k' in value:
                    return float(value.replace('K', '').replace('k', '').strip()) * 1e3  
                else:
                    return float(value)  # No suffix, directly return the float
            except ValueError:
                return 0.0  # Return 0 if conversion fails

        # Extract Average Volume (30D) and Shares Float using class names 
        items = driver.find_elements(By.CLASS_NAME, "item-cXDWtdxq")
        
        shares_float = None
        avg_volume = None
        for item in items:
            try:
                title = item.find_element(By.CLASS_NAME, "title-cXDWtdxq").text.strip()
                value = item.find_element(By.CLASS_NAME, "data-cXDWtdxq").text.strip()
                
                if title == "Shares float":
                    shares_float = parse_float(value)
                elif title == "Average Volume (30D)":
                    avg_volume = parse_float(value)
            except Exception as e:
                print(f"Error processing item {item}: {e}")

        # Extract Current Volume
        current_volume_text = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".valueValue-l31H9iuA.apply-common-tooltip"))
        ).text.strip()
        print('Current volume without parsing is ',current_volume_text)
        current_volume = parse_float(current_volume_text)

        # Extract Percentage Change (2nd occurrence)
        percentage_change_text = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "change-SNvPvlJ3"))
        )[1].text.strip()
        percentage_change = parse_float(percentage_change_text.replace('%', '').replace('−', '-'))

        # Extract Current Price
        current_price_text = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "highlight-maJ2WnzA"))
        ).text.strip().replace(' ', '')
        current_price = parse_float(current_price_text)

        # Calculate Relative Volume (RVOL) correctly
        if avg_volume and current_volume:
            relative_volume = (current_volume / avg_volume) * 100  # Relative Volume as a percentage
        else:
            relative_volume = None

        # Return stock details
        stock_data = {
            "avg_volume": avg_volume,
            "shares_float": shares_float,
            "current_volume": current_volume,
            "percentage_change": percentage_change,
            "current_price": current_price,
            "relative_volume": relative_volume
        }

        
        # #save stock's detail to a file 
        # with open('file.txt','w') as f:
        #     f.write(stock_data)
                    
        return stock_data

    except Exception as e:
        print(f"Error extracting stock details: {e}")
        return None
    
    
#buy stock
def automate_buy(driver,shares,stop_loss,profit_take):
    wait = WebDriverWait(driver, 10)
    
    # Wait for the "Buy" button and click it
    buy_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.buyButton-hw_3o_pb')))
    ActionChains(driver).move_to_element(buy_button).click().perform()
    
    # Set the quantity
    quantity_field = wait.until(EC.presence_of_element_located((By.ID, 'quantity-field')))
    quantity_field.clear()
    quantity_field.send_keys(str(shares))

    # --- Handling "Take Profit" Checkbox ---
    try:
        take_profit_checkbox = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-name="order-ticket-profit-checkbox-bracket"]')))
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView();", take_profit_checkbox)
        time.sleep(1)  # Give time for UI update

        # Try clicking parent element
        parent_label = take_profit_checkbox.find_element(By.XPATH, './..')
        parent_label.click()
        
        print('clicked on the checkbox')
        
        # If still not checked, force click via JavaScript
        if not take_profit_checkbox.is_selected():
            driver.execute_script("arguments[0].click();", take_profit_checkbox)
            
        print('We are done uptil this points')
        
        take_profit_field = wait.until(EC.presence_of_element_located((By.ID, 'take-profit-price-field')))
        take_profit_field.clear()
        take_profit_field.send_keys(profit_take)

    except Exception as e:
        print(f"Error clicking Take Profit checkbox: {e}")

    # --- Handling "Stop Loss" Checkbox ---
    try:
        stop_loss_checkbox = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-name="order-ticket-loss-checkbox-bracket"]')))
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView();", stop_loss_checkbox)
        time.sleep(1)

        # Try clicking parent element
        parent_label = stop_loss_checkbox.find_element(By.XPATH, './..')
        parent_label.click()
        
        print('click on the loss checkbox')

        # If still not checked, force click via JavaScript
        if not stop_loss_checkbox.is_selected():
            driver.execute_script("arguments[0].click();", stop_loss_checkbox)
        
        stop_loss_field = wait.until(EC.presence_of_element_located((By.ID, 'stop-loss-price-field')))
        stop_loss_field.clear()
        stop_loss_field.send_keys(stop_loss)

    except Exception as e:
        print(f"Error clicking Stop Loss checkbox: {e}")

    # Click the "Place Order" button
    place_order_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-name="place-and-modify-button"]')))
    place_order_button.click()

    # Wait for the order to be processed
    time.sleep(3)

def search_remaining(driver, stock_symbol):
    """
    Searches for a given stock symbol using the TradingView search functionality.
    
    :param driver: Selenium WebDriver instance
    :param stock_symbol: The stock symbol to search (e.g., "NVDA")
    """
    try:
        time.sleep(3)  # Allow page to load

        # Click the symbol search button
        search_button = driver.find_element(By.ID, "header-toolbar-symbol-search")
        ActionChains(driver).move_to_element(search_button).click().perform()
        print('Button is clicked')
        time.sleep(10)  # Wait for search box to appear

        # Find the search input field
        search_input = driver.find_element(By.XPATH, "//input[@data-role='search']")
        search_input.clear()  # Clear existing text
        search_input.send_keys(stock_symbol)  # Enter the stock symbol
        search_input.send_keys(Keys.RETURN)  # Press Enter

        print(f"Searched for stock: {stock_symbol}")

        # Add your logic here to extract the stock details after searching
        stock_info = get_stock_info(driver)  # Assuming get_stock_info extracts stock details
        if stock_info:
            print(f"Stock Details: {stock_info}")
        else:
            print("Failed to retrieve stock details")

    except Exception as e:
        print(f"Error searching for stock: {e}")

def get_stock_info(driver):
    """
    Extract stock details from the page.
    
    :param driver: Selenium WebDriver instance
    :return: Dictionary containing stock info (e.g., shares, price)
    """
    try:
        # Example of extracting stock details
        shares_float = driver.find_element(By.CSS_SELECTOR, ".shares-float-class").text  # Replace with actual selector
        current_price = driver.find_element(By.CSS_SELECTOR, ".current-price-class").text  # Replace with actual selector
        
        return {'shares_float': shares_float, 'current_price': current_price}
    
    except Exception as e:
        print(f"Error extracting stock details: {e}")
        return None

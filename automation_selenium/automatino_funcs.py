import time 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import shutil
import os 
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def search_market(driver, stock_name):
    """
    Searches for a stock (e.g., NVDA) using the provided search button.
    Handles both cases:
    1. When the search bar is directly available.
    2. When "Get started for free" must be clicked first, then "Search markets here".
    """
    try:
        time.sleep(3)  # Ensure page is fully loaded

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
    """
    Captures a screenshot of the candlestick chart after clicking the download button,
    and saves it to the specified directory.
    """
    try:
        time.sleep(5)  # Ensure the page is fully loaded

        # Find and click the download button (identified by its div ID and class)
        download_button = driver.find_element(By.ID, "header-toolbar-screenshot")  # Update XPath if needed
        download_button.click()

        time.sleep(5)  # Wait for the download action to trigger (adjust timing as necessary)
        
        chart_element = driver.find_element(By.CLASS_NAME, "chart-container")  # Update selector if needed

        # Save screenshot in the desired directory
        screenshot_path = "candlestick_chart.png"
        chart_element.screenshot(screenshot_path)

        # Move the screenshot to the specified directory
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        
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


def automate_sell():
    pass

def automate_buy():
    pass 

def stock_details(driver):
    """
    Extracts stock details such as average volume, shares float, current volume,
    percentage change, and current price using class names.
    """
    try:
        # Function to convert text to float (if possible)
        def parse_float(value):
            value = re.sub(r'[^\d.-]', '', value)
            try:
                return value
            except ValueError:
                return 0.0  # Return 0 if conversion fails

        # Extract Average Volume (30D) and Shares Float using class names
        items = driver.find_elements(By.CLASS_NAME, "item-cXDWtdxq")
        
        
        # Loop through all items and find the ones we need
        shares_float = None
        avg_volume = None
        for item in items:
            title = item.find_element(By.CLASS_NAME, "title-cXDWtdxq").text.strip()
            print('The titles are ',title)
            if title == "Shares float":
                shares_float_text = item.find_element(By.CLASS_NAME, "data-cXDWtdxq").text.strip()
                shares_float = parse_float(shares_float_text)
            elif title == "Average Volume (30D)":
                avg_volume_text = item.find_element(By.CLASS_NAME, "data-cXDWtdxq").text.strip()
                avg_volume = parse_float(avg_volume_text)

        # Extract Current Volume using a CSS selector (for multiple classes)
        current_volume_text = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".valueValue-l31H9iuA.apply-common-tooltip"))
        ).text.strip()
        current_volume = parse_float(current_volume_text)

        # Extract Percentage Change (using the second occurrence)
        percentage_change_text = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "change-SNvPvlJ3"))
        )[1].text.strip()
        percentage_change = parse_float(percentage_change_text.replace('%', '').replace('−', '-'))

        # Extract Current Price
        current_price_text = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "highlight-maJ2WnzA"))
        ).text.strip().replace(' ', '')
        current_price = parse_float(current_price_text)

        # Return stock details
        stock_data = {
            "avg_volume": avg_volume,
            "shares_float": shares_float,
            "current_volume": current_volume,
            "percentage_change": percentage_change,
            "current_price": current_price
        }

        print(stock_data)
        return stock_data

    except Exception as e:
        print(f"Error extracting stock details: {e}")
        return None
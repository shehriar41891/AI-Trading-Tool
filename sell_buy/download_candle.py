from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def click_svg_element(url, xpath):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.prompt_for_download": False,
    })

    # Set up the ChromeDriver Service
    service = Service(ChromeDriverManager().install())

    # Set up the webdriver (Chrome in this case)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Navigate to the URL
    driver.get(url)

    try:
        # Wait for the SVG element to be clickable (using WebDriverWait)
        svg_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )

        # Click the SVG element
        svg_element.click()
        print("SVG element clicked successfully!")

        # Wait for any effects of the click
        time.sleep(3)  # Adjust the wait time if needed

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the browser after the interaction
        driver.quit()

# Example usage
url = "http://127.0.0.1:8050/"  # Your URL here
xpath = "//svg[@class='icon']"  # XPath to the <svg> element
click_svg_element(url, xpath)

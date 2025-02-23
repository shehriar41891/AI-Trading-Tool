import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def show_custom_alert(driver, message="⚠️ Please connect with your broker! ⚠️"):
    """Injects a styled custom alert into the webpage."""
    custom_alert_script = """
    var modal = document.createElement('div');
    modal.innerHTML = '<div id="customAlert" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 20px; background: white; box-shadow: 0 4px 8px rgba(0,0,0,0.2); text-align: center; font-size: 18px; border-radius: 10px; z-index: 10000;">' +
                    '<p style="margin: 0; font-weight: bold;">⚠️ Please connect with your broker! ⚠️</p>' +
                    '<button id="closeAlert" style="margin-top: 10px; padding: 8px 12px; border: none; background: #007BFF; color: white; cursor: pointer; border-radius: 5px;">OK</button>' +
                    '</div>';
    document.body.appendChild(modal);

    document.getElementById("closeAlert").onclick = function() {
        document.body.removeChild(modal);
    };
    """

    # Inject the styled alert
    driver.execute_script(custom_alert_script)
    print("Styled alert displayed!")
    
    
def alert_candle(driver, message="⚠️ Please connect with your broker! ⚠️"):
    """Injects a styled custom alert into the webpage."""
    custom_alert_script = """
    var modal = document.createElement('div');
    modal.innerHTML = '<div id="customAlert" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 20px; background: white; box-shadow: 0 4px 8px rgba(0,0,0,0.2); text-align: center; font-size: 18px; border-radius: 10px; z-index: 10000;">' +
                    '<p style="margin: 0; font-weight: bold;">⚠️ Adjust the candlestick chart if needed before proceeding in 10 seconds ⚠️</p>' +
                    '<button id="closeAlert" style="margin-top: 10px; padding: 8px 12px; border: none; background: #007BFF; color: white; cursor: pointer; border-radius: 5px;">OK</button>' +
                    '</div>';
    document.body.appendChild(modal);

    document.getElementById("closeAlert").onclick = function() {
        document.body.removeChild(modal);
    };
    """

    # Inject the styled alert
    driver.execute_script(custom_alert_script)
    print("Styled alert displayed!")
    
    
def confirm_alert(driver, message="Do you want to adjust the candlestick chart before proceeding?"):
    """Injects a custom Yes/No popup and returns user's choice."""
    script = f"""
    var modal = document.createElement('div');
    modal.innerHTML = '<div id="customConfirm" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 20px; background: white; box-shadow: 0 4px 8px rgba(0,0,0,0.2); text-align: center; font-size: 18px; border-radius: 10px; z-index: 10000;">' +
                      '<p style="margin: 0; font-weight: bold;">{message}</p>' +
                      '<button id="yesButton" style="margin: 10px; padding: 8px 12px; border: none; background: #28a745; color: white; cursor: pointer; border-radius: 5px;">Yes</button>' +
                      '<button id="noButton" style="margin: 10px; padding: 8px 12px; border: none; background: #dc3545; color: white; cursor: pointer; border-radius: 5px;">No</button>' +
                      '</div>';
    document.body.appendChild(modal);

    window.userResponse = null;

    document.getElementById("yesButton").onclick = function() {{
        window.userResponse = true;
        document.body.removeChild(modal);
    }};
    document.getElementById("noButton").onclick = function() {{
        window.userResponse = false;
        document.body.removeChild(modal);
    }};
    """

    driver.execute_script(script)

    # Wait for user input
    while True:
        response = driver.execute_script("return window.userResponse;")
        if response is not None:
            return response
        time.sleep(0.5)

# Example Usage:
# driver = webdriver.Chrome()
# driver.get("https://www.tradingview.com/")

# user_response = confirm_alert(driver)
# if user_response:
#     print("User wants to adjust the chart.")
# else:
#     print("User chose to proceed without adjustments.")

# print("We executed the styled alert!")
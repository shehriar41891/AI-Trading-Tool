import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize WebDriver
driver = webdriver.Chrome()

# Open a webpage
driver.get("https://www.tradingview.com/")

# JavaScript for a custom styled alert
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

# Pause execution to see the alert
time.sleep(5)

print("We executed the styled alert!")

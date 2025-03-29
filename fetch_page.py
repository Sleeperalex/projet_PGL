#!/usr/bin/env python3
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

if len(sys.argv) != 2:
    print("Usage: python fetch_page.py <URL>")
    sys.exit(1)

url = sys.argv[1]

# Configure Chrome options for headless mode and stealth settings
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
# Use a common user agent string to mimic a typical browser
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
# Disable automation flags
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Initialize the Chrome driver (adjust the executable_path if necessary)
driver = webdriver.Chrome(options=chrome_options)

# Set extra HTTP headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {"headers": headers})

# Load the target URL and wait for the page to fully render
driver.get(url)
time.sleep(5)  # Adjust this delay as necessary

# Save the page HTML to a local file
html = driver.page_source
with open("page.html", "w", encoding="utf-8") as f:
    f.write(html)

driver.quit()
print("HTML saved to page.html")
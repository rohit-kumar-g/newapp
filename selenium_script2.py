import os
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict


def fetch_new_data() -> Dict[str, str]:
    # Initialize Chrome WebDriver in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize Chrome WebDriver with options
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # URL of the YouTube search results page
        url = "https://www.youtube.com/results?search_query=mera+desh+mahan"
        driver.get(url)

        # Wait for elements to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'yt-formatted-string')))

        # Find all elements with the tag 'yt-formatted-string'
        yt_formatted_strings = driver.find_elements(By.TAG_NAME, 'yt-formatted-string')

        # Process formatted strings
        long_strings = []
        short_strings = []
        
        for element in yt_formatted_strings:
            text = element.text.strip()
            if text:
                if len(text) > 20:
                    long_strings.append(text)
                else:
                    short_strings.append(text)

        # Flatten the long and short strings as comma-separated strings
        long_strings_flat = ', '.join(long_strings)
        short_strings_flat = ', '.join(short_strings)

        return {
            "long_strings": long_strings_flat,
            "short_strings": short_strings_flat
        }
    finally:
        driver.quit()

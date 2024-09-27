import re
import os
from typing import Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_new_data(video_text: str, public_folder: str) -> Dict[str, str]:
    print("extracting description started")

    # Remove any non-ASCII characters (including emojis) from the video_text
    video_text_cleaned = re.sub(r'[^a-zA-Z0-9 ]', '', video_text)
    # Get environment variables
    HOSTING_DOMAIN = os.getenv("HOSTING_DOMAIN")

    # Initialize Chrome WebDriver in headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')  # Disable GPU rendering
    chrome_options.add_argument('--no-sandbox')    # Required when running as root
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Block images, videos, and audio
    chrome_options.add_experimental_option('prefs', {
        'profile.managed_default_content_settings.images': 2,  # Block images
        'profile.managed_default_content_settings.video': 2,   # Block videos
        'profile.managed_default_content_settings.audio': 2    # Block audio
    })

    # Check the HOSTING_DOMAIN and decide how to initialize the WebDriver
    if HOSTING_DOMAIN.endswith("onrender.com"):
        # Specify the path to the chromedriver
        service = Service("/opt/chromedriver-linux64/chromedriver")
        # Create the WebDriver instance with the service
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        # Create the WebDriver instance without the service
        driver = webdriver.Chrome(options=chrome_options)

    try:
        # Use the cleaned video_text in the YouTube search URL
        url = f"https://www.youtube.com/results?search_query={video_text_cleaned}"
        driver.get(url)

        # Wait for elements to load
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'yt-formatted-string')))

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

        print("hey r i am back 2")
        return {
            "long_strings": long_strings_flat,
            "short_strings": short_strings_flat,
            "db": "ytdesc91"
            }
    except Exception as e:
        # Log the error message and return the screenshot path
        print(f"hey r Error occurred: {e}")
        return {"error": str(e)}

    finally:
        # Capture screenshot
        screenshot_path = os.path.join(public_folder, f"{video_text_cleaned}_debug.png")
        driver.save_screenshot(screenshot_path)
        driver.quit()

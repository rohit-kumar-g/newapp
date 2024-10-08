import os
import re
import requests
from typing import Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
from fastapi import BackgroundTasks

def save_media(video_id: str, public_folder: str) -> Dict[str, str]:
    print("downloading new media started")
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
        # Open the target URL
        driver.get(f"https://y2meta.tube/convert/?videoId={video_id}")

        # Wait and switch to the iframe
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "widgetv2Api")))

        # Click on the desired tab using JavaScript
        element = driver.find_element(By.CSS_SELECTOR, "#selectTab > li:nth-child(2) a")
        driver.execute_script("arguments[0].click();", element)

        # Wait for the MP4 download button to be present and clickable
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#mp4 > table > tbody > tr:nth-child(1) > td.txt-center > button")))

        # Click the download button to start the process
        download_button = driver.find_element(By.CSS_SELECTOR, "#mp4 > table > tbody > tr:nth-child(1) > td.txt-center > button")
        driver.execute_script("arguments[0].click();", download_button)

        # Wait for the process result element to be present and visible
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#process-result > div > a")))

        # Get the download link
        download_link_element = driver.find_element(By.CSS_SELECTOR, "#process-result > div > a")
        download_link = download_link_element.get_attribute("href")

        if download_link and not download_link.startswith("javascript:void(0)"):
            # Construct a valid filename using video_id
            file_name = f"{video_id}.mp4"
            file_path = os.path.join(public_folder, file_name)

            # Download the media file
            response = requests.get(download_link, stream=True)
            response.raise_for_status()  # Ensure we notice bad responses
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(file_path)
            print(str(file_size)+ "hey r sizee")
            # Return the download URL
            return {
                "file_size": str(file_size),
                "db":"ytvidurl81",
                "path": f"{public_folder}/{file_name}",
                "file_name": f"{file_name}"
                }
        return {"error": "no link"}

    except Exception as e:
        # Log the error message and return the screenshot path
        print(f"hey r Error occurred: {e}")
        return {"error": str(e)}

    finally:
         # Capture screenshot on error
        screenshot_path = os.path.join(public_folder, f"{video_id}debug.png")
        driver.save_screenshot(screenshot_path)
        driver.quit()

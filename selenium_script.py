import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
import requests
import re


def save_media(video_id: str, public_folder: str):
    # Initialize Chrome WebDriver
    driver = webdriver.Chrome()

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
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#process-result > div > a")))

        # Get the download link
        download_link_element = driver.find_element(By.CSS_SELECTOR, "#process-result > div > a")
        download_link = download_link_element.get_attribute("href")

        if download_link and not download_link.startswith("javascript:void(0)"):
            # Download the media file directly to the server

            # Parse URL to extract query parameters
            parsed_url = urlparse(download_link)
            query_params = parse_qs(parsed_url.query)

            # Construct a valid filename
            file_name = query_params.get('id', ['default'])[0]
            file_name = re.sub(r'[\/:*?"<>|]', '', file_name) + '.mp4'
            file_path = os.path.join(public_folder, file_name)
            
            # Download the media file
            response = requests.get(download_link, stream=True)
            response.raise_for_status()  # Ensure we notice bad responses
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
    finally:
        driver.quit()
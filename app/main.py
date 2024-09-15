from fastapi import FastAPI, BackgroundTasks, Request, HTTPException
from pydantic import BaseModel
import os
import json
import requests
from fastapi.responses import JSONResponse
from selenium_script import save_media
from selenium_script2 import fetch_new_data
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import os
from selenium_script import save_media

app = FastAPI()

# Define the public folder path
PUBLIC_FOLDER = "public"
HOSTING_DOMAIN = "http://applee.me"  # Replace with your actual domain

class MediaRequest(BaseModel):
    video_id: str

def save_media_task(video_id: str):
    download_url = save_media(video_id, PUBLIC_FOLDER)
    # Append the hosting domain to the download URL
    full_download_url = f"{HOSTING_DOMAIN}{download_url}"
    postSheet({"url" :full_download_url})

@app.post("/save_media/")
async def save_media_endpoint(request: MediaRequest, background_tasks: BackgroundTasks):
    # Add a background task to download the video
    background_tasks.add_task(save_media_task, request.video_id)
    
    return {"message": "Media download started"}


class FetchDetailsRequest(BaseModel):
    title: str  # For fetching YouTube data


@app.get("/media/")
async def list_media():
    media_files = [f for f in os.listdir(PUBLIC_FOLDER) if f.endswith('.mp4')]
    media_links = [f"/media/{file}" for file in media_files]
    return {"media_links": media_links}

@app.get("/media/{file_name}")
async def get_media(file_name: str):
    file_path = os.path.join(PUBLIC_FOLDER, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

def postSheet(data):
    # Google Apps Script URL
    reqUrl = "https://script.google.com/macros/s/AKfycbwm56hDzjdPndI-ii8goVM78w-2wHrnShbLkOoXpVw/dev?access_token=ya29.a0AcM612wPpH_qqIbTqUXV0BRJy8xEAjH3AXcs2dXv0glYVij3nCnSnYE3_cvM9192XnhmX8f66-0bf-1GLEXXki-dd_KB1aLQ0DWU0QabuQr7XMUqPu_mgvHM7O2YkAKoH4jr9pm_mrkxz6r7lG8coWofIKiHYmnSObqcvIXkfgaCgYKAU8SARISFQHGX2MiIsHtJoNhoKA1Ikr9ke0TTg0177"

    # Headers for the POST request
    headersList = {
        "Accept": "*/*",
        "Content-Type": "application/json"
    }

    # Convert the data to JSON
    payload = json.dumps(data)

    # Make the POST request
    response = requests.request("POST", reqUrl, data=payload, headers=headersList)

    print(response.text)

def fetchdetailshelper(video_text_search: str):
    data = fetch_new_data(video_text_search)
    postSheet(data)


@app.post("/fetchdetails/")
async def get_details(request: FetchDetailsRequest, background_tasks: BackgroundTasks):
    # Get the title from the request body
    background_tasks.add_task(fetchdetailshelper, request.title)
    return {"message": "description download started"}


    
@app.get("/delete_media/{video_id}")
async def delete_media(video_id: str):
    # Construct the file path
    file_path = os.path.join(PUBLIC_FOLDER, f"{video_id}.mp4")

    # Check if the file exists
    if os.path.exists(file_path):
        # Remove the file
        os.remove(file_path)
        return {"message": f"File {video_id}.mp4 has been deleted successfully"}
    else:
        # Raise an error if the file doesn't exist
        raise HTTPException(status_code=404, detail=f"File {video_id}.mp4 not found")

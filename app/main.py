from fastapi import FastAPI, BackgroundTasks, Request, HTTPException
from pydantic import BaseModel
import os
import json
import requests
from fastapi.responses import JSONResponse
from app.selenium_script import save_media
from app.selenium_script2 import fetch_new_data
from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import os
from app.selenium_script import save_media
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
app.mount("/media", StaticFiles(directory="app/media"), name="public")


# Define the public folder path
PUBLIC_FOLDER = "./app/media"
HOSTING_DOMAIN = os.getenv("HOSTING_DOMAIN", "http://localhost")

class MediaRequest(BaseModel):
    video_id: str

    
def save_media_task(video_id: str):
    # try:
        download_url = save_media(video_id, PUBLIC_FOLDER)
        # Append the hosting domain to the download URL
        full_download_url = f"{HOSTING_DOMAIN}{download_url}"
        postSheet({"url": full_download_url}, "yt_full_download_url_server")
    # except Exception as e:
    #     # Handle the exception (e.g., log the error)
    #     print(f"An error occurred: {e}")


@app.post("/save_media/")
async def save_media_endpoint(request: MediaRequest, background_tasks: BackgroundTasks):
    # Add a background task to download the video
    background_tasks.add_task(save_media_task, request.video_id)
    
    return {"message": "Media download started"}


class FetchDetailsRequest(BaseModel):
    title: str  # For fetching YouTube data


@app.get("/")
async def root():
    return {"message": "Hello World"}

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

def postSheet(data, id):
    print("posting "+ id)
    # Google Apps Script URL
    try:
        reqUrl = f"{os.getenv('SCRIPT_URL', 'http://localhost')}?id={id}"
        

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
    except Exception as e:
        # Handle the exception (e.g., log the error)
        print(f"An error occurred: {e}")
def fetchdetailshelper(video_text_search: str):
    data = fetch_new_data(video_text_search)
    postSheet(data, "yt_search_details_ok")

@app.post("/fet/")
async def get_det(request: FetchDetailsRequest):
    video_text_search = request.title  # Assuming FetchDetailsRequest has a field named 'video_text'
    data = fetch_new_data(video_text_search)
    return data


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

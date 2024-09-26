from fastapi import FastAPI, BackgroundTasks, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse,FileResponse
from pydantic import BaseModel
import os
import json
import requests
from app.postDataToDb import postSheet
from app.uploader_script3 import upload_video_in_chunks
from app.selenium_script import save_media
from app.selenium_script2 import fetch_new_data
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.mount("/public", StaticFiles(directory="app/media"), name="public")


# Define the public folder path
PUBLIC_FOLDER = "./app/media"
HOSTING_DOMAIN = os.getenv("HOSTING_DOMAIN", "http://localhost")

class MediaRequest(BaseModel):
    video_id: str
    caller_to: str

    
def save_media_task(video_id: str , caller_to: str):
    # try:
        download_url = save_media(video_id, PUBLIC_FOLDER)
        # Append the hosting domain to the download URL
        full_download_url = f"{HOSTING_DOMAIN}{download_url}"
        postSheet({"url": full_download_url, "db":"ytvidurl81","caller_to":caller_to}, "yt_full_download_url_server")
    # except Exception as e:
    #     # Handle the exception (e.g., log the error)
    #     print(f"An error occurred: {e}")


@app.post("/save_media/")
async def save_media_endpoint(request: MediaRequest, background_tasks: BackgroundTasks):
    # Add a background task to download the video
    background_tasks.add_task(save_media_task, request.video_id, request.caller_to)
    
    return {"message": "Media download started"}


class FetchDetailsRequest(BaseModel):
    title: str  # For fetching YouTube data
    caller_to: str


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return ""

@app.get("/media/")
async def list_media():
    media_files = [f for f in os.listdir(PUBLIC_FOLDER) if f.endswith('.mp4')]
    media_links = [f"/public/{file}" for file in media_files]
    return {"media_links": media_links}


@app.get("/medias/", response_class=HTMLResponse)
async def list_media():
    media_files = [f for f in os.listdir(PUBLIC_FOLDER) if f.endswith('.mp4')]
    media_links = [f'<a href="/public/{file}">{file}</a>' for file in media_files]
    return "<br>".join(media_links)


@app.get("/media/{file_name}")
async def get_media(file_name: str):
    file_path = os.path.join(PUBLIC_FOLDER, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}


def fetchdetailshelper(video_text_search: str, caller_to: str):
    data = fetch_new_data(video_text_search)
    data['caller_to'] = caller_to  # Add caller_to to the data object
    postSheet(data, "yt_search_details_ok")


@app.post("/fet/")
async def get_det(request: FetchDetailsRequest):
    video_text_search = request.title  # Assuming FetchDetailsRequest has a field named 'video_text'
    caller_to = request.caller_to
    data = fetch_new_data(video_text_search)
    data['caller_to'] = caller_to  
    return data


@app.post("/fetchdetails/")
async def get_details(request: FetchDetailsRequest, background_tasks: BackgroundTasks):
    # Get the title from the request body
    background_tasks.add_task(fetchdetailshelper, request.title, request.caller_to)
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

# Pydantic model to validate input data
class UploadRequest(BaseModel):
    resumable_url: str
    video_file_path: str

@app.post("/helperup")
async def helperup(upload_req: UploadRequest, background_tasks: BackgroundTasks):
    # Start background task to handle the resumable upload
    background_tasks.add_task(upload_video_in_chunks, upload_req.resumable_url, upload_req.video_file_path)
    return {"message": "please check back soon"}

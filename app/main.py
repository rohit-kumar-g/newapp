from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import os
from selenium_script import save_media
from selenium_script2 import fetch_new_data
from fastapi.responses import JSONResponse

app = FastAPI()

# Define the public folder path
PUBLIC_FOLDER = "public"

class MediaRequest(BaseModel):
    video_id: str

def save_media_task(video_id: str):
    save_media(video_id, PUBLIC_FOLDER)

@app.post("/save_media/")
async def save_media_endpoint(request: MediaRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(save_media_task, request.video_id)
    return {"message": "Media download started in the background"}

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


@app.get("/fetchdetails")
async def get_details():
    data = fetch_new_data()
    return JSONResponse(content=data)
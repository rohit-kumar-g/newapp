from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import selenium_script

app = FastAPI()

# Define the public folder for storing media files
PUBLIC_FOLDER = "public"
os.makedirs(PUBLIC_FOLDER, exist_ok=True)

app.mount("/public", StaticFiles(directory=PUBLIC_FOLDER), name="public")

class MediaRequest(BaseModel):
    video_id: str

@app.post("/save_media/")
async def save_media_endpoint(request: MediaRequest):
    from selenium_script import save_media  # Import the function here
    save_media(request.video_id, PUBLIC_FOLDER)
    return {"message": "Media download started"}

@app.get("/media/")
async def list_media():
    media_files = [f for f in os.listdir(PUBLIC_FOLDER) if os.path.isfile(os.path.join(PUBLIC_FOLDER, f))]
    if not media_files:
        raise HTTPException(status_code=404, detail="No media files found")
    return {"media_files": media_files}

@app.get("/media/{file_name}")
async def get_media(file_name: str):
    file_path = os.path.join(PUBLIC_FOLDER, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

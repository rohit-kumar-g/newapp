import os
import requests
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel




def upload_video_in_chunks(resumable_url: str, video_file_path: str):
    chunk_size = 10 * 1024 * 1024  # Chunk size (10MB per chunk)
    
    try:
        # Get the file size
        video_file_size = os.path.getsize(video_file_path)
        
        # Open the video file in binary mode
        with open(video_file_path, 'rb') as video_file:
            start = 0
            while True:
                video_file.seek(start)
                chunk = video_file.read(chunk_size)
                if not chunk:
                    break

                # Set the headers for the current chunk
                headers = {
                    'Content-Length': str(len(chunk)),
                    'Content-Range': f'bytes {start}-{start + len(chunk) - 1}/{video_file_size}'
                }

                # Send the chunk to the resumable upload URL
                response = requests.put(resumable_url, headers=headers, data=chunk)

                # Check the response status
                if response.status_code in [200, 201]:
                    print('hey r Upload complete')
                    break
                elif response.status_code == 308:
                    # Continue uploading by adjusting the start position from the Range header
                    start = int(response.headers['Range'].split('-')[1]) + 1
                else:
                    print(f"hey r Error during upload: {response.status_code}")
                    break

    except Exception as e:
        print(f"hey r Error: {str(e)}")

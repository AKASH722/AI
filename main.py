from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from moviepy.editor import VideoFileClip
import uuid
import os
import whisper

app = FastAPI()

origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
temp_audio_dir = "temp_audio"
if not os.path.exists(temp_audio_dir):
    os.makedirs(temp_audio_dir)


def save_audio_to_temp(video_path: str) -> str:
    # Extract audio from the video
    video = VideoFileClip(video_path)
    audio_filename = f"temp_audio_{uuid.uuid4().hex}.mp3"
    audio_filepath = os.path.join(temp_audio_dir, audio_filename).replace("\\", "/")
    try:
        video.audio.write_audiofile(audio_filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    video.close()
    del video

    return audio_filepath


@app.post("/video-to-audio/")
async def video_to_audio(file: UploadFile = File(...)):
    try:
        video_path = f"temp_video_{uuid.uuid4().hex}.mp4"
        with open(video_path, "wb") as buffer:
            buffer.write(file.file.read())

        audio_filepath = save_audio_to_temp(video_path)

        os.remove(video_path)
        audio_url = f"http://127.0.0.1:8000/{audio_filepath}"
        result = model.transcribe("./temp_audio_726610c8ab154b9bbd99bbc6c9527b32.mp3")
        return result['text']
        # return audio_url

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


app.mount("/temp_audio", StaticFiles(directory=temp_audio_dir), name="temp_audio")

model = whisper.load_model("base")


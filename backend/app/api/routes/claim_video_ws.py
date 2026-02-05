from fastapi import APIRouter, WebSocket
from datetime import datetime
import os
from app.state.session_store import session_data

router = APIRouter()

@router.websocket("/ws/claim/video")
async def claim_video(ws: WebSocket):
    await ws.accept()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    VIDEO_DIR = os.path.join(os.getcwd(), "backend", "videos")
    os.makedirs(VIDEO_DIR, exist_ok=True)

    video_path = os.path.join(VIDEO_DIR, f"interview_{ts}.webm")
    session_data["video_path"] = video_path

    f = open(video_path, "ab")

    try:
        while True:
            chunk = await ws.receive_bytes()
            f.write(chunk)
    finally:
        f.close()
        print(f"🎥 Saved video: {video_path}")

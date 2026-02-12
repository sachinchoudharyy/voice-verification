from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.api.routes import claim_audio_ws, claim_video_ws, results
from app.api.routes import upload

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(claim_audio_ws.router)
app.include_router(claim_video_ws.router)
app.include_router(results.router)
app.include_router(upload.router)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(BASE_DIR, "build")

# Serve static assets properly
app.mount("/static", StaticFiles(directory=os.path.join(BUILD_DIR, "static")), name="static")

# Serve React index
@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    return FileResponse(os.path.join(BUILD_DIR, "index.html"))

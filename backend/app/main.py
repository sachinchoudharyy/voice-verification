from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import claim_audio_ws, claim_video_ws, results
from app.api.routes import upload



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(claim_audio_ws.router)
app.include_router(claim_video_ws.router)
app.include_router(results.router)
app.include_router(upload.router)

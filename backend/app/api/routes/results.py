from fastapi import APIRouter
from app.state.session_store import session_data

router = APIRouter()

@router.get("/claim/result")
def get_claim_result():
    return {
        "qa": session_data["qa"],
        "video_path": session_data["video_path"]
    }

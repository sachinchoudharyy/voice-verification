from fastapi import APIRouter
from app.state.session_store import session_data
from app.services.mongo_uploader import save_interview

router = APIRouter()

@router.post("/claim/upload")
def upload_claim(data: dict):
    result = save_interview(
        session_id=session_data["session_id"],
        qa_list=session_data["qa"],
        location=data.get("location"),
        video_path=session_data["video_path"]
    )

    return {
        "status": "saved_to_mongodb",
        "session_id": session_data["session_id"]
    }

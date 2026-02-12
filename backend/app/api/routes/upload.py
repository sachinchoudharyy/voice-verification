from fastapi import APIRouter
from app.state.session_store import session_data
from app.services.supabase_uploader import upload_interview_to_supabase

router = APIRouter()

@router.post("/claim/upload")
def upload_claim(data: dict):
    video_url = upload_interview_to_supabase(
        session_id=session_data["session_id"],
        video_path=session_data["video_path"],
        qa=session_data["qa"],
        location=data.get("location")
    )

    return {
        "status": "saved_to_supabase",
        "video_url": video_url
    }

import uuid
from app.core.supabase import supabase

def upload_interview_to_supabase(session_id, video_path, qa, location):
    # 1️⃣ Upload video to Storage
    with open(video_path, "rb") as f:
        supabase.storage.from_("interview-videos").upload(
            f"{session_id}.webm",
            f,
            {"content-type": "video/webm"}
        )

    # 2️⃣ Get public video URL
    video_url = supabase.storage.from_("interview-videos").get_public_url(
        f"{session_id}.webm"
    )

    # 3️⃣ Insert metadata into Postgres
    supabase.table("interviews").insert({
        "id": session_id,
        "location": location,
        "qa": qa,
        "video_url": video_url
    }).execute()

    return video_url

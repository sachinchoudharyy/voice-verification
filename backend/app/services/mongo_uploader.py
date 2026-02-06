from datetime import datetime
from app.core.mongodb import interviews_collection

def save_interview(session_id, qa_list, location, video_path):
    doc = {
        "session_id": session_id,
        "location": location,
        "qa": qa_list,
        "video_path": video_path,
        "created_at": datetime.utcnow()
    }

    interviews_collection.insert_one(doc)
    return doc

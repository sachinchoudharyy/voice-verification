from fastapi import APIRouter, WebSocket
from app.core.groq_llm import generate_next_question
from app.state.claim_state import claim_state, CLAIM_FIELDS_ORDER
from app.state.session_store import session_data
from app.services.speech_to_text import transcribe_audio

router = APIRouter()

def update_claim_state(answer: str):
    for field in CLAIM_FIELDS_ORDER:
        if claim_state[field] is None:
            claim_state[field] = answer
            return field
    return None

@router.websocket("/ws/claim/audio")
async def claim_audio(ws: WebSocket):
    await ws.accept()

    # First question
    q = generate_next_question()
    session_data["qa"].append({
        "question": q["question"],
        "answer": None
    })

    await ws.send_json({
        "type": "question",
        "question": q["question"]
    })

    while True:
        audio_bytes = await ws.receive_bytes()

        if len(audio_bytes) % 2 != 0:
            continue

        text = transcribe_audio(audio_bytes)

        # Save answer
        session_data["qa"][-1]["answer"] = text or "(unrecognized)"

        if text:
            update_claim_state(text)

        q = generate_next_question(last_answer=text)
        if not q:
            await ws.send_json({"type": "completed"})
            break

        session_data["qa"].append({
            "question": q["question"],
            "answer": None
        })

        await ws.send_json({
            "type": "question",
            "question": q["question"]
        })

# from fastapi import APIRouter, WebSocket
# from datetime import datetime
# import os
# import json

# from app.core.groq_llm import generate_next_question
# from app.state.claim_state import claim_state, CLAIM_FIELDS_ORDER
# from app.services.speech_to_text import transcribe_audio

# router = APIRouter()

# def update_claim_state(answer: str):
#     for field in CLAIM_FIELDS_ORDER:
#         if claim_state[field] is None:
#             claim_state[field] = answer
#             return field
#     return None

# @router.websocket("/ws/claim")
# async def claim_interview(ws: WebSocket):
#     await ws.accept()

#     # -------- VIDEO SETUP --------
#     ts = datetime.now().strftime("%Y%m%d_%H%M%S")
#     VIDEO_DIR = os.path.join(os.getcwd(), "backend", "videos")
#     os.makedirs(VIDEO_DIR, exist_ok=True)

#     video_path = os.path.join(VIDEO_DIR, f"interview_{ts}.webm")
#     video_file = open(video_path, "ab")

#     try:
#         # -------- FIRST QUESTION --------
#         next_q = generate_next_question()
#         if not next_q:
#             await ws.send_json({
#                 "type": "completed",
#                 "final_claim": claim_state
#             })
#             return

#         await ws.send_json({
#             "type": "question",
#             "field": next_q["field"],
#             "question": next_q["question"]
#         })

#         # -------- MAIN LOOP --------
#         while True:
#             meta_msg = await ws.receive()

#             if meta_msg["type"] != "text":
#                 continue

#             meta = json.loads(meta_msg["text"])
#             data_type = meta.get("type")

#             # Receive binary frame next
#             binary = await ws.receive_bytes()

#             # -------- VIDEO --------
#             if data_type == "video":
#                 video_file.write(binary)
#                 continue

#             # -------- AUDIO --------
#             if data_type == "audio":
#                 if len(binary) % 2 != 0:
#                     print("⚠️ Invalid PCM length, skipping")
#                     continue

#                 text = transcribe_audio(binary)
#                 if not text:
#                     await ws.send_json({
#                         "type": "error",
#                         "message": "Could not understand speech"
#                     })
#                     continue

#                 update_claim_state(text)

#                 next_q = generate_next_question()
#                 if not next_q:
#                     await ws.send_json({
#                         "type": "completed",
#                         "final_claim": claim_state
#                     })
#                     break

#                 await ws.send_json({
#                     "type": "question",
#                     "field": next_q["field"],
#                     "question": next_q["question"]
#                 })

#     finally:
#         video_file.close()
#         print(f"🎥 Interview video saved: {video_path}")

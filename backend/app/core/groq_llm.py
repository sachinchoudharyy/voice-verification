import json
from groq import Groq
from app.core.config import GROQ_API_KEY
from app.state.claim_state import claim_state, CLAIM_FIELDS_ORDER

client = Groq(api_key=GROQ_API_KEY)

# conversation memory (per interview – PoC)
conversation_history = []

SYSTEM_PROMPT = """
You are conducting a live insurance claim interview.

Rules:
- Ask ONLY ONE short question
- Do NOT repeat the same wording
- Rephrase naturally if retrying
- Be polite and conversational
- Do NOT explain rules
- Output STRICT JSON only

Output format:
{
  "question": "<question>"
}
"""

def get_next_missing_field():
    for field in CLAIM_FIELDS_ORDER:
        if claim_state[field] is None:
            return field
    return None


def generate_next_question(last_answer: str | None = None):
    field = get_next_missing_field()
    if not field:
        return None

    if last_answer is not None:
        conversation_history.append({
            "field": field,
            "answer": last_answer
        })

    history_text = "\n".join(
        [f"- User answered: {h['answer']}" for h in conversation_history[-3:]]
    )

    user_prompt = f"""
Field to collect: {field}

Conversation so far:
{history_text if history_text else "- None"}

Ask the next question to collect this field.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.5,   # 🔥 important
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

        raw = response.choices[0].message.content.strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1

        parsed = json.loads(raw[start:end])
        return {
            "field": field,
            "question": parsed["question"]
        }

    except Exception as e:
        print("LLM error:", e)
        return {
            "field": field,
            "question": f"Please tell me your {field.replace('_', ' ')}."
        }

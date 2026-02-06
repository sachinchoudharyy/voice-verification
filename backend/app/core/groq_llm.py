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

    user_prompt = f"""
Field to collect: {field}

Previous answer:
{last_answer or "None"}

Ask ONE clear question to collect this field.
Return ONLY valid JSON.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.5,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

        raw = response.choices[0].message.content.strip()

        # 🔒 HARD JSON EXTRACTION
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError("No JSON found")

        parsed = json.loads(match.group())

        return {
            "field": field,
            "question": parsed["question"]
        }

    except Exception as e:
        print("LLM error:", e)

        # 🔁 SAFE FALLBACK (never blocks interview)
        return {
            "field": field,
            "question": f"Please tell me your {field.replace('_', ' ')}."
        }
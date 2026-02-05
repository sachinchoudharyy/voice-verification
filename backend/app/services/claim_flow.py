from app.state.claim_state import claim_state, CLAIM_FIELDS_ORDER

def update_claim(answer: str):
    for field in CLAIM_FIELDS_ORDER:
        if claim_state[field] is None:
            claim_state[field] = answer
            return field
    return None

def is_claim_complete():
    return all(value is not None for value in claim_state.values())

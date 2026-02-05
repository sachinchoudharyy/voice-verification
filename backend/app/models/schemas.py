from pydantic import BaseModel
from typing import Literal

class NextQuestion(BaseModel):
    field: Literal[
        "policy_number",
        "accident_date",
        "accident_location",
        "vehicle_damage",
        "police_report"
    ]
    question: str

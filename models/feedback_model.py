from typing import Optional
from pydantic import BaseModel, UUID1

class FeedbackInput(BaseModel):
    mission_id: UUID1
    user_comment: str
    rating: int
    prompt_version: Optional[str] = 'unknown'

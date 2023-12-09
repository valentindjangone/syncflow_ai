from typing import Optional
from pydantic import BaseModel

class MissionUpdate(BaseModel):
    abstract: Optional[str] = None
    detail: Optional[str] = None
    # Ajouter les autres modifs ici + tard

class Mission(BaseModel):
    mission: str

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class MissionUpdate(BaseModel):
    abstract: Optional[str] = None
    detail: Optional[str] = None
    # Ajouter les autres modifs ici + tard

class Mission(BaseModel):
    mission: str
    
class Role(BaseModel):
    role_name: str = Field(description="Emoji related to the role + name of the role.")
    skills_required: List[str] = Field(description="List of skills required for the role.")
    reason: str = Field(description="The reason why this role is required, with details on the tech and process.")

class BudgetDetail(BaseModel):
    role_name: str = Field(description="Name of the role.")
    allocated_budget: float = Field(description="Budget allocated for this role.")

class Budget(BaseModel):
    total: float = Field(description="The total cost of the mission.")
    roles_budget: List[BudgetDetail] = Field(description="Budget allocation for each role involved in the mission.")

class ExtractedMission(BaseModel):
    name: str = Field(description="A synthetic name of the mission.")
    abstract: str = Field(description="A reformulated, synthetic description of the mission.")
    detail: str = Field(description="An advanced technical reformulation of the mission, highlighting important details.")
    roles: List[Role] = Field(description="List of the different required roles for the mission.")
    budget: Budget = Field(description="Budget details of the mission.")

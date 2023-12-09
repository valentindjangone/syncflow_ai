import openai
from fastapi import APIRouter, HTTPException
from pydantic import UUID1
from models.mission_model import Mission, MissionUpdate
from services.mission_service import extract_mission_details
from services.db_service import store_processed_mission, store_raw_response, update_mission_details
import os

router = APIRouter(prefix='/mission')

@router.post("/extract_details")
async def extract_mission_details_route(mission: Mission, include_raw: bool = False, api_key=os.getenv('OPENAI_API_KEY')):
    openai.api_key=api_key
    try:
        processed_mission, raw_response = await extract_mission_details(mission.mission)
        await store_processed_mission(processed_mission)
        await store_raw_response(raw_response)
        if include_raw:
            return {"processed_mission": processed_mission, "raw_response": raw_response}
        else:
            return processed_mission
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur rencontrée : {str(e)}")

@router.patch("/{mission_id}")
async def update_mission(mission_id: UUID1, mission_update: MissionUpdate):
    try:
        # Appel à la fonction pour mettre à jour la mission
        update_response = update_mission_details(mission_id, mission_update)
        return update_response
    except HTTPException as e:
        # Gestion des erreurs, par exemple si la mission n'est pas trouvée ou en cas d'erreur serveur
        raise e
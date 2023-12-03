from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, UUID1
from typing import Optional, List, Dict
import uvicorn
import syncflowai


api = FastAPI()

origins = [
    "http://localhost:3000",
]


api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class MissionUpdate(BaseModel):
    abstract: Optional[str] = None
    detail: Optional[str] = None
    # Ajouter les autres modifs ici + tard

class Mission(BaseModel):
    mission: str

class FeedbackInput(BaseModel):
    mission_id: UUID1
    user_comment: str
    rating: int
    prompt_version: Optional[str] = 'unknown'

@api.post("/extract_all_details")
async def extract_mission_details(mission: Mission, include_raw: bool = False):
    try:
        processed_mission, raw_response = syncflowai.extract_mission_details(mission.mission)
        syncflowai.store_processed_mission(processed_mission)
        syncflowai.store_raw_response(raw_response)
        # Retourner mission_details et raw_response si include_raw est True
        if include_raw:
            return {"processed_mission": processed_mission, "raw_response": raw_response}
        else:
            return processed_mission

    except Exception as e:
            # Cela capturera toutes les exceptions, y compris KeyError, MySQLdb.Error, etc.
            raise HTTPException(status_code=500, detail=f"Erreur rencontrée : {str(e)}")

@api.patch("/missions/{mission_id}")
async def update_mission(mission_id: UUID1, mission_update: MissionUpdate):
    try:
        # Appel à la fonction pour mettre à jour la mission
        update_response = syncflowai.update_mission_details(mission_id, mission_update)
        return update_response
    except HTTPException as e:
        # Gestion des erreurs, par exemple si la mission n'est pas trouvée ou en cas d'erreur serveur
        raise e

@api.post('/feedback')    
async def submit_feedback(feedback_input: FeedbackInput):
    try:
        feedback_response = syncflowai.write_feedback(
            feedback_input.mission_id,
            feedback_input.user_comment,
            feedback_input.rating,
            feedback_input.prompt_version
        )
        return {"message": "Feedback submitted successfully", "feedback_id": feedback_response["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Définition du nouveau point de terminaison
@api.get("/wordcloud-data")
async def wordcloud_data():
    try:
        # Appel de la fonction get_wordcount et récupération des données
        data = syncflowai.get_wordcount()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@api.get("/stats")
async def stats_data():
    try:
        # Appel de la fonction get_wordcount et récupération des données
        data = syncflowai.get_stats()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Exécuter l'application si ce fichier est le point d'entrée principal
if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)
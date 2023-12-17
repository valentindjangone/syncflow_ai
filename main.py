<<<<<<< HEAD
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
=======
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, UUID1
from typing import Optional, List, Dict
>>>>>>> 9632665f9faabbf0e9a4eed41d34d3d9e2bd6af9
import uvicorn
from routes import mission_route, feedback_route, data_analysis_route
from openai import OpenAI
import instructor
from dotenv import load_dotenv

load_dotenv()


client = OpenAI()
instructor.patch(client)


<<<<<<< HEAD
=======
api = FastAPI()

>>>>>>> 9632665f9faabbf0e9a4eed41d34d3d9e2bd6af9
origins = [
    "*"# http://localhost:3000", "https://dework.fly.dev/create/mission"
]


api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# Missions
api.include_router(mission_route.router)
api.include_router(feedback_route.router)
api.include_router(data_analysis_route.router)


<<<<<<< HEAD
=======
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
async def wordcloud_data(which_db: str = Query(enum=["A", "B"])):
    try:
        # Appel de la fonction get_wordcount et récupération des données
        data = syncflowai.get_wordcount(which_db)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@api.get("/stats")
async def stats_data(days : int):
    try:
        # Appel de la fonction get_wordcount et récupération des données
        data = syncflowai.get_stats(days)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Exécuter l'application si ce fichier est le point d'entrée principal
>>>>>>> 9632665f9faabbf0e9a4eed41d34d3d9e2bd6af9
if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)
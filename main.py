from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
    allow_headers=["*"],
)



class Mission(BaseModel):
    mission: str

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
        
# Exécuter l'application si ce fichier est le point d'entrée principal
if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import syncflowai
from syncflowai import to_db
import MySQLdb


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
        mission_details, raw_response = syncflowai.extract_mission_details(mission.mission)
        to_db(mission_details)
        
        # Retourner mission_details et raw_response si include_raw est True
        if include_raw:
            return {"mission_details": mission_details, "raw_response": raw_response}
        else:
            return mission_details
        
    except MySQLdb.Error as err:
        raise HTTPException(status_code=503, detail=f"Erreur lors de l'insertion dans la base de données: {err}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# Exécuter l'application si ce fichier est le point d'entrée principal
if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)
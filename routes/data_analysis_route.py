from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends
from starlette.requests import Request
from services.data_analysis_service import get_wordcount, get_stats
from fastapi_auth_middleware import AuthMiddleware, FastAPIUser
from typing import Tuple, List


# Fonction de vérification de l'autorisation
def verify_authorization_header(auth_header: str) -> Tuple[List[str], FastAPIUser]:
    # Ici, implémentez la logique pour décoder et vérifier le JWT
    # Exemple simple :
    user = FastAPIUser(first_name="Valentin", last_name="MLOps", user_id=1)
    scopes = []
    return scopes, user

app = FastAPI()

# Ajouter le middleware avec votre méthode de vérification à l'application principale
app.add_middleware(AuthMiddleware, verify_authorization_header=verify_authorization_header)

# Création d'une instance de APIRouter
router = APIRouter(prefix='/data-analysis', tags=["Data Analysis"])

@router.get("/wordcloud-data")
async def wordcloud_data(request: Request, which_db: str = Query(enum=["A", "B"])):
    user = request.user  # Accéder à l'utilisateur via l'objet Request
    try:
        data = get_wordcount(which_db)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def stats_data(request: Request, days: int):
    user = request.user  # Accéder à l'utilisateur via l'objet Request
    try:
        data = get_stats(days)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ajouter le routeur à l'application principale
app.include_router(router)

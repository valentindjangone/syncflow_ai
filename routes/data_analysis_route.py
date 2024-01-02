from fastapi import APIRouter, HTTPException, Query
from services.data_analysis_service import get_wordcount, get_stats
from fastapi_auth_middleware import AuthMiddleware, FastAPIUser

# Création d'une instance de APIRouter
router = APIRouter(prefix='/data-analysis', tags=["Data Analysis"])

# Configuration de l'authentification
auth_middleware = AuthMiddleware(
    secret_key="password",  # Utilisez votre clé secrète pour les jetons JWT
    algorithm="HS256",  # Algorithme utilisé pour les jetons JWT
    auth_header_prefix="Bearer"  # Préfixe utilisé dans le header d'authentification
)

# Ajout du middleware au routeur
router.middleware('http')(auth_middleware)

@router.get("/wordcloud-data")
async def wordcloud_data(user: FastAPIUser, which_db: str = Query(enum=["A", "B"])):
    try:
        data = get_wordcount(which_db)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def stats_data(user: FastAPIUser, days: int):
    try:
        data = get_stats(days)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
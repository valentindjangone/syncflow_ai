from fastapi import APIRouter, HTTPException, Query
from services.data_analysis_service import get_wordcount, get_stats
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWTError
from pydantic import BaseModel
from typing import Optional

# Configuration du schéma de sécurité OAuth2 avec Password (et Bearer)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    username: Optional[str] = None

# Fonction pour vérifier le token JWT
def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Votre clé secrète pour le décodage du JWT
        secret_key = "YOUR_SECRET_KEY"
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    return token_data

router = APIRouter(prefix='/data-analysis', tags=["Data Analysis"])

@router.get("/wordcloud-data")
async def wordcloud_data(token_data: TokenData = Depends(verify_token), which_db: str = Query(enum=["A", "B"])):
    try:
        data = get_wordcount(which_db)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def stats_data(token_data: TokenData = Depends(verify_token), days: int):
    try:
        data = get_stats(days)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
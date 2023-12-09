from fastapi import APIRouter, HTTPException, Query
from services.data_analysis_service import get_wordcount, get_stats

router = APIRouter(prefix ='/data-analysis', tags=["Data Analysis"])


@router.get("/wordcloud-data")
async def wordcloud_data(which_db: str = Query(enum=["A", "B"])):
    try:
        # Appel de la fonction get_wordcount et récupération des données
        data = get_wordcount(which_db)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/stats")
async def stats_data(days : int):
    try:
        # Appel de la fonction get_wordcount et récupération des données
        data = get_stats(days)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

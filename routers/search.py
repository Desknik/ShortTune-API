from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from models.schemas import SearchRequest, SearchResponse, ErrorResponse
from services.youtube_music_service import youtube_music_service
from config.logging import logger

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/", response_model=SearchResponse)
async def search_music(
    query: str = Query(..., description="Termo de busca (título + artista)", min_length=1),
    limit: Optional[int] = Query(20, ge=1, le=50, description="Número máximo de resultados")
):
    """
    Busca músicas no YouTube Music
    
    **Parâmetros:**
    - **query**: Termo de busca contendo título e/ou artista
    - **limit**: Número máximo de resultados (1-50, padrão: 20)
    
    **Retorna:**
    - Lista de músicas encontradas com videoId, título, artista e duração
    
    **Exemplo de uso:**
    ```
    GET /search?query=Imagine Dragons Bones&limit=10
    ```
    """
    try:
        logger.info(f"Busca solicitada: '{query}' (limite: {limit})")
        
        # Executa busca
        results = await youtube_music_service.search_songs(query, limit)
        
        response = SearchResponse(
            results=results,
            total_results=len(results)
        )
        
        logger.info(f"Busca concluída: {len(results)} resultados para '{query}'")
        return response
        
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "search_failed",
                "message": "Falha na busca de músicas",
                "details": str(e)
            }
        )


@router.post("/", response_model=SearchResponse)
async def search_music_post(request: SearchRequest):
    """
    Busca músicas no YouTube Music (método POST)
    
    **Body:**
    ```json
    {
        "query": "Imagine Dragons Bones"
    }
    ```
    
    **Retorna:**
    - Lista de músicas encontradas
    """
    try:
        logger.info(f"Busca POST solicitada: '{request.query}'")
        
        results = await youtube_music_service.search_songs(request.query)
        
        response = SearchResponse(
            results=results,
            total_results=len(results)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Erro na busca POST: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "search_failed",
                "message": "Falha na busca de músicas",
                "details": str(e)
            }
        )

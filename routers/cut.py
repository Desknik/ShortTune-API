from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.schemas import CutRequest, CutResponse
from services.audio_edit_service import audio_edit_service
from utils.file_manager import file_manager
from config.logging import logger

router = APIRouter(prefix="/cut", tags=["Audio Editing"])


async def cleanup_file(filepath: str):
    """Task em background para limpeza de arquivo"""
    try:
        import asyncio
        await asyncio.sleep(1800)  # Aguarda 30 minutos
        file_manager.delete_file(filepath)
    except:
        pass


@router.post("/", response_model=CutResponse)
async def cut_audio(
    request: CutRequest,
    background_tasks: BackgroundTasks
):
    """
    Corta trecho do áudio entre dois tempos
    
    **Body:**
    ```json
    {
        "filepath": "temp/audio_123.mp3",
        "start": 30.0,
        "end": 60.0
    }
    ```
    
    **Parâmetros:**
    - **filepath**: Caminho do arquivo de áudio (obtido do endpoint /download)
    - **start**: Tempo de início em segundos (>=0)
    - **end**: Tempo de fim em segundos (>start)
    
    **Retorna:**
    - Caminho do arquivo cortado
    - Duração original e do corte
    - Tamanho do arquivo gerado
    
    **Validações:**
    - Arquivo deve existir no sistema
    - Tempos devem estar dentro da duração do áudio
    - Tempo de fim deve ser maior que tempo de início
    
    **Exemplo de uso:**
    1. Faça download de uma música: `POST /download`
    2. Use o filepath retornado para cortar: `POST /cut`
    3. Arquivo cortado será disponibilizado temporariamente
    """
    try:
        logger.info(f"Corte solicitado: {request.filepath} ({request.start}s-{request.end}s)")
        
        # Valida arquivo
        if not file_manager.file_exists(request.filepath):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "file_not_found",
                    "message": "Arquivo de áudio não encontrado",
                    "details": f"Caminho: {request.filepath}"
                }
            )
        
        # Valida intervalo de tempo
        if request.start >= request.end:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_time_range",
                    "message": "Tempo de fim deve ser maior que tempo de início"
                }
            )
        
        if request.start < 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_start_time",
                    "message": "Tempo de início não pode ser negativo"
                }
            )
        
        # Executa corte
        result = await audio_edit_service.cut_audio(
            request.filepath,
            request.start,
            request.end
        )
        
        # Agenda limpeza do arquivo cortado
        background_tasks.add_task(cleanup_file, result['filepath'])
        
        response = CutResponse(
            success=True,
            filepath=result['filepath'],
            original_duration=result['original_duration'],
            cut_duration=result['cut_duration'],
            file_size=result['file_size']
        )
        
        logger.info(f"Corte concluído: {result['filepath']} ({result['cut_duration']}s)")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no corte de áudio: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "cut_failed",
                "message": "Falha ao cortar áudio",
                "details": str(e)
            }
        )


@router.get("/metadata")
async def get_audio_metadata(filepath: str):
    """
    Obtém metadados de um arquivo de áudio
    
    **Parâmetros:**
    - **filepath**: Caminho do arquivo de áudio
    
    **Retorna:**
    - Duração, codec, sample rate, canais, bitrate, tamanho
    
    **Uso:**
    ```
    GET /cut/metadata?filepath=temp/audio_123.mp3
    ```
    """
    try:
        if not filepath:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "missing_filepath",
                    "message": "Caminho do arquivo é obrigatório"
                }
            )
        
        metadata = await audio_edit_service.get_audio_metadata(filepath)
        
        return {
            "success": True,
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter metadados: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "metadata_failed",
                "message": "Falha ao obter metadados do áudio",
                "details": str(e)
            }
        )

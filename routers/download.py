from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.schemas import DownloadRequest, DownloadResponse, AudioFormat
from services.download_service import download_service
from utils.file_manager import file_manager
from config.logging import logger

router = APIRouter(prefix="/download", tags=["Download"])


async def cleanup_file(filepath: str):
    """Task em background para limpeza de arquivo"""
    try:
        import asyncio
        await asyncio.sleep(3600)  # Aguarda 1 hora
        file_manager.delete_file(filepath)
    except:
        pass


@router.post("/", response_model=DownloadResponse)
async def download_audio(
    request: DownloadRequest,
    background_tasks: BackgroundTasks
):
    """
    Baixa áudio de uma música do YouTube
    
    **Body:**
    ```json
    {
        "video_id": "abc123",
        "format": "mp3"
    }
    ```
    
    **Formatos suportados:**
    - `mp3`: Formato MP3 (padrão)
    - `wav`: Formato WAV (maior qualidade)
    
    **Retorna:**
    - Caminho do arquivo baixado
    - Metadados da música (título, artista, duração)
    - Informações do arquivo (tamanho, formato)
    
    **Considerações:**
    - Arquivos são automaticamente removidos após 1 hora
    - Tamanho máximo: 100MB
    - Apenas para uso educacional e preview
    """
    try:
        logger.info(f"Download solicitado: {request.video_id} (formato: {request.format.value})")
        
        # Valida video_id
        if not request.video_id or len(request.video_id) < 5:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_video_id",
                    "message": "Video ID inválido"
                }
            )
        
        # Executa download
        result = await download_service.download_audio(request.video_id, request.format)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "download_failed",
                    "message": "Falha no download do áudio"
                }
            )
        
        # Valida tamanho do arquivo
        if not file_manager.validate_file_size(result['filepath']):
            file_manager.delete_file(result['filepath'])
            raise HTTPException(
                status_code=413,
                detail={
                    "error": "file_too_large",
                    "message": f"Arquivo excede o limite de {file_manager.settings.max_file_size_mb}MB"
                }
            )
        
        # Agenda limpeza do arquivo
        background_tasks.add_task(cleanup_file, result['filepath'])
        
        response = DownloadResponse(
            success=True,
            filepath=result['filepath'],
            title=result['title'],
            artist=result['artist'],
            duration=result['duration'],
            format=result['format'],
            file_size=result['file_size']
        )
        
        logger.info(f"Download concluído: {result['filepath']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no download: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "download_error",
                "message": "Erro interno no download",
                "details": str(e)
            }
        )


@router.get("/formats")
async def get_supported_formats():
    """
    Lista formatos de áudio suportados
    
    **Retorna:**
    - Lista de formatos disponíveis com descrições
    """
    return {
        "formats": [
            {
                "value": "mp3",
                "name": "MP3",
                "description": "Formato padrão, boa qualidade e tamanho reduzido"
            },
            {
                "value": "wav",
                "name": "WAV",
                "description": "Alta qualidade, arquivo maior"
            }
        ]
    }

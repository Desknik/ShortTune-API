from fastapi import APIRouter
from models.schemas import HealthResponse
from services import transcription_service
from config.settings import settings
import psutil
import platform

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Verifica saúde da API e serviços
    
    **Retorna:**
    - Status geral da API
    - Disponibilidade dos serviços
    - Informações do sistema
    """
    try:
        # Verifica disponibilidade dos serviços
        services_status = {}
        
        # YouTube Music API
        try:
            services_status["youtube_music"] = "available"
        except:
            services_status["youtube_music"] = "unavailable"
        
        # Whisper Local
        try:
            services_status["whisper_local"] = "available"
        except:
            services_status["whisper_local"] = "unavailable"
        
        # OpenAI API
        if settings.openai_api_key:
            services_status["openai_api"] = "configured"
        else:
            services_status["openai_api"] = "not_configured"
        
        # FFmpeg
        try:
            import ffmpeg
            services_status["ffmpeg"] = "available"
        except:
            services_status["ffmpeg"] = "unavailable"
        
        # Engines de transcrição disponíveis
        available_engines = await transcription_service.get_available_engines()
        services_status["transcription_engines"] = available_engines
        
        # Informações do sistema
        system_info = {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('.').percent
        }
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            services={
                "services": services_status,
                "system": system_info,
                "configuration": {
                    "debug": settings.debug,
                    "temp_dir": settings.temp_dir,
                    "max_file_size_mb": settings.max_file_size_mb,
                    "rate_limit": f"{settings.rate_limit_requests}/{settings.rate_limit_window}s"
                }
            }
        )
        
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            services={
                "error": str(e)
            }
        )


@router.get("/")
async def root():
    """
    Endpoint raiz da API
    
    **Retorna:**
    - Informações básicas da API
    - Links para documentação
    """
    return {
        "name": "ShortTune API",
        "version": "1.0.0",
        "description": "API para criação de vídeos curtos musicais",
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "search": "/search - Buscar músicas no YouTube Music",
            "download": "/download - Baixar áudio de músicas",
            "transcribe": "/transcribe - Transcrever áudio com timestamps",
            "cut": "/cut - Cortar trechos de áudio"
        },
        "legal_notice": "Esta API é destinada apenas para fins educacionais e de preview. Respeite os direitos autorais e Termos de Serviço do YouTube."
    }

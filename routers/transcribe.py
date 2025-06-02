from fastapi import APIRouter, HTTPException, UploadFile, File, Query, BackgroundTasks
from typing import Optional
from models.schemas import TranscriptionResponse, TranscriptionEngine, TranslationEngine
from services.transcription_service import transcription_service
from utils.file_manager import file_manager
from config.settings import settings
from config.logging import logger
from utils.translation_utils import translate_segments, get_supported_languages

router = APIRouter(prefix="/transcribe", tags=["Transcription"])


async def cleanup_file(filepath: str):
    """Task em background para limpeza de arquivo"""
    try:
        import asyncio
        await asyncio.sleep(1800)  # Aguarda 30 minutos
        file_manager.delete_file(filepath)
    except:
        pass


@router.post("/", response_model=TranscriptionResponse)
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Arquivo de áudio (.mp3, .wav, .m4a, .flac)"),
    engine: TranscriptionEngine = Query(
        TranscriptionEngine.LOCAL, 
        description="Engine de transcrição: 'local' (Whisper local) ou 'openai' (API OpenAI)"
    ),
    target_lang: Optional[str] = Query(None, description="Código do idioma de destino para tradução (ex: 'pt', 'en', 'ru')"),
    translation_engine: TranslationEngine = Query(
        TranslationEngine.AI_MODEL,
        description="Engine de tradução: 'ai_model' (modelos Helsinki-NLP) ou 'deep_translator' (Google Translate)"
    )
):
    """
    Transcreve arquivo de áudio com timestamps
    
    **Parâmetros:**
    - **file**: Arquivo de áudio para transcrição
    - **engine**: Engine de transcrição
      - `local`: Usa Whisper local (padrão, gratuito)
      - `openai`: Usa API da OpenAI (requer API key)
    - **target_lang**: Código do idioma de destino para tradução (opcional). Exemplos:
      - pt (português), en (inglês), es (espanhol), fr (francês), de (alemão), ru (russo), it (italiano), nl (holandês), pl (polonês), tr (turco), ar (árabe), zh (chinês), ja (japonês), ko (coreano)
    - **translation_engine**: Engine de tradução
      - `ai_model`: Usa modelos Helsinki-NLP (padrão, local, mais lento)
      - `deep_translator`: Usa Google Translate via deep-translator (online, mais rápido, mais idiomas)
    
    **Formatos suportados:**
    - MP3, WAV, M4A, FLAC, OGG, WEBM
    
    **Retorna:**
    - Transcrição completa com timestamps por segmento
    - Idioma detectado automaticamente
    - Texto completo da transcrição
    - Traduções opcionais por segmento
    
    **Limitações:**
    - Arquivo máximo: 100MB (local) / 25MB (OpenAI)
    - OpenAI requer configuração de API key
    - deep_translator requer conexão com internet
    
    **Exemplo de resposta:**
    ```json
    {
        "success": true,
        "language": "pt",
        "segments": [
            {
                "start": 0.0,
                "end": 3.5,
                "text": "Esta é uma música incrível",
                "translation": "This is an amazing song"
            }
        ],
        "full_text": "Esta é uma música incrível..."
    }
    ```
    """
    temp_filepath = None
    
    try:
        logger.info(f"Transcrição solicitada com engine: {engine.value}, tradução: {translation_engine.value}")
        
        # Valida tipo de arquivo
        if not file.content_type or not any(
            fmt in file.content_type.lower() 
            for fmt in ['audio', 'video']
        ):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_file_type",
                    "message": "Tipo de arquivo não suportado. Use arquivos de áudio (.mp3, .wav, etc.)"
                }
            )
        
        # Lê conteúdo do arquivo
        file_content = await file.read()
        
        # Valida tamanho
        file_size_mb = len(file_content) / (1024 * 1024)
        max_size = 25 if engine == TranscriptionEngine.OPENAI else settings.max_file_size_mb
        
        if file_size_mb > max_size:
            raise HTTPException(
                status_code=413,
                detail={
                    "error": "file_too_large",
                    "message": f"Arquivo muito grande: {file_size_mb:.1f}MB (máximo: {max_size}MB para {engine.value})"
                }
            )
        
        # Salva arquivo temporário
        temp_filepath = await file_manager.save_uploaded_file(file_content, file.filename)
        
        # Verifica se formato é suportado
        if not transcription_service.is_supported_format(temp_filepath):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "unsupported_format",
                    "message": "Formato de áudio não suportado"
                }
            )
        
        # Executa transcrição
        result = await transcription_service.transcribe_audio(temp_filepath, engine)

        # Tradução opcional dos segmentos
        segments = [s.dict() if hasattr(s, 'dict') else dict(s) for s in result['segments']]
        if target_lang:
            segments = translate_segments(segments, target_lang, translation_engine.value)

        # Agenda limpeza do arquivo
        background_tasks.add_task(cleanup_file, temp_filepath)

        response = TranscriptionResponse(
            success=True,
            language=result.get('language'),
            segments=segments,
            full_text=result['full_text']
        )
        
        logger.info(f"Transcrição concluída: {len(result['segments'])} segmentos")
        return response
        
    except HTTPException:
        # Limpa arquivo em caso de erro HTTP
        if temp_filepath:
            file_manager.delete_file(temp_filepath)
        raise
        
    except Exception as e:
        # Limpa arquivo em caso de erro interno
        if temp_filepath:
            file_manager.delete_file(temp_filepath)
            
        logger.error(f"Erro na transcrição: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "transcription_failed",
                "message": "Falha na transcrição do áudio",
                "details": str(e)
            }
        )


@router.get("/translation-engines")
async def get_translation_engines():
    """
    Lista engines de tradução disponíveis e idiomas suportados
    
    **Retorna:**
    - Lista de engines de tradução disponíveis
    - Idiomas suportados por cada engine
    """
    try:
        engines_info = []
        
        # AI Model Engine
        ai_info = get_supported_languages("ai_model")
        engines_info.append({
            "value": "ai_model",
            "name": "AI Models (Helsinki-NLP)",
            "description": "Modelos de IA locais para tradução (offline, mais lento)",
            "engine_details": ai_info["engine"],
            "supported_languages": ai_info["supported_languages"],
            "language_names": ai_info["language_names"],
            "auto_detect": ai_info["auto_detect"],
            "requires_internet": False,
            "speed": "Lento",
            "quality": "Alta"
        })
        
        # Deep Translator Engine
        deep_info = get_supported_languages("deep_translator")
        engines_info.append({
            "value": "deep_translator",
            "name": "Google Translate",
            "description": "Google Translate via deep-translator (online, mais rápido)",
            "engine_details": deep_info["engine"],
            "supported_languages": deep_info["supported_languages"],
            "language_names": deep_info["language_names"],
            "auto_detect": deep_info["auto_detect"],
            "requires_internet": True,
            "speed": "Rápido",
            "quality": "Alta"
        })
        
        return {
            "translation_engines": engines_info,
            "default": "ai_model",
            "total_languages": {
                "ai_model": len(ai_info["supported_languages"]),
                "deep_translator": len(deep_info["supported_languages"])
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar engines de tradução: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "translation_engines_error",
                "message": "Erro ao obter engines de tradução disponíveis"
            }
        )


@router.get("/engines")
async def get_available_engines():
    """
    Lista engines de transcrição disponíveis
    
    **Retorna:**
    - Lista de engines disponíveis no sistema
    """
    try:
        engines = await transcription_service.get_available_engines()
        
        engine_info = []
        for engine in engines:
            if engine == "local":
                engine_info.append({
                    "value": "local",
                    "name": "Whisper Local",
                    "description": "Transcrição local usando OpenAI Whisper (gratuito)",
                    "max_file_size": f"{settings.max_file_size_mb}MB"
                })
            elif engine == "openai":
                engine_info.append({
                    "value": "openai",
                    "name": "OpenAI API",
                    "description": "Transcrição via API da OpenAI (requer API key)",
                    "max_file_size": "25MB"
                })
        
        return {
            "engines": engine_info,
            "default": "local"
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar engines: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "engines_error",
                "message": "Erro ao obter engines disponíveis"
            }
        )

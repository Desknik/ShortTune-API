import whisper
import openai
import asyncio
import tempfile
import os
from typing import List, Optional
from pathlib import Path
from models.schemas import TranscriptionSegment, TranscriptionEngine
from config.settings import settings
from config.logging import logger

# Configurar PATH do FFmpeg se não estiver disponível
def configure_ffmpeg_path():
    """Configura o PATH para incluir FFmpeg"""
    try:
        # Verificar se ffmpeg já está disponível
        import subprocess
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # FFmpeg não encontrado, adicionar ao PATH
        current_dir = Path(__file__).parent.parent
        ffmpeg_path = current_dir / "ffmpeg-master-latest-win64-gpl" / "bin"
        if ffmpeg_path.exists():
            os.environ['PATH'] = str(ffmpeg_path) + os.pathsep + os.environ.get('PATH', '')
            logger.info(f"FFmpeg PATH configurado: {ffmpeg_path}")
        else:
            logger.warning("FFmpeg não encontrado no diretório esperado")

# Configurar FFmpeg ao importar o módulo
configure_ffmpeg_path()


class TranscriptionService:
    """Serviço para transcrição de áudio usando Whisper"""
    
    def __init__(self):
        self.local_model = None
        self.model_loaded = False
        
        # Configurar OpenAI se API key estiver disponível
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
    
    async def transcribe_audio(self, file_path: str, engine: TranscriptionEngine = TranscriptionEngine.LOCAL) -> dict:
        """Transcreve áudio usando engine especificado"""
        try:
            logger.info(f"Iniciando transcrição com engine: {engine.value}")
            
            if engine == TranscriptionEngine.OPENAI:
                return await self._transcribe_with_openai(file_path)
            else:
                return await self._transcribe_with_local_whisper(file_path)
                
        except Exception as e:
            logger.error(f"Erro na transcrição: {e}")
            
            # Fallback: tenta com outro engine se possível
            if engine == TranscriptionEngine.LOCAL and settings.openai_api_key:
                logger.info("Tentando fallback para OpenAI API")
                try:
                    return await self._transcribe_with_openai(file_path)
                except Exception as fallback_error:
                    logger.error(f"Fallback também falhou: {fallback_error}")
            
            raise Exception(f"Falha na transcrição: {str(e)}")
    
    async def _transcribe_with_local_whisper(self, file_path: str) -> dict:
        """Transcreve usando Whisper local"""
        try:
            # Carrega modelo se necessário
            if not self.model_loaded:
                await self._load_local_model()
            
            logger.info("Transcrevendo com Whisper local...")
            
            # Executa transcrição em thread separada
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: self.local_model.transcribe(
                    file_path, 
                    word_timestamps=True,
                    verbose=False
                )
            )
            
            # Processa segmentos
            segments = []
            for segment in result.get('segments', []):
                segments.append(TranscriptionSegment(
                    start=segment['start'],
                    end=segment['end'],
                    text=segment['text'].strip()
                ))
            
            return {
                'language': result.get('language'),
                'segments': segments,
                'full_text': result.get('text', '').strip()
            }
            
        except Exception as e:
            logger.error(f"Erro no Whisper local: {e}")
            raise
    
    async def _transcribe_with_openai(self, file_path: str) -> dict:
        """Transcreve usando API da OpenAI"""
        try:
            if not settings.openai_api_key:
                raise Exception("OpenAI API key não configurada")
            
            logger.info("Transcrevendo com OpenAI API...")
            
            # Verifica tamanho do arquivo (limite OpenAI: 25MB)
            file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
            if file_size_mb > 25:
                raise Exception(f"Arquivo muito grande para OpenAI API: {file_size_mb:.1f}MB (máximo: 25MB)")
            
            # Executa transcrição
            loop = asyncio.get_event_loop()
            
            with open(file_path, "rb") as audio_file:
                result = await loop.run_in_executor(
                    None,
                    lambda: openai.Audio.transcribe(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json",
                        timestamp_granularities=["segment"]
                    )
                )
            
            # Processa segmentos
            segments = []
            for segment in result.get('segments', []):
                segments.append(TranscriptionSegment(
                    start=segment['start'],
                    end=segment['end'],
                    text=segment['text'].strip()
                ))
            
            return {
                'language': result.get('language'),
                'segments': segments,
                'full_text': result.get('text', '').strip()
            }
            
        except Exception as e:
            logger.error(f"Erro na API OpenAI: {e}")
            raise
    
    async def _load_local_model(self, model_name: str = "base"):
        """Carrega modelo Whisper local"""
        try:
            logger.info(f"Carregando modelo Whisper: {model_name}")
            
            loop = asyncio.get_event_loop()
            self.local_model = await loop.run_in_executor(
                None, 
                lambda: whisper.load_model(model_name)
            )
            
            self.model_loaded = True
            logger.info("Modelo Whisper carregado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo Whisper: {e}")
            raise Exception(f"Falha ao carregar Whisper: {str(e)}")
    
    def is_supported_format(self, file_path: str) -> bool:
        """Verifica se formato de áudio é suportado"""
        supported_formats = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm'}
        file_ext = Path(file_path).suffix.lower()
        return file_ext in supported_formats
    
    async def get_available_engines(self) -> List[str]:
        """Retorna engines de transcrição disponíveis"""
        engines = [TranscriptionEngine.LOCAL.value]
        
        if settings.openai_api_key:
            engines.append(TranscriptionEngine.OPENAI.value)
        
        return engines


# Global service instance
transcription_service = TranscriptionService()

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum


class AudioFormat(str, Enum):
    MP3 = "mp3"
    WAV = "wav"


class TranscriptionEngine(str, Enum):
    LOCAL = "local"
    OPENAI = "openai"


# Search Models
class SearchRequest(BaseModel):
    query: str = Field(..., description="Termo de busca para a música")


class SearchResult(BaseModel):
    video_id: str = Field(..., description="ID do vídeo no YouTube")
    title: str = Field(..., description="Título da música")
    artist: str = Field(..., description="Nome do artista")
    duration: Optional[str] = Field(None, description="Duração da música")
    thumbnail: Optional[str] = Field(None, description="URL da thumbnail")
    colors: Optional[List[str]] = Field(None, description="Cores dominantes da capa (3-4 cores em hex)")


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int


# Download Models
class DownloadRequest(BaseModel):
    video_id: str = Field(..., description="ID do vídeo do YouTube")
    format: AudioFormat = Field(AudioFormat.MP3, description="Formato do áudio")


class DownloadResponse(BaseModel):
    success: bool
    filepath: str = Field(..., description="Caminho do arquivo baixado")
    title: str = Field(..., description="Título da música")
    artist: Optional[str] = Field(None, description="Nome do artista")
    duration: Optional[float] = Field(None, description="Duração em segundos")
    format: AudioFormat
    file_size: int = Field(..., description="Tamanho do arquivo em bytes")


# Transcription Models
class TranscriptionSegment(BaseModel):
    start: float = Field(..., description="Tempo de início em segundos")
    end: float = Field(..., description="Tempo de fim em segundos")
    text: str = Field(..., description="Texto transcrito")
    translation: Optional[str] = Field(None, description="Tradução do texto para o idioma de destino")


class TranscriptionResponse(BaseModel):
    success: bool
    language: Optional[str] = Field(None, description="Idioma detectado")
    segments: List[TranscriptionSegment]
    full_text: str = Field(..., description="Texto completo da transcrição")


# Cut Models
class CutRequest(BaseModel):
    filepath: str = Field(..., description="Caminho do arquivo de áudio")
    start: float = Field(..., ge=0, description="Tempo de início em segundos")
    end: float = Field(..., gt=0, description="Tempo de fim em segundos")
    
    class Config:
        schema_extra = {
            "example": {
                "filepath": "temp/audio_123.mp3",
                "start": 30.0,
                "end": 60.0
            }
        }


class CutResponse(BaseModel):
    success: bool
    filepath: str = Field(..., description="Caminho do arquivo cortado")
    original_duration: float = Field(..., description="Duração original em segundos")
    cut_duration: float = Field(..., description="Duração do corte em segundos")
    file_size: int = Field(..., description="Tamanho do arquivo cortado em bytes")


# Error Models
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None


# Health Check
class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    services: dict

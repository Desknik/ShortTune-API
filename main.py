from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import asyncio
import uvicorn

# Imports locais
from config.settings import settings
from config.logging import logger
from routers import (
    search_router,
    download_router, 
    transcribe_router,
    cut_router,
    health_router
)
from utils import start_cleanup_task

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Criação da aplicação FastAPI
app = FastAPI(
    title="ShortTune API",
    description="""
    ## API para Criação de Vídeos Curtos Musicais

    Esta API fornece ferramentas completas para criação de conteúdo musical curto:

    ### 🎵 Funcionalidades Principais
    
    - **Busca de Músicas**: Integração com YouTube Music para encontrar músicas
    - **Download de Áudio**: Download seguro de áudio em MP3/WAV
    - **Transcrição Inteligente**: Whisper local + fallback OpenAI com timestamps
    - **Edição de Áudio**: Corte preciso de trechos com FFmpeg
    
    ### 🔒 Proteções e Limites
    
    - Rate limiting: 10 requisições/minuto por IP
    - Limpeza automática de arquivos temporários
    - Validação rigorosa de entradas
    - Tratamento robusto de erros
    
    ### ⚖️ Uso Responsável
    
    **Esta API é destinada APENAS para:**
    - Fins educacionais
    - Preview de conteúdo
    - Uso justo (Fair Use)
    
    **Importante**: Respeite os direitos autorais e Termos de Serviço do YouTube.
    
    ### 🚀 Exemplo de Fluxo de Uso
    
    1. **Buscar música**: `GET /search?query=Imagine Dragons Bones`
    2. **Baixar áudio**: `POST /download` com videoId
    3. **Transcrever**: `POST /transcribe` com arquivo de áudio
    4. **Cortar trecho**: `POST /cut` com timestamps desejados
    
    ### 🛠️ Tecnologias
    
    - FastAPI, ytmusicapi, yt-dlp, OpenAI Whisper, FFmpeg
    """,
    version="1.0.0",
    contact={
        "name": "ShortTune Team",
        "email": "support@shorttune.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting personalizado para rotas específicas
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Middleware para rate limiting global"""
    try:
        # Aplica rate limiting baseado nas configurações
        # 10 requests por minuto é aplicado automaticamente pelo slowapi
        response = await call_next(request)
        return response
    except RateLimitExceeded:
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": f"Limite de {settings.rate_limit_requests} requisições por {settings.rate_limit_window} segundos excedido",
                "retry_after": settings.rate_limit_window
            }
        )

# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de requisições"""
    start_time = asyncio.get_event_loop().time()
    
    # Log da requisição
    logger.info(f"REQUEST: {request.method} {request.url} - IP: {request.client.host}")
    
    response = await call_next(request)
    
    # Log da resposta
    process_time = asyncio.get_event_loop().time() - start_time
    logger.info(f"RESPONSE: {response.status_code} - {process_time:.3f}s")
    
    return response

# Exception handler global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas"""
    logger.error(f"Exceção não tratada: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "Erro interno do servidor",
            "details": str(exc) if settings.debug else "Contate o suporte"
        }
    )

# Incluir routers
app.include_router(health_router)
app.include_router(search_router)
app.include_router(download_router)
app.include_router(transcribe_router)
app.include_router(cut_router)

# Adicionar rate limiting às rotas
@app.get("/")
@limiter.limit(f"{settings.rate_limit_requests}/{settings.rate_limit_window} seconds")
async def read_root(request: Request):
    """Redireciona para informações da API"""
    return {
        "message": "ShortTune API - Criação de Vídeos Curtos Musicais",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "legal_notice": "Apenas para fins educacionais e preview. Respeite direitos autorais."
    }

# Eventos de startup e shutdown
@app.on_event("startup")
async def startup_event():
    """Eventos executados no startup da aplicação"""
    logger.info("ShortTune API iniciando...")
    logger.info(f"Modo debug: {settings.debug}")
    logger.info(f"Diretório temporário: {settings.temp_dir}")
    logger.info(f"Rate limiting: {settings.rate_limit_requests}/{settings.rate_limit_window}s")
    
    # Inicia tarefa de limpeza automática
    asyncio.create_task(start_cleanup_task())
    logger.info("Tarefa de limpeza automática iniciada")
    
    logger.info("ShortTune API iniciada com sucesso!")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos executados no shutdown da aplicação"""
    logger.info("ShortTune API finalizando...")
    
    # Aqui você pode adicionar lógica de limpeza
    # Por exemplo: fechar conexões, salvar estado, etc.
    
    logger.info("ShortTune API finalizada com sucesso!")

# Função para executar a aplicação
def run_app():
    """Executa a aplicação FastAPI"""
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    run_app()

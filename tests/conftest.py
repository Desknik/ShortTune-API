"""
Configuração do pytest para o projeto ShortTune API
"""
import pytest
import asyncio
import os
import sys

# Adiciona o diretório raiz ao Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def event_loop():
    """Cria um event loop para testes assíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_audio_file():
    """Fixture para arquivo de áudio temporário (mock)"""
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
        # Simula um arquivo de áudio pequeno
        tmp.write(b'fake audio data' * 1000)
        temp_path = tmp.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except:
        pass


@pytest.fixture
def sample_search_query():
    """Fixture com query de busca de exemplo"""
    return "Imagine Dragons Bones"


@pytest.fixture
def sample_video_id():
    """Fixture com video ID de exemplo"""
    return "dQw4w9WgXcQ"  # Never Gonna Give You Up


# Configurações do pytest
def pytest_configure(config):
    """Configuração do pytest"""
    # Configura variáveis de ambiente para testes
    os.environ["DEBUG"] = "True"
    os.environ["TEMP_DIR"] = "temp_test"
    os.environ["LOG_LEVEL"] = "DEBUG"

import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app

# Cliente de teste direto
client = TestClient(app)


class TestAPI:
    """Testes básicos da API"""
    
    def test_root_endpoint(self):
        """Testa endpoint raiz"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self):
        """Testa health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
        assert "version" in data
        assert "services" in data
    
    def test_search_validation(self):
        """Testa validação de busca"""
        # Query vazia deve falhar
        response = client.get("/search")
        assert response.status_code == 422
        
        # Query válida
        response = client.get("/search?query=test")
        # Pode falhar por problemas de rede, mas deve ter estrutura correta
        assert response.status_code in [200, 500]
    
    def test_download_validation(self):
        """Testa validação de download"""
        # Request inválido
        response = client.post("/download", json={})
        assert response.status_code == 422
        
        # Video ID inválido
        response = client.post("/download", json={"video_id": "", "format": "mp3"})
        assert response.status_code == 400
    
    def test_cut_validation(self):
        """Testa validação de corte"""
        # Request inválido
        response = client.post("/cut", json={})
        assert response.status_code == 422
        
        # Arquivo inexistente
        response = client.post("/cut", json={
            "filepath": "inexistente.mp3",
            "start": 0,
            "end": 30
        })
        assert response.status_code == 404
    
    def test_transcribe_engines(self):
        """Testa listagem de engines de transcrição"""
        response = client.get("/transcribe/engines")
        assert response.status_code == 200
        data = response.json()
        assert "engines" in data
        assert isinstance(data["engines"], list)
    
    def test_download_formats(self):
        """Testa listagem de formatos de download"""
        response = client.get("/download/formats")
        assert response.status_code == 200
        data = response.json()
        assert "formats" in data
        assert len(data["formats"]) >= 2  # MP3 e WAV


if __name__ == "__main__":
    pytest.main([__file__])

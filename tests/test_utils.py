import pytest
import tempfile
import os
from utils.file_manager import FileManager
from utils.audio_converter import AudioConverter


class TestFileManager:
    """Testes para gerenciador de arquivos"""
    
    def setup_method(self):
        self.file_manager = FileManager()
    
    def test_get_temp_filepath(self):
        """Testa geração de caminho temporário"""
        filepath = self.file_manager.get_temp_filepath()
        assert filepath.endswith('.mp3')
        assert 'audio_' in filepath
    
    def test_file_exists(self):
        """Testa verificação de existência de arquivo"""
        # Arquivo inexistente
        assert not self.file_manager.file_exists('inexistente.mp3')
        
        # Cria arquivo temporário para teste
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'test data')
            temp_path = tmp.name
        
        try:
            assert self.file_manager.file_exists(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_get_file_size(self):
        """Testa obtenção de tamanho de arquivo"""
        # Arquivo inexistente
        assert self.file_manager.get_file_size('inexistente.mp3') == 0
        
        # Arquivo com conteúdo
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            test_data = b'test data' * 100
            tmp.write(test_data)
            temp_path = tmp.name
        
        try:
            size = self.file_manager.get_file_size(temp_path)
            assert size == len(test_data)
        finally:
            os.unlink(temp_path)
    
    def test_validate_file_size(self):
        """Testa validação de tamanho de arquivo"""
        # Arquivo pequeno (válido)
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'small file')
            temp_path = tmp.name
        
        try:
            assert self.file_manager.validate_file_size(temp_path)
        finally:
            os.unlink(temp_path)


class TestAudioConverter:
    """Testes para conversor de áudio"""
    
    def test_validate_time_range(self):
        """Testa validação de intervalo de tempo"""
        converter = AudioConverter()
        
        # Válido
        valid, msg = converter.validate_time_range(10, 30, 60)
        assert valid
        assert msg == "Válido"
        
        # Início negativo
        valid, msg = converter.validate_time_range(-5, 30, 60)
        assert not valid
        assert "negativo" in msg
        
        # Fim menor que início
        valid, msg = converter.validate_time_range(30, 10, 60)
        assert not valid
        assert "maior que tempo de início" in msg
        
        # Início maior que duração
        valid, msg = converter.validate_time_range(70, 80, 60)
        assert not valid
        assert "maior que a duração" in msg


if __name__ == "__main__":
    pytest.main([__file__])

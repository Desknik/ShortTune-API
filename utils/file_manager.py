import os
import aiofiles
import asyncio
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
from config.settings import settings
from config.logging import logger


class FileManager:
    """Gerenciador de arquivos temporários"""
    
    def __init__(self):
        self.temp_dir = Path(settings.temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
    
    def get_temp_filepath(self, prefix: str = "audio", suffix: str = ".mp3") -> str:
        """Gera um caminho único para arquivo temporário"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{prefix}_{timestamp}{suffix}"
        return str(self.temp_dir / filename)
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Salva arquivo enviado pelo usuário"""
        try:
            filepath = self.get_temp_filepath(prefix="upload", suffix=f"_{filename}")
            
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(file_content)
            
            logger.info(f"Arquivo salvo: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo: {e}")
            raise
    
    def file_exists(self, filepath: str) -> bool:
        """Verifica se arquivo existe"""
        return Path(filepath).exists()
    
    def get_file_size(self, filepath: str) -> int:
        """Retorna tamanho do arquivo em bytes"""
        try:
            return Path(filepath).stat().st_size
        except:
            return 0
    
    def delete_file(self, filepath: str) -> bool:
        """Remove arquivo do sistema"""
        try:
            if self.file_exists(filepath):
                Path(filepath).unlink()
                logger.info(f"Arquivo removido: {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao remover arquivo {filepath}: {e}")
            return False
    
    async def cleanup_old_files(self, max_age_hours: Optional[int] = None) -> int:
        """Remove arquivos temporários antigos"""
        if max_age_hours is None:
            max_age_hours = settings.cleanup_interval_hours
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        removed_count = 0
        
        try:
            for file_path in self.temp_dir.iterdir():
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        self.delete_file(str(file_path))
                        removed_count += 1
            
            logger.info(f"Limpeza automática: {removed_count} arquivos removidos")
            return removed_count
            
        except Exception as e:
            logger.error(f"Erro na limpeza automática: {e}")
            return 0
    
    def validate_file_size(self, filepath: str) -> bool:
        """Valida se arquivo não excede tamanho máximo"""
        max_size_bytes = settings.max_file_size_mb * 1024 * 1024
        file_size = self.get_file_size(filepath)
        return file_size <= max_size_bytes


# Global file manager instance
file_manager = FileManager()


async def start_cleanup_task():
    """Inicia tarefa de limpeza automática"""
    while True:
        try:
            await file_manager.cleanup_old_files()
            # Aguarda 1 hora
            await asyncio.sleep(settings.cleanup_interval_hours * 3600)
        except Exception as e:
            logger.error(f"Erro na tarefa de limpeza: {e}")
            await asyncio.sleep(3600)  # Retry em 1 hora

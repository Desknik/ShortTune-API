import os
from typing import Dict, Any, Optional
from utils.audio_converter import audio_converter
from utils.file_manager import file_manager
from config.logging import logger


class AudioEditService:
    """Serviço para edição de áudio"""
    
    async def cut_audio(self, filepath: str, start: float, end: float) -> Dict[str, Any]:
        """Corta trecho do áudio entre dois tempos"""
        try:
            logger.info(f"Cortando áudio: {filepath} ({start}s - {end}s)")
            
            # Valida se arquivo existe
            if not file_manager.file_exists(filepath):
                raise Exception("Arquivo de áudio não encontrado")
            
            # Obtém informações do áudio original
            audio_info = await audio_converter.get_audio_info(filepath)
            if not audio_info:
                raise Exception("Não foi possível obter informações do áudio")
            
            original_duration = audio_info['duration']            # Valida intervalo de tempo
            is_valid, error_msg = await audio_converter.validate_time_range(filepath, start, end)
            if not is_valid:
                raise Exception(error_msg)
            
            # Gera filepath para o arquivo cortado
            file_extension = os.path.splitext(filepath)[1]
            cut_filepath = file_manager.get_temp_filepath(
                prefix="cut", 
                suffix=file_extension
            )
            
            # Executa corte
            success = await audio_converter.cut_audio(filepath, cut_filepath, start, end)
            if not success:
                raise Exception("Falha ao cortar áudio")
            
            # Calcula duração do corte
            cut_duration = end - start
            
            # Obtém tamanho do arquivo cortado
            file_size = file_manager.get_file_size(cut_filepath)
            
            result = {
                'filepath': cut_filepath,
                'original_duration': original_duration,
                'cut_duration': cut_duration,
                'file_size': file_size,
                'start_time': start,
                'end_time': end
            }
            
            logger.info(f"Áudio cortado com sucesso: {cut_filepath}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao cortar áudio: {e}")
            raise Exception(f"Falha no corte: {str(e)}")
    
    async def normalize_audio(self, filepath: str) -> Optional[str]:
        """Normaliza volume do áudio"""
        try:
            logger.info(f"Normalizando áudio: {filepath}")
            
            if not file_manager.file_exists(filepath):
                raise Exception("Arquivo de áudio não encontrado")
            
            normalized_path = await audio_converter.normalize_audio(filepath)
            if not normalized_path:
                raise Exception("Falha na normalização")
            
            logger.info(f"Áudio normalizado: {normalized_path}")
            return normalized_path
            
        except Exception as e:
            logger.error(f"Erro na normalização: {e}")
            raise Exception(f"Falha na normalização: {str(e)}")
    
    async def get_audio_metadata(self, filepath: str) -> Dict[str, Any]:
        """Obtém metadados do arquivo de áudio"""
        try:
            if not file_manager.file_exists(filepath):
                raise Exception("Arquivo não encontrado")
            
            audio_info = await audio_converter.get_audio_info(filepath)
            if not audio_info:
                raise Exception("Não foi possível obter informações do áudio")
            
            file_size = file_manager.get_file_size(filepath)
            
            return {
                'duration': audio_info['duration'],
                'codec': audio_info.get('codec'),
                'sample_rate': audio_info.get('sample_rate'),
                'channels': audio_info.get('channels'),
                'bitrate': audio_info.get('bitrate'),
                'file_size': file_size
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter metadados: {e}")
            raise Exception(f"Falha ao obter metadados: {str(e)}")


# Global service instance
audio_edit_service = AudioEditService()

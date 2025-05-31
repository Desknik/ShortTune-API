import yt_dlp
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from models.schemas import AudioFormat
from utils.file_manager import file_manager
from utils.audio_converter import audio_converter
from config.logging import logger


class DownloadService:
    """Serviço para download de áudio do YouTube"""
    
    def __init__(self):
        self.download_options = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': f'{file_manager.temp_dir}/%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,  # Ajuda com problemas de SSL
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            # Opções adicionais para contornar problemas de rede
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,            # Headers para contornar detecção de bot
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }
    
    async def download_audio(self, video_id: str, format: AudioFormat = AudioFormat.MP3) -> Optional[Dict[str, Any]]:
        """Baixa áudio de um vídeo do YouTube"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"Iniciando download de áudio: {video_id}")
            
            # Configurações específicas do formato
            options = self.download_options.copy()
            if format == AudioFormat.WAV:
                options['audioformat'] = 'wav'
                options['audioquality'] = '0'  # Melhor qualidade para WAV
            
            # Adiciona timeout mais baixo para evitar travamentos
            options['socket_timeout'] = 10
            
            # Gera nome único para o arquivo
            temp_filename = file_manager.get_temp_filepath(
                prefix=f"download_{video_id}", 
                suffix=f".{format.value}"
            )
            options['outtmpl'] = temp_filename.replace(f".{format.value}", ".%(ext)s")
            
            logger.info(f"Configurações do download: {options['outtmpl']}")
            
            # Executa download em thread separada
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, self._download_with_ytdlp, url, options)
            
            if not info:
                raise Exception("Falha no download - informações não obtidas")
            
            # Encontra o arquivo baixado
            downloaded_file = self._find_downloaded_file(temp_filename, info)
            if not downloaded_file or not file_manager.file_exists(downloaded_file):
                raise Exception("Arquivo baixado não encontrado")
            
            # Converte para formato desejado se necessário
            final_file = await self._convert_if_needed(downloaded_file, format)            # Obtém informações do áudio
            audio_info = await audio_converter.get_audio_info(final_file)
            
            # Prepara resposta
            result = {
                'filepath': final_file,
                'title': info.get('title', 'Unknown'),
                'artist': info.get('uploader', 'Unknown Artist'),
                'duration': audio_info.get('duration') if audio_info else None,
                'format': format,
                'file_size': file_manager.get_file_size(final_file)
            }
              # Remove arquivo original se foi convertido
            if final_file != downloaded_file:
                file_manager.delete_file(downloaded_file)
            
            logger.info(f"Download concluído: {final_file}")
            return result
            
        except Exception as e:
            logger.error(f"Erro no download de áudio {video_id}: {e}")
            raise Exception(f"Falha no download: {str(e)}")
    
    def _download_with_ytdlp(self, url: str, options: dict) -> Optional[dict]:
        """Executa download usando yt-dlp com fallbacks para problemas comuns"""
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                return info
                
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e).lower()
            
            # Problemas específicos conhecidos e suas soluções
            if 'certificate' in error_msg or 'ssl' in error_msg:
                logger.warning("Problema de SSL detectado, tentando com configurações alternativas...")
                # Tenta novamente com SSL desabilitado
                fallback_options = options.copy()
                fallback_options.update({
                    'nocheckcertificate': True,
                    'no_check_certificate': True,
                })
                try:
                    with yt_dlp.YoutubeDL(fallback_options) as ydl:
                        info = ydl.extract_info(url, download=True)
                        return info
                except Exception as fallback_error:
                    logger.error(f"Fallback SSL também falhou: {fallback_error}")
                    
            elif 'sign in' in error_msg or 'login' in error_msg:
                raise Exception("Vídeo requer autenticação - não disponível para download automático")
                
            elif 'private' in error_msg or 'unavailable' in error_msg:
                raise Exception("Vídeo privado ou indisponível")
                
            elif 'age' in error_msg:
                raise Exception("Vídeo com restrição de idade")
                
            # Re-lança o erro original se não conseguiu tratar
            logger.error(f"Erro no yt-dlp: {e}")
            raise Exception(f"Falha no download: {str(e)}")
            
        except Exception as e:
            logger.error(f"Erro inesperado no yt-dlp: {e}")
            return None
    
    def _find_downloaded_file(self, base_path: str, info: dict) -> Optional[str]:
        """Encontra o arquivo baixado baseado nas informações"""
        try:
            # Remove extensão do base_path
            base_without_ext = str(Path(base_path).with_suffix(''))
            
            # Extensões possíveis
            possible_extensions = ['.mp3', '.m4a', '.webm', '.opus', '.wav']
            
            for ext in possible_extensions:
                candidate = base_without_ext + ext
                if file_manager.file_exists(candidate):
                    return candidate
            
            # Fallback: procura por arquivos com título similar
            if 'title' in info:
                title_clean = "".join(c for c in info['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
                for ext in possible_extensions:
                    pattern_path = f"{file_manager.temp_dir}/{title_clean}{ext}"
                    if file_manager.file_exists(pattern_path):
                        return pattern_path
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao encontrar arquivo baixado: {e}")
            return None
    
    async def _convert_if_needed(self, input_file: str, target_format: AudioFormat) -> str:
        """Converte arquivo para formato desejado se necessário"""
        try:
            input_ext = Path(input_file).suffix[1:].lower()  # Remove o ponto
            
            # Se já está no formato correto, retorna o arquivo original
            if input_ext == target_format.value:
                return input_file
              # Converte para o formato desejado
            output_file = file_manager.get_temp_filepath(
                prefix="converted", 
                suffix=f".{target_format.value}"
            )
            
            success = await audio_converter.convert_audio(
                input_file, output_file, target_format.value
            )
            
            if success and file_manager.file_exists(output_file):
                return output_file
            else:
                # Se conversão falhou, retorna arquivo original
                logger.warning(f"Conversão falhou, usando arquivo original: {input_file}")
                return input_file
                
        except Exception as e:
            logger.error(f"Erro na conversão: {e}")
            return input_file


# Global service instance
download_service = DownloadService()

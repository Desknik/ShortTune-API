"""Audio converter using FFmpeg subprocess calls"""
import asyncio
import subprocess
import json
import os
from pathlib import Path
from typing import Optional, Tuple


# Configure FFmpeg paths
FFMPEG_PATH = r"c:\Projects\ShortTune API\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
FFPROBE_PATH = r"c:\Projects\ShortTune API\ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe"


class AudioConverter:
    """Conversor e manipulador de áudio usando FFmpeg"""
    
    @staticmethod
    async def get_audio_info(filepath: str) -> Optional[dict]:
        """Obtém informações do arquivo de áudio"""
        try:
            cmd = [
                FFPROBE_PATH,
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                filepath
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # Extract audio stream info
                audio_streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'audio']
                if not audio_streams:
                    return None
                
                audio_stream = audio_streams[0]
                format_info = data.get('format', {})
                
                return {
                    'duration': float(format_info.get('duration', 0)),
                    'bitrate': int(format_info.get('bit_rate', 0)),
                    'format': format_info.get('format_name', ''),
                    'codec': audio_stream.get('codec_name', ''),
                    'sample_rate': int(audio_stream.get('sample_rate', 0)),
                    'channels': int(audio_stream.get('channels', 0)),
                    'size': int(format_info.get('size', 0))
                }
            else:
                print(f"FFprobe error: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Error getting audio info: {e}")
            return None
    
    @staticmethod
    async def cut_audio(input_file: str, output_file: str, start_time: float, end_time: float) -> bool:
        """Corta um segmento de áudio"""
        try:
            duration = end_time - start_time
            
            cmd = [
                FFMPEG_PATH,
                '-i', input_file,
                '-ss', str(start_time),
                '-t', str(duration),
                '-c', 'copy',
                '-avoid_negative_ts', 'make_zero',
                '-y',  # Overwrite output file
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return os.path.exists(output_file) and os.path.getsize(output_file) > 0
            else:
                print(f"FFmpeg cut error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error cutting audio: {e}")
            return False
    
    @staticmethod
    async def convert_audio(input_file: str, output_file: str, target_format: str) -> bool:
        """Converte áudio para outro formato"""
        try:
            cmd = [
                FFMPEG_PATH,
                '-i', input_file,
                '-acodec', 'libmp3lame' if target_format == 'mp3' else 'aac',
                '-y',  # Overwrite output file
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                return os.path.exists(output_file) and os.path.getsize(output_file) > 0
            else:
                print(f"FFmpeg convert error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error converting audio: {e}")
            return False
    
    @staticmethod
    async def normalize_audio(input_file: str, output_file: str) -> bool:
        """Normaliza o volume do áudio"""
        try:
            cmd = [
                FFMPEG_PATH,
                '-i', input_file,
                '-filter:a', 'loudnorm',
                '-y',  # Overwrite output file
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                return os.path.exists(output_file) and os.path.getsize(output_file) > 0
            else:
                print(f"FFmpeg normalize error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error normalizing audio: {e}")
            return False
    
    @staticmethod
    async def validate_time_range(filepath: str, start_time: float, end_time: float) -> Tuple[bool, str]:
        """Valida se o range de tempo é válido para o arquivo"""
        if start_time < 0:
            return False, "Tempo de início não pode ser negativo"
        
        if start_time >= end_time:
            return False, "Tempo de início deve ser menor que o tempo de fim"
        
        info = await AudioConverter.get_audio_info(filepath)
        if not info:
            return False, "Não foi possível obter informações do arquivo"
        
        duration = info.get('duration', 0)
        if start_time >= duration:
            return False, "Tempo de início não pode ser maior que a duração do áudio"
        
        if end_time > duration:
            return False, "Tempo de fim não pode ser maior que a duração do áudio"
        
        return True, "Válido"


# Global converter instance
audio_converter = AudioConverter()

#!/usr/bin/env python3
"""
Script para baixar um arquivo de áudio válido para testes
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.download_service import DownloadService
from models.schemas import AudioFormat

async def download_test_audio():
    """Baixa um arquivo de áudio para testes"""
    
    print("🎵 Baixando arquivo de áudio para testes...")
    
    try:
        download_service = DownloadService()
        
        # Rick Astley - Never Gonna Give You Up (áudio curto e conhecido)
        video_id = "dQw4w9WgXcQ"
        
        result = await download_service.download_audio(video_id, AudioFormat.MP3)
        
        if result:
            print(f"✅ Arquivo baixado com sucesso!")
            print(f"📁 Caminho: {result['filepath']}")
            print(f"📊 Tamanho: {result['file_size']} bytes")
            print(f"⏱️ Duração: {result['duration']:.2f} segundos")
            
            return result['filepath']
        else:
            print("❌ Falha no download")
            return None
            
    except Exception as e:
        print(f"❌ Erro durante o download: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(download_test_audio())

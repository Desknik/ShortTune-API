#!/usr/bin/env python3
"""
Teste direto do serviço de transcrição sem passar pela API.
"""

import sys
import os
import asyncio
from pathlib import Path

# Adicionar o diretório raiz ao PATH
sys.path.insert(0, os.path.abspath('.'))

from services.transcription_service import TranscriptionService
from models.schemas import TranscriptionEngine

async def test_direct_transcription():
    """Testa o serviço de transcrição diretamente."""
    
    print("🔧 Testando serviço de transcrição diretamente...")
    
    # Inicializar o serviço
    service = TranscriptionService()
    
    # Verificar se há arquivos de áudio
    temp_dir = Path("temp")
    audio_files = list(temp_dir.glob("*.mp3"))
    
    if not audio_files:
        print("❌ Nenhum arquivo de áudio encontrado em temp/")
        return
    
    # Usar o menor arquivo
    audio_file = min(audio_files, key=lambda f: f.stat().st_size)
    file_size = audio_file.stat().st_size / (1024 * 1024)  # MB
    
    print(f"📝 Usando arquivo: {audio_file} ({file_size:.2f} MB)")
    
    try:
        print("🚀 Iniciando transcrição...")
        print("⏳ Primeira execução pode demorar para baixar modelo Whisper...")
        
        import time
        start_time = time.time()
        
        # Executar transcrição
        result = await service.transcribe_audio(
            str(audio_file), 
            TranscriptionEngine.LOCAL
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Tempo total: {duration:.2f} segundos")
        print("✅ Transcrição bem-sucedida!")
        print(f"📄 Texto: {result.get('text', 'N/A')}")
        print(f"🎯 Segments: {len(result.get('segments', []))}")
          if result.get('segments'):
            print("📍 Primeiros segments:")
            for i, segment in enumerate(result['segments'][:3]):
                if hasattr(segment, 'start'):
                    # Se for objeto TranscriptionSegment
                    print(f"  {i+1}. [{segment.start:.1f}s-{segment.end:.1f}s]: {segment.text}")
                else:
                    # Se for dict
                    print(f"  {i+1}. [{segment['start']:.1f}s-{segment['end']:.1f}s]: {segment['text']}")
        
        print(f"🔧 Provider: {result.get('provider', 'N/A')}")
        print(f"📊 Estatísticas: {result.get('stats', {})}")
        
    except Exception as e:
        print(f"❌ Erro na transcrição: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_transcription())

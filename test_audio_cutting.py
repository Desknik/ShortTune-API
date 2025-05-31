#!/usr/bin/env python3
"""
Script para testar a funcionalidade de corte de áudio
"""

import asyncio
import os
from services.audio_edit_service import audio_edit_service
from utils.audio_converter import audio_converter
from config.logging import logger

async def test_audio_cutting():
    """Testa a funcionalidade de corte de áudio"""
      # Arquivo de áudio para teste
    audio_file = r"c:\Projects\ShortTune API\temp\test_audio.mp3"
    
    print("🎵 Testando funcionalidade de corte de áudio...")
    print(f"📁 Arquivo: {audio_file}")
    
    # Verifica se o arquivo existe
    if not os.path.exists(audio_file):
        print("❌ Arquivo de áudio não encontrado!")
        return
    
    try:
        # 1. Obtém informações do áudio
        print("\n1️⃣ Obtendo informações do áudio...")
        audio_info = await audio_converter.get_audio_info(audio_file)
        
        if audio_info:
            print(f"   ✅ Duração: {audio_info['duration']:.2f} segundos")
            print(f"   ✅ Codec: {audio_info.get('codec', 'N/A')}")
            print(f"   ✅ Sample Rate: {audio_info.get('sample_rate', 'N/A')}")
            print(f"   ✅ Canais: {audio_info.get('channels', 'N/A')}")
        else:
            print("   ❌ Não foi possível obter informações do áudio")
            return
        
        # 2. Testa corte de áudio (primeiros 10 segundos)
        print("\n2️⃣ Testando corte de áudio (0-10 segundos)...")
        
        start_time = 0.0
        end_time = min(10.0, audio_info['duration'])
        
        result = await audio_edit_service.cut_audio(audio_file, start_time, end_time)
        
        if result:
            print(f"   ✅ Arquivo cortado: {result['filepath']}")
            print(f"   ✅ Duração original: {result['original_duration']:.2f}s")
            print(f"   ✅ Duração do corte: {result['cut_duration']:.2f}s")
            print(f"   ✅ Tamanho do arquivo: {result['file_size']} bytes")
            
            # Verifica se o arquivo cortado foi criado
            if os.path.exists(result['filepath']):
                print(f"   ✅ Arquivo cortado criado com sucesso!")
                
                # Testa informações do arquivo cortado
                cut_info = await audio_converter.get_audio_info(result['filepath'])
                if cut_info:
                    print(f"   ✅ Duração do arquivo cortado: {cut_info['duration']:.2f}s")
                
            else:
                print(f"   ❌ Arquivo cortado não foi encontrado!")
        else:
            print("   ❌ Falha no corte do áudio")
        
        # 3. Testa metadados
        print("\n3️⃣ Testando obtenção de metadados...")
        metadata = await audio_edit_service.get_audio_metadata(audio_file)
        
        if metadata:
            print(f"   ✅ Metadados obtidos:")
            for key, value in metadata.items():
                print(f"      {key}: {value}")
        else:
            print("   ❌ Falha ao obter metadados")
        
        print("\n🎉 Teste de corte de áudio concluído!")
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        logger.error(f"Erro no teste de corte de áudio: {e}")

if __name__ == "__main__":
    asyncio.run(test_audio_cutting())

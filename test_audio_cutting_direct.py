#!/usr/bin/env python3
"""
Script para testar a funcionalidade de corte de áudio (versão direta)
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import directly from modules
from utils.audio_converter import AudioConverter
from utils.file_manager import FileManager

async def test_audio_cutting_direct():
    """Testa a funcionalidade de corte de áudio diretamente"""
    
    # Arquivo de áudio para teste
    audio_file = r"c:\Projects\ShortTune API\temp\test_audio.mp3"
    
    print("🎵 Testando funcionalidade de corte de áudio (importação direta)...")
    print(f"📁 Arquivo: {audio_file}")
    
    # Verifica se o arquivo existe
    if not os.path.exists(audio_file):
        print("❌ Arquivo de áudio não encontrado!")
        return
    
    try:
        # Cria instâncias
        audio_converter = AudioConverter()
        file_manager = FileManager()
        
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
        
        # 2. Testa corte de áudio (primeiros 5 segundos)
        print("\n2️⃣ Testando corte de áudio (0-5 segundos)...")
        
        start_time = 0.0
        end_time = min(5.0, audio_info['duration'])
        
        cut_filepath = await audio_converter.cut_audio(audio_file, start_time, end_time)
        
        if cut_filepath:
            print(f"   ✅ Arquivo cortado: {cut_filepath}")
            
            # Verifica se o arquivo cortado foi criado
            if os.path.exists(cut_filepath):
                print(f"   ✅ Arquivo cortado criado com sucesso!")
                
                # Obtém tamanho do arquivo
                file_size = os.path.getsize(cut_filepath)
                print(f"   ✅ Tamanho: {file_size} bytes")
                
                # Testa informações do arquivo cortado
                cut_info = await audio_converter.get_audio_info(cut_filepath)
                if cut_info:
                    print(f"   ✅ Duração do arquivo cortado: {cut_info['duration']:.2f}s")
                    print(f"   ✅ Codec do arquivo cortado: {cut_info.get('codec', 'N/A')}")
                
            else:
                print(f"   ❌ Arquivo cortado não foi encontrado!")
        else:
            print("   ❌ Falha no corte do áudio")
        
        # 3. Testa validação de tempo
        print("\n3️⃣ Testando validação de intervalos de tempo...")
        
        # Teste válido
        is_valid, msg = audio_converter.validate_time_range(0, 5, audio_info['duration'])
        print(f"   ✅ Intervalo 0-5s: {is_valid} ({msg})")
        
        # Teste inválido
        is_valid, msg = audio_converter.validate_time_range(10, 5, audio_info['duration'])
        print(f"   ❌ Intervalo 10-5s: {is_valid} ({msg})")
        
        print("\n🎉 Teste de corte de áudio concluído com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_audio_cutting_direct())

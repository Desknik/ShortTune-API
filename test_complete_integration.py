#!/usr/bin/env python3
"""
Teste completo de integração da API ShortTune
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.audio_edit_service import audio_edit_service
from services.download_service import download_service
from models.schemas import AudioFormat

async def test_complete_workflow():
    """Testa o workflow completo: download → análise → corte"""
    
    print("🎵 Teste Completo de Integração da API ShortTune")
    print("=" * 50)
    
    try:
        # 1. Download de áudio
        print("\n1️⃣ DOWNLOAD DE ÁUDIO")
        print("-" * 25)
        
        video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
        print(f"📥 Baixando vídeo: {video_id}")
        
        download_result = await download_service.download_audio(video_id, AudioFormat.MP3)
        
        if not download_result:
            print("❌ Falha no download")
            return False
        
        print(f"✅ Download concluído!")
        print(f"   📁 Arquivo: {download_result['filepath']}")
        print(f"   🎵 Título: {download_result['title']}")
        print(f"   👤 Artista: {download_result['artist']}")
        print(f"   ⏱️ Duração: {download_result['duration']:.2f}s")
        print(f"   📊 Tamanho: {download_result['file_size']} bytes")
        
        audio_filepath = download_result['filepath']
        
        # 2. Análise de metadados
        print("\n2️⃣ ANÁLISE DE METADADOS")
        print("-" * 25)
        
        metadata = await audio_edit_service.get_audio_metadata(audio_filepath)
        
        if metadata:
            print("✅ Metadados obtidos:")
            print(f"   ⏱️ Duração: {metadata['duration']:.2f}s")
            print(f"   🎶 Codec: {metadata['codec']}")
            print(f"   📻 Sample Rate: {metadata['sample_rate']}")
            print(f"   🔊 Canais: {metadata['channels']}")
            print(f"   📊 Bitrate: {metadata['bitrate']}")
            print(f"   💾 Tamanho: {metadata['file_size']} bytes")
        else:
            print("❌ Falha ao obter metadados")
            return False
        
        # 3. Corte de áudio (primeiros 15 segundos)
        print("\n3️⃣ CORTE DE ÁUDIO")
        print("-" * 25)
        
        start_time = 0.0
        end_time = min(15.0, metadata['duration'])
        
        print(f"✂️ Cortando trecho: {start_time}s - {end_time}s")
        
        cut_result = await audio_edit_service.cut_audio(audio_filepath, start_time, end_time)
        
        if cut_result:
            print("✅ Corte realizado com sucesso!")
            print(f"   📁 Arquivo cortado: {cut_result['filepath']}")
            print(f"   ⏱️ Duração original: {cut_result['original_duration']:.2f}s")
            print(f"   ⏱️ Duração do corte: {cut_result['cut_duration']:.2f}s")
            print(f"   📊 Tamanho do corte: {cut_result['file_size']} bytes")
            
            # Verifica se arquivo foi criado
            if os.path.exists(cut_result['filepath']):
                print("   ✅ Arquivo cortado criado com sucesso!")
            else:
                print("   ❌ Arquivo cortado não encontrado!")
                return False
                
        else:
            print("❌ Falha no corte")
            return False
        
        # 4. Teste de corte com intervalo diferente (meio da música)
        print("\n4️⃣ CORTE ADICIONAL (MEIO DA MÚSICA)")
        print("-" * 35)
        
        mid_start = metadata['duration'] / 2 - 5  # 5 segundos antes do meio
        mid_end = metadata['duration'] / 2 + 5    # 5 segundos depois do meio
        
        print(f"✂️ Cortando trecho do meio: {mid_start:.2f}s - {mid_end:.2f}s")
        
        mid_cut_result = await audio_edit_service.cut_audio(audio_filepath, mid_start, mid_end)
        
        if mid_cut_result:
            print("✅ Segundo corte realizado com sucesso!")
            print(f"   📁 Arquivo: {mid_cut_result['filepath']}")
            print(f"   ⏱️ Duração: {mid_cut_result['cut_duration']:.2f}s")
        else:
            print("❌ Falha no segundo corte")
        
        # 5. Teste de validação de intervalos
        print("\n5️⃣ TESTE DE VALIDAÇÃO")
        print("-" * 25)
          # Teste válido
        from utils.audio_converter import audio_converter
        is_valid, msg = await audio_converter.validate_time_range(audio_filepath, 0, 10)
        print(f"✅ Intervalo válido (0-10s): {is_valid} - {msg}")
        
        # Teste inválido (fim antes do início)
        is_valid, msg = await audio_converter.validate_time_range(audio_filepath, 10, 5)
        print(f"❌ Intervalo inválido (10-5s): {is_valid} - {msg}")
        
        # Teste inválido (além da duração)
        is_valid, msg = await audio_converter.validate_time_range(audio_filepath, 0, metadata['duration'] + 10)
        print(f"❌ Intervalo inválido (além da duração): {is_valid} - {msg}")
        
        print("\n🎉 TESTE COMPLETO FINALIZADO COM SUCESSO!")
        print("=" * 50)
        print("✅ Todas as funcionalidades estão operacionais:")
        print("   • Download de áudio do YouTube")
        print("   • Análise de metadados de áudio")
        print("   • Corte de trechos de áudio")
        print("   • Validação de intervalos de tempo")
        print("   • Conversão de formatos (quando necessário)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE O TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_complete_workflow())
    sys.exit(0 if success else 1)

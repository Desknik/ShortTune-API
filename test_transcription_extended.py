#!/usr/bin/env python3
"""
Teste de transcrição com timeout estendido para permitir download do modelo Whisper.
"""

import requests
import os
import time

def test_transcription_extended():
    """Testa transcrição com timeout estendido."""
    
    base_url = "http://127.0.0.1:8000"
    
    # Verificar se o servidor está funcionando
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Servidor está funcionando: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Servidor não está respondendo: {e}")
        return
    
    # Usar um arquivo de áudio pequeno para teste
    audio_file = "temp/cut_20250531_020348_751801.mp3"  # Este é menor
    
    if not os.path.exists(audio_file):
        print(f"❌ Arquivo de áudio não encontrado: {audio_file}")
        # Listar arquivos disponíveis
        try:
            files = os.listdir("temp/")
            mp3_files = [f for f in files if f.endswith('.mp3')]
            if mp3_files:
                audio_file = f"temp/{mp3_files[0]}"
                print(f"📁 Usando arquivo: {audio_file}")
            else:
                print("❌ Nenhum arquivo MP3 encontrado para testar")
                return
        except:
            print("❌ Diretório temp não encontrado")
            return
    
    # Verificar tamanho do arquivo
    file_size = os.path.getsize(audio_file) / (1024 * 1024)  # MB
    print(f"📝 Testando transcrição com arquivo: {audio_file} ({file_size:.2f} MB)")
    
    # Preparar arquivo para upload
    with open(audio_file, 'rb') as f:
        files = {'file': (os.path.basename(audio_file), f, 'audio/mpeg')}
        data = {
            'provider': 'local',  # Provider local
            'language': 'pt'
        }
        
        print("🚀 Enviando requisição de transcrição...")
        print("⏳ Primeira execução pode demorar para baixar modelo Whisper (até 5 minutos)...")
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/transcribe",
                files=files,
                data=data,
                timeout=600  # 10 minutos para primeira execução
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️  Tempo de resposta: {duration:.2f} segundos")
            print(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Transcrição bem-sucedida!")
                print(f"📄 Texto: {result.get('text', 'N/A')}")
                print(f"🎯 Segments: {len(result.get('segments', []))}")
                if result.get('segments'):
                    print("📍 Primeiros segments:")
                    for i, segment in enumerate(result['segments'][:3]):
                        print(f"  {i+1}. [{segment['start']:.1f}s-{segment['end']:.1f}s]: {segment['text']}")
                        
                print(f"🔧 Provider usado: {result.get('provider', 'N/A')}")
                print(f"📊 Estatísticas: {result.get('stats', {})}")
            else:
                print(f"❌ Erro na transcrição: {response.status_code}")
                print(f"📝 Resposta: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout na requisição (mais de 10 minutos)")
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_transcription_extended()

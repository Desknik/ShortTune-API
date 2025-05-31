#!/usr/bin/env python3
"""
Teste específico para o endpoint de transcrição.
"""

import requests
import os
import time

def test_transcription():
    """Testa apenas o endpoint de transcrição."""
    
    base_url = "http://127.0.0.1:8000"
    
    # Verificar se o servidor está funcionando
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Servidor está funcionando: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Servidor não está respondendo: {e}")
        return
      # Usar um arquivo de áudio existente
    audio_file = "temp/converted_20250531_020402_496054.mp3"
    
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
    
    print(f"📝 Testando transcrição com arquivo: {audio_file}")
    
    # Preparar arquivo para upload
    with open(audio_file, 'rb') as f:
        files = {'file': (os.path.basename(audio_file), f, 'audio/mpeg')}
        data = {
            'provider': 'local',  # Começar com o provider local
            'language': 'pt'
        }
        
        print("🚀 Enviando requisição de transcrição...")
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/transcribe",
                files=files,
                data=data,
                timeout=120  # 2 minutos de timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️  Tempo de resposta: {duration:.2f} segundos")
            print(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Transcrição bem-sucedida!")
                print(f"📄 Texto: {result.get('text', 'N/A')[:100]}...")
                print(f"🎯 Segments: {len(result.get('segments', []))}")
                if result.get('segments'):
                    print(f"📍 Primeiro segment: {result['segments'][0]}")
            else:
                print(f"❌ Erro na transcrição: {response.status_code}")
                print(f"📝 Resposta: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout na requisição (mais de 2 minutos)")
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_transcription()

#!/usr/bin/env python3
"""
Teste final da API de transcrição com arquivo pequeno.
"""

import requests
import os

def test_api_transcription():
    """Teste final da API de transcrição."""
    
    base_url = "http://127.0.0.1:8000"
    audio_file = "temp/test_small.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ Arquivo não encontrado: {audio_file}")
        return
    
    file_size = os.path.getsize(audio_file) / 1024  # KB
    print(f"📝 Testando API com arquivo pequeno: {audio_file} ({file_size:.1f} KB)")
    
    with open(audio_file, 'rb') as f:
        files = {'file': (os.path.basename(audio_file), f, 'audio/mpeg')}
        data = {'provider': 'local', 'language': 'en'}
        
        print("🚀 Enviando para API...")
        
        try:
            response = requests.post(
                f"{base_url}/transcribe",
                files=files,
                data=data,
                timeout=120  # 2 minutos
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API funcionando!")
                print(f"📄 Texto: {result.get('text', 'N/A')}")
                print(f"🎯 Segments: {len(result.get('segments', []))}")
            else:
                print(f"❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_api_transcription()

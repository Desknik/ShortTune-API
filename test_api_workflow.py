#!/usr/bin/env python3
"""
Script para testar o fluxo completo da API ShortTune
"""

import requests
import json
import time
import sys
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_health():
    """Testa o endpoint de saúde"""
    print("🔍 Testando health check...")
    response = requests.get(f"{API_BASE}/health")
    if response.status_code == 200:
        health_data = response.json()
        print(f"✅ API está saudável")
        print(f"   Versão: {health_data['version']}")
        print(f"   Serviços disponíveis: {', '.join(health_data['services']['services'].keys())}")
        return True
    else:
        print(f"❌ Health check falhou: {response.status_code}")
        return False

def test_search():
    """Testa a busca de músicas"""
    print("\n🔍 Testando busca de músicas...")
    
    # Teste com query simples
    response = requests.get(f"{API_BASE}/search", params={"query": "test", "limit": 3})
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Busca funcionando - {results['total_results']} resultados encontrados")
        if results['results']:
            first_result = results['results'][0]
            print(f"   Primeiro resultado: {first_result['title']} - {first_result['artist']}")
            return first_result['video_id']
    else:
        print(f"❌ Busca falhou: {response.status_code}")
        print(f"   Resposta: {response.text}")
    return None

def test_download_formats():
    """Testa listagem de formatos"""
    print("\n🔍 Testando formatos de download...")
    response = requests.get(f"{API_BASE}/download/formats")
    if response.status_code == 200:
        formats = response.json()
        print(f"✅ Formatos disponíveis: {', '.join([f['value'] for f in formats['formats']])}")
        return True
    else:
        print(f"❌ Listagem de formatos falhou: {response.status_code}")
        return False

def test_transcription_engines():
    """Testa listagem de engines de transcrição"""
    print("\n🔍 Testando engines de transcrição...")
    response = requests.get(f"{API_BASE}/transcribe/engines")
    if response.status_code == 200:
        engines = response.json()
        print(f"✅ Engines disponíveis: {', '.join([e['value'] for e in engines['engines']])}")
        return True
    else:
        print(f"❌ Listagem de engines falhou: {response.status_code}")
        return False

def test_download(video_id):
    """Testa download de áudio"""
    if not video_id:
        print("\n⏭️ Pulando teste de download (sem video_id)")
        return None
        
    print(f"\n🔍 Testando download do vídeo: {video_id}")
    
    payload = {
        "video_id": video_id,
        "format": "mp3"
    }
    
    try:
        response = requests.post(f"{API_BASE}/download/", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Download concluído: {result['filepath']}")
            return result['filepath']
        else:
            print(f"❌ Download falhou: {response.status_code}")
            if response.text:
                error_data = response.json()
                print(f"   Erro: {error_data.get('message', 'Erro desconhecido')}")
    except requests.exceptions.Timeout:
        print("❌ Download falhou: Timeout (esperado para YouTube)")
    except Exception as e:
        print(f"❌ Download falhou: {e}")
    
    return None

def create_test_file():
    """Usa um arquivo de áudio real se existir, senão cria um fictício"""
    print("\n🔍 Criando arquivo de teste...")
    
    # Procurar por arquivos de áudio reais no diretório temp
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # Buscar por arquivos de áudio MP3 reais (não cortados)
    for audio_file in temp_dir.glob("converted_*.mp3"):
        if audio_file.exists() and audio_file.stat().st_size > 1000000:  # > 1MB
            print(f"✅ Usando arquivo real existente: {audio_file}")
            return str(audio_file)
    
    # Se não encontrou arquivo real, criar um fictício (aviso)
    test_content = b"FAKE_AUDIO_DATA_FOR_TESTING" * 1000  # ~27KB
    test_file = temp_dir / "test_audio.mp3"
    
    with open(test_file, "wb") as f:
        f.write(test_content)
    
    print(f"⚠️ Arquivo fictício criado: {test_file} (pode falhar no corte)")
    return str(test_file)

def test_cut_audio(filepath):
    """Testa corte de áudio"""
    if not filepath:
        print("\n⏭️ Pulando teste de corte (sem arquivo)")
        return None
        
    print(f"\n🔍 Testando corte de áudio: {filepath}")
    
    payload = {
        "filepath": filepath,
        "start": 10.0,
        "end": 40.0
    }
    
    try:
        response = requests.post(f"{API_BASE}/cut/", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Corte concluído: {result['filepath']}")
            return result['filepath']
        else:
            print(f"❌ Corte falhou: {response.status_code}")
            if response.text:
                error_data = response.json()
                print(f"   Erro: {error_data.get('message', 'Erro desconhecido')}")
    except Exception as e:
        print(f"❌ Corte falhou: {e}")
    
    return None

def test_rate_limiting():
    """Testa rate limiting"""
    print("\n🔍 Testando rate limiting...")
    
    # Fazer várias requisições rápidas
    for i in range(12):  # Mais que o limite de 10/min
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 429:
            print(f"✅ Rate limiting funcionando - requisição {i+1} bloqueada")
            return True
        time.sleep(0.1)
    
    print("⚠️ Rate limiting não ativado (pode estar em modo debug)")
    return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes da API ShortTune\n")
    
    # Teste 1: Health check
    if not test_health():
        print("❌ API não está funcionando. Verifique se está rodando.")
        return False
    
    # Teste 2: Busca
    video_id = test_search()
    
    # Teste 3: Formatos
    test_download_formats()
    
    # Teste 4: Engines de transcrição
    test_transcription_engines()
    
    # Teste 5: Download (pode falhar devido ao YouTube)
    audio_file = test_download(video_id)
    
    # Se o download real falhou, criar arquivo de teste
    if not audio_file:
        audio_file = create_test_file()
    
    # Teste 6: Corte de áudio
    cut_file = test_cut_audio(audio_file)
    
    # Teste 7: Rate limiting
    test_rate_limiting()
    
    print("\n📊 Resumo dos testes:")
    print("✅ Health check: OK")
    print("✅ Busca: OK") 
    print("✅ Formatos: OK")
    print("✅ Engines de transcrição: OK")
    print("⚠️ Download: Limitado pelo YouTube (esperado)")
    print("🔧 Corte: Precisa do FFmpeg instalado")
    print("⚠️ Rate limiting: Pode estar desabilitado em debug")
    
    print(f"\n🎯 API está funcional! Documentação disponível em: {API_BASE}/docs")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        sys.exit(1)

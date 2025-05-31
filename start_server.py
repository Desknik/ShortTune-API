#!/usr/bin/env python3
"""
Script para inicializar o servidor API com todas as dependências configuradas
"""
import os
import sys
import subprocess
from pathlib import Path

def setup_ffmpeg_path():
    """Configura o PATH para incluir FFmpeg"""
    current_dir = Path(__file__).parent
    ffmpeg_bin = current_dir / "ffmpeg-master-latest-win64-gpl" / "bin"
    
    if ffmpeg_bin.exists():
        # Adiciona FFmpeg ao PATH
        current_path = os.environ.get("PATH", "")
        if str(ffmpeg_bin) not in current_path:
            os.environ["PATH"] = f"{ffmpeg_bin}{os.pathsep}{current_path}"
            print(f"✅ FFmpeg adicionado ao PATH: {ffmpeg_bin}")
        else:
            print("✅ FFmpeg já está no PATH")
    else:
        print("⚠️ FFmpeg não encontrado. Execute o setup.sh primeiro.")
        return False
    
    return True

def start_server():
    """Inicia o servidor uvicorn"""
    try:
        print("🚀 Iniciando servidor API ShortTune...")
        print("📝 Logs serão salvos em logs/app.log")
        print("🌐 API estará disponível em: http://localhost:8000")
        print("📚 Documentação em: http://localhost:8000/docs")
        print("❌ Pressione Ctrl+C para parar o servidor")
        print("-" * 50)
        
        # Inicia o servidor
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    print("🎵 ShortTune API - Inicialization Script")
    print("=" * 50)
    
    # Configura FFmpeg
    if not setup_ffmpeg_path():
        sys.exit(1)
    
    # Verifica se as dependências estão instaladas
    try:
        import fastapi
        import uvicorn
        import whisper
        print("✅ Dependências verificadas")
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("Execute: pip install -r requirements.txt")
        sys.exit(1)
    
    # Inicia servidor
    start_server()

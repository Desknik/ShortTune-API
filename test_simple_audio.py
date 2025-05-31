#!/usr/bin/env python3
"""
Teste simples de funcionalidade de áudio sem dependências complexas
"""

import asyncio
import subprocess
import json
import os

async def test_simple_audio():
    """Teste simples usando FFmpeg diretamente"""
    
    # Caminhos
    ffprobe_path = r"c:\Projects\ShortTune API\ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe"
    ffmpeg_path = r"c:\Projects\ShortTune API\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
    audio_file = r"c:\Projects\ShortTune API\temp\download_dQw4w9WgXcQ_20250531_010311_704126.webm"
    
    print("🎵 Teste simples de funcionalidade de áudio...")
    print(f"📁 Arquivo: {audio_file}")
    
    # Verifica se arquivos existem
    if not os.path.exists(ffprobe_path):
        print(f"❌ FFprobe não encontrado: {ffprobe_path}")
        return
    
    if not os.path.exists(ffmpeg_path):
        print(f"❌ FFmpeg não encontrado: {ffmpeg_path}")
        return
        
    if not os.path.exists(audio_file):
        print(f"❌ Arquivo de áudio não encontrado: {audio_file}")
        return
    
    try:
        # 1. Teste FFprobe para obter informações
        print("\n1️⃣ Testando FFprobe...")
        cmd = [
            ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            audio_file
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if process.returncode == 0:
            print("   ✅ FFprobe executado com sucesso")
            
            # Parse do JSON
            data = json.loads(process.stdout)
            duration = float(data['format']['duration'])
            print(f"   ✅ Duração: {duration:.2f} segundos")
            
            # Encontra stream de áudio
            audio_stream = next(
                (s for s in data['streams'] if s['codec_type'] == 'audio'),
                None
            )
            
            if audio_stream:
                print(f"   ✅ Codec: {audio_stream.get('codec_name', 'N/A')}")
                print(f"   ✅ Canais: {audio_stream.get('channels', 'N/A')}")
        else:
            print(f"   ❌ Erro no FFprobe: {process.stderr}")
            return
          # 2. Teste FFmpeg para cortar áudio
        print("\n2️⃣ Testando corte de áudio (0-3 segundos)...")
        
        output_file = r"c:\Projects\ShortTune API\temp\test_cut_simple.webm"
        
        cmd = [
            ffmpeg_path,
            "-i", audio_file,
            "-ss", "0",
            "-t", "3",
            "-acodec", "copy",  # Manter codec original
            "-y",
            output_file
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if process.returncode == 0:
            print("   ✅ FFmpeg executado com sucesso")
            
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"   ✅ Arquivo cortado criado: {output_file}")
                print(f"   ✅ Tamanho: {size} bytes")
                
                # Verifica duração do arquivo cortado
                cmd_check = [
                    ffprobe_path,
                    "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    output_file
                ]
                
                check_process = subprocess.run(cmd_check, capture_output=True, text=True)
                if check_process.returncode == 0:
                    check_data = json.loads(check_process.stdout)
                    cut_duration = float(check_data['format']['duration'])
                    print(f"   ✅ Duração do corte: {cut_duration:.2f} segundos")
            else:
                print("   ❌ Arquivo cortado não foi criado")
        else:
            print(f"   ❌ Erro no FFmpeg: {process.stderr}")
        
        print("\n🎉 Teste simples concluído com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_audio())

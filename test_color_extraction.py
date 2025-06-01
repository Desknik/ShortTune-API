#!/usr/bin/env python3
"""
Teste da extração de cores das capas de música
"""
import asyncio
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.youtube_music_service import youtube_music_service


async def test_color_extraction():
    """Testa a extração de cores das capas de música"""
    try:
        print("🎵 Testando extração de cores das capas de música...\n")
        
        # Teste com busca
        query = "Bohemian Rhapsody Queen"
        print(f"🔍 Buscando: {query}")
        
        results = await youtube_music_service.search_songs(query, limit=2)
        
        if not results:
            print("❌ Nenhum resultado encontrado")
            return
        
        print(f"✅ Encontrados {len(results)} resultados\n")
        
        for i, result in enumerate(results, 1):
            print(f"📀 Música {i}:")
            print(f"   🎵 Título: {result.title}")
            print(f"   🎤 Artista: {result.artist}")
            print(f"   ⏱️ Duração: {result.duration}")
            print(f"   🖼️ Thumbnail: {result.thumbnail}")
            print(f"   🎨 Cores extraídas: {result.colors}")
            
            if result.colors:
                print("   🌈 Visualização das cores:")
                for j, color in enumerate(result.colors):
                    print(f"      Cor {j+1}: {color}")
            
            print("-" * 60)
        
        return results
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_color_extraction())

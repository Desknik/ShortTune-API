from ytmusicapi import YTMusic
from typing import List, Optional
from models.schemas import SearchResult
from config.logging import logger


class YouTubeMusicService:
    """Serviço para busca de músicas no YouTube Music"""
    
    def __init__(self):
        self.ytmusic = YTMusic()
    
    async def search_songs(self, query: str, limit: int = 20) -> List[SearchResult]:
        """Busca músicas no YouTube Music"""
        try:
            logger.info(f"Buscando músicas para: {query}")
            
            # Executa busca
            search_results = self.ytmusic.search(query, filter="songs", limit=limit)
            
            results = []
            for item in search_results:
                try:
                    # Extrai informações do resultado
                    video_id = item.get('videoId')
                    title = item.get('title', 'Unknown')
                    
                    # Artista pode estar em diferentes formatos
                    artist = "Unknown Artist"
                    if 'artists' in item and item['artists']:
                        artist = item['artists'][0].get('name', 'Unknown Artist')
                    
                    # Duration pode estar em diferentes formatos
                    duration = None
                    if 'duration' in item and item['duration']:
                        duration = item['duration']
                    elif 'duration_seconds' in item:
                        duration = f"{item['duration_seconds']}s"
                    
                    # Thumbnail
                    thumbnail = None
                    if 'thumbnails' in item and item['thumbnails']:
                        thumbnail = item['thumbnails'][-1].get('url')  # Maior qualidade
                    
                    if video_id:  # Só adiciona se tiver video_id válido
                        result = SearchResult(
                            video_id=video_id,
                            title=title,
                            artist=artist,
                            duration=duration,
                            thumbnail=thumbnail
                        )
                        results.append(result)
                        
                except Exception as e:
                    logger.warning(f"Erro ao processar resultado de busca: {e}")
                    continue
            
            logger.info(f"Encontradas {len(results)} músicas para '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca do YouTube Music: {e}")
            raise Exception(f"Falha na busca: {str(e)}")
    
    async def get_song_info(self, video_id: str) -> Optional[dict]:
        """Obtém informações detalhadas de uma música"""
        try:
            song_info = self.ytmusic.get_song(video_id)
            return song_info
        except Exception as e:
            logger.error(f"Erro ao obter informações da música {video_id}: {e}")
            return None


# Global service instance
youtube_music_service = YouTubeMusicService()

import io
import requests
from PIL import Image
from colorthief import ColorThief
from typing import List, Optional
from config.logging import logger


class ColorExtractor:
    """Utilitário para extrair cores dominantes de imagens"""
    
    @staticmethod
    def rgb_to_hex(rgb_tuple: tuple) -> str:
        """Converte RGB para formato hexadecimal"""
        return "#{:02x}{:02x}{:02x}".format(*rgb_tuple)
    
    @staticmethod
    async def extract_colors_from_url(image_url: str, color_count: int = 4) -> Optional[List[str]]:
        """
        Extrai cores dominantes de uma imagem a partir da URL
        
        Args:
            image_url: URL da imagem
            color_count: Número de cores para extrair (3-4)
            
        Returns:
            Lista de cores em formato hexadecimal ou None se houver erro
        """
        try:
            # Download da imagem
            logger.info(f"Baixando imagem para extração de cores: {image_url}")
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Abre a imagem com PIL
            image = Image.open(io.BytesIO(response.content))
            
            # Converte para RGB se necessário
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Redimensiona para melhor performance (mantém proporção)
            image.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Salva temporariamente em bytes para ColorThief
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            # Extrai cores dominantes
            color_thief = ColorThief(img_bytes)
            
            # Obtém a cor dominante
            dominant_color = color_thief.get_color(quality=1)
            colors = [ColorExtractor.rgb_to_hex(dominant_color)]
            
            # Obtém palette adicional
            try:
                palette = color_thief.get_palette(color_count=color_count, quality=1)
                colors = [ColorExtractor.rgb_to_hex(color) for color in palette[:color_count]]
            except Exception as e:
                logger.warning(f"Erro ao extrair palette completa: {e}")
                # Fallback para apenas a cor dominante
                pass
            
            logger.info(f"Cores extraídas: {colors}")
            return colors
            
        except requests.RequestException as e:
            logger.error(f"Erro ao baixar imagem {image_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao extrair cores da imagem {image_url}: {e}")
            return None
    
    @staticmethod
    def get_default_colors() -> List[str]:
        """Retorna cores padrão caso a extração falhe"""
        return [
            "#1a1a1a",  # Preto escuro
            "#333333",  # Cinza escuro
            "#666666",  # Cinza médio
            "#999999"   # Cinza claro
        ]


# Instance global
color_extractor = ColorExtractor()

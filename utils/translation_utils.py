# Funções utilitárias para tradução segmentada e detecção de idioma
from functools import lru_cache
from typing import List, Optional
from transformers import MarianMTModel, MarianTokenizer
from langdetect import detect
from deep_translator import GoogleTranslator
import logging

logger = logging.getLogger(__name__)

# Mapeamento padronizado de códigos de idioma
STANDARD_LANG_CODES = {
    # Idiomas principais
    'pt': 'pt',     # Português
    'pt-br': 'pt',  # Português brasileiro
    'pt-pt': 'pt',  # Português de Portugal
    'en': 'en',     # Inglês
    'en-us': 'en',  # Inglês americano
    'en-gb': 'en',  # Inglês britânico
    'es': 'es',     # Espanhol
    'fr': 'fr',     # Francês
    'de': 'de',     # Alemão
    'it': 'it',     # Italiano
    'ru': 'ru',     # Russo
    'ja': 'ja',     # Japonês
    'ko': 'ko',     # Coreano
    'zh': 'zh',     # Chinês
    'zh-cn': 'zh',  # Chinês simplificado
    'zh-tw': 'zh',  # Chinês tradicional
    'ar': 'ar',     # Árabe
    'hi': 'hi',     # Hindi
    'tr': 'tr',     # Turco
    'nl': 'nl',     # Holandês
    'pl': 'pl',     # Polonês
    'sv': 'sv',     # Sueco
    'da': 'da',     # Dinamarquês
    'no': 'no',     # Norueguês
    'fi': 'fi',     # Finlandês
    'th': 'th',     # Tailandês
    'vi': 'vi',     # Vietnamita
    'uk': 'uk',     # Ucraniano
    'cs': 'cs',     # Tcheco
    'hu': 'hu',     # Húngaro
    'ro': 'ro',     # Romeno
    'bg': 'bg',     # Búlgaro
    'hr': 'hr',     # Croata
    'sk': 'sk',     # Eslovaco
    'sl': 'sl',     # Esloveno
    'et': 'et',     # Estoniano
    'lv': 'lv',     # Letão
    'lt': 'lt',     # Lituano
    'he': 'he',     # Hebraico
    'fa': 'fa',     # Persa
    'ur': 'ur',     # Urdu
    'bn': 'bn',     # Bengali
    'ta': 'ta',     # Tamil
    'te': 'te',     # Telugu
    'ml': 'ml',     # Malayalam
    'kn': 'kn',     # Kannada
    'gu': 'gu',     # Gujarati
    'pa': 'pa',     # Punjabi
    'mr': 'mr',     # Marathi
    'ne': 'ne',     # Nepalês
    'si': 'si',     # Cingalês
    'my': 'my',     # Birmanês
    'km': 'km',     # Khmer
    'lo': 'lo',     # Lao
    'ka': 'ka',     # Georgiano
    'am': 'am',     # Amárico
    'sw': 'sw',     # Suaíli
    'yo': 'yo',     # Iorubá
    'ig': 'ig',     # Igbo
    'ha': 'ha',     # Hauçá
    'zu': 'zu',     # Zulu
    'af': 'af',     # Africâner
    'sq': 'sq',     # Albanês
    'az': 'az',     # Azerbaijano
    'be': 'be',     # Bielorrusso
    'bs': 'bs',     # Bósnio
    'ca': 'ca',     # Catalão
    'co': 'co',     # Corso
    'cy': 'cy',     # Galês
    'eo': 'eo',     # Esperanto
    'eu': 'eu',     # Basco
    'fy': 'fy',     # Frísio
    'ga': 'ga',     # Irlandês
    'gd': 'gd',     # Gaélico escocês
    'gl': 'gl',     # Galego
    'hy': 'hy',     # Armênio
    'is': 'is',     # Islandês
    'jw': 'jw',     # Javanês
    'kk': 'kk',     # Cazaque
    'ky': 'ky',     # Quirguiz
    'la': 'la',     # Latim
    'lb': 'lb',     # Luxemburguês
    'mk': 'mk',     # Macedônio
    'mg': 'mg',     # Malgaxe
    'ms': 'ms',     # Malaio
    'mt': 'mt',     # Maltês
    'mn': 'mn',     # Mongol
    'ny': 'ny',     # Chichewa
    'ps': 'ps',     # Pashto
    'sm': 'sm',     # Samoano
    'sn': 'sn',     # Shona
    'so': 'so',     # Somali
    'st': 'st',     # Sesoto
    'su': 'su',     # Sundanês
    'tg': 'tg',     # Tadjique
    'tl': 'tl',     # Filipino
    'tk': 'tk',     # Turcomano
    'uz': 'uz',     # Uzbeque
    'xh': 'xh',     # Xhosa
    'yi': 'yi',     # Iídiche
}

# Mapeamento para deep-translator (Google Translate)
DEEP_TRANSLATOR_LANG_MAP = {
    'pt': 'portuguese',
    'en': 'english',
    'es': 'spanish',
    'fr': 'french',
    'de': 'german',
    'it': 'italian',
    'ru': 'russian',
    'ja': 'japanese',
    'ko': 'korean',
    'zh': 'chinese (simplified)',
    'ar': 'arabic',
    'hi': 'hindi',
    'tr': 'turkish',
    'nl': 'dutch',
    'pl': 'polish',
    'sv': 'swedish',
    'da': 'danish',
    'no': 'norwegian',
    'fi': 'finnish',
    'th': 'thai',
    'vi': 'vietnamese',
    'uk': 'ukrainian',
    'cs': 'czech',
    'hu': 'hungarian',
    'ro': 'romanian',
    'bg': 'bulgarian',
    'hr': 'croatian',
    'sk': 'slovak',
    'sl': 'slovenian',
    'et': 'estonian',
    'lv': 'latvian',
    'lt': 'lithuanian',
    'he': 'hebrew',
    'fa': 'persian',
    'ur': 'urdu',
    'bn': 'bengali',
    'ta': 'tamil',
    'te': 'telugu',
    'ml': 'malayalam',
    'kn': 'kannada',
    'gu': 'gujarati',
    'pa': 'punjabi',
    'mr': 'marathi',
    'ne': 'nepali',
    'si': 'sinhala',
    'my': 'myanmar (burmese)',
    'km': 'khmer',
    'lo': 'lao',
    'ka': 'georgian',
    'am': 'amharic',
    'sw': 'swahili',
    'yo': 'yoruba',
    'ig': 'igbo',
    'ha': 'hausa',
    'zu': 'zulu',
    'af': 'afrikaans',
    'sq': 'albanian',
    'az': 'azerbaijani',
    'be': 'belarusian',
    'bs': 'bosnian',
    'ca': 'catalan',
    'co': 'corsican',
    'cy': 'welsh',
    'eo': 'esperanto',
    'eu': 'basque',
    'fy': 'frisian',
    'ga': 'irish',
    'gd': 'scots gaelic',
    'gl': 'galician',
    'hy': 'armenian',
    'is': 'icelandic',
    'jw': 'javanese',
    'kk': 'kazakh',
    'ky': 'kyrgyz',
    'la': 'latin',
    'lb': 'luxembourgish',
    'mk': 'macedonian',
    'mg': 'malagasy',
    'ms': 'malay',
    'mt': 'maltese',
    'mn': 'mongolian',
    'ny': 'chichewa',
    'ps': 'pashto',
    'sm': 'samoan',
    'sn': 'shona',
    'so': 'somali',
    'st': 'sesotho',
    'su': 'sundanese',
    'tg': 'tajik',
    'tl': 'filipino',
    'tk': 'turkmen',
    'uz': 'uzbek',
    'xh': 'xhosa',
    'yi': 'yiddish',
}

# Modelos especiais que requerem tratamento diferente para IA
SPECIAL_AI_MODELS = {
    'pt': 'Helsinki-NLP/opus-mt-tc-big-en-pt',
    # Adicione outros modelos especiais aqui conforme necessário
}

# Prefixos de idioma para modelos especiais de IA
AI_LANGUAGE_PREFIXES = {
    'pt': '>>pob<<',  # Para português brasileiro
    'pt-pt': '>>por<<',  # Para português de Portugal
}

def normalize_language_code(lang_code: str) -> str:
    """Normaliza códigos de idioma para o padrão usado internamente"""
    if not lang_code:
        return 'en'
    
    lang_code = lang_code.lower().strip()
    return STANDARD_LANG_CODES.get(lang_code, lang_code)

@lru_cache(maxsize=8)
def get_ai_translation_model(model_name: str):
    """Carrega modelo de IA para tradução"""
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    return tokenizer, model

def detect_language(text: str) -> str:
    """Detecta idioma do texto"""
    try:
        detected = detect(text)
        return normalize_language_code(detected)
    except Exception:
        return 'en'  # fallback

def translate_with_ai(text: str, src_lang: str, tgt_lang: str) -> str:
    """Traduz texto usando modelos de IA (Helsinki-NLP)"""
    if src_lang == tgt_lang:
        return text
    
    # Pipeline: src -> en (se necessário) -> tgt
    intermediate = text
    
    # Se idioma fonte não é inglês, traduzir para inglês primeiro
    if src_lang != 'en':
        try:
            tokenizer, model = get_ai_translation_model('Helsinki-NLP/opus-mt-mul-en')
            batch = tokenizer([text], return_tensors="pt", padding=True)
            gen = model.generate(**batch)
            intermediate = tokenizer.batch_decode(gen, skip_special_tokens=True)[0]
        except Exception as e:
            logger.error(f"Erro na tradução IA para inglês: {e}")
            return text  # fallback para texto original
    
    # Se idioma alvo não é inglês, traduzir do inglês para alvo
    if tgt_lang != 'en':
        try:
            # Verificar se é um modelo especial
            if tgt_lang in SPECIAL_AI_MODELS:
                model_name = SPECIAL_AI_MODELS[tgt_lang]
                # Adicionar prefixo se necessário
                if tgt_lang in AI_LANGUAGE_PREFIXES:
                    intermediate = f"{AI_LANGUAGE_PREFIXES[tgt_lang]} {intermediate}"
            else:
                model_name = f"Helsinki-NLP/opus-mt-en-{tgt_lang}"
            
            tokenizer, model = get_ai_translation_model(model_name)
            batch = tokenizer([intermediate], return_tensors="pt", padding=True)
            gen = model.generate(**batch)
            translated = tokenizer.batch_decode(gen, skip_special_tokens=True)[0]
            return translated
        except Exception as e:
            logger.error(f"Erro na tradução IA para {tgt_lang}: {e}")
            return intermediate  # fallback para texto em inglês
    
    return intermediate

def translate_with_deep_translator(text: str, src_lang: str, tgt_lang: str) -> str:
    """Traduz texto usando deep-translator (Google Translate)"""
    if src_lang == tgt_lang:
        return text
    
    try:
        # Converter códigos para nomes de idiomas do Google Translate
        src_lang_name = DEEP_TRANSLATOR_LANG_MAP.get(src_lang, 'auto')
        tgt_lang_name = DEEP_TRANSLATOR_LANG_MAP.get(tgt_lang)
        
        if not tgt_lang_name:
            logger.error(f"Idioma de destino {tgt_lang} não suportado pelo deep-translator")
            return text
        
        # Usar 'auto' para detecção automática se o idioma fonte não for encontrado
        if src_lang not in DEEP_TRANSLATOR_LANG_MAP:
            src_lang_name = 'auto'
        
        translator = GoogleTranslator(source=src_lang_name, target=tgt_lang_name)
        translated = translator.translate(text)
        
        return translated if translated else text
        
    except Exception as e:
        logger.error(f"Erro na tradução deep-translator: {e}")
        return text

def translate_text(text: str, src_lang: str, tgt_lang: str, engine: str = "ai_model") -> str:
    """Traduz texto usando o engine especificado"""
    # Normalizar códigos de idioma
    src_lang = normalize_language_code(src_lang)
    tgt_lang = normalize_language_code(tgt_lang)
    
    if src_lang == tgt_lang:
        return text
    
    if engine == "deep_translator":
        return translate_with_deep_translator(text, src_lang, tgt_lang)
    else:  # "ai_model"
        return translate_with_ai(text, src_lang, tgt_lang)

def translate_segments(segments: List[dict], target_lang: Optional[str], translation_engine: str = "ai_model") -> List[dict]:
    """Traduz segmentos usando o engine de tradução especificado"""
    if not target_lang:
        return segments
    
    target_lang = normalize_language_code(target_lang)
    result = []
    
    for seg in segments:
        src_lang = detect_language(seg['text'])
        translation = translate_text(seg['text'], src_lang, target_lang, translation_engine)
        seg_out = dict(seg)
        seg_out['translation'] = translation
        result.append(seg_out)
    
    return result

def get_supported_languages(engine: str = "ai_model") -> dict:
    """Retorna lista de idiomas suportados pelo engine especificado"""
    if engine == "deep_translator":
        return {
            "supported_languages": list(DEEP_TRANSLATOR_LANG_MAP.keys()),
            "language_names": {code: name.title() for code, name in DEEP_TRANSLATOR_LANG_MAP.items()},
            "engine": "Google Translate (via deep-translator)",
            "auto_detect": True
        }
    else:  # "ai_model"
        # Para IA, retornar um subconjunto dos idiomas mais comuns que têm modelos disponíveis
        ai_supported = ['pt', 'en', 'es', 'fr', 'de', 'it', 'ru', 'zh', 'ja', 'ko', 'ar', 'hi', 'tr', 'nl', 'pl']
        return {
            "supported_languages": ai_supported,
            "language_names": {code: DEEP_TRANSLATOR_LANG_MAP.get(code, code).title() for code in ai_supported if code in DEEP_TRANSLATOR_LANG_MAP},
            "engine": "Helsinki-NLP AI Models",
            "auto_detect": True
        }

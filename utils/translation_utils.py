# Funções utilitárias para tradução segmentada e detecção de idioma
from functools import lru_cache
from typing import List, Optional
from transformers import MarianMTModel, MarianTokenizer
from langdetect import detect
import logging

logger = logging.getLogger(__name__)

# Mapeamento de códigos de idioma para nomes usados nos modelos Helsinki-NLP
LANG_CODE_MAP = {
    'pt': 'pt', 'en': 'en', 'es': 'es', 'fr': 'fr', 'de': 'de', 'ru': 'ru', 'it': 'it',
    'nl': 'nl', 'pl': 'pl', 'tr': 'tr', 'ar': 'ar', 'zh': 'zh', 'ja': 'ja', 'ko': 'ko',
    # Adicione mais conforme necessário
}

# Modelos especiais que requerem tratamento diferente
SPECIAL_MODELS = {
    'pt': 'Helsinki-NLP/opus-mt-tc-big-en-pt',
    # Adicione outros modelos especiais aqui conforme necessário
}

# Prefixos de idioma para modelos especiais
LANGUAGE_PREFIXES = {
    'pt': '>>pob<<',  # Para português brasileiro
    'pt-pt': '>>por<<',  # Para português de Portugal
}

@lru_cache(maxsize=8)
def get_translation_model(model_name: str):
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    return tokenizer, model

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return 'en'  # fallback

def translate_text(text: str, src_lang: str, tgt_lang: str) -> str:
    if src_lang == tgt_lang:
        return text
    
    # Pipeline: src -> en (se necessário) -> tgt
    intermediate = text
    
    # Se idioma fonte não é inglês, traduzir para inglês primeiro
    if src_lang != 'en':
        try:
            tokenizer, model = get_translation_model('Helsinki-NLP/opus-mt-mul-en')
            batch = tokenizer([text], return_tensors="pt", padding=True)
            gen = model.generate(**batch)
            intermediate = tokenizer.batch_decode(gen, skip_special_tokens=True)[0]
        except Exception as e:
            logger.error(f"Erro na tradução para inglês: {e}")
            return text  # fallback para texto original
    
    # Se idioma alvo não é inglês, traduzir do inglês para alvo
    if tgt_lang != 'en':
        try:
            # Verificar se é um modelo especial
            if tgt_lang in SPECIAL_MODELS:
                model_name = SPECIAL_MODELS[tgt_lang]
                # Adicionar prefixo se necessário
                if tgt_lang in LANGUAGE_PREFIXES:
                    intermediate = f"{LANGUAGE_PREFIXES[tgt_lang]} {intermediate}"
            else:
                model_name = f"Helsinki-NLP/opus-mt-en-{tgt_lang}"
            
            tokenizer, model = get_translation_model(model_name)
            batch = tokenizer([intermediate], return_tensors="pt", padding=True)
            gen = model.generate(**batch)
            translated = tokenizer.batch_decode(gen, skip_special_tokens=True)[0]
            return translated
        except Exception as e:
            logger.error(f"Erro na tradução para {tgt_lang}: {e}")
            return intermediate  # fallback para texto em inglês
    
    return intermediate

def translate_segments(segments: List[dict], target_lang: Optional[str]) -> List[dict]:
    if not target_lang:
        return segments
    result = []
    for seg in segments:
        src_lang = detect_language(seg['text'])
        translation = translate_text(seg['text'], src_lang, target_lang)
        seg_out = dict(seg)
        seg_out['translation'] = translation
        result.append(seg_out)
    return result

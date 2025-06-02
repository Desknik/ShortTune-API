#!/usr/bin/env python3
"""
Teste para verificar se os engines de tradução estão funcionando corretamente.
"""

import asyncio
import sys
import os

# Adicionar o diretório raiz ao PATH
sys.path.insert(0, os.path.abspath('.'))

from utils.translation_utils import (
    translate_text, 
    translate_segments, 
    get_supported_languages,
    normalize_language_code,
    detect_language
)

def test_language_normalization():
    """Testa a normalização de códigos de idioma"""
    print("🔧 Testando normalização de códigos de idioma...")
    
    test_cases = [
        ('pt-br', 'pt'),
        ('pt-pt', 'pt'), 
        ('en-us', 'en'),
        ('zh-cn', 'zh'),
        ('PT', 'pt'),
        ('', 'en'),
        ('invalid', 'invalid')
    ]
    
    for input_code, expected in test_cases:
        result = normalize_language_code(input_code)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_code}' → '{result}' (esperado: '{expected}')")

def test_language_detection():
    """Testa detecção de idioma"""
    print("\n🔍 Testando detecção de idioma...")
    
    test_texts = [
        ("Hello, how are you today?", "en"),
        ("Olá, como você está hoje?", "pt"),
        ("Hola, ¿cómo estás hoy?", "es"),
        ("Bonjour, comment allez-vous aujourd'hui?", "fr"),
        ("Guten Tag, wie geht es Ihnen heute?", "de"),
    ]
    
    for text, expected_lang in test_texts:
        detected = detect_language(text)
        print(f"  Texto: '{text[:30]}...'")
        print(f"  Detectado: {detected} (esperado: {expected_lang})")

def test_ai_translation():
    """Testa tradução com IA"""
    print("\n🤖 Testando tradução com IA (Helsinki-NLP)...")
    
    test_text = "Hello, this is a test message."
    target_langs = ['pt', 'es', 'fr']
    
    for lang in target_langs:
        try:
            result = translate_text(test_text, 'en', lang, 'ai_model')
            print(f"  EN → {lang.upper()}: '{result}'")
        except Exception as e:
            print(f"  ❌ Erro EN → {lang.upper()}: {e}")

def test_deep_translator():
    """Testa tradução com deep-translator"""
    print("\n🌐 Testando tradução com deep-translator...")
    
    test_text = "Hello, this is a test message."
    target_langs = ['pt', 'es', 'fr', 'de', 'it']
    
    for lang in target_langs:
        try:
            result = translate_text(test_text, 'en', lang, 'deep_translator')
            print(f"  EN → {lang.upper()}: '{result}'")
        except Exception as e:
            print(f"  ❌ Erro EN → {lang.upper()}: {e}")

def test_segments_translation():
    """Testa tradução de segmentos"""
    print("\n📝 Testando tradução de segmentos...")
    
    test_segments = [
        {
            "start": 0.0,
            "end": 3.0,
            "text": "Hello, welcome to our service."
        },
        {
            "start": 3.0,
            "end": 6.0,
            "text": "This is a demonstration of translation."
        }
    ]
    
    # Testar com AI
    print("  🤖 Com IA:")
    try:
        ai_result = translate_segments(test_segments, 'pt', 'ai_model')
        for seg in ai_result:
            print(f"    [{seg['start']:.1f}s-{seg['end']:.1f}s]: {seg['text']}")
            if 'translation' in seg:
                print(f"    Tradução: {seg['translation']}")
    except Exception as e:
        print(f"    ❌ Erro: {e}")
    
    # Testar com deep-translator
    print("  🌐 Com deep-translator:")
    try:
        deep_result = translate_segments(test_segments, 'pt', 'deep_translator')
        for seg in deep_result:
            print(f"    [{seg['start']:.1f}s-{seg['end']:.1f}s]: {seg['text']}")
            if 'translation' in seg:
                print(f"    Tradução: {seg['translation']}")
    except Exception as e:
        print(f"    ❌ Erro: {e}")

def test_supported_languages():
    """Testa listagem de idiomas suportados"""
    print("\n📋 Testando listagem de idiomas suportados...")
    
    # AI Model
    print("  🤖 IA (Helsinki-NLP):")
    try:
        ai_langs = get_supported_languages('ai_model')
        print(f"    Engine: {ai_langs['engine']}")
        print(f"    Idiomas: {len(ai_langs['supported_languages'])}")
        print(f"    Exemplos: {ai_langs['supported_languages'][:5]}")
    except Exception as e:
        print(f"    ❌ Erro: {e}")
    
    # Deep Translator
    print("  🌐 Deep Translator:")
    try:
        deep_langs = get_supported_languages('deep_translator')
        print(f"    Engine: {deep_langs['engine']}")
        print(f"    Idiomas: {len(deep_langs['supported_languages'])}")
        print(f"    Exemplos: {deep_langs['supported_languages'][:5]}")
    except Exception as e:
        print(f"    ❌ Erro: {e}")

def main():
    """Executa todos os testes"""
    print("🧪 Teste dos Engines de Tradução")
    print("=" * 50)
    
    try:
        test_language_normalization()
        test_language_detection()
        test_supported_languages()
        test_deep_translator()
        
        print("\n⚠️  Pulando teste de IA (pode demorar para baixar modelos)")
        print("   Para testar IA, descomente as linhas no código")
        # test_ai_translation()
        # test_segments_translation()
        
        print("\n✅ Testes concluídos!")
        
    except Exception as e:
        print(f"\n❌ Erro geral nos testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

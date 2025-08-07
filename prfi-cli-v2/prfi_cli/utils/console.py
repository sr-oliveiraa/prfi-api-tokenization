#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Console Utils
Console compatível com Windows
"""

import os
import sys
from rich.console import Console

def create_console() -> Console:
    """Criar console compatível com Windows"""
    
    # Configurar encoding para Windows
    if os.name == 'nt':  # Windows
        # Tentar configurar UTF-8
        try:
            os.system('chcp 65001 >nul 2>&1')  # UTF-8 code page
        except:
            pass
    
    # Criar console com configurações seguras para Windows
    console = Console(
        force_terminal=True,
        legacy_windows=True,
        safe_box=True,
        _environ=dict(os.environ, TERM='xterm-256color')
    )
    
    return console

def safe_print(console: Console, text: str, **kwargs):
    """Print seguro que funciona no Windows"""
    try:
        console.print(text, **kwargs)
    except UnicodeEncodeError:
        # Fallback: remover emojis e caracteres especiais
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        console.print(safe_text, **kwargs)
    except Exception as e:
        # Fallback final: print básico
        print(text.encode('ascii', 'ignore').decode('ascii'))

# Emojis seguros para Windows (fallback)
SAFE_EMOJIS = {
    '🎯': '[*]',
    '🚀': '[>]',
    '🧪': '[T]',
    '📊': '[D]',
    '🔗': '[L]',
    '🌐': '[W]',
    '✨': '[+]',
    '✅': '[OK]',
    '❌': '[X]',
    '⚠️': '[!]',
    '💰': '[$]',
    '🔧': '[T]',
    '📋': '[L]',
    '🎉': '[!]',
    '👋': '[B]',
    '🔍': '[S]',
    '⚙️': '[C]',
    '📈': '[G]',
    '🏦': '[B]',
    '⛓️': '[C]',
    '🌟': '[*]'
}

def replace_emojis(text: str) -> str:
    """Substituir emojis por caracteres seguros"""
    for emoji, safe in SAFE_EMOJIS.items():
        text = text.replace(emoji, safe)
    return text

def windows_safe_print(text: str, **kwargs):
    """Print completamente seguro para Windows"""
    try:
        # Tentar print normal primeiro
        print(text, **kwargs)
    except UnicodeEncodeError:
        # Substituir emojis e tentar novamente
        safe_text = replace_emojis(text)
        try:
            print(safe_text, **kwargs)
        except:
            # Fallback final: apenas ASCII
            ascii_text = safe_text.encode('ascii', 'ignore').decode('ascii')
            print(ascii_text, **kwargs)

#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Template Utils
Gerenciamento de templates
"""

from typing import Dict, Any, List
from ..templates.presets import PROJECT_TEMPLATES, list_templates

def get_available_templates() -> List[Dict[str, str]]:
    """Obter lista de templates disponíveis"""
    return list_templates()

def load_template(template_name: str) -> Dict[str, Any]:
    """Carregar template específico"""
    from ..templates.presets import get_project_template
    
    template = get_project_template(template_name)
    if not template:
        raise ValueError(f"Template '{template_name}' não encontrado")
    
    return template

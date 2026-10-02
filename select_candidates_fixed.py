#!/usr/bin/env python3
"""
Script de selección de candidatos para el workflow de fusión.
Determina qué archivos de SOURCE deben integrarse en TARGET.
"""

import json
import sys
import os
from pathlib import Path

def load_comparison_map():
    """Carga el mapa comparativo desde la salida del agente anterior."""
    # En un entorno real, esto vendría del agente anterior
    # Para este ejemplo, simularemos basado en lo que sabemos
    # En la práctica, el workflow pasará esto como argumento

    # Simulación basada en conocimiento previo del sistema
    target_path = r"D:\Mi unidad\Proyectos\Dorama Studio AI"
    source_path = r"C:\Users\LENOVO\Desktop\Proyectos\DORAMA_STUDIO_IA_SEGURO"

    # Directorios clave que queremos enfocar para la mejora
    priority_dirs = [
        r"\dorama_studio\agents\narrative",
        r"\dorama_studio\agents\learning",
        r"\dorama_studio\config",
        r"\dorama_studio\dna",
        r"\dorama_studio\intelligence",
        r"\dorama_studio\agents\visual",
        r"\dorama_studio\agents\audio"
    ]

    # Candidatos específicos que sabemos son mejoras valiosas
    specific_candidates = [
        r"dorama_studio\agents\narrative\master_writer.py",
        r"dorama_studio\agents\narrative\viral_analyst.py",
        r"dorama_studio\dna\global_entertainment_intelligence.py",
        r"dorama_studio\intelligence\global_trend_hunter.py",
        r"dorama_studio\intelligence\emotional_director.py",
        r"dorama_studio\intelligence\character_brain.py",
        r"dorama_studio\intelligence\hit_predictor.py",
        r"dorama_studio\config\model_router.py",
        r"dorama_studio\agents\learning\analytics_engine.py",
        r"dorama_studio\agents\learning\feedback_loop.py",
        r"dorama_studio\agents\visual\visual_agent.py",
        r"dorama_studio\agents\visual\storyboard_agent.py",
        r"dorama_studio\agents\audio\music_supervisor_agent.py",
        r"dorama_studio\agents\audio\voice_director_agent.py",
        r"dorama_studio\agents\audio\sound_designer_agent.py"
    ]

    # Filtrar solo los que existen en SOURCE
    actual_candidates = []
    source_base = Path(source_path)

    for candidate in specific_candidates:
        full_path = source_base / candidate
        if full_path.exists():
            actual_candidates.append(candidate)

    return {"candidates": actual_candidates}

if __name__ == "__main__":
    result = load_comparison_map()
    print(json.dumps(result, indent=2))
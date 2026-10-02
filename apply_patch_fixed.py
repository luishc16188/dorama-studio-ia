#!/usr/bin/env python3
"""
Script de aplicación de parches para el workflow de fusión.
Copia archivos seleccionados desde SOURCE a TARGET con adaptación necesaria.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

def adapt_master_writer(source_path, target_path):
    """Adaptaciones específicas para master_writer.py"""
    # Por ahora, copia directa. En el futuro podrían necesitarse adaptaciones
    shutil.copy2(source_path, target_path)
    print(f"Adapted master_writer: {source_path} -> {target_path}")

def adapt_viral_analyst(source_path, target_path):
    """Adaptaciones específicas para viral_analyst.py"""
    shutil.copy2(source_path, target_path)
    print(f"Adapted viral_analyst: {source_path} -> {target_path}")

def adapt_global_entertainment_intelligence(source_path, target_path):
    """Adaptar el DNA como módulo de intelligence"""
    # Crear el directorio si no existe
    target_path.parent.mkdir(parents=True, exist_ok=True)
    # Renombrar y adaptar como módulo de intelligence
    intelligence_target = target_path.parent.parent / "intelligence" / "global_entertainment.py"
    intelligence_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, intelligence_target)
    print(f"Adapted global_entertainment_intelligence: {source_path} -> {intelligence_target}")

def adapt_model_router(source_path, target_path):
    """Mejorar el model_router existente con lógica de SOURCE"""
    # Leer ambas versiones y fusionar lo mejor
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            source_content = f.read()
        with open(target_path, 'r', encoding='utf-8') as f:
            target_content = f.read()

        # Estrategia: usar el target como base pero incorporar mejoras del source
        # Por simplicidad, si el source es significativamente más largo, usarlo
        if len(source_content) > len(target_content) * 1.5:
            shutil.copy2(source_path, target_path)
            print(f"Adapted model_router (source preferred): {source_path} -> {target_path}")
        else:
            print(f"Kept target model_router (target preferred or similar): {target_path}")
    except Exception as e:
        # En caso de error, copiar source
        shutil.copy2(source_path, target_path)
        print(f"Adapted model_router (error fallback): {source_path} -> {target_path}")

def adapt_analytics_engine(source_path, target_path):
    """Fusionar analytics_engine de ambas versiones"""
    try:
        # Similar a model_router
        with open(source_path, 'r', encoding='utf-8') as f:
            source_content = f.read()
        with open(target_path, 'r', encoding='utf-8') as f:
            target_content = f.read()

        if len(source_content) > len(target_content) * 1.2:
            shutil.copy2(source_path, target_path)
            print(f"Adapted analytics_engine (source preferred): {source_path} -> {target_path}")
        else:
            print(f"Kept target analytics_engine (target preferred or similar): {target_path}")
    except Exception as e:
        shutil.copy2(source_path, target_path)
        print(f"Adapted analytics_engine (error fallback): {source_path} -> {target_path}")

def default_adapter(source_path, target_path):
    """Adaptador por defecto: copia directa con creación de directorios"""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target_path)
    print(f"Copied: {source_path} -> {target_path}")

def main():
    parser = argparse.ArgumentParser(description='Apply patches from SOURCE to TARGET')
    parser.add_argument('--candidate', required=True, help='Relative path of the file to process')
    args = parser.parse_args()

    candidate = args.candidate.strip()

    # Rutas base
    source_base = Path(r"C:\Users\LENOVO\Desktop\Proyectos\DORAMA_STUDIO_IA_SEGURO")
    target_base = Path(r"D:\Mi unidad\Proyectos\Dorama Studio AI")

    source_path = source_base / candidate
    target_path = target_base / candidate

    # Verificar que el source existe
    if not source_path.exists():
        print(f"ERROR: Source file does not exist: {source_path}")
        sys.exit(1)

    # Seleccionar adaptador basado en el tipo de archivo
    if "master_writer" in candidate and candidate.endswith(".py"):
        adapt_master_writer(source_path, target_path)
    elif "viral_analyst" in candidate and candidate.endswith(".py"):
        adapt_viral_analyst(source_path, target_path)
    elif "global_entertainment_intelligence" in candidate:
        adapt_global_entertainment_intelligence(source_path, target_path)
    elif "model_router" in candidate and candidate.endswith(".py"):
        adapt_model_router(source_path, target_path)
    elif "analytics_engine" in candidate and candidate.endswith(".py"):
        adapt_analytics_engine(source_path, target_path)
    else:
        # Adaptador por defecto
        default_adapter(source_path, target_path)

if __name__ == "__main__":
    main()
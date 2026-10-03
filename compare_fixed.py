#!/usr/bin/env python3
"""
Script de comparación para el workflow de fusión.
Genera un mapa comparativo entre TARGET y SOURCE.
"""

import hashlib
from pathlib import Path


def get_file_hash(filepath):
    """Calcula el hash MD5 de un archivo."""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except Exception:
        return None
    return hash_md5.hexdigest()

def scan_directory(root_path, exclude_patterns=None):
    """Escanea un directorio y retorna un diccionario de archivos relativos con sus hashes."""
    if exclude_patterns is None:
        exclude_patterns = ['.git', '__pycache__', '.pyc', '.tmp']

    file_map = {}
    root_path = Path(root_path)

    for file_path in root_path.rglob('*'):
        if file_path.is_file():
            # Verificar si el archivo debe excluirse
            excluded = False
            for pattern in exclude_patterns:
                if pattern in str(file_path):
                    excluded = True
                    break

            if not excluded:
                try:
                    rel_path = str(file_path.relative_to(root_path))
                    file_hash = get_file_hash(file_path)
                    if file_hash:
                        file_map[rel_path] = file_hash
                except Exception:
                    continue

    return file_map

def compare_directories(target_path, source_path):
    """Compara dos directorios y retorna las diferencias."""
    target_files = scan_directory(target_path)
    source_files = scan_directory(source_path)

    only_in_target = []
    only_in_source = []
    identical = []
    similar = []  # Archivos con mismo nombre pero contenido diferente
    conflicts = []  # Para casos especiales que necesitan revisión manual

    # Archivos solo en TARGET
    for rel_path in target_files:
        if rel_path not in source_files:
            only_in_target.append(rel_path)

    # Archivos solo en SOURCE
    for rel_path in source_files:
        if rel_path not in target_files:
            only_in_source.append(rel_path)

    # Archivos en ambos - verificar si son idénticos
    common_paths = set(target_files.keys()) & set(source_files.keys())
    for rel_path in common_paths:
        if target_files[rel_path] == source_files[rel_path]:
            identical.append(rel_path)
        else:
            similar.append(rel_path)

    return {
        'onlyInTarget': only_in_target,
        'onlyInSource': only_in_source,
        'identical': identical,
        'similar': similar,
        'conflicts': conflicts
    }

if __name__ == "__main__":
    target_path = r"D:\Mi unidad\Proyectos\Dorama Studio AI"
    source_path = r"C:\Users\LENOVO\Desktop\Proyectos\DORAMA_STUDIO_IA_SEGURO"

    result = compare_directories(target_path, source_path)

    # Output como JSON para que el workflow lo procese
    import json
    print(json.dumps(result, indent=2))

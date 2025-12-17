# Adquisición segura de imágenes
"""
Módulo de adquisición segura de imágenes
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict
import logging

logger = logging.getLogger('ForensicAnalyzer')

def acquire_image(source_path: str, destination_dir: str) -> Dict[str, any]:
    """
    Adquiere una imagen de forma segura manteniendo cadena de custodia
    
    Args:
        source_path: Ruta de origen de la imagen
        destination_dir:  Directorio de destino
    
    Returns:
        Diccionario con metadata de adquisición
    """
    logger.info(f"Iniciando adquisición segura:  {source_path}")
    
    source = Path(source_path)
    
    if not source.exists():
        logger.error(f"Archivo fuente no encontrado: {source_path}")
        raise FileNotFoundError(f"Archivo fuente no encontrado: {source_path}")
    
    # Crear directorio de destino
    dest_dir = Path(destination_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar nombre con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest_file = dest_dir / f"{timestamp}_{source.name}"
    
    # Copiar archivo
    logger.debug(f"Copiando a: {dest_file}")
    shutil.copy2(source, dest_file)
    
    # Metadata de adquisición
    metadata = {
        'original_path': str(source. absolute()),
        'acquired_path': str(dest_file.absolute()),
        'timestamp':  datetime.now().isoformat(),
        'size_bytes': dest_file.stat().st_size,
        'filename': source.name
    }
    
    logger.info("✅ Adquisición completada")
    
    return metadata
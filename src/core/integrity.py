# Verificación hash/integridad
"""
Módulo de verificación de integridad mediante hashing
"""

import hashlib
from pathlib import Path
from typing import Dict
import logging

logger = logging.getLogger('ForensicAnalyzer')

def calculate_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Calcula el hash de un archivo
    
    Args:
        file_path: Ruta al archivo
        algorithm: Algoritmo de hash (sha256, md5, sha1)
    
    Returns:
        Hash del archivo en formato hexadecimal
    """
    logger.debug(f"Calculando hash {algorithm. upper()} de {file_path}")
    
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        # Leer en chunks para archivos grandes
        for chunk in iter(lambda: f. read(4096), b''):
            hash_func.update(chunk)
    
    hash_value = hash_func.hexdigest()
    logger.info(f"{algorithm.upper()}: {hash_value}")
    
    return hash_value

def verify_integrity(file_path: str) -> Dict[str, str]: 
    """
    Verifica la integridad de un archivo calculando múltiples hashes
    
    Args: 
        file_path: Ruta al archivo
    
    Returns:
        Diccionario con los hashes calculados
    """
    logger. info(f"Verificando integridad de:  {file_path}")
    
    if not Path(file_path).exists():
        logger.error(f"Archivo no encontrado: {file_path}")
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
    
    hashes = {
        'md5': calculate_hash(file_path, 'md5'),
        'sha1': calculate_hash(file_path, 'sha1'),
        'sha256': calculate_hash(file_path, 'sha256')
    }
    
    return hashes
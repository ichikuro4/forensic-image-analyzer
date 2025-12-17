# Sistema de logging
"""
Sistema de logging para análisis forense
"""

import logging
import colorlog
from pathlib import Path
from datetime import datetime

def setup_logger(log_level='INFO'):
    """
    Configura el sistema de logging con salida a consola y archivo
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    
    # Crear directorio de logs si no existe
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Nombre del archivo de log con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'forensic_{timestamp}.log'
    
    # Configurar logger raíz
    logger = logging. getLogger('ForensicAnalyzer')
    logger.setLevel(getattr(logging, log_level. upper()))
    
    # Limpiar handlers existentes
    logger.handlers. clear()
    
    # Handler para consola con colores
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level. upper()))
    
    console_format = colorlog.ColoredFormatter(
        '%(log_color)s[%(asctime)s] %(levelname)-8s%(reset)s %(message)s',
        datefmt='%H:%M:%S',
        log_colors={
            'DEBUG':  'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_format)
    
    # Handler para archivo sin colores
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    file_format = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Añadir handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logger.info(f"Log guardado en: {log_file}")
    
    return logger
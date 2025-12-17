"""
Wrapper para Exiftool - Extracción de metadatos EXIF
"""

import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.base_analyzer import BaseAnalyzer
from typing import Dict
import subprocess
import json
import logging

logger = logging.getLogger('ForensicAnalyzer')

class ExiftoolAnalyzer(BaseAnalyzer):
    """Analizador usando Exiftool"""
    
    def __init__(self):
        super().__init__(name='Exiftool', command='exiftool')
    
    def run(self, image_path: str) -> Dict:
        """
        Ejecuta exiftool sobre la imagen
        
        Args: 
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con metadatos EXIF
        """
        logger. info(f"Ejecutando {self.name} en: {image_path}")
        
        if not self.enabled:
            logger.warning(f"{self.name} no está disponible")
            return {'error': 'Tool not available'}
        
        try:
            # Ejecutar exiftool con salida JSON
            result = subprocess. run(
                [self.command, '-json', image_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.results = json.loads(result.stdout)[0]
                logger.info(f"✅ {self.name} completado")
                return self.results
            else:
                logger.error(f"Error ejecutando {self.name}: {result.stderr}")
                return {'error': result.stderr}
                
        except Exception as e:
            logger.error(f"Excepción en {self.name}: {str(e)}")
            return {'error': str(e)}
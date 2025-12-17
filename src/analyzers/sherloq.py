"""
Wrapper para Sherloq - Detección de manipulación
TODO: Implementar en fase posterior
"""

from .base_analyzer import BaseAnalyzer
from typing import Dict
import logging

logger = logging.getLogger('ForensicAnalyzer')

class SherloqAnalyzer(BaseAnalyzer):
    """Analizador usando Sherloq"""
    
    def __init__(self):
        super().__init__(name='Sherloq', command='sherloq')
    
    def run(self, image_path: str) -> Dict:
        """
        Ejecuta Sherloq sobre la imagen
        
        Args:
            image_path: Ruta a la imagen
        
        Returns: 
            Diccionario con resultados del análisis
        """
        logger.info(f"Ejecutando {self.name} en: {image_path}")
        
        if not self.enabled:
            logger.warning(f"{self.name} no está disponible")
            return {'error': 'Tool not available'}
        
        # TODO: Implementar wrapper para Sherloq
        logger. warning(f"{self.name} - Implementación pendiente")
        return {'status': 'not_implemented'}
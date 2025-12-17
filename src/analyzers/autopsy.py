"""
Wrapper para Autopsy - Análisis forense profundo
TODO: Implementar en fase posterior
"""

from .base_analyzer import BaseAnalyzer
from typing import Dict
import logging

logger = logging.getLogger('ForensicAnalyzer')

class AutopsyAnalyzer(BaseAnalyzer):
    """Analizador usando Autopsy"""
    
    def __init__(self):
        super().__init__(name='Autopsy', command='autopsy')
    
    def run(self, image_path: str) -> Dict:
        """
        Ejecuta Autopsy sobre la imagen
        
        Args:
            image_path:  Ruta a la imagen
        
        Returns:
            Diccionario con resultados del análisis
        """
        logger.info(f"Ejecutando {self.name} en: {image_path}")
        
        if not self.enabled:
            logger. warning(f"{self.name} no está disponible")
            return {'error': 'Tool not available'}
        
        # TODO:  Implementar wrapper para Autopsy
        logger.warning(f"{self.name} - Implementación pendiente")
        return {'status': 'not_implemented'}
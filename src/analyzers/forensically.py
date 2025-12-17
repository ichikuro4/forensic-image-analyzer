"""
Wrapper para Forensically - Análisis ELA y detección de clonación
TODO: Implementar en fase posterior
"""

from .base_analyzer import BaseAnalyzer
from typing import Dict
import logging

logger = logging.getLogger('ForensicAnalyzer')

class ForensicallyAnalyzer(BaseAnalyzer):
    """Analizador usando Forensically"""
    
    def __init__(self):
        super().__init__(name='Forensically', command='forensically')
    
    def run(self, image_path: str) -> Dict:
        """
        Ejecuta Forensically sobre la imagen
        
        Args: 
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con resultados del análisis
        """
        logger.info(f"Ejecutando {self.name} en: {image_path}")
        
        if not self. enabled:
            logger.warning(f"{self.name} no está disponible")
            return {'error': 'Tool not available'}
        
        # TODO: Implementar wrapper para Forensically
        logger.warning(f"{self. name} - Implementación pendiente")
        return {'status': 'not_implemented'}
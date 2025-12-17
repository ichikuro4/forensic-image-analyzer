"""
Pipeline de orquestación de análisis forenses
"""

from typing import List, Dict
import logging
import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.base_analyzer import BaseAnalyzer
from analyzers.exiftool import ExiftoolAnalyzer
from analyzers.ela_analyzer import ELAAnalyzer  # ← NUEVO

logger = logging.getLogger('ForensicAnalyzer')

class ForensicPipeline:
    """Orquestador del pipeline de análisis"""
    
    def __init__(self):
        self.analyzers: List[BaseAnalyzer] = []
        self.results: Dict = {}
        self._initialize_analyzers()
    
    def _initialize_analyzers(self):
        """Inicializa todos los analizadores"""
        logger.info("Inicializando analizadores...")
        
        # Analizadores actuales
        self.analyzers. append(ExiftoolAnalyzer())
        self.analyzers. append(ELAAnalyzer())  # ← NUEVO
        
        # TODO: Añadir más adelante
        # from analyzers.sherloq import SherloqAnalyzer
        # from analyzers.clone_detection import CloneDetectionAnalyzer
        # self.analyzers.append(SherloqAnalyzer())
        # self.analyzers.append(CloneDetectionAnalyzer())
        
        enabled_count = sum(1 for a in self. analyzers if a.enabled)
        logger.info(f"Analizadores activos: {enabled_count}/{len(self.analyzers)}")
    
    def execute_all(self, image_path: str) -> Dict:
        """
        Ejecuta todos los analizadores sobre una imagen
        
        Args: 
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con todos los resultados
        """
        logger.info(f"Ejecutando pipeline completo sobre: {image_path}")
        
        self.results = {}
        
        for analyzer in self.analyzers:
            if analyzer.enabled:
                try:
                    result = analyzer. run(image_path)
                    self.results[analyzer.name] = result
                except Exception as e:
                    logger.error(f"Error en {analyzer.name}: {str(e)}")
                    self.results[analyzer.name] = {'error': str(e)}
        
        logger.info("✅ Pipeline completado")
        return self.results
# Clase base para todos los analizadores
"""
Clase base abstracta para todos los analizadores forenses
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import logging
import shutil

logger = logging.getLogger('ForensicAnalyzer')

class BaseAnalyzer(ABC):
    """Clase base para analizadores forenses"""
    
    def __init__(self, name: str, command: str):
        """
        Inicializa el analizador
        
        Args: 
            name: Nombre del analizador
            command: Comando para ejecutar la herramienta
        """
        self.name = name
        self.command = command
        self. enabled = self. check_tool_available()
        self.results:  Optional[Dict] = None
    
    def check_tool_available(self) -> bool:
        """
        Verifica si la herramienta está disponible en el sistema
        
        Returns: 
            True si está disponible, False en caso contrario
        """
        is_available = shutil.which(self.command) is not None
        
        if is_available:
            logger.debug(f"✅ {self.name} disponible")
        else:
            logger.warning(f"❌ {self.name} no encontrado")
        
        return is_available
    
    @abstractmethod
    def run(self, image_path: str) -> Dict:
        """
        Ejecuta el análisis sobre una imagen
        
        Args: 
            image_path: Ruta a la imagen a analizar
        
        Returns:
            Diccionario con los resultados del análisis
        """
        pass
    
    def get_results(self) -> Optional[Dict]:
        """Retorna los resultados del último análisis"""
        return self. results
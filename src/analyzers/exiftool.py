"""
Wrapper para Exiftool - Extracción de metadatos EXIF
"""

from . base_analyzer import BaseAnalyzer
from typing import Dict
import subprocess
import json
import logging

logger = logging.getLogger('ForensicAnalyzer')

class ExiftoolAnalyzer(BaseAnalyzer):
    """Extrae metadatos EXIF usando exiftool"""
    
    def __init__(self):
        super().__init__(name='Exiftool', command='exiftool')
    
    def run(self, image_path: str) -> Dict:
        """
        Ejecuta exiftool sobre la imagen
        
        Args: 
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con todos los metadatos EXIF
        """
        logger.info(f"Ejecutando {self.name} en:  {image_path}")
        
        try:
            # Ejecutar exiftool en modo JSON para obtener TODOS los campos
            cmd = [self.command, '-j', '-G', '-a', '-s', image_path]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Error ejecutando exiftool: {result.stderr}")
                return {'error': result.stderr}
            
            # Parsear JSON
            metadata_list = json.loads(result.stdout)
            
            if not metadata_list:
                return {'error': 'No metadata found'}
            
            # Exiftool devuelve una lista con un elemento
            metadata = metadata_list[0]
            
            # Eliminar campos internos de exiftool
            clean_metadata = {}
            skip_fields = ['SourceFile', 'ExifToolVersion', 'FileName', 'Directory', 'FilePermissions']
            
            for key, value in metadata.items():
                if key not in skip_fields:
                    clean_metadata[key] = value
            
            self. results = clean_metadata
            logger.info(f"✅ {self.name} completado - {len(clean_metadata)} campos extraídos")
            
            return clean_metadata
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout ejecutando {self.name}")
            return {'error': 'Timeout'}
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON de exiftool: {str(e)}")
            return {'error': f'JSON parse error: {str(e)}'}
        except Exception as e: 
            logger.error(f"Excepción en {self.name}: {str(e)}")
            return {'error': str(e)}
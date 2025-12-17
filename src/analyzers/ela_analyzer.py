"""
Analizador ELA (Error Level Analysis)
Detecta manipulaciones mediante análisis de niveles de error de compresión
"""

from . base_analyzer import BaseAnalyzer
from typing import Dict
import logging
from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance
import tempfile
import os

logger = logging.getLogger('ForensicAnalyzer')

class ELAAnalyzer(BaseAnalyzer):
    """Analizador ELA propio - No requiere herramientas externas"""
    
    def __init__(self):
        # ELA no requiere comando externo, siempre está disponible
        super().__init__(name='ELA (Error Level Analysis)', command='python')
        self.enabled = True  # Siempre disponible
    
    def calculate_ela(self, image_path: str, quality: int = 90) -> Dict:
        """
        Calcula Error Level Analysis de una imagen
        
        Args: 
            image_path: Ruta a la imagen
            quality: Calidad JPEG para recomprimir (90 por defecto)
        
        Returns:
            Diccionario con resultados del análisis
        """
        try:
            # Abrir imagen original
            original = Image.open(image_path)
            
            # Convertir a RGB si es necesario
            if original. mode != 'RGB':
                original = original.convert('RGB')
            
            # Crear archivo temporal para recomprimir
            temp_fd, temp_path = tempfile. mkstemp(suffix='.jpg')
            os.close(temp_fd)
            
            try:
                # Recomprimir con calidad específica
                original.save(temp_path, 'JPEG', quality=quality)
                
                # Abrir imagen recomprimida
                compressed = Image.open(temp_path)
                
                # Calcular diferencia (ELA)
                ela_image = ImageChops.difference(original, compressed)
                
                # Amplificar diferencias para visualización
                extrema = ela_image.getextrema()
                max_diff = max([ex[1] for ex in extrema])
                
                if max_diff == 0:
                    max_diff = 1  # Evitar división por cero
                
                scale = 255.0 / max_diff
                ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)
                
                # Guardar imagen ELA en el directorio temporal
                output_dir = Path('data/temp/ela_results')
                output_dir.mkdir(parents=True, exist_ok=True)
                
                image_name = Path(image_path).stem
                ela_output = output_dir / f'ela_{image_name}.png'
                ela_image.save(ela_output)
                
                # Analizar estadísticas
                ela_array = list(ela_image.getdata())
                avg_diff = sum([sum(pixel) / 3 for pixel in ela_array]) / len(ela_array)
                
                # Clasificar nivel de sospecha
                if avg_diff < 10:
                    suspicion_level = "Bajo"
                    interpretation = "La imagen muestra diferencias mínimas en compresión.  Probablemente sin ediciones significativas."
                elif avg_diff < 25:
                    suspicion_level = "Moderado"
                    interpretation = "Se detectan algunas inconsistencias en compresión.  Posibles ediciones menores o recompresión."
                elif avg_diff < 50:
                    suspicion_level = "Alto"
                    interpretation = "Diferencias notables en compresión. Probable manipulación o edición de áreas específicas."
                else:
                    suspicion_level = "Muy Alto"
                    interpretation = "Diferencias extremas en compresión. Alta probabilidad de manipulación significativa."
                
                return {
                    'status': 'success',
                    'ela_image_path': str(ela_output),
                    'max_difference': float(max_diff),
                    'average_difference': float(avg_diff),
                    'suspicion_level': suspicion_level,
                    'interpretation': interpretation,
                    'recompression_quality': quality
                }
                
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e: 
            logger.error(f"Error en análisis ELA: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def run(self, image_path: str) -> Dict:
        """
        Ejecuta análisis ELA sobre la imagen
        
        Args: 
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con resultados del análisis
        """
        logger.info(f"Ejecutando {self.name} en:  {image_path}")
        
        try:
            # Verificar que la imagen existe
            if not Path(image_path).exists():
                return {'error': 'Image file not found'}
            
            # Ejecutar análisis ELA
            results = self.calculate_ela(image_path, quality=90)
            
            self.results = results
            logger.info(f"✅ {self.name} completado")
            
            return results
            
        except Exception as e: 
            logger.error(f"Excepción en {self.name}:  {str(e)}")
            return {'error': str(e)}
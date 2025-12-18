"""
Analizador de Calidad JPEG
Detecta múltiples compresiones y estima calidad de compresión
"""

from .base_analyzer import BaseAnalyzer
from typing import Dict, List, Tuple
import logging
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
import io

logger = logging.getLogger('ForensicAnalyzer')

class JPEGQualityAnalyzer(BaseAnalyzer):
    """Analiza la calidad de compresión JPEG"""
    
    def __init__(self):
        super().__init__(name='JPEG Quality Analysis', command='python')
        self.enabled = True
    
    def estimate_jpeg_quality(self, image_path: str) -> int:
        """
        Estima la calidad JPEG de una imagen
        
        Args:
            image_path:  Ruta a la imagen
        
        Returns:
            Calidad estimada (0-100)
        """
        try:
            with Image.open(image_path) as img:
                # Verificar si es JPEG
                if img. format != 'JPEG': 
                    return -1
                
                # Obtener tablas de cuantización si existen
                if hasattr(img, 'quantization'):
                    qtables = img.quantization
                    if qtables:
                        # Estimar calidad basada en primera tabla
                        first_table = list(qtables.values())[0] if isinstance(qtables, dict) else qtables[0]
                        avg_q = np.mean(first_table)
                        
                        # Conversión aproximada de tabla Q a calidad
                        if avg_q < 10:
                            quality = 95
                        elif avg_q < 20:
                            quality = 85
                        elif avg_q < 40:
                            quality = 75
                        elif avg_q < 60:
                            quality = 60
                        else:
                            quality = 50
                        
                        return quality
                
                # Método alternativo: comparar con recompresiones
                return self._estimate_by_comparison(image_path)
                
        except Exception as e:
            logger. error(f"Error estimando calidad JPEG: {str(e)}")
            return -1
    
    def _estimate_by_comparison(self, image_path: str) -> int:
        """
        Estima calidad comparando con diferentes niveles de compresión
        
        Args:
            image_path: Ruta a la imagen
        
        Returns:
            Calidad estimada
        """
        try:
            original = Image.open(image_path)
            original_array = np.array(original)
            
            min_diff = float('inf')
            best_quality = 75
            
            # Probar diferentes calidades
            for quality in range(50, 100, 5):
                # Recomprimir
                buffer = io.BytesIO()
                original.save(buffer, format='JPEG', quality=quality)
                buffer.seek(0)
                
                # Comparar
                recompressed = Image.open(buffer)
                recompressed_array = np.array(recompressed)
                
                # Calcular diferencia
                diff = np.mean(np.abs(original_array. astype(float) - recompressed_array. astype(float)))
                
                if diff < min_diff: 
                    min_diff = diff
                    best_quality = quality
            
            return best_quality
            
        except Exception as e:
            logger.error(f"Error en estimación por comparación: {str(e)}")
            return 75  # Valor por defecto
    
    def detect_double_compression(self, image_path: str) -> Dict:
        """
        Detecta si la imagen fue comprimida múltiples veces
        
        Args:
            image_path:  Ruta a la imagen
        
        Returns:
            Información sobre compresión múltiple
        """
        try:
            # Leer imagen
            img = cv2.imread(image_path)
            if img is None:
                return {'error': 'No se pudo leer la imagen'}
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Analizar bloques de 8x8 (tamaño estándar JPEG)
            height, width = gray.shape
            block_artifacts = []
            
            for i in range(0, height - 8, 8):
                for j in range(0, width - 8, 8):
                    block = gray[i:i+8, j:j+8]. astype(float)
                    
                    # Calcular variación dentro del bloque
                    variance = np.var(block)
                    
                    # Calcular diferencia en bordes (artefactos de bloque)
                    if i + 8 < height and j + 8 < width:
                        right_edge = np.mean(np.abs(gray[i: i+8, j+7] - gray[i: i+8, j+8]))
                        bottom_edge = np.mean(np.abs(gray[i+7, j:j+8] - gray[i+8, j: j+8]))
                        edge_artifact = (right_edge + bottom_edge) / 2
                        block_artifacts.append(edge_artifact)
            
            # Analizar artefactos
            if block_artifacts:
                mean_artifact = np.mean(block_artifacts)
                std_artifact = np.std(block_artifacts)
            else:
                mean_artifact = 0
                std_artifact = 0
            
            # Clasificar
            if mean_artifact < 2:
                double_compression = "No Detectada"
                interpretation = "No se detectan artefactos significativos de compresión múltiple.  Probablemente una sola compresión."
                suspicion_level = "Bajo"
            elif mean_artifact < 5:
                double_compression = "Posible"
                interpretation = "Se detectan algunos artefactos de bloque. Posible compresión múltiple o calidad baja."
                suspicion_level = "Moderado"
            elif mean_artifact < 10:
                double_compression = "Probable"
                interpretation = "Artefactos de bloque notables. Alta probabilidad de compresión múltiple (edición y re-guardado)."
                suspicion_level = "Alto"
            else:
                double_compression = "Muy Probable"
                interpretation = "Artefactos de bloque muy evidentes. Compresión múltiple muy probable (varias ediciones)."
                suspicion_level = "Muy Alto"
            
            # Crear visualización de bloques
            block_vis = self._visualize_blocks(gray)
            
            output_dir = Path('data/temp/jpeg_results')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            image_name = Path(image_path).stem
            output_path = output_dir / f'jpeg_{image_name}.png'
            
            cv2.imwrite(str(output_path), block_vis)
            
            return {
                'double_compression': double_compression,
                'mean_artifact_score': float(mean_artifact),
                'std_artifact_score':  float(std_artifact),
                'suspicion_level': suspicion_level,
                'interpretation': interpretation,
                'jpeg_image_path': str(output_path)
            }
            
        except Exception as e:
            logger. error(f"Error detectando doble compresión: {str(e)}")
            return {'error': str(e)}
    
    def _visualize_blocks(self, gray: np.ndarray) -> np.ndarray:
        """
        Visualiza bloques de 8x8 para mostrar artefactos JPEG
        
        Args: 
            gray: Imagen en escala de grises
        
        Returns:
            Imagen con bloques resaltados
        """
        height, width = gray.shape
        vis = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        # Dibujar grid de 8x8
        for i in range(0, height, 8):
            cv2.line(vis, (0, i), (width, i), (0, 255, 0), 1)
        
        for j in range(0, width, 8):
            cv2.line(vis, (j, 0), (j, height), (0, 255, 0), 1)
        
        return vis
    
    def analyze_jpeg(self, image_path: str) -> Dict:
        """
        Análisis completo de JPEG
        
        Args: 
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con resultados
        """
        try:
            # Verificar formato
            with Image.open(image_path) as img:
                if img. format != 'JPEG': 
                    return {
                        'status': 'not_jpeg',
                        'format': img.format,
                        'message': 'La imagen no está en formato JPEG.  Este análisis solo funciona con JPEG/JPG.'
                    }
            
            # Estimar calidad
            estimated_quality = self.estimate_jpeg_quality(image_path)
            
            # Detectar doble compresión
            compression_results = self.detect_double_compression(image_path)
            
            # Combinar resultados
            results = {
                'status': 'success',
                'estimated_quality': estimated_quality,
                **compression_results
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error en análisis JPEG:  {str(e)}")
            return {'error': str(e)}
    
    def run(self, image_path: str) -> Dict:
        """
        Ejecuta análisis JPEG sobre la imagen
        
        Args: 
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con resultados
        """
        logger.info(f"Ejecutando {self.name} en: {image_path}")
        
        try:
            if not Path(image_path).exists():
                return {'error': 'Image file not found'}
            
            results = self.analyze_jpeg(image_path)
            
            self.results = results
            logger.info(f"✅ {self.name} completado")
            
            return results
            
        except Exception as e: 
            logger.error(f"Excepción en {self.name}: {str(e)}")
            return {'error': str(e)}
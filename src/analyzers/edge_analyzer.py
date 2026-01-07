"""
Analizador de Inconsistencias en Bordes
Detecta bordes artificiales y transiciones no naturales
"""

from .base_analyzer import BaseAnalyzer
from typing import Dict, Tuple
import logging
from pathlib import Path
import numpy as np
import cv2

logger = logging.getLogger('ForensicAnalyzer')

class EdgeAnalyzer(BaseAnalyzer):
    """Analiza bordes para detectar manipulaciones"""
    
    def __init__(self):
        super().__init__(name='Edge Inconsistency', command='python')
        self.enabled = True
    
    def detect_edges_multi_scale(self, gray:  np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Detecta bordes en múltiples escalas
        
        Args:
            gray:  Imagen en escala de grises
        
        Returns:
            Tupla (bordes_finos, bordes_medios, bordes_gruesos)
        """
        # Escala fina (detalles)
        edges_fine = cv2.Canny(gray, 50, 150)
        
        # Escala media
        blurred_medium = cv2.GaussianBlur(gray, (5, 5), 0)
        edges_medium = cv2.Canny(blurred_medium, 50, 150)
        
        # Escala gruesa (estructuras grandes)
        blurred_coarse = cv2.GaussianBlur(gray, (9, 9), 0)
        edges_coarse = cv2.Canny(blurred_coarse, 50, 150)
        
        return edges_fine, edges_medium, edges_coarse
    
    def analyze_edge_strength(self, edges: np.ndarray, block_size: int = 32) -> np.ndarray:
        """
        Analiza la fuerza de bordes por bloques
        
        Args: 
            edges: Mapa de bordes
            block_size: Tamaño de bloque
        
        Returns: 
            Mapa de densidad de bordes
        """
        height, width = edges.shape
        density_map = np.zeros((height // block_size, width // block_size))
        
        for i in range(0, height - block_size, block_size):
            for j in range(0, width - block_size, block_size):
                block = edges[i:i+block_size, j:j+block_size]
                density = np.sum(block > 0) / (block_size * block_size)
                density_map[i//block_size, j//block_size] = density
        
        return density_map
    
    def detect_artificial_boundaries(self, gray: np.ndarray) -> np.ndarray:
        """
        Detecta límites artificiales (líneas rectas sospechosas)
        
        Args:
            gray: Imagen en escala de grises
        
        Returns:
            Mapa de límites artificiales
        """
        # Detectar bordes
        edges = cv2.Canny(gray, 50, 150)
        
        # Detectar líneas con transformada de Hough
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                minLineLength=30, maxLineGap=10)
        
        # Crear mapa de líneas
        line_map = np.zeros_like(gray)
        
        if lines is not None: 
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(line_map, (x1, y1), (x2, y2), 255, 2)
        
        return line_map
    
    def analyze_edge_consistency(self, edges_fine: np.ndarray, edges_medium: np.ndarray, 
                                 edges_coarse: np.ndarray) -> Tuple[float, str]:
        """
        Analiza consistencia entre escalas
        
        Args: 
            edges_fine: Bordes finos
            edges_medium:  Bordes medios
            edges_coarse: Bordes gruesos
        
        Returns: 
            Tupla (score, interpretación)
        """
        # Analizar densidad en cada escala
        density_fine = self.analyze_edge_strength(edges_fine)
        density_medium = self. analyze_edge_strength(edges_medium)
        density_coarse = self.analyze_edge_strength(edges_coarse)
        
        # Calcular varianza entre escalas
        mean_fine = np.mean(density_fine)
        mean_medium = np.mean(density_medium)
        mean_coarse = np. mean(density_coarse)
        
        std_fine = np.std(density_fine)
        std_medium = np.std(density_medium)
        std_coarse = np.std(density_coarse)
        
        # Score de inconsistencia
        cv_fine = std_fine / (mean_fine + 1e-6)
        cv_medium = std_medium / (mean_medium + 1e-6)
        cv_coarse = std_coarse / (mean_coarse + 1e-6)
        
        # Variación entre escalas
        scale_variance = np.std([cv_fine, cv_medium, cv_coarse])
        
        inconsistency_score = scale_variance
        
        return inconsistency_score
    
    def analyze_edges(self, image_path: str) -> Dict:
        """
        Análisis completo de bordes
        
        Args:
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con resultados
        """
        try:
            # Leer imagen
            img = cv2.imread(image_path)
            if img is None:
                return {'error': 'No se pudo leer la imagen'}
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detectar bordes multi-escala
            edges_fine, edges_medium, edges_coarse = self.detect_edges_multi_scale(gray)
            
            # Detectar límites artificiales
            artificial_boundaries = self.detect_artificial_boundaries(gray)
            
            # Analizar consistencia
            inconsistency_score = self.analyze_edge_consistency(edges_fine, edges_medium, edges_coarse)
            
            # Combinar bordes para visualización
            edges_combined = cv2.addWeighted(edges_fine, 0.5, edges_medium, 0.3, 0)
            edges_combined = cv2.addWeighted(edges_combined, 1.0, edges_coarse, 0.2, 0)
            
            # Colorear bordes
            edges_colored = cv2.applyColorMap(edges_combined, cv2.COLORMAP_HOT)
            
            # Overlay sobre original
            alpha = 0.6
            overlay = cv2.addWeighted(img, 1-alpha, edges_colored, alpha, 0)
            
            # Añadir límites artificiales en verde brillante
            mask = artificial_boundaries > 0
            overlay[mask] = [0, 255, 0]
            
            # Guardar visualización
            output_dir = Path('data/temp/edge_results')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            image_name = Path(image_path).stem
            output_path = output_dir / f'edges_{image_name}.png'
            
            cv2.imwrite(str(output_path), overlay)
            
            # Contar líneas artificiales
            num_artificial_lines = 0
            if artificial_boundaries is not None:
                num_artificial_lines = np.sum(artificial_boundaries > 0) // 100
            
            # Clasificar
            if inconsistency_score < 0.1 and num_artificial_lines < 10:
                suspicion_level = "Bajo"
                interpretation = "Los bordes son consistentes y naturales. No se detectan límites artificiales significativos."
            elif inconsistency_score < 0.2 and num_artificial_lines < 30:
                suspicion_level = "Moderado"
                interpretation = "Se detectan algunas inconsistencias menores en bordes. Posible compresión o edición leve."
            elif inconsistency_score < 0.3 or num_artificial_lines < 50:
                suspicion_level = "Alto"
                interpretation = "Inconsistencias notables en bordes.  Probable manipulación con copy-paste o inserción de elementos."
            else:
                suspicion_level = "Muy Alto"
                interpretation = "Bordes altamente inconsistentes y/o múltiples límites artificiales. Alta probabilidad de montaje o edición extensiva."
            
            return {
                'status': 'success',
                'edge_image_path': str(output_path),
                'inconsistency_score': float(inconsistency_score),
                'artificial_boundaries_detected': int(num_artificial_lines),
                'suspicion_level': suspicion_level,
                'interpretation': interpretation
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de bordes: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def run(self, image_path: str) -> Dict:
        """
        Ejecuta análisis de bordes
        
        Args:
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con resultados
        """
        logger.info(f"Ejecutando {self.name} en: {image_path}")
        
        try:
            if not Path(image_path).exists():
                return {'error':  'Image file not found'}
            
            results = self.analyze_edges(image_path)
            
            self.results = results
            logger.info(f"✅ {self.name} completado")
            
            return results
            
        except Exception as e:
            logger.error(f"Excepción en {self.name}: {str(e)}")
            return {'error':  str(e)}
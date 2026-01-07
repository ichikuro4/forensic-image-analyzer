"""
Analizador de Gradiente de Luminancia
Detecta inconsistencias en la dirección e intensidad de la iluminación
"""

from . base_analyzer import BaseAnalyzer
from typing import Dict, List, Tuple
import logging
from pathlib import Path
import numpy as np
import cv2
from scipy import ndimage

logger = logging.getLogger('ForensicAnalyzer')

class LuminanceAnalyzer(BaseAnalyzer):
    """Analiza gradientes de luminancia para detectar inconsistencias de iluminación"""
    
    def __init__(self):
        super().__init__(name='Luminance Gradient', command='python')
        self.enabled = True
    
    def calculate_luminance_gradient(self, image:  np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula gradientes de luminancia en X e Y
        
        Args: 
            image: Imagen en escala de grises
        
        Returns:
            Tupla (gradiente_x, gradiente_y)
        """
        # Aplicar suavizado para reducir ruido
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        
        # Calcular gradientes usando Sobel
        grad_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
        
        return grad_x, grad_y
    
    def calculate_gradient_direction(self, grad_x: np.ndarray, grad_y: np.ndarray) -> np.ndarray:
        """
        Calcula la dirección del gradiente
        
        Args:
            grad_x: Gradiente en X
            grad_y: Gradiente en Y
        
        Returns: 
            Mapa de direcciones (en radianes)
        """
        direction = np.arctan2(grad_y, grad_x)
        return direction
    
    def calculate_gradient_magnitude(self, grad_x: np.ndarray, grad_y: np.ndarray) -> np.ndarray:
        """
        Calcula la magnitud del gradiente
        
        Args: 
            grad_x: Gradiente en X
            grad_y:  Gradiente en Y
        
        Returns:
            Mapa de magnitudes
        """
        magnitude = np. sqrt(grad_x**2 + grad_y**2)
        return magnitude
    
    def analyze_direction_consistency(self, direction: np.ndarray, block_size: int = 32) -> Tuple[float, np.ndarray]:
        """
        Analiza la consistencia de dirección por bloques
        
        Args: 
            direction: Mapa de direcciones
            block_size: Tamaño de bloque
        
        Returns: 
            Tupla (score_inconsistencia, mapa_varianza)
        """
        height, width = direction.shape
        variance_map = np.zeros((height // block_size, width // block_size))
        
        for i in range(0, height - block_size, block_size):
            for j in range(0, width - block_size, block_size):
                block = direction[i:i+block_size, j:j+block_size]
                
                # Calcular varianza circular (para ángulos)
                # Convertir a vectores unitarios
                cos_vals = np.cos(block)
                sin_vals = np.sin(block)
                
                mean_cos = np.mean(cos_vals)
                mean_sin = np.mean(sin_vals)
                
                # Varianza circular
                R = np.sqrt(mean_cos**2 + mean_sin**2)
                circular_variance = 1 - R
                
                variance_map[i//block_size, j//block_size] = circular_variance
        
        # Score global de inconsistencia
        mean_variance = np.mean(variance_map)
        std_variance = np.std(variance_map)
        
        inconsistency_score = std_variance / (mean_variance + 1e-6)
        
        return inconsistency_score, variance_map
    
    def visualize_gradient_direction(self, direction: np.ndarray, magnitude: np.ndarray, 
                                     step: int = 20) -> np.ndarray:
        """
        Visualiza direcciones de gradiente con flechas
        
        Args: 
            direction: Mapa de direcciones
            magnitude: Mapa de magnitudes
            step:  Paso entre flechas
        
        Returns:
            Imagen con visualización
        """
        height, width = direction.shape
        
        # Crear imagen base
        vis = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # Dibujar flechas
        for i in range(step, height - step, step):
            for j in range(step, width - step, step):
                angle = direction[i, j]
                mag = magnitude[i, j]
                
                # Normalizar magnitud para longitud de flecha
                arrow_length = int(min(mag / np.max(magnitude) * step * 0.8, step * 0.8))
                
                if arrow_length > 2:
                    # Calcular punto final de flecha
                    end_x = int(j + arrow_length * np.cos(angle))
                    end_y = int(i + arrow_length * np.sin(angle))
                    
                    # Color basado en dirección (HSV)
                    hue = int(((angle + np.pi) / (2 * np.pi)) * 180)
                    color_hsv = np.uint8([[[hue, 255, 255]]])
                    color_bgr = cv2.cvtColor(color_hsv, cv2.COLOR_HSV2BGR)[0][0]
                    color = tuple(map(int, color_bgr))
                    
                    # Dibujar flecha
                    cv2.arrowedLine(vis, (j, i), (end_x, end_y), color, 1, tipLength=0.3)
        
        return vis
    
    def analyze_luminance(self, image_path: str) -> Dict:
        """
        Análisis completo de luminancia
        
        Args:
            image_path:  Ruta a la imagen
        
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
            
            # Calcular gradientes
            grad_x, grad_y = self.calculate_luminance_gradient(gray)
            
            # Calcular dirección y magnitud
            direction = self. calculate_gradient_direction(grad_x, grad_y)
            magnitude = self.calculate_gradient_magnitude(grad_x, grad_y)
            
            # Analizar consistencia
            inconsistency_score, variance_map = self.analyze_direction_consistency(direction)
            
            # Visualizar direcciones
            arrow_vis = self.visualize_gradient_direction(direction, magnitude, step=20)
            
            # Crear mapa de calor de varianza
            variance_normalized = cv2.normalize(variance_map, None, 0, 255, cv2.NORM_MINMAX)
            variance_normalized = variance_normalized.astype(np. uint8)
            variance_colored = cv2.applyColorMap(variance_normalized, cv2.COLORMAP_JET)
            variance_resized = cv2.resize(variance_colored, (img.shape[1], img.shape[0]), 
                                         interpolation=cv2.INTER_NEAREST)
            
            # Overlay sobre imagen original
            alpha = 0.6
            overlay = cv2.addWeighted(img, 1-alpha, variance_resized, alpha, 0)
            
            # Guardar visualizaciones
            output_dir = Path('data/temp/luminance_results')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            image_name = Path(image_path).stem
            
            # Guardar mapa de calor
            heatmap_path = output_dir / f'luminance_heatmap_{image_name}.png'
            cv2.imwrite(str(heatmap_path), overlay)
            
            # Guardar visualización de flechas
            arrows_path = output_dir / f'luminance_arrows_{image_name}.png'
            cv2.imwrite(str(arrows_path), arrow_vis)
            
            # Clasificar nivel de sospecha
            if inconsistency_score < 0.3:
                suspicion_level = "Bajo"
                interpretation = "La iluminación es consistente en toda la imagen.  No se detectan inconsistencias significativas en la dirección de la luz."
            elif inconsistency_score < 0.6:
                suspicion_level = "Moderado"
                interpretation = "Se detectan algunas variaciones en la iluminación.  Podría ser iluminación natural compleja o edición menor."
            elif inconsistency_score < 1.0:
                suspicion_level = "Alto"
                interpretation = "Inconsistencias notables en la dirección de iluminación. Probable inserción de elementos de diferentes fuentes."
            else:
                suspicion_level = "Muy Alto"
                interpretation = "Dirección de iluminación altamente inconsistente. Alta probabilidad de montaje con objetos de diferentes fotografías."
            
            return {
                'status': 'success',
                'luminance_heatmap_path': str(heatmap_path),
                'luminance_arrows_path': str(arrows_path),
                'inconsistency_score': float(inconsistency_score),
                'mean_gradient_magnitude': float(np.mean(magnitude)),
                'suspicion_level': suspicion_level,
                'interpretation': interpretation
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de luminancia: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def run(self, image_path: str) -> Dict:
        """
        Ejecuta análisis de luminancia
        
        Args:
            image_path:  Ruta a la imagen
        
        Returns:
            Diccionario con resultados
        """
        logger.info(f"Ejecutando {self.name} en:  {image_path}")
        
        try:
            if not Path(image_path).exists():
                return {'error': 'Image file not found'}
            
            results = self.analyze_luminance(image_path)
            
            self.results = results
            logger.info(f"✅ {self.name} completado")
            
            return results
            
        except Exception as e:
            logger.error(f"Excepción en {self.name}:  {str(e)}")
            return {'error': str(e)}
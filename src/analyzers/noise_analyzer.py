"""
Analizador de Ruido Digital (Noise Analysis)
Detecta inconsistencias en el patrón de ruido de la imagen
"""

from . base_analyzer import BaseAnalyzer
from typing import Dict, Tuple
import logging
from pathlib import Path
import numpy as np
import cv2
from scipy import ndimage

logger = logging.getLogger('ForensicAnalyzer')

class NoiseAnalyzer(BaseAnalyzer):
    """Analiza el ruido digital para detectar manipulaciones"""
    
    def __init__(self):
        super().__init__(name='Noise Analysis', command='python')
        self.enabled = True  # Siempre disponible
    
    def extract_noise(self, image:  np.ndarray) -> np.ndarray:
        """
        Extrae el ruido de la imagen usando filtro de mediana
        
        Args: 
            image: Imagen en escala de grises
        
        Returns:
            Mapa de ruido extraído
        """
        # Aplicar filtro de mediana para obtener versión suavizada
        denoised = cv2.medianBlur(image, 5)
        
        # El ruido es la diferencia entre original y suavizada
        noise = cv2.absdiff(image, denoised)
        
        return noise
    
    def calculate_noise_variance(self, noise:  np.ndarray, block_size: int = 32) -> np.ndarray:
        """
        Calcula la varianza del ruido en bloques
        
        Args: 
            noise: Mapa de ruido
            block_size:  Tamaño de bloque para análisis
        
        Returns: 
            Mapa de varianza del ruido
        """
        height, width = noise.shape
        variance_map = np.zeros((height // block_size, width // block_size))
        
        for i in range(0, height - block_size, block_size):
            for j in range(0, width - block_size, block_size):
                block = noise[i:i+block_size, j:j+block_size]
                variance_map[i//block_size, j//block_size] = np.var(block)
        
        return variance_map
    
    def analyze_noise_consistency(self, variance_map: np.ndarray) -> Tuple[float, str]:
        """
        Analiza la consistencia del ruido
        
        Args:
            variance_map: Mapa de varianza
        
        Returns: 
            Tupla (score, interpretación)
        """
        # Calcular estadísticas
        mean_var = np.mean(variance_map)
        std_var = np.std(variance_map)
        
        # Coeficiente de variación (indica consistencia)
        if mean_var > 0:
            cv = std_var / mean_var
        else:
            cv = 0
        
        # Clasificar
        if cv < 0.3:
            level = "Muy Consistente"
            interpretation = "El ruido es muy uniforme en toda la imagen.  No se detectan inconsistencias significativas."
        elif cv < 0.5:
            level = "Consistente"
            interpretation = "El ruido muestra variaciones normales. Compatible con imagen sin manipular."
        elif cv < 0.8:
            level = "Moderadamente Inconsistente"
            interpretation = "Se detectan algunas inconsistencias en el patrón de ruido. Posible edición menor o compresión."
        elif cv < 1.2:
            level = "Inconsistente"
            interpretation = "Inconsistencias notables en el ruido. Probable manipulación o inserción de elementos."
        else:
            level = "Muy Inconsistente"
            interpretation = "Patrón de ruido altamente inconsistente. Alta probabilidad de manipulación significativa."
        
        return cv, level, interpretation
    
    def analyze_noise(self, image_path: str) -> Dict:
        """
        Análisis completo de ruido
        
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
            
            # Extraer ruido
            noise = self.extract_noise(gray)
            
            # Calcular varianza por bloques
            variance_map = self.calculate_noise_variance(noise, block_size=32)
            
            # Analizar consistencia
            cv_score, consistency_level, interpretation = self.analyze_noise_consistency(variance_map)
            
            # Normalizar mapa de varianza para visualización
            variance_normalized = cv2.normalize(variance_map, None, 0, 255, cv2.NORM_MINMAX)
            variance_normalized = variance_normalized.astype(np.uint8)
            
            # Aplicar mapa de calor
            variance_colored = cv2.applyColorMap(variance_normalized, cv2.COLORMAP_JET)
            
            # Redimensionar al tamaño original
            variance_colored_resized = cv2.resize(variance_colored, (img.shape[1], img.shape[0]), 
                                                   interpolation=cv2.INTER_NEAREST)
            
            # Superponer sobre imagen original
            alpha = 0.5
            overlay = cv2.addWeighted(img, 1-alpha, variance_colored_resized, alpha, 0)
            
            # Guardar visualización
            output_dir = Path('data/temp/noise_results')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            image_name = Path(image_path).stem
            output_path = output_dir / f'noise_{image_name}.png'
            
            cv2.imwrite(str(output_path), overlay)
            
            # Clasificar nivel de sospecha
            if cv_score < 0.5:
                suspicion_level = "Bajo"
            elif cv_score < 0.8:
                suspicion_level = "Moderado"
            elif cv_score < 1.2:
                suspicion_level = "Alto"
            else:
                suspicion_level = "Muy Alto"
            
            return {
                'status': 'success',
                'noise_image_path': str(output_path),
                'coefficient_of_variation': float(cv_score),
                'consistency_level': consistency_level,
                'suspicion_level': suspicion_level,
                'interpretation': interpretation,
                'mean_variance': float(np.mean(variance_map)),
                'std_variance': float(np.std(variance_map)),
                'block_size': 32
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de ruido: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def run(self, image_path: str) -> Dict:
        """
        Ejecuta análisis de ruido sobre la imagen
        
        Args: 
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con resultados
        """
        logger.info(f"Ejecutando {self.name} en:  {image_path}")
        
        try:
            if not Path(image_path).exists():
                return {'error': 'Image file not found'}
            
            results = self.analyze_noise(image_path)
            
            self.results = results
            logger.info(f"✅ {self.name} completado")
            
            return results
            
        except Exception as e:
            logger.error(f"Excepción en {self.name}:  {str(e)}")
            return {'error': str(e)}
"""
Detector de Splicing (Unión de Imágenes)
Combina múltiples técnicas para detectar si la imagen está compuesta por partes de diferentes fuentes
"""

from . base_analyzer import BaseAnalyzer
from typing import Dict, Tuple, List
import logging
from pathlib import Path
import numpy as np
import cv2
from scipy import ndimage, stats

logger = logging.getLogger('ForensicAnalyzer')

class SplicingDetector(BaseAnalyzer):
    """Detecta splicing usando múltiples técnicas combinadas"""
    
    def __init__(self):
        super().__init__(name='Splicing Detection', command='python')
        self.enabled = True
    
    def extract_noise_residual(self, gray:  np.ndarray) -> np.ndarray:
        """
        Extrae residuo de ruido de la imagen
        
        Args:
            gray: Imagen en escala de grises
        
        Returns:
            Residuo de ruido
        """
        # Aplicar filtro de mediana
        denoised = cv2.medianBlur(gray, 5)
        
        # Residuo = original - denoised
        residual = cv2.absdiff(gray, denoised)
        
        return residual
    
    def analyze_noise_regions(self, residual: np.ndarray, block_size: int = 32) -> np.ndarray:
        """
        Analiza varianza de ruido por regiones
        
        Args:  
            residual: Residuo de ruido
            block_size: Tamaño de bloque
        
        Returns: 
            Mapa de varianza de ruido
        """
        height, width = residual.shape
        noise_map = np.zeros((height // block_size, width // block_size))
        
        for i in range(0, height - block_size, block_size):
            for j in range(0, width - block_size, block_size):
                block = residual[i:i+block_size, j:j+block_size]
                noise_map[i//block_size, j//block_size] = np.var(block)
        
        return noise_map
    
    def analyze_dct_coefficients(self, gray: np. ndarray, block_size: int = 32) -> np.ndarray:
        """
        Analiza coeficientes DCT por bloques
        
        Args:  
            gray: Imagen en escala de grises
            block_size: Tamaño de bloque (ahora 32x32 para consistencia)
        
        Returns:  
            Mapa de anomalías DCT
        """
        height, width = gray.shape
        dct_map = np.zeros((height // block_size, width // block_size))
        
        for i in range(0, height - block_size, block_size):
            for j in range(0, width - block_size, block_size):
                block = gray[i:i+block_size, j:j+block_size]. astype(float)
                
                # Aplicar DCT 2D
                dct_block = cv2.dct(block)
                
                # Analizar coeficientes de alta frecuencia (más sensibles a manipulación)
                # Usar la mitad superior derecha del bloque
                half = block_size // 2
                high_freq = dct_block[half: , half:]
                high_freq_energy = np.sum(np.abs(high_freq))
                
                dct_map[i//block_size, j//block_size] = high_freq_energy
        
        return dct_map
    
    def analyze_color_statistics(self, img: np.ndarray, block_size: int = 32) -> np.ndarray:
        """
        Analiza estadísticas de color por regiones
        
        Args: 
            img: Imagen BGR
            block_size: Tamaño de bloque
        
        Returns: 
            Mapa de anomalías de color
        """
        height, width = img.shape[: 2]
        color_map = np.zeros((height // block_size, width // block_size))
        
        # Convertir a LAB (mejor para análisis de color)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        
        for i in range(0, height - block_size, block_size):
            for j in range(0, width - block_size, block_size):
                block = lab[i:i+block_size, j:j+block_size]
                
                # Calcular varianza en cada canal
                var_l = np.var(block[: , :, 0])
                var_a = np.var(block[:, :, 1])
                var_b = np. var(block[:, :, 2])
                
                # Combinación de varianzas
                total_var = var_l + var_a + var_b
                color_map[i//block_size, j//block_size] = total_var
        
        return color_map
    
    def detect_boundaries(self, noise_map: np.ndarray, dct_map: np. ndarray, 
                         color_map: np.ndarray) -> np.ndarray:
        """
        Detecta límites sospechosos combinando múltiples mapas
        
        Args: 
            noise_map:  Mapa de varianza de ruido
            dct_map:  Mapa DCT
            color_map: Mapa de color
        
        Returns:
            Mapa de límites sospechosos
        """
        # Verificar que todos los mapas tienen el mismo tamaño
        if noise_map.shape != dct_map.shape or noise_map.shape != color_map. shape:
            logger.warning(f"Tamaños de mapas inconsistentes: noise={noise_map.shape}, dct={dct_map.shape}, color={color_map.shape}")
            # Redimensionar si es necesario
            target_shape = noise_map.shape
            if dct_map.shape != target_shape:
                dct_map = cv2.resize(dct_map, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_LINEAR)
            if color_map.shape != target_shape:
                color_map = cv2.resize(color_map, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_LINEAR)
        
        # Normalizar mapas
        noise_norm = cv2.normalize(noise_map, None, 0, 1, cv2.NORM_MINMAX)
        dct_norm = cv2.normalize(dct_map, None, 0, 1, cv2.NORM_MINMAX)
        color_norm = cv2.normalize(color_map, None, 0, 1, cv2.NORM_MINMAX)
        
        # Combinar mapas (ponderación)
        combined = (noise_norm * 0.4 + dct_norm * 0.3 + color_norm * 0.3)
        
        # Detectar bordes en el mapa combinado (transiciones = splicing)
        sobel_x = ndimage.sobel(combined, axis=1)
        sobel_y = ndimage.sobel(combined, axis=0)
        boundaries = np.hypot(sobel_x, sobel_y)
        
        return boundaries
    
    def calculate_splicing_score(self, boundaries:  np.ndarray, noise_map: np.ndarray, 
                                 dct_map: np. ndarray, color_map: np.ndarray) -> Tuple[float, List[float]]: 
        """
        Calcula score de splicing
        
        Args:
            boundaries: Mapa de límites
            noise_map: Mapa de ruido
            dct_map: Mapa DCT
            color_map: Mapa de color
        
        Returns:
            Tupla (score_global, [scores_individuales])
        """
        # Score de límites (más límites fuertes = más sospechoso)
        boundary_score = np.mean(boundaries) * 100
        
        # Score de inconsistencia de ruido
        noise_cv = np. std(noise_map) / (np.mean(noise_map) + 1e-6)
        noise_score = min(noise_cv * 50, 100)
        
        # Score de inconsistencia DCT
        dct_cv = np.std(dct_map) / (np.mean(dct_map) + 1e-6)
        dct_score = min(dct_cv * 50, 100)
        
        # Score de inconsistencia de color
        color_cv = np.std(color_map) / (np.mean(color_map) + 1e-6)
        color_score = min(color_cv * 50, 100)
        
        # Score global (promedio ponderado)
        global_score = (boundary_score * 0.4 + noise_score * 0.3 + 
                       dct_score * 0.2 + color_score * 0.1)
        
        return global_score, [boundary_score, noise_score, dct_score, color_score]
    
    def detect_splicing(self, image_path: str) -> Dict:
        """
        Análisis completo de splicing
        
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
            
            # Usar mismo tamaño de bloque para todos los análisis
            block_size = 32
            
            # 1. Análisis de ruido
            residual = self.extract_noise_residual(gray)
            noise_map = self.analyze_noise_regions(residual, block_size=block_size)
            
            # 2. Análisis DCT (ahora con mismo block_size)
            dct_map = self.analyze_dct_coefficients(gray, block_size=block_size)
            
            # 3. Análisis de color
            color_map = self.analyze_color_statistics(img, block_size=block_size)
            
            # 4. Detectar límites
            boundaries = self.detect_boundaries(noise_map, dct_map, color_map)
            
            # 5. Calcular scores
            global_score, individual_scores = self.calculate_splicing_score(
                boundaries, noise_map, dct_map, color_map
            )
            
            boundary_score, noise_score, dct_score, color_score = individual_scores
            
            # Crear visualización combinada
            # Redimensionar mapas al tamaño original
            h, w = img.shape[:2]
            
            noise_resized = cv2.resize(noise_map, (w, h), interpolation=cv2.INTER_NEAREST)
            noise_resized = cv2.normalize(noise_resized, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            noise_colored = cv2.applyColorMap(noise_resized, cv2.COLORMAP_JET)
            
            boundaries_resized = cv2.resize(boundaries, (w, h), interpolation=cv2.INTER_NEAREST)
            boundaries_resized = cv2.normalize(boundaries_resized, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            boundaries_colored = cv2.applyColorMap(boundaries_resized, cv2.COLORMAP_HOT)
            
            # Overlay de límites sobre imagen original
            alpha = 0.6
            overlay = cv2.addWeighted(img, 1-alpha, boundaries_colored, alpha, 0)
            
            # Guardar visualizaciones
            output_dir = Path('data/temp/splicing_results')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            image_name = Path(image_path).stem
            
            # Guardar overlay de límites (SIN ESPACIOS)
            boundaries_path = output_dir / f'splicing_boundaries_{image_name}.png'
            cv2.imwrite(str(boundaries_path), overlay)
            
            # Guardar mapa de ruido (SIN ESPACIOS)
            noise_path = output_dir / f'splicing_noise_{image_name}.png'
            cv2.imwrite(str(noise_path), noise_colored)
            
            # Clasificar
            if global_score < 20:
                suspicion_level = "Bajo"
                interpretation = "No se detectan evidencias significativas de splicing.  Los análisis de ruido, DCT y color son consistentes en toda la imagen."
            elif global_score < 40:
                suspicion_level = "Moderado"
                interpretation = "Se detectan algunas inconsistencias menores.  Podría ser variación natural, compresión o edición ligera."
            elif global_score < 60:
                suspicion_level = "Alto"
                interpretation = "Inconsistencias notables detectadas en múltiples análisis. Alta probabilidad de que la imagen contenga regiones de diferentes fuentes."
            else:
                suspicion_level = "Muy Alto"
                interpretation = "Múltiples evidencias fuertes de splicing. La imagen muy probablemente está compuesta por partes de diferentes fotografías."
            
            return {
                'status': 'success',
                'splicing_boundaries_path': str(boundaries_path),
                'splicing_noise_path': str(noise_path),
                'global_splicing_score': float(global_score),
                'boundary_detection_score': float(boundary_score),
                'noise_inconsistency_score': float(noise_score),
                'dct_inconsistency_score': float(dct_score),
                'color_inconsistency_score': float(color_score),
                'suspicion_level': suspicion_level,
                'interpretation': interpretation
            }
            
        except Exception as e:
            logger.error(f"Error en detección de splicing: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def run(self, image_path: str) -> Dict:
        """
        Ejecuta detección de splicing
        
        Args:
            image_path:  Ruta a la imagen
        
        Returns:
            Diccionario con resultados
        """
        logger.info(f"Ejecutando {self.name} en:  {image_path}")
        
        try:
            if not Path(image_path).exists():
                return {'error': 'Image file not found'}
            
            results = self.detect_splicing(image_path)
            
            self.results = results
            logger.info(f"✅ {self.name} completado")
            
            return results
            
        except Exception as e:
            logger.error(f"Excepción en {self.name}: {str(e)}")
            return {'error': str(e)}
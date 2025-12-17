"""
Analizador de Detección de Clonación
Detecta áreas duplicadas en la imagen (copy-move forgery)
"""

from . base_analyzer import BaseAnalyzer
from typing import Dict, List, Tuple
import logging
from pathlib import Path
import numpy as np
import cv2
import tempfile
import os

logger = logging.getLogger('ForensicAnalyzer')

class CloneDetectionAnalyzer(BaseAnalyzer):
    """Detector de clonación usando algoritmos de matching"""
    
    def __init__(self):
        # No requiere comando externo
        super().__init__(name='Clone Detection', command='python')
        self.enabled = True  # Siempre disponible
    
    def detect_clones(self, image_path: str, threshold: float = 0.95) -> Dict: 
        """
        Detecta áreas clonadas en la imagen usando feature matching
        
        Args: 
            image_path: Ruta a la imagen
            threshold: Umbral de similitud (0.9-0.99)
        
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
            
            # Detectar keypoints usando SIFT
            sift = cv2.SIFT_create()
            keypoints, descriptors = sift.detectAndCompute(gray, None)
            
            if descriptors is None or len(keypoints) < 10:
                return {
                    'status': 'insufficient_features',
                    'message': 'No se detectaron suficientes características para análisis',
                    'keypoints_found': 0,
                    'clones_detected': 0,
                    'suspicion_level': 'No Evaluable'
                }
            
            # Matching usando FLANN
            FLANN_INDEX_KDTREE = 1
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            search_params = dict(checks=50)
            flann = cv2.FlannBasedMatcher(index_params, search_params)
            
            matches = flann.knnMatch(descriptors, descriptors, k=2)
            
            # Filtrar buenos matches (excluyendo auto-matches)
            good_matches = []
            clone_regions = []
            
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    # Excluir el match consigo mismo y aplicar ratio test
                    if m.queryIdx != m.trainIdx and m.distance < threshold * n.distance:
                        # Verificar que los puntos están suficientemente separados
                        pt1 = keypoints[m.queryIdx].pt
                        pt2 = keypoints[m.trainIdx].pt
                        distance = np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)
                        
                        # Solo considerar si están a más de 50 píxeles
                        if distance > 50:
                            good_matches.append(m)
                            clone_regions.append((pt1, pt2, distance))
            
            # Generar imagen de visualización
            output_dir = Path('data/temp/clone_results')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            image_name = Path(image_path).stem
            output_path = output_dir / f'clone_{image_name}.png'
            
            # Dibujar matches sospechosos
            result_img = img.copy()
            
            for pt1, pt2, dist in clone_regions[: 50]:  # Limitar a 50 para no saturar
                # Dibujar línea entre regiones sospechosas
                cv2.line(result_img, 
                        (int(pt1[0]), int(pt1[1])), 
                        (int(pt2[0]), int(pt2[1])), 
                        (0, 0, 255), 2)
                # Marcar puntos
                cv2.circle(result_img, (int(pt1[0]), int(pt1[1])), 5, (0, 255, 0), -1)
                cv2.circle(result_img, (int(pt2[0]), int(pt2[1])), 5, (255, 0, 0), -1)
            
            cv2.imwrite(str(output_path), result_img)
            
            # Clasificar nivel de sospecha
            num_clones = len(good_matches)
            
            if num_clones < 5:
                suspicion_level = "Bajo"
                interpretation = "Pocas o ninguna región duplicada detectada.  La imagen no muestra signos evidentes de clonación."
            elif num_clones < 20:
                suspicion_level = "Moderado"
                interpretation = "Se detectaron algunas regiones similares.  Podría ser clonación o características naturales repetitivas."
            elif num_clones < 50:
                suspicion_level = "Alto"
                interpretation = "Múltiples regiones duplicadas detectadas. Alta probabilidad de clonación intencional."
            else:
                suspicion_level = "Muy Alto"
                interpretation = "Gran cantidad de regiones duplicadas.  Muy probable que la imagen haya sido manipulada mediante clonación."
            
            return {
                'status': 'success',
                'keypoints_found': len(keypoints),
                'total_matches': len(matches),
                'suspicious_clones': num_clones,
                'suspicion_level': suspicion_level,
                'interpretation': interpretation,
                'clone_image_path': str(output_path),
                'threshold_used': threshold
            }
            
        except Exception as e: 
            logger.error(f"Error en detección de clonación: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def run(self, image_path: str) -> Dict:
        """
        Ejecuta detección de clonación sobre la imagen
        
        Args: 
            image_path: Ruta a la imagen
        
        Returns:
            Diccionario con resultados
        """
        logger.info(f"Ejecutando {self.name} en:  {image_path}")
        
        try:
            # Verificar que la imagen existe
            if not Path(image_path).exists():
                return {'error': 'Image file not found'}
            
            # Ejecutar detección
            results = self.detect_clones(image_path, threshold=0.7)
            
            self.results = results
            logger.info(f"✅ {self.name} completado")
            
            return results
            
        except Exception as e:
            logger.error(f"Excepción en {self.name}: {str(e)}")
            return {'error': str(e)}
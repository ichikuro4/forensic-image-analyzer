# Consolidar resultados
"""
Consolidador de resultados de análisis
"""

from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger('ForensicAnalyzer')

def consolidate_results(
    analysis_results: Dict,
    integrity_data: Dict,
    acquisition_data: Dict
) -> Dict:
    """
    Consolida todos los resultados en una estructura unificada
    
    Args: 
        analysis_results: Resultados de los analizadores
        integrity_data:  Datos de integridad (hashes)
        acquisition_data:  Metadata de adquisición
    
    Returns:
        Diccionario consolidado
    """
    logger.info("Consolidando resultados...")
    
    consolidated = {
        'report_metadata': {
            'generated_at': datetime.now().isoformat(),
            'version': '0.1.0',
            'report_type': 'forensic_image_analysis'
        },
        'image_info': acquisition_data,
        'integrity':  integrity_data,
        'analysis':  analysis_results
    }
    
    logger.info("✅ Resultados consolidados")
    return consolidated
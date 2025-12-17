"""
Generador de informes forenses
"""

import json
from pathlib import Path
from typing import Dict
from datetime import datetime
import logging
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger('ForensicAnalyzer')

def format_file_size(size_bytes: int) -> str:
    """
    Formatea bytes a formato legible
    
    Args:
        size_bytes:  Tamaño en bytes
    
    Returns:
        String formateado (ej: "2.5 MB")
    """
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return "{:.2f} {}".format(size, unit)
        size /= 1024.0
    return "{:.2f} TB". format(size)

def generate_json_report(consolidated_data:  Dict, output_dir: str) -> str:
    """
    Genera informe en formato JSON
    
    Args: 
        consolidated_data: Datos consolidados
        output_dir:  Directorio de salida
    
    Returns:
        Ruta al informe generado
    """
    logger.info("Generando informe JSON...")
    
    # Crear directorio de salida
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Nombre del informe con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = out_dir / f'forensic_report_{timestamp}.json'
    
    # Escribir JSON
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Informe JSON generado:  {report_file}")
    return str(report_file)

def generate_html_report(consolidated_data: Dict, output_dir:  str) -> str:
    """
    Genera informe en formato HTML profesional
    
    Args:
        consolidated_data:  Datos consolidados
        output_dir: Directorio de salida
    
    Returns:
        Ruta al informe generado
    """
    logger.info("Generando informe HTML...")
    
    try:
        # Crear directorio de salida
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar Jinja2
        template_dir = Path(__file__).parent / 'templates'
        
        if not template_dir.exists():
            logger.error(f"Directorio de templates no encontrado: {template_dir}")
            raise FileNotFoundError(f"Templates directory not found: {template_dir}")
        
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template('report_template.html')
        
        # Preparar datos para el template
        image_info = consolidated_data.get('image_info', {})
        integrity = consolidated_data.get('integrity', {})
        analysis = consolidated_data. get('analysis', {})
        metadata = consolidated_data.get('report_metadata', {})
        
        # Convertir size_bytes a int si es necesario
        size_bytes = image_info.get('size_bytes', 0)
        if isinstance(size_bytes, str):
            size_bytes = int(size_bytes)
        
        template_data = {
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': metadata.get('version', '0.1.0'),
            'image_name':  image_info.get('filename', 'Desconocido'),
            'original_path': image_info.get('original_path', 'N/A'),
            'file_size': format_file_size(size_bytes),
            'acquisition_date': image_info.get('timestamp', 'N/A'),
            'md5_hash': integrity.get('md5', 'N/A'),
            'sha1_hash': integrity.get('sha1', 'N/A'),
            'sha256_hash': integrity.get('sha256', 'N/A'),
            'analysis_results': analysis,
            'analyzers_count': len([a for a in analysis.values() if not a.get('error')])
        }
        
        # Renderizar HTML
        html_content = template. render(**template_data)
        
        # Guardar archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = out_dir / f'forensic_report_{timestamp}. html'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ Informe HTML generado:  {report_file}")
        return str(report_file)
        
    except Exception as e: 
        logger.error(f"Error generando informe HTML: {str(e)}")
        logger.exception(e)  # Log completo del error
        raise

def generate_reports(consolidated_data: Dict, output_dir: str) -> Dict[str, str]:
    """
    Genera todos los formatos de informes
    
    Args:
        consolidated_data:  Datos consolidados
        output_dir: Directorio de salida
    
    Returns:
        Diccionario con rutas de informes generados
    """
    reports = {}
    
    # Generar JSON
    reports['json'] = generate_json_report(consolidated_data, output_dir)
    
    # Generar HTML
    try:
        reports['html'] = generate_html_report(consolidated_data, output_dir)
    except Exception as e:
        logger.error(f"No se pudo generar informe HTML: {str(e)}")
        reports['html'] = None
    
    return reports
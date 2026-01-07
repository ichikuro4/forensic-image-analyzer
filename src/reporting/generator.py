"""
Generador de informes forenses
"""

import json
import base64
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import logging
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger('ForensicAnalyzer')

def format_file_size(size_bytes: int) -> str:
    """
    Formatea bytes a formato legible
    
    Args:
        size_bytes: Tamaño en bytes
    
    Returns:
        String formateado (ej: "2.5 MB")
    """
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return "{:.2f} {}".format(size, unit)
        size /= 1024.0
    return "{:.2f} TB".format(size)

def image_to_base64(image_path: str) -> str:
    """
    Convierte una imagen a Base64 para embeber en HTML
    
    Args:
        image_path: Ruta a la imagen
    
    Returns: 
        String Base64 de la imagen
    """
    try: 
        with open(image_path, 'rb') as img_file:
            encoded = base64.b64encode(img_file.read()).decode('utf-8')
            # Detectar tipo MIME
            ext = Path(image_path).suffix.lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '. jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif':  'image/gif',
                '.bmp': 'image/bmp',
                '.tiff': 'image/tiff'
            }
            mime = mime_types.get(ext, 'image/jpeg')
            return f"data:{mime};base64,{encoded}"
    except Exception as e: 
        logger.error(f"Error convirtiendo imagen a Base64: {str(e)}")
        return ""

def analyze_exif_suspicions(exif_data: Dict) -> List[Tuple[str, str, str]]:
    """
    Analiza metadatos EXIF para detectar campos sospechosos
    
    Args: 
        exif_data: Diccionario con datos EXIF
    
    Returns:
        Lista de tuplas (campo, valor, motivo_sospecha)
    """
    suspicions = []
    
    # Campos que indican software de edición
    editing_software = [
        'Software', 'ProcessingSoftware', 'CreatorTool',
        'HistoryAction', 'HistorySoftwareAgent'
    ]
    
    for field in editing_software:
        if field in exif_data:
            value = str(exif_data[field])
            if any(editor in value. lower() for editor in [
                'photoshop', 'gimp', 'paint', 'editor', 'adobe', 
                'lightroom', 'affinity', 'pixlr', 'fotor'
            ]):
                suspicions.append((
                    field,
                    value,
                    '⚠️ Software de edición detectado'
                ))
    
    # Verificar inconsistencias de fecha
    date_fields = {}
    for field in ['CreateDate', 'ModifyDate', 'DateTimeOriginal', 'FileModifyDate']:
        if field in exif_data:
            date_fields[field] = exif_data[field]
    
    if len(date_fields) > 1:
        dates = list(date_fields.values())
        if len(set(dates)) > 1:  # Fechas diferentes
            suspicions.append((
                'Fechas',
                ', '.join([f"{k}:  {v}" for k, v in date_fields.items()]),
                '⚠️ Inconsistencia en fechas de creación/modificación'
            ))
    
    # GPS sin fecha
    has_gps = any(k. startswith('GPS') for k in exif_data. keys())
    has_date = 'DateTimeOriginal' in exif_data or 'CreateDate' in exif_data
    
    if has_gps and not has_date:
        suspicions.append((
            'GPS sin fecha',
            'Coordenadas GPS presentes',
            '⚠️ Datos GPS sin fecha de captura (poco común)'
        ))
    
    # Thumbnail diferente
    if 'ThumbnailImage' in exif_data and 'Warning' not in str(exif_data. get('ThumbnailImage', '')):
        suspicions.append((
            'Thumbnail',
            'Presente',
            'ℹ️ Verificar consistencia con imagen principal'
        ))
    
    # Falta de metadatos esperados
    expected_fields = ['Make', 'Model', 'DateTimeOriginal']
    missing = [f for f in expected_fields if f not in exif_data]
    
    if len(missing) == len(expected_fields):
        suspicions.append((
            'Metadatos básicos',
            'Ausentes',
            '⚠️ Falta de metadatos de cámara (posible generación digital)'
        ))
    
    return suspicions

def generate_json_report(consolidated_data: Dict, output_dir: str) -> str:
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

def generate_html_report(consolidated_data: Dict, output_dir: str) -> str:
    """
    Genera informe en formato HTML profesional
    
    Args: 
        consolidated_data: Datos consolidados
        output_dir:  Directorio de salida
    
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
        analysis = consolidated_data.get('analysis', {})
        metadata = consolidated_data.get('report_metadata', {})
        
        # Convertir size_bytes a int si es necesario
        size_bytes = image_info.get('size_bytes', 0)
        if isinstance(size_bytes, str):
            size_bytes = int(size_bytes)
        
        # Convertir imagen a Base64
        original_path = image_info.get('original_path', '')
        acquired_path = image_info.get('acquired_path', '')
        image_base64 = ''
        
        # Intentar con el archivo adquirido primero, luego el original
        if acquired_path and Path(acquired_path).exists():
            image_base64 = image_to_base64(acquired_path)
        elif original_path and Path(original_path).exists():
            image_base64 = image_to_base64(original_path)
        
        # Analizar sospechas en EXIF
        exif_data = analysis.get('Exiftool', {})
        suspicions = []
        if exif_data and not exif_data.get('error'):
            suspicions = analyze_exif_suspicions(exif_data)
        
        template_data = {
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': metadata.get('version', '0.1. 0'),
            'image_name': image_info.get('filename', 'Desconocido'),
            'original_path': original_path,
            'file_size': format_file_size(size_bytes),
            'acquisition_date': image_info.get('timestamp', 'N/A'),
            'md5_hash': integrity.get('md5', 'N/A'),
            'sha1_hash': integrity.get('sha1', 'N/A'),
            'sha256_hash':  integrity.get('sha256', 'N/A'),
            'analysis_results': analysis,
            'analyzers_count': len([a for a in analysis.values() if not a.get('error')]),
            'image_base64': image_base64,
            'exif_suspicions': suspicions,
            # Añadir imagen ELA si existe
            'ela_image_base64': ''
        }
                # Verificar si hay resultados ELA y convertir imagen
        ela_results = analysis.get('ELA (Error Level Analysis)', {})
        if ela_results and ela_results.get('ela_image_path'):
            ela_path = ela_results['ela_image_path']
            if Path(ela_path).exists():
                template_data['ela_image_base64'] = image_to_base64(ela_path)
        
        # Verificar si hay resultados Clone Detection y convertir imagen
        clone_results = analysis. get('Clone Detection', {})
        template_data['clone_image_base64'] = ''
        if clone_results and clone_results.get('clone_image_path'):
            clone_path = clone_results['clone_image_path']
            if Path(clone_path).exists():
                template_data['clone_image_base64'] = image_to_base64(clone_path)
        
        # Verificar si hay resultados Noise Analysis y convertir imagen ← NUEVO
        noise_results = analysis.get('Noise Analysis', {})
        template_data['noise_image_base64'] = ''
        if noise_results and noise_results.get('noise_image_path'):
            noise_path = noise_results['noise_image_path']
            if Path(noise_path).exists():
                template_data['noise_image_base64'] = image_to_base64(noise_path)
        
                # Verificar si hay resultados JPEG Quality y convertir imagen
        jpeg_results = analysis.get('JPEG Quality Analysis', {})
        template_data['jpeg_image_base64'] = ''
        if jpeg_results and jpeg_results.get('jpeg_image_path'):
            jpeg_path = jpeg_results['jpeg_image_path']
            if Path(jpeg_path).exists():
                template_data['jpeg_image_base64'] = image_to_base64(jpeg_path)
        
        # Verificar si hay resultados Luminance Gradient ← NUEVO
        luminance_results = analysis.get('Luminance Gradient', {})
        template_data['luminance_heatmap_base64'] = ''
        template_data['luminance_arrows_base64'] = ''
        if luminance_results and luminance_results.get('luminance_heatmap_path'):
            heatmap_path = luminance_results['luminance_heatmap_path']
            if Path(heatmap_path).exists():
                template_data['luminance_heatmap_base64'] = image_to_base64(heatmap_path)
        if luminance_results and luminance_results.get('luminance_arrows_path'):
            arrows_path = luminance_results['luminance_arrows_path']
            if Path(arrows_path).exists():
                template_data['luminance_arrows_base64'] = image_to_base64(arrows_path)
        
    # Verificar si hay resultados Edge Inconsistency
        edge_results = analysis.get('Edge Inconsistency', {})
        template_data['edge_image_base64'] = ''
        if edge_results and edge_results.get('edge_image_path'):
            edge_path = edge_results['edge_image_path']
            if Path(edge_path).exists():
                template_data['edge_image_base64'] = image_to_base64(edge_path)
        
    # Verificar si hay resultados Splicing Detection ← NUEVO
        splicing_results = analysis.get('Splicing Detection', {})
        template_data['splicing_boundaries_base64'] = ''
        template_data['splicing_noise_base64'] = ''
        if splicing_results and splicing_results.get('splicing_boundaries_path'):
            boundaries_path = splicing_results['splicing_boundaries_path']
            if Path(boundaries_path).exists():
                template_data['splicing_boundaries_base64'] = image_to_base64(boundaries_path)
        if splicing_results and splicing_results.get('splicing_noise_path'):
            noise_path = splicing_results['splicing_noise_path']
            if Path(noise_path).exists():
                template_data['splicing_noise_base64'] = image_to_base64(noise_path)

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
        logger.exception(e)
        raise

def generate_reports(consolidated_data: Dict, output_dir: str) -> Dict[str, str]:
    """
    Genera todos los formatos de informes
    
    Args: 
        consolidated_data: Datos consolidados
        output_dir:  Directorio de salida
    
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
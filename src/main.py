# Punto de entrada principal
#!/usr/bin/env python3
"""
Forensic Image Analyzer - Main Entry Point
Autor: ichikuro4
"""

import argparse
import sys
from pathlib import Path

# Añadir el directorio src al path
sys. path.insert(0, str(Path(__file__).parent))

from core.logger import setup_logger
from core.integrity import verify_integrity
from core.acquisition import acquire_image
from orchestrator.pipeline import ForensicPipeline
from reporting.consolidator import consolidate_results
from reporting.generator import generate_json_report

def main():
    """Punto de entrada principal del programa"""
    
    # Configurar argumentos CLI
    parser = argparse.ArgumentParser(
        description="Sistema automatizado de análisis forense de imágenes"
    )
    parser.add_argument(
        '--image',
        type=str,
        help='Ruta a la imagen a analizar'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/output',
        help='Directorio de salida para informes'
    )
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Iniciar interfaz gráfica'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Modo verbose (DEBUG)'
    )
    
    args = parser.parse_args()
    
    # Configurar logger
    log_level = 'DEBUG' if args.verbose else 'INFO'
    logger = setup_logger(log_level)
    
    # Banner
    logger.info("=" * 50)
    logger.info("🔍 Forensic Image Analyzer v0.1.0")
    logger.info("=" * 50)
    
    # Modo GUI
    if args.gui:
        logger.info("Iniciando modo GUI...")
        logger.warning("GUI no implementada aún - Próximamente")
        return
    
    # Modo CLI
    if not args.image:
        logger. error("Debe especificar una imagen con --image")
        parser.print_help()
        sys.exit(1)
    
    logger.info(f"Imagen objetivo: {args.image}")
    logger.info(f"Directorio de salida: {args. output}")
    
    try:
        # 1. Verificar integridad
        logger.info("\n[1/4] Verificando integridad...")
        integrity_data = verify_integrity(args.image)
        
        # 2. Adquirir imagen
        logger.info("\n[2/4] Adquiriendo imagen...")
        acquisition_data = acquire_image(args.image, 'data/temp')
        
        # 3. Ejecutar pipeline de análisis
        logger.info("\n[3/4] Ejecutando análisis forense...")
        pipeline = ForensicPipeline()
        analysis_results = pipeline.execute_all(acquisition_data['acquired_path'])
        
        # 4. Generar informe
        logger.info("\n[4/4] Generando informes...")
        consolidated = consolidate_results(analysis_results, integrity_data, acquisition_data)
        
        # Importar la nueva función
        from reporting.generator import generate_reports
        
        # Generar todos los formatos
        reports = generate_reports(consolidated, args.output)
        
        logger.info("=" * 50)
        logger.info(f"✅ Análisis completado exitosamente")
        logger.info(f"📄 Informe JSON: {reports['json']}")
        logger.info(f"🌐 Informe HTML: {reports['html']}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Error durante el análisis:  {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
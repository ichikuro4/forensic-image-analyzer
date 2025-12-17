# 🔍 Forensic Image Analyzer

Sistema automatizado para análisis forense de imágenes digitales con pipeline completo de adquisición, análisis y generación de informes.

## 📋 Descripción

Herramienta profesional para análisis forense de imágenes digitales que automatiza el proceso completo desde la adquisición hasta la generación de informes. El sistema implementa cadena de custodia, verificación de integridad, análisis mediante múltiples técnicas forenses y consolidación de resultados en informes profesionales HTML/JSON.

## ✨ Características Implementadas

- 🔐 **Verificación de integridad**: Hashing SHA-256, MD5 y SHA-1 de archivos
- 📥 **Adquisición segura**: Copia con timestamp y cadena de custodia
- 🔍 **Análisis de metadatos**: Extracción completa con Exiftool
- 🖼️ **Análisis ELA**: Detección de manipulación mediante Error Level Analysis
- 🔬 **Detección de clonación**: Identificación de regiones duplicadas
- 📊 **Informes consolidados**: Generación automática en JSON y HTML
- 📝 **Logging profesional**: Sistema de logs con colores y niveles
- 🎨 **Visualizaciones**: Mapas de calor y gráficos interactivos con Plotly
- ⚙️ **Configuración flexible**: Archivos YAML para herramientas y sistema

## 🛠️ Módulos Implementados

| Módulo | Estado | Descripción |
|--------|--------|-------------|
| **core/integrity** | ✅ | Cálculo y verificación de hashes múltiples |
| **core/acquisition** | ✅ | Adquisición segura con metadata de custodia |
| **core/logger** | ✅ | Sistema de logging con ColorLog |
| **analyzers/exiftool** | ✅ | Extracción de metadatos EXIF/XMP/IPTC |
| **analyzers/ela_analyzer** | ✅ | Error Level Analysis para detectar manipulación |
| **analyzers/clone_detection** | ✅ | Detección de regiones clonadas/duplicadas |
| **orchestrator/pipeline** | ✅ | Orquestación automática de analizadores |
| **reporting/consolidator** | ✅ | Consolidación de resultados |
| **reporting/generator** | ✅ | Generación de informes HTML/JSON |
| **gui/main_window** | 🚧 | Interfaz gráfica (en desarrollo) |

## 📦 Requisitos del Sistema

- **Sistema Base**: Linux (Kali Linux recomendado)
- **Python**: 3.8 o superior
- **RAM**: Mínimo 4GB (8GB recomendado)
- **Dependencias externas**: 
  - `exiftool` (instalable via apt/brew)

## 📋 Dependencias Python

```
pyyaml>=6.0          # Configuración YAML
colorlog>=6.7.0      # Logging con colores
Pillow>=10.0.0       # Procesamiento de imágenes
jinja2>=3.1.0        # Generación de templates HTML
plotly>=5.18.0       # Visualizaciones interactivas
numpy>=1.24.0        # Operaciones numéricas
opencv-python>=4.8.0 # Análisis de imágenes
scipy>=1.11.0        # Procesamiento científico
```

## 🚀 Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/ichikuro4/forensic-image-analyzer.git
cd forensic-image-analyzer

# 2. Instalar exiftool (Debian/Ubuntu/Kali)
sudo apt update && sudo apt install -y exiftool

# 3. Ejecutar script de configuración
chmod +x setup.sh
./setup.sh

# 4. Verificar instalación
python src/main.py --help
```

## 💻 Uso

### Modo CLI (Análisis completo)
```bash
# Análisis básico
python src/main.py --image /path/to/imagen.jpg

# Análisis con directorio de salida personalizado
python src/main.py --image foto.jpg --output ./resultados

# Modo verbose (debug)
python src/main.py --image foto.png --verbose
```

### Modo GUI
```bash
python src/main.py --gui  # En desarrollo
```

### Ejemplos de salida

El sistema genera dos tipos de informes:

1. **JSON** (`report_TIMESTAMP.json`): Datos estructurados para procesamiento
2. **HTML** (`report_TIMESTAMP.html`): Informe visual interactivo con:
   - Metadata de la imagen
   - Hashes de integridad
   - Metadatos EXIF completos
   - Mapa de calor ELA
   - Detección de clonación
   - Estadísticas del análisis

## 📁 Estructura del Proyecto

```
forensic-image-analyzer/
├── config/                      # Configuración del sistema
│   ├── settings.yaml           # Configuración general
│   └── tools.yaml              # Configuración de herramientas
│
├── src/
│   ├── core/                   # Funcionalidades principales
│   │   ├── integrity.py        # ✅ Verificación de hashes
│   │   ├── acquisition.py      # ✅ Adquisición segura
│   │   └── logger.py           # ✅ Sistema de logging
│   │
│   ├── analyzers/              # Analizadores forenses
│   │   ├── base_analyzer.py    # ✅ Clase base abstracta
│   │   ├── exiftool.py         # ✅ Extractor de metadatos
│   │   ├── ela_analyzer.py     # ✅ Error Level Analysis
│   │   ├── clone_detection.py  # ✅ Detección de clonación
│   │   ├── ghiro.py            # 🚧 Pendiente
│   │   ├── sherloq.py          # 🚧 Pendiente
│   │   ├── forensically.py     # 🚧 Pendiente
│   │   └── autopsy.py          # 🚧 Pendiente
│   │
│   ├── orchestrator/           # Orquestación del pipeline
│   │   └── pipeline.py         # ✅ Coordinador de análisis
│   │
│   ├── reporting/              # Generación de informes
│   │   ├── consolidator.py     # ✅ Consolidación de datos
│   │   ├── generator.py        # ✅ Generador HTML/JSON
│   │   ├── templates/          # Templates Jinja2
│   │   │   └── report_template.html
│   │   └── static/             # Recursos estáticos
│   │
│   ├── gui/                    # Interfaz gráfica
│   │   └── main_window.py      # 🚧 En desarrollo
│   │
│   └── main.py                 # ✅ Punto de entrada principal
│
├── data/                        # Datos del sistema
│   ├── input/                  # Imágenes de entrada
│   ├── output/                 # Informes generados
│   └── temp/                   # Archivos temporales
│
├── logs/                        # Logs del sistema
│
├── requirements.txt             # Dependencias Python
├── setup.sh                     # Script de instalación
└── README.md                    # Documentación
```

## 🔧 Arquitectura

### Pipeline de Análisis

```
Imagen → [1] Verificación → [2] Adquisición → [3] Análisis → [4] Reporte
         Integridad        Segura            Forense       Consolidado
```

**Fase 1: Verificación de Integridad**
- Cálculo de hashes SHA-256, MD5, SHA-1
- Validación de existencia y acceso

**Fase 2: Adquisición Segura**
- Copia con timestamp
- Preservación de metadatos del sistema
- Registro de cadena de custodia

**Fase 3: Análisis Forense**
- Ejecución paralela/secuencial de analizadores
- Extracción de metadatos (Exiftool)
- Detección de manipulación (ELA)
- Detección de clonación (OpenCV)

**Fase 4: Generación de Informes**
- Consolidación de resultados
- Generación HTML interactivo
- Exportación JSON estructurado

### Analizadores Disponibles

| Analizador | Estado | Técnica | Output |
|-----------|--------|---------|--------|
| **Exiftool** | ✅ Activo | Metadatos EXIF/IPTC/XMP | JSON estructurado |
| **ELA Analyzer** | ✅ Activo | Error Level Analysis | Mapa de calor, métricas |
| **Clone Detection** | ✅ Activo | Detección de duplicados | Regiones clonadas |
| **Sherloq** | 🔜 Planificado | Análisis multitécnica | Varios |
| **Ghiro** | 🔜 Planificado | Análisis automatizado | JSON |
| **Forensically** | 🔜 Planificado | ELA + Clonación web | Visualizaciones |
| **Autopsy** | 🔜 Planificado | Análisis profundo | Base de datos |

## 🗺️ Roadmap de Desarrollo

### ✅ Fase 1: Fundamentos (Completado)
- [x] Estructura base del proyecto
- [x] Sistema de logging profesional
- [x] Configuración YAML
- [x] Módulo de verificación de integridad (hashing)
- [x] Módulo de adquisición segura con cadena de custodia
- [x] Clase base para analizadores (BaseAnalyzer)

### ✅ Fase 2: Analizadores Core (Completado)
- [x] Wrapper de Exiftool (metadatos)
- [x] ELA Analyzer (Error Level Analysis)
- [x] Clone Detection (detección de regiones duplicadas)
- [x] Orquestador de pipeline
- [x] Consolidador de resultados
- [x] Generador de informes JSON
- [x] Generador de informes HTML con Jinja2

### 🚧 Fase 3: Expansión (En Desarrollo)
- [ ] Integración de Sherloq
- [ ] Integración de Ghiro
- [ ] Mejoras en visualizaciones
- [ ] Interfaz gráfica (GUI) completa
- [ ] Tests unitarios
- [ ] Documentación de API

### 🔜 Fase 4: Optimización (Planificado)
- [ ] Ejecución paralela de analizadores
- [ ] Caché de resultados
- [ ] Análisis batch de múltiples imágenes
- [ ] Exportación a PDF
- [ ] Base de datos de resultados históricos
- [ ] API REST para integración

### 🔜 Fase 5: Producción (Futuro)
- [ ] Optimización para LiveUSB
- [ ] Modo offline completo
- [ ] Firma digital de informes
- [ ] Sistema de plugins
- [ ] Documentación forense legal
- [ ] Certificaciones y compliance

## 📊 Estado Actual del Proyecto

- **Versión**: 0.1.0 (Alpha)
- **Completado**: ~60%
- **Analizadores activos**: 3/7
- **Módulos core**: 100%
- **Sistema de informes**: 100%
- **GUI**: 10%

## 🧪 Testing

```bash
# Ejecutar análisis de prueba con imagen de ejemplo
python src/main.py --image data/input/test_image.jpg --verbose

# Verificar logs
tail -f logs/forensic_analyzer.log
```

## 📚 Documentación Adicional

### Configuración Personalizada

**config/settings.yaml** - Configuración general:
```yaml
system:
  log_level: INFO          # DEBUG, INFO, WARNING, ERROR
  temp_dir: data/temp
  
acquisition:
  preserve_metadata: true
  chain_of_custody: true
  
analysis:
  supported_formats:       # Formatos soportados
    - jpg
    - jpeg
    - png
    - bmp
    - tiff
    - gif
  parallel_execution: false  # Experimental
```

**config/tools.yaml** - Activar/desactivar herramientas:
```yaml
tools:
  exiftool:
    enabled: true
  ela_analyzer:
    enabled: true
  clone_detection:
    enabled: true
```

### Formatos de Salida

**Informe JSON** (`report_YYYYMMDD_HHMMSS.json`):
```json
{
  "report_metadata": {
    "generated_at": "2024-12-17T14:20:00",
    "version": "0.1.0"
  },
  "image_info": { ... },
  "integrity": {
    "sha256": "...",
    "md5": "...",
    "sha1": "..."
  },
  "analysis": {
    "exiftool": { ... },
    "ela_analysis": { ... },
    "clone_detection": { ... }
  }
}
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 🐛 Reporte de Bugs

Si encuentras un bug, por favor abre un issue con:
- Descripción del problema
- Pasos para reproducirlo
- Logs relevantes (en `logs/forensic_analyzer.log`)
- Sistema operativo y versión de Python

## 📝 Notas Técnicas

### Limitaciones Conocidas
- ELA Analyzer requiere imágenes JPEG para mejores resultados
- Clone Detection puede ser lento con imágenes grandes (>10MP)
- GUI aún no implementada completamente

### Rendimiento
- Imagen 5MP: ~5-10 segundos
- Imagen 20MP: ~20-30 segundos
- Depende de: CPU, I/O del disco, número de analizadores activos

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles

## 👤 Autor

**ichikuro4**
- GitHub: [@ichikuro4](https://github.com/ichikuro4)

## 🙏 Agradecimientos

- **Exiftool** por Phil Harvey
- **OpenCV** team por las herramientas de visión computacional
- Comunidad forense digital por las metodologías

## 📞 Contacto y Soporte

Para preguntas, sugerencias o soporte:
- Abrir un issue en GitHub
- Revisar la documentación en el repositorio

---

## 🔍 Quick Start

```bash
# Instalación rápida
git clone https://github.com/ichikuro4/forensic-image-analyzer.git
cd forensic-image-analyzer
sudo apt install -y exiftool
./setup.sh

# Primer análisis
python src/main.py --image tu_imagen.jpg

# Ver resultados
ls data/output/
```

---

⚠️ **Nota Legal**: Esta herramienta está diseñada para análisis forense legítimo. El uso de esta herramienta debe cumplir con las leyes locales y tener la autorización apropiada.

🚀 **Estado**: Proyecto en desarrollo activo. Versión Alpha 0.1.0

⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub! 
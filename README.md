# 🔍 Forensic Image Analyzer

Sistema automatizado en LiveUSB para estandarizar el análisis forense de imágenes digitales.

## 📋 Descripción

Herramienta completa y optimizada para LiveUSB que estandariza el análisis forense de imágenes digitales. El sistema orquesta múltiples herramientas forenses (Ghiro, Sherloq, Forensically, Exiftool y Autopsy) y genera un informe consolidado profesional.

## ✨ Características Principales

- 🔐 **Verificación de integridad** con hashing SHA256
- 📥 **Adquisición segura** de imágenes con cadena de custodia
- 🔧 **Orquestación automática** de 5 herramientas forenses sin GUI
- 📊 **Informes consolidados** en formato JSON/HTML
- 📝 **Logging exhaustivo** para auditoría forense
- 💾 **Optimizado para LiveUSB** (ligero, portable)
- 🖥️ **GUI intuitiva** con Python

## 🛠️ Herramientas Integradas

| Herramienta | Propósito |
|------------|-----------|
| **Exiftool** | Extracción de metadatos EXIF |
| **Ghiro** | Análisis automatizado de imágenes |
| **Sherloq** | Detección de manipulación |
| **Forensically** | Análisis ELA y clonación |
| **Autopsy** | Análisis forense profundo |

## 📦 Requisitos del Sistema

- **Sistema Base**:  Kali Linux (LiveUSB)
- **Python**:  3.12. 3
- **RAM**:  Mínimo 4GB
- **Espacio**: ~8GB para LiveUSB optimizado

## 🚀 Instalación

```bash
# Clonar repositorio
git clone https://github.com/ichikuro4/forensic-image-analyzer.git
cd forensic-image-analyzer

# Ejecutar script de configuración
chmod +x setup.sh
./setup.sh
```

## 💻 Uso

### Modo CLI
```bash
python src/main.py --image /path/to/image.jpg --output /path/to/report
```

### Modo GUI
```bash
python src/main.py --gui
```

## 📁 Estructura del Proyecto

```
forensic-image-analyzer/
├── config/          # Configuración de herramientas y sistema
├── src/
│   ├── core/        # Funciones principales (integrity, logging, acquisition)
│   ├── analyzers/   # Wrappers de herramientas forenses
│   ├── orchestrator/# Orquestación del pipeline de análisis
│   ├── reporting/   # Generación de informes consolidados
│   └── gui/         # Interfaz gráfica
├── data/            # Datos de entrada/salida
└── logs/            # Logs del sistema
```

## 🗺️ Roadmap

- [x] Estructura base del proyecto
- [ ] Módulo de verificación de integridad
- [ ] Módulo de adquisición segura
- [ ] Wrappers de herramientas forenses
- [ ] Orquestador central
- [ ] Generador de informes
- [ ] Interfaz gráfica (GUI)
- [ ] Optimización para LiveUSB
- [ ] Documentación completa

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles

## 👤 Autor

**ichikuro4**

---

⚠️ **Nota**:  Este proyecto está en fase de desarrollo activo. 
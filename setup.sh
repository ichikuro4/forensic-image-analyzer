#!/bin/bash

echo "🔍 Forensic Image Analyzer - Setup"
echo "===================================="

# Verificar Python
echo "Verificando Python..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Python encontrado: $PYTHON_VERSION"

# Crear directorios necesarios
echo "Creando directorios..."
mkdir -p data/input data/output data/temp logs

# Instalar dependencias - Intentar diferentes métodos
echo "Instalando dependencias..."

if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
elif command -v pip &> /dev/null; then
    pip install -r requirements. txt
else
    python -m pip install -r requirements. txt
fi

# Verificar herramientas forenses
echo ""
echo "Verificando herramientas forenses..."
command -v exiftool >/dev/null 2>&1 && echo "✅ Exiftool encontrado" || echo "❌ Exiftool no encontrado"

echo ""
echo "✅ Setup completado!"
echo ""
echo "Prueba el sistema con:"
echo "  python src/main.py --help"
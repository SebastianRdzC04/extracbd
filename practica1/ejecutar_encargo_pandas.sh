#!/usr/bin/env bash
# ==============================================================================
# Script de Ejecución Estética - Práctica 1: Ganancias por Autor con Pandas
# Base de Datos: pubs | Servicio Docker: db-practica1 (Puerto 3307)
# Regla: Máximo 2 JOINs en SQL (Extracción atómica 0 JOINs + Álgebra en Pandas)
# ==============================================================================

set -e

# Determinar directorio raíz del proyecto
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$DIR/../docker-compose.yml" ]; then
    ROOT_DIR="$(cd "$DIR/.." && pwd)"
else
    ROOT_DIR="$DIR"
fi

cd "$ROOT_DIR"

echo "================================================================================="
echo "  🐼 PRÁCTICA 1: ANÁLISIS FORENSE DE GANANCIAS POR AUTOR CON PYTHON & PANDAS"
echo "  🗄️  Base de Datos: pubs (Puerto 3307) | 📓 Jupyter Notebooks & Pandas"
echo "================================================================================="

# 1. Asegurar que el contenedor de Docker esté activo
if command -v docker &>/dev/null; then
    if ! docker ps --format '{{.Names}}' | grep -q "db_practica1"; then
        echo "🚀 Iniciando contenedor db_practica1 (MySQL 8.0)..."
        docker compose up -d db-practica1
        sleep 2
    fi
fi

# 2. Localizar intérprete de Python en el entorno virtual
PYTHON_BIN="python3"
if [ -f "$ROOT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
fi

# 3. Ejecutar la suite de auditoría técnica en terminal
"$PYTHON_BIN" "$ROOT_DIR/practica1/scripts/test_encargo1_pandas.py"

echo ""
echo "📓 El Jupyter Notebook pre-renderizado está disponible en:"
echo "   👉 practica1/notebooks/encargo1_ganancias_por_autor.ipynb"
echo "   👉 analisis_pandas/notebooks/practica1_encargo1_ganancias_por_autor.ipynb"
echo "💡 Para abrirlo interactivamente en Jupyter Lab, ejecute:"
echo "   make notebook-p1"
echo "================================================================================="

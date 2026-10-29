#!/usr/bin/env bash
# ==============================================================================
# Script de Ejecución del Jupyter Notebook - Práctica 1: Ganancias por Autor
# Ejecuta el notebook de forma headless y opcionalmente genera un reporte HTML
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$DIR/../docker-compose.yml" ]; then
    ROOT_DIR="$(cd "$DIR/.." && pwd)"
else
    ROOT_DIR="$DIR"
fi

cd "$ROOT_DIR"

NOTEBOOK="practica1/encargo1_pandas.ipynb"
SERVICE="db-practica1"
PORT="${PRACTICA1_DB_PORT:-3307}"

# 1. Verificar servicio Docker
if command -v docker &>/dev/null; then
    if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${SERVICE}$"; then
        echo "🐳 Iniciando servicio Docker $SERVICE..."
        docker compose up -d "$SERVICE" 2>/dev/null || docker-compose up -d "$SERVICE"
        sleep 2
    fi
fi

# 2. Configurar variables de Jupyter y Python
export JUPYTER_CONFIG_DIR="/tmp/jupyter"
export JUPYTER_DATA_DIR="/tmp/jupyter_data"
export JUPYTER_RUNTIME_DIR="/tmp/jupyter_runtime"
export IPYTHONDIR="/tmp/ipython"
export PRACTICA1_DB_PORT="$PORT"
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH}"

NBCONVERT_BIN="$ROOT_DIR/.venv/bin/jupyter-nbconvert"
if [ ! -f "$NBCONVERT_BIN" ]; then
    NBCONVERT_BIN="jupyter-nbconvert"
fi

echo "🚀 Ejecutando celdas del Notebook: $NOTEBOOK..."
"$NBCONVERT_BIN" --to notebook --execute --inplace "$NOTEBOOK"

echo "📑 Generando reporte estático HTML: practica1/encargo1_pandas.html..."
"$NBCONVERT_BIN" --to html "$NOTEBOOK" --output "encargo1_pandas.html"

echo "✅ Notebook y Reporte HTML ejecutados y certificados exitosamente."

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

# 1. Credenciales: .env si existe, si no los valores por defecto del proyecto
if [ -f "$ROOT_DIR/.env" ]; then
    set -a
    # shellcheck disable=SC1091
    . "$ROOT_DIR/.env"
    set +a
fi
export PRACTICA1_DB_NAME="${PRACTICA1_DB_NAME:-pubs}"
export PRACTICA1_DB_ROOT_PASSWORD="${PRACTICA1_DB_ROOT_PASSWORD:-rootpassword}"

# 2. Verificar servicio Docker
if command -v docker &>/dev/null; then
    if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${SERVICE}$"; then
        echo "🐳 Iniciando servicio Docker $SERVICE..."
        docker compose up -d "$SERVICE" 2>/dev/null || docker-compose up -d "$SERVICE"
    fi
    # 3. Esperar a que MySQL esté listo. Con volumen nuevo el entrypoint
    #    inicializa el esquema en un servidor TEMPORAL que no escucha en TCP:
    #    sin esta espera el notebook falla con "Lost connection during query".
    #    Ver scripts/esperar_mysql.sh para el detalle.
    # shellcheck source=../scripts/esperar_mysql.sh
    . "$ROOT_DIR/scripts/esperar_mysql.sh"
    if ! esperar_mysql "$SERVICE" db_practica1 "$PRACTICA1_DB_ROOT_PASSWORD"; then
        exit 1
    fi
fi

# 4. Configurar variables de Jupyter y Python
export JUPYTER_CONFIG_DIR="/tmp/jupyter"
export JUPYTER_DATA_DIR="/tmp/jupyter_data"
export JUPYTER_RUNTIME_DIR="/tmp/jupyter_runtime"
export IPYTHONDIR="/tmp/ipython"
export PRACTICA1_DB_PORT="$PORT"
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH}"
# El notebook se conecta como root: necesita leer todas las tablas del esquema.
# OJO: se exporta DESPUÉS del arranque de Docker a propósito.
# PRACTICA1_DB_USER alimenta MYSQL_USER en docker-compose.yml y el entrypoint
# de MySQL rechaza MYSQL_USER="root" -> el contenedor no arrancaría.
export PRACTICA1_DB_CONNECT_USER="root"

NBCONVERT_BIN="$ROOT_DIR/.venv/bin/jupyter-nbconvert"
if [ ! -f "$NBCONVERT_BIN" ]; then
    NBCONVERT_BIN="jupyter-nbconvert"
fi

echo "🚀 Ejecutando celdas del Notebook: $NOTEBOOK..."
"$NBCONVERT_BIN" --to notebook --execute --inplace "$NOTEBOOK"

echo "📑 Generando reporte estático HTML: practica1/encargo1_pandas.html..."
"$NBCONVERT_BIN" --to html "$NOTEBOOK" --output "encargo1_pandas.html"

echo "✅ Notebook y Reporte HTML ejecutados y certificados exitosamente."

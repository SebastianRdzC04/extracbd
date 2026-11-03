#!/usr/bin/env bash
# ==============================================================================
# Script de Ejecución del Jupyter Notebook - Práctica 2: Encargo 1 (Ganancias por Región)
# Base de Datos: northwind | Servicio Docker: db-practica2 (Puerto 3308)
# Ejecuta el notebook de forma headless y genera el reporte HTML estático
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$DIR/../docker-compose.yml" ]; then
    ROOT_DIR="$(cd "$DIR/.." && pwd)"
else
    ROOT_DIR="$DIR"
fi

cd "$ROOT_DIR"

NOTEBOOK="practica2/encargo1_pandas.ipynb"
SERVICE="db-practica2"
PORT="${PRACTICA2_DB_PORT:-3308}"

# 1. Credenciales: .env si existe, si no los valores por defecto del proyecto
if [ -f "$ROOT_DIR/.env" ]; then
    set -a
    # shellcheck disable=SC1091
    . "$ROOT_DIR/.env"
    set +a
fi
export PRACTICA2_DB_NAME="${PRACTICA2_DB_NAME:-northwind}"
export PRACTICA2_DB_ROOT_PASSWORD="${PRACTICA2_DB_ROOT_PASSWORD:-rootpassword}"

# 2. Verificar servicio Docker
if command -v docker &>/dev/null; then
    if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${SERVICE}$"; then
        echo "🐳 Iniciando servicio Docker $SERVICE..."
        docker compose up -d "$SERVICE" 2>/dev/null || docker-compose up -d "$SERVICE"
    fi
    # 3. Esperar a que MySQL esté listo Y haya terminado el script de
    #    inicialización. Ver scripts/esperar_mysql.sh para el porqué:
    #    el servidor temporal del entrypoint no escucha en TCP.
    # shellcheck source=../scripts/esperar_mysql.sh
    . "$ROOT_DIR/scripts/esperar_mysql.sh"
    if ! esperar_mysql "$SERVICE" db_practica2 "$PRACTICA2_DB_ROOT_PASSWORD"; then
        exit 1
    fi
fi

# 4. El notebook se conecta como root (necesita leer las 14 tablas del esquema).
#    OJO: se exporta DESPUÉS del arranque de Docker a propósito.
#    PRACTICA2_DB_USER alimenta MYSQL_USER en docker-compose.yml y el entrypoint
#    de MySQL rechaza MYSQL_USER="root" -> el contenedor no arrancaría.
export PRACTICA2_DB_CONNECT_USER="root"

# 5. Configurar variables de Jupyter y Python
export JUPYTER_CONFIG_DIR="/tmp/jupyter"
export JUPYTER_DATA_DIR="/tmp/jupyter_data"
export JUPYTER_RUNTIME_DIR="/tmp/jupyter_runtime"
export IPYTHONDIR="/tmp/ipython"
export PRACTICA2_DB_PORT="$PORT"
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH}"

NBCONVERT_BIN="$ROOT_DIR/.venv/bin/jupyter-nbconvert"
if [ ! -f "$NBCONVERT_BIN" ]; then
    NBCONVERT_BIN="jupyter-nbconvert"
fi

echo "🚀 Ejecutando celdas del Notebook: $NOTEBOOK..."
"$NBCONVERT_BIN" --to notebook --execute --inplace "$NOTEBOOK"

echo "📑 Generando reporte estático HTML: practica2/encargo1_pandas.html..."
"$NBCONVERT_BIN" --to html "$NOTEBOOK" --output "encargo1_pandas.html"

echo "✅ Notebook y Reporte HTML ejecutados y certificados exitosamente."

#!/usr/bin/env bash
# ==============================================================================
# Script de Ejecución Estética - Práctica 2: Encargo 1 (Ganancias por Región)
# Base de Datos: northwind | Servicio Docker: db-practica2 (Puerto 3308)
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

SQL_FILE="practica2/encargo1.sql"
SERVICE="db-practica2"
DATABASE="northwind"
PORT="${PRACTICA2_DB_PORT:-3308}"
TITLE="PRÁCTICA 2 - ENCARGO 1: GANANCIAS POR REGIÓN"

# Ejecutar mediante el runner visual estilizado
if command -v python3 &>/dev/null; then
    python3 "$ROOT_DIR/scripts/runner.py" \
        --file "$SQL_FILE" \
        --service "$SERVICE" \
        --database "$DATABASE" \
        --port "$PORT" \
        --title "$TITLE"
else
    # Fallback directo en bash si python3 no estuviera presente
    echo "=================================================================="
    echo "  $TITLE"
    echo "=================================================================="
    docker compose up -d "$SERVICE"
    docker compose exec -T -e MYSQL_PWD=rootpassword "$SERVICE" mysql -u root -t "$DATABASE" < "$SQL_FILE"
fi

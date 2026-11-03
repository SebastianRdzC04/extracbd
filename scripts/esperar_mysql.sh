#!/usr/bin/env bash
# ==============================================================================
# Helper: espera a que el contenedor MySQL esté realmente listo para recibir
# conexiones TCP.
#
# POR QUÉ EXISTE ESTE ESPERÓN:
# El entrypoint oficial de MySQL 8.0 inicializa el esquema en un SERVIDOR
# TEMPORAL y luego lo reinicia para arrancar el definitivo. Ese servidor
# temporal:
#   - responde a queries por socket (docker compose exec funciona), y
#   - NO escucha en TCP (arranca con "port: 0").
# Como los Notebooks se conectan por TCP (127.0.0.1:<puerto>), si se conecta
# durante la carga obtiene "Lost connection to MySQL server during query" al
# reiniciar el servidor.
#
# Uso:  source scripts/esperar_mysql.sh <compose-service> <container_name> <password>
# ==============================================================================

esperar_mysql() {
    local SERVICE="$1"
    local CONTAINER="$2"
    local PASSWORD="$3"
    local MAX_INTENTOS="${4:-120}"

    echo "⏳ Esperando a que MySQL esté listo (TCP)..."
    local i READY=0
    for ((i = 1; i <= MAX_INTENTOS; i++)); do
        # (a) el servidor FINAL escucha en TCP 3306 (el temporal usa "port: 0")
        if docker logs "$CONTAINER" 2>&1 | grep -q "port: 3306.*MySQL Community Server"; then
            # (b) y responde por TCP con el esquema ya cargado
            if docker compose exec -T "$SERVICE" mysql -u root -p"$PASSWORD" \
                 --protocol=TCP -h 127.0.0.1 -P 3306 \
                 -e "SELECT 1 FROM information_schema.tables LIMIT 1;" >/dev/null 2>&1; then
                READY=1
                echo "✅ MySQL listo (${i} intentos)"
                break
            fi
        fi
        sleep 5
    done

    if [ "$READY" -ne 1 ]; then
        echo "❌ MySQL no respondió a tiempo. Revisa 'make logs-${SERVICE#db-}'." >&2
        return 1
    fi
    return 0
}

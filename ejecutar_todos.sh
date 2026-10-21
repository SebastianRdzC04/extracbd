#!/usr/bin/env bash
# ==============================================================================
# Ejecución Integral de Todos los Encargos
# Práctica 1 + Práctica 2 (Encargo 1, Encargo 2, Encargo 3)
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "================================================================================"
echo "  🚀 INICIANDO EJECUCIÓN SECUENCIAL DE TODOS LOS ENCARGOS"
echo "================================================================================"

bash "$DIR/practica1/ejecutar_encargo.sh"
bash "$DIR/practica2/ejecutar_encargo1.sh"
bash "$DIR/practica2/ejecutar_encargo2.sh"
bash "$DIR/practica2/ejecutar_encargo3.sh"

echo "================================================================================"
echo "  ✨ TODOS LOS ENCARGOS FUERON EJECUTADOS CON ÉXITO"
echo "================================================================================"

.PHONY: help db-practica1 db-practica2 db-all stop down restart logs logs-practica1 logs-practica2 status clean-volumes \
        encargo-p1 encargo1 encargo2 encargo3 encargos \
        p1-encargo encargo1-p1 encargo-practica1 \
        encargo1-p2 p2-encargo1 practica2-encargo1 encargo-1 \
        encargo2-p2 p2-encargo2 practica2-encargo2 encargo-2 \
        encargo3-p2 p2-encargo3 practica2-encargo3 encargo-3 \
        encargos-all all-encargos ejecutar-todos

help:
	@echo "================================================================================="
	@echo "  🛠️  COMANDOS DISPONIBLES EN EL MAKEFILE"
	@echo "================================================================================="
	@echo "  --- Ejecución de Encargos (Formato Estético en Terminal) ---"
	@echo "  make encargo-p1      - Ejecuta el Encargo de la Práctica 1 (Ganancias por Autor - pubs)"
	@echo "  make encargo1        - Ejecuta el Encargo 1 de la Práctica 2 (Ganancias por Región - northwind)"
	@echo "  make encargo2        - Ejecuta el Encargo 2 de la Práctica 2 (Productos Menos Vendidos - northwind)"
	@echo "  make encargo3        - Ejecuta el Encargo 3 de la Práctica 2 (Ganancias Editorial x Autor - pubs)"
	@echo "  make encargos        - Ejecuta secuencialmente todos los encargos (Práctica 1 y Práctica 2)"
	@echo ""
	@echo "  --- Gestión de Bases de Datos en Docker ---"
	@echo "  make db-practica1    - Inicia el contenedor de la Práctica 1 (pubs en puerto 3307)"
	@echo "  make db-practica2    - Inicia el contenedor de la Práctica 2 (northwind en puerto 3308)"
	@echo "  make db-all          - Inicia ambas bases de datos"
	@echo "  make status          - Muestra el estado de los contenedores (docker compose ps)"
	@echo "  make logs            - Muestra logs en tiempo real de todos los contenedores"
	@echo "  make logs-practica1  - Muestra logs de la Práctica 1"
	@echo "  make logs-practica2  - Muestra logs de la Práctica 2"
	@echo "  make stop            - Detiene los contenedores sin borrar volúmenes"
	@echo "  make down            - Detiene y remueve los contenedores"
	@echo "  make restart         - Reinicia todos los contenedores"
	@echo "  make clean-volumes   - Detiene contenedores y elimina volúmenes (reinicia BD a 0)"
	@echo "================================================================================="

# ==============================================================================
# EJECUCIÓN ESTÉTICA DE ENCARGOS
# ==============================================================================

encargo-p1:
	@bash practica1/ejecutar_encargo.sh

encargo1:
	@bash practica2/ejecutar_encargo1.sh

encargo2:
	@bash practica2/ejecutar_encargo2.sh

encargo3:
	@bash practica2/ejecutar_encargo3.sh

encargos:
	@bash ejecutar_todos.sh

# Aliases convenientes
p1-encargo: encargo-p1
encargo1-p1: encargo-p1
encargo-practica1: encargo-p1

encargo1-p2: encargo1
p2-encargo1: encargo1
practica2-encargo1: encargo1
encargo-1: encargo1

encargo2-p2: encargo2
p2-encargo2: encargo2
practica2-encargo2: encargo2
encargo-2: encargo2

encargo3-p2: encargo3
p2-encargo3: encargo3
practica2-encargo3: encargo3
encargo-3: encargo3

encargos-all: encargos
all-encargos: encargos
ejecutar-todos: encargos

# ==============================================================================
# GESTIÓN DOCKER
# ==============================================================================

db-practica1:
	docker compose up -d db-practica1

db-practica2:
	docker compose up -d db-practica2

db-all:
	docker compose up -d

stop:
	docker compose stop

down:
	docker compose down

restart:
	docker compose restart

status:
	docker compose ps

logs:
	docker compose logs -f

logs-practica1:
	docker compose logs -f db-practica1

logs-practica2:
	docker compose logs -f db-practica2

clean-volumes:
	docker compose down -v

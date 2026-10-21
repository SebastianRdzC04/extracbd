.PHONY: help db-practica1 db-practica2 db-all stop down restart logs logs-practica1 logs-practica2 status clean-volumes

help:
	@echo "Comandos disponibles:"
	@echo "  make db-practica1    - Inicia el contenedor de la Práctica 1 (pubs en puerto 3307)"
	@echo "  make db-practica2    - Inicia el contenedor de la Práctica 2 (northwind en puerto 3308)"
	@echo "  make db-all          - Inicia ambas bases de datos"
	@echo "  make stop            - Detiene los contenedores sin borrar volúmenes"
	@echo "  make down            - Detiene y remueve los contenedores"
	@echo "  make restart         - Reinicia todos los contenedores"
	@echo "  make status          - Muestra el estado de los contenedores"
	@echo "  make logs            - Muestra logs en tiempo real de todos los contenedores"
	@echo "  make logs-practica1  - Muestra logs de la Práctica 1"
	@echo "  make logs-practica2  - Muestra logs de la Práctica 2"
	@echo "  make clean-volumes   - Detiene contenedores y elimina volúmenes (reinicia bases de datos a 0)"

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

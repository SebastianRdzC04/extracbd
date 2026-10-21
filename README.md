# Infraestructura de Bases de Datos - Prácticas

Este proyecto contiene la configuración con Docker Compose y Makefile para levantar de manera independiente o conjunta los entornos de base de datos para la **Práctica 1** (`pubs`) y la **Práctica 2** (`northwind`).

---

## 🛠️ Requisitos Previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) en ejecución.
- `make` instalado en tu sistema.

---

## 🚀 Inicio Rápido

### 1. Variables de entorno
El archivo `.env` ya viene configurado con valores por defecto. Si necesitas cambiar contraseñas o puertos, puedes editar `.env` (guíate con `.env.example`).

### 2. Levantar los contenedores con Make

- **Levantar solo Práctica 1 (`pubs` en puerto 3307):**
  ```bash
  make db-practica1
  ```

- **Levantar solo Práctica 2 (`northwind` en puerto 3308):**
  ```bash
  make db-practica2
  ```

- **Levantar ambas bases de datos:**
  ```bash
  make db-all
  ```

---

## 📊 Datos de Conexión

| Parámetro | Práctica 1 | Práctica 2 |
| :--- | :--- | :--- |
| **Motor** | MySQL 8.0 | MySQL 8.0 |
| **Host** | `localhost` | `localhost` |
| **Puerto Host** | `3307` | `3308` |
| **Base de Datos** | `pubs` | `northwind` |
| **Usuario Root** | `root` | `root` |
| **Password Root** | `rootpassword` | `rootpassword` |
| **Usuario Regular** | `user_practica1` | `user_practica2` |
| **Password Regular** | `userpassword` | `userpassword` |

> Los scripts iniciales `database.sql` de cada práctica se ejecutan automáticamente en la primera inicialización del contenedor.

---

## 📋 Comandos Make Disponibles

| Comando | Descripción |
| :--- | :--- |
| `make db-practica1` | Levanta el contenedor de la Práctica 1 |
| `make db-practica2` | Levanta el contenedor de la Práctica 2 |
| `make db-all` | Levanta ambos contenedores |
| `make status` | Consulta el estado de los contenedores (`docker compose ps`) |
| `make logs` | Muestra los logs en vivo de todos los servicios |
| `make logs-practica1` | Muestra los logs del contenedor de la Práctica 1 |
| `make logs-practica2` | Muestra los logs del contenedor de la Práctica 2 |
| `make stop` | Pausa los contenedores sin borrar datos |
| `make down` | Detiene y remueve los contenedores |
| `make clean-volumes` | **Atención:** Detiene y elimina los volúmenes para reiniciar las BD desde cero |

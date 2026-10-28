# 📊 Entorno de Análisis de Bases de Datos & Encargos

Infraestructura contenerizada con **Docker**, **Docker Compose** y **Makefile** para ejecutar y auditar análisis de datos avanzados sobre las bases de datos relacionales **`pubs`** y **`northwind`** (MySQL 8.0).

---

## 🚀 Inicio Rápido (Zero Setup)

Solo requieres tener **Docker Desktop** encendido.

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/SebastianRdzC04/extracbd.git
   cd extracbd
   ```

2. **Copiar variables de entorno (opcional si deseas cambiar puertos o credenciales):**
   ```bash
   cp .env.example .env
   ```
   *(Si no se define `.env`, se usan automáticamente los valores predeterminados seguros).*

3. **Ejecutar cualquier encargo con Make:**
   Los scripts detectan automáticamente si el contenedor está apagado, lo levantan y muestran los resultados estilizados en la terminal con tablas formateadas y análisis forense paso a paso:
   ```bash
   make encargo-p1   # Práctica 1: Ganancias por Autor (pubs)
   make encargo1     # Práctica 2 - Encargo 1: Ganancias por Región (northwind)
   make encargo2     # Práctica 2 - Encargo 2: Productos Menos Vendidos (northwind)
   make encargo3     # Práctica 2 - Encargo 3: Ganancias Editorial x Autor (pubs)
   ```

---

## 📑 Catálogo de Encargos

| Comando Make | Script Shell | Base de Datos | Descripción / Entregable |
| :--- | :--- | :--- | :--- |
| `make encargo-p1` | [`practica1/ejecutar_encargo.sh`](practica1/ejecutar_encargo.sh) | `pubs` (3307) | **Ganancias por Autor (SQL)**: Auditoría contra línea base ($3,863.80), resolución de duplicidad en libros multi-autor mediante `royaltyper`, detección de libros huérfanos y Master Query para los 23 autores. |
| `make encargo-p1-pandas` | [`practica1/ejecutar_encargo_pandas.sh`](practica1/ejecutar_encargo_pandas.sh) | `pubs` (3307) | **Práctica 1 con Pandas**: Auditoría con DataFrames, límite estricto de $\le$ 2 JOINs en SQL, resolución del error ingenuo (+$845.10) y conciliación contable al centavo en Python. |
| `make notebook-p1` | [`practica1/notebooks/encargo1_ganancias_por_autor.ipynb`](practica1/notebooks/encargo1_ganancias_por_autor.ipynb) | `pubs` (3307) | Abre el **Jupyter Notebook interactivo de la Práctica 1** con las 10 fases forenses y visualizaciones ejecutivas. |
| `make encargo1` | [`practica2/ejecutar_encargo1.sh`](practica2/ejecutar_encargo1.sh) | `northwind` (3308) | **Ganancias por Región**: Diagnóstico del error del 394.5% por unión cartesiana de territorios, desacoplamiento empleado-región y cuadre al centavo de los $1,354,458.59 facturados. |
| `make encargo2` | [`practica2/ejecutar_encargo2.sh`](practica2/ejecutar_encargo2.sh) | `northwind` (3308) | **Productos Menos Vendidos por Región y Año**: Matriz pivoteada (Año x 4 Regiones) con desempate mediante funciones de ventana `DENSE_RANK()` y certificación celda por celda. |
| `make encargo3` | [`practica2/ejecutar_encargo3.sh`](practica2/ejecutar_encargo3.sh) | `pubs` (3307) | **Ganancias por Editorial y Autor**: Reporte jerárquico multinivel con `ROLLUP`, matriz cruzada bidimensional (Editorial x Autor) y conciliación del 100% de la facturación. |
| `make encargos` | [`ejecutar_todos.sh`](ejecutar_todos.sh) | Ambas | Ejecuta la batería completa de los 4 encargos de forma secuencial. |
| `make test-pandas-encargo1` | [`analisis_pandas/scripts/test_encargo1.py`](analisis_pandas/scripts/test_encargo1.py) | `northwind` (3308) | **Encargo 1 con Pandas**: Auditoría con DataFrames, límite estricto de $\le$ 2 JOINs en SQL, resolución del error ingenuo (+394.5%) y conciliación contable al centavo en Python. |
| `make notebook-encargo1` | [`analisis_pandas/notebooks/encargo1_ganancias_por_region.ipynb`](analisis_pandas/notebooks/encargo1_ganancias_por_region.ipynb) | `northwind` (3308) | Abre el **Jupyter Notebook interactivo** del Encargo 1 con las 8 fases forenses y visualizaciones. |

---

## 🛠️ Comandos de Infraestructura Docker

| Comando | Acción |
| :--- | :--- |
| `make db-practica1` | Levanta únicamente el contenedor de la **Práctica 1** (`pubs` en puerto `3307`) |
| `make db-practica2` | Levanta únicamente el contenedor de la **Práctica 2** (`northwind` en puerto `3308`) |
| `make db-all` | Levanta ambos contenedores simultáneamente |
| `make status` | Consulta el estado y healthcheck de los contenedores (`docker compose ps`) |
| `make logs` | Muestra logs interactivos en vivo |
| `make stop` | Pausa los contenedores conservando datos |
| `make down` | Detiene y remueve los contenedores |
| `make clean-volumes` | **Reset completo:** Elimina volúmenes persistentes y reconstruye las BDs desde los `.sql` originales |

---

## 🔑 Credenciales y Parámetros de Conexión

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
| **Volumen de Datos** | `practica1_data` | `practica2_data` |

> En la primera inicialización de cada contenedor, MySQL ejecuta automáticamente los scripts maestros `database.sql` montados en `/docker-entrypoint-initdb.d/`.

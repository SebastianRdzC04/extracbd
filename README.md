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

4. **Ejecutar los Notebooks de Pandas (requiere entorno Python):**
   ```bash
   make venv-setup   # Crea .venv e instala las dependencias (solo la primera vez)
   make notebook-p1  # Práctica 1 en Pandas: Ganancias por Autor
   make notebook-p2  # Práctica 2 en Pandas: Ganancias por Región
   ```

---

## 📑 Catálogo de Encargos

| Comando Make | Script Shell | Base de Datos | Descripción / Entregable |
| :--- | :--- | :--- | :--- |
| `make encargo-p1` | [`practica1/ejecutar_encargo.sh`](practica1/ejecutar_encargo.sh) | `pubs` (3307) | **Ganancias por Autor (SQL)**: Auditoría contra línea base ($3,863.80), resolución de duplicidad en libros multi-autor mediante `royaltyper`, detección de libros huérfanos y Master Query para los 23 autores. |
| `make notebook-p1` | [`practica1/encargo1_pandas.ipynb`](practica1/encargo1_pandas.ipynb) | `pubs` (3307) | **Ganancias por Autor (Jupyter Notebook & Pandas)**: Solución 100% auto-contenida en memoria, restricción estricta de **SQL $\le$ 2 JOINs**, validación cruzada y conciliación al 100%. |
| `make notebook-p2` | [`practica2/encargo1_pandas.ipynb`](practica2/encargo1_pandas.ipynb) | `northwind` (3308) | **Ganancias por Región (Jupyter Notebook & Pandas)**: ETL en memoria sobre 2,155 líneas y 830 pedidos, diagnóstico del fan-out de `employeeterritories` (+394.5%), pre-agregación en el motor (×3.46 más rápido) y conciliación al centavo de $1,354,458.59. |
| `make encargo1` | [`practica2/ejecutar_encargo1.sh`](practica2/ejecutar_encargo1.sh) | `northwind` (3308) | **Ganancias por Región**: Diagnóstico del error del 394.5% por unión cartesiana de territorios, desacoplamiento empleado-región y cuadre al centavo de los $1,354,458.59 facturados. |
| `make encargo2` | [`practica2/ejecutar_encargo2.sh`](practica2/ejecutar_encargo2.sh) | `northwind` (3308) | **Productos Menos Vendidos por Región y Año**: Matriz pivoteada (Año x 4 Regiones) con desempate mediante funciones de ventana `DENSE_RANK()` y certificación celda por celda. |
| `make encargo3` | [`practica2/ejecutar_encargo3.sh`](practica2/ejecutar_encargo3.sh) | `pubs` (3307) | **Ganancias por Editorial y Autor**: Reporte jerárquico multinivel con `ROLLUP`, matriz cruzada bidimensional (Editorial x Autor) y conciliación del 100% de la facturación. |
| `make encargos` | [`ejecutar_todos.sh`](ejecutar_todos.sh) | Ambas | Ejecuta la batería completa de los 4 encargos de forma secuencial. |

---

## 🐼 Práctica 1 - Encargo 1 en Jupyter Notebook & Pandas (ETL en Memoria)

Implementación con arquitectura **Extract-Transform-Load (ETL) local** en Pandas para resolver el **Encargo 1** bajo la restricción técnica estricta: **Ninguna consulta SQL supera 2 JOINs**. Todo el análisis vive de forma aislada y auto-contenida dentro del Notebook.

### 🏗️ Estructura del Apartado
```
practica1/
├── database.sql                  # Script DDL/DML de la BD pubs (MySQL 8.0)
├── encargo.sql                   # Solución original en SQL
├── ejecutar_encargo.sh           # Runner del script SQL con formato ANSI
├── encargo1_pandas.ipynb         # ⭐ Jupyter Notebook auto-contenido (100% funcional con gráficos)
├── encargo1_pandas.html          # Reporte web estático para visualización en navegador
└── ejecutar_notebook.sh          # Runner para re-ejecutar el Notebook y exportar a HTML
```

### ⚡ Comandos Rápidos:
```bash
make notebook-p1         # Re-ejecuta todas las celdas del Notebook y actualiza el HTML
# o directamente:
bash practica1/ejecutar_notebook.sh
```

---

## 🐼 Práctica 2 - Encargo 1 en Jupyter Notebook & Pandas (ETL en Memoria)

Réplica en memoria del **Encargo 1 de la Práctica 2** (Ganancias por Región sobre `northwind`), bajo el mismo criterio de diseño del apartado anterior: **el fan-out relacional se resuelve en Pandas**, el SQL contra MySQL se limita a extracción directa (0 JOINs) y controles puntuales (≤ 2 JOINs).

### 🏗️ Estructura del Apartado
```
practica2/
├── database.sql                  # Script DDL/DML de la BD northwind (MySQL 8.0)
├── encargo1.sql                  # Solución original en SQL
├── ejecutar_encargo1.sh          # Runner del script SQL con formato ANSI
├── encargo1_pandas.ipynb         # ⭐ Jupyter Notebook auto-contenido (100% funcional con gráficos)
├── encargo1_pandas.html          # Reporte web estático para visualización en navegador
└── ejecutar_notebook.sh          # Runner para re-ejecutar el Notebook y exportar a HTML
```

### 🔍 El problema forense y su solución

| Etapa | Hallazgo |
| :--- | :--- |
| **Línea base** | $1,354,458.59 facturados en 51,317 unidades y 830 pedidos |
| **Intento ingenuo** | $6,698,176.56 → **+394.5%** de error; 2,155 líneas se inflan a 10,129 filas |
| **Causa raíz** | `employeeterritories` es N:M: cada pedido se replica tantas veces como territorios tiene su vendedor (hasta ×10) |
| **Verificación** | Los 9 empleados pertenecen a **exactamente 1 región** → el fan-out es eliminable con `DISTINCT` |
| **Segunda trampa** | Sumar `Freight` tras unir con el detalle lo infla de $64,942.69 a $207,306.10 (+219%) |
| **Solución** | Desacoplar empleado → región (1:1) y pre-agregar a nivel `OrderID` |
| **Optimización** | Pre-agregar en el motor: 830 filas en vez de 2,155 (×3.46 más rápido) |
| **Conciliación** | Suma de las 4 regiones = $1,354,458.59 → **descuadre $0.00** |

### ⚡ Comandos Rápidos:
```bash
make notebook-p2         # Re-ejecuta todas las celdas del Notebook y actualiza el HTML
# o directamente:
bash practica2/ejecutar_notebook.sh
```

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
| `make venv-setup` | Crea el entorno virtual `.venv` e instala las dependencias de `requirements.txt` |

> **Nota de arranque:** `make clean-volumes` seguido de `make notebook-p1` / `make notebook-p2` reconstruye las bases desde cero. MySQL inicializa el esquema en un servidor temporal que **no escucha en TCP**, por lo que los scripts esperan (`scripts/esperar_mysql.sh`) a que el servidor definitivo esté listo antes de ejecutar el Notebook. El proceso completo tarda ~2 min por base en el primer arranque.

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

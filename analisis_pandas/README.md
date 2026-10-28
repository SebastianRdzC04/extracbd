# 🐼 Proyecto de Análisis de Datos Relacionales con Pandas & Jupyter Notebooks

Entorno analítico empresarial que traslada y profundiza la auditoría de bases de datos relacionales (**`pubs`** y **`northwind`**) hacia un entorno moderno de **Python**, **Pandas** y **Jupyter Notebooks**, implementando arquitectura desacoplada y auditoría forense al centavo.

---

## 🎯 Regla de Ingeniería y Restricción de Diseño

> ⚠️ **Restricción Estricta del Encargo:**
> **Las consultas enviadas al motor SQL no pueden tener más de dos `JOIN`s.**

### Estrategia de Arquitectura:
En sistemas distribuidos y microservicios modernos, realizar consultas SQL complejas con 4, 5 o 6 `JOIN`s genera bloqueos de tablas, consumo excesivo de memoria en el motor y vulnerabilidad a multiplicaciones cartesianas N:M.

Para cumplir rigurosamente con esta restricción sin sacrificar precisión:
1. **Extracción en Bruto (0 JOINs):** Se extraen las tablas maestras y transaccionales completas hacia DataFrames de Pandas mediante consultas atómicas directas (`SELECT * FROM tabla`).
2. **Validación Automática:** El módulo `src/database.py` incorpora el método `validate_max_joins(sql, max_joins=2)` que intercepta cualquier consulta que viole esta norma.
3. **Álgebra Relacional en Memoria:** Toda la lógica de negocio, detección y eliminación de duplicidades, normalización de campos, agrupaciones multivariadas y conciliaciones contables se realiza en memoria mediante **Pandas**.

---

## 📂 Estructura del Subproyecto

```text
analisis_pandas/
├── README.md                                           # Documentación técnica del proyecto
├── requirements.txt                                    # Dependencias de Python (Pandas, SQLAlchemy, PyMySQL, etc.)
├── src/                                                # Módulos Python reutilizables
│   ├── __init__.py
│   └── database.py                                     # Gestor de conexiones, validador de JOINs y extracción
├── notebooks/                                          # Cuadernos Jupyter reproducibles pre-renderizados
│   ├── practica1_encargo1_ganancias_por_autor.ipynb    # Práctica 1: Ganancias por Autor (pubs)
│   └── encargo1_ganancias_por_region.ipynb             # Práctica 2 - Encargo 1: Ganancias por Región (northwind)
└── scripts/                                            # Scripts de soporte y auditoría headless
    ├── test_practica1_encargo1.py                      # Auditoría y aserciones de Práctica 1 en terminal ($0.00 de error)
    ├── test_encargo1.py                                # Auditoría y aserciones de Práctica 2 en terminal ($0.00 de error)
    ├── generate_notebook_practica1.py                  # Generador del notebook de Práctica 1
    ├── generate_notebook_encargo1.py                   # Generador del notebook de Práctica 2 - Encargo 1
    └── execute_notebook.py                             # Ejecutor headless para persistir outputs en .ipynb
```

---

## 🚀 Inicio Rápido y Ejecución

### 1. Requisitos Previos (Bases de Datos en Docker)
```bash
make db-practica1    # Levanta pubs en puerto 3307
make db-practica2    # Levanta northwind en puerto 3308
# o ambas juntas:
make db-all
```

### 2. Entorno Virtual de Python
El entorno virtual `.venv` en la raíz del repositorio contiene todas las librerías necesarias:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r analisis_pandas/requirements.txt
```

### 3. Ejecutar la Auditoría Técnica desde la Terminal
* **Práctica 1 (Ganancias por Autor - `pubs`):**
  ```bash
  make test-pandas-p1
  # O con el runner visual:
  make encargo-p1-pandas
  ```

* **Práctica 2 - Encargo 1 (Ganancias por Región - `northwind`):**
  ```bash
  make test-pandas-encargo1
  ```

### 4. Abrir los Jupyter Notebooks Interactivos
* **Práctica 1 (Pubs):**
  ```bash
  make notebook-p1
  ```
* **Práctica 2 (Northwind):**
  ```bash
  make notebook-encargo1
  ```

---

## ⚖️ Resumen Comparativo de Conciliación Contable

### Práctica 1: Ganancias por Autor (`pubs`)
- **Línea Base Oficial:** `$3,863.80` (Facturación real en caja).
- **Intento Ingenuo:** `$4,708.90` (+$845.10 de inflación artificial).
- **Anomalías Identificadas:**
  - Duplicidad en libros multi-autor (PC8888 y MC3021): `+$1,044.85`.
  - Omisión de libro huérfano sin autor (PS7777): `-$199.75`.
- **Ecuación de Conciliación:**
  `$3,863.80 + $1,044.85 - $199.75 = $4,708.90` (Diferencia: **$0.00**).
- **Conciliación Definitiva:**
  - Asignado a autores registrados: `$2,893.50` (74.89%)
  - Ventas huérfanas: `$199.75` (5.17%)
  - Remanente editorial: `$770.55` (19.94%)
  - Total General: **`$3,863.80`** (100.00% al centavo).

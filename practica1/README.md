# 📚 Práctica 1: Determinación Forense de Ganancias por Autor (`pubs`)

Este directorio contiene la solución completa de la **Práctica 1**, abordada desde dos paradigmas complementarios de ingeniería de datos:
1. **Enfoque SQL Puro:** Mediante el script interactivo y forense `encargo.sql`.
2. **Enfoque Moderno de Data Science (Python, Pandas & Jupyter Notebooks):** Extracción desacoplada (≤ 2 JOINs) con análisis, resolución de anomalías y conciliación contable al centavo en memoria.

---

## 🎯 Regla de Ingeniería y Restricción del Encargo

> ⚠️ **Restricción Estricta:**
> **Las consultas enviadas a SQL no pueden tener más de dos `JOIN`s.**

### 🏛️ Estrategia de Arquitectura:
- **Extracción Atómica (0 JOINs):** Se extraen las tablas completas (`authors`, `titles`, `titleauthor`, `sales`) hacia DataFrames de Pandas mediante `SELECT * FROM tabla`.
- **Validación Automatizada:** Interceptor `validate_max_joins(sql, max_joins=2)` que audita y asegura el cumplimiento del límite.
- **Álgebra Relacional en Memoria:** Toda la detección de duplicidad cartesiana, cálculo de cuotas de autoría (`royaltyper`), inclusión de los 23 autores mediante `LEFT JOIN` y conciliación contable se realiza en Python con Pandas.

---

## 📂 Estructura del Directorio `practica1/`

```text
practica1/
├── database.sql                    # Script DDL/DML para inicializar la base de datos pubs
├── encargo.sql                     # Script SQL forense de 24 consultas comentadas
├── ejecutar_encargo.sh             # Runner visual de terminal para la versión SQL
├── ejecutar_encargo_pandas.sh      # Runner visual de terminal para la versión Pandas & Python
├── notebooks/
│   └── encargo1_ganancias_por_autor.ipynb   # Jupyter Notebook pre-renderizado con gráficos y tablas
└── scripts/
    ├── test_encargo1_pandas.py     # Suite de pruebas y validación contable ($0.00 de error)
    └── generate_notebook_encargo1.py # Generador y ejecutor headless del notebook
```

---

## 🚀 Guía de Ejecución

### 1. Iniciar la Base de Datos en Docker
```bash
make db-practica1
# O directamente: docker compose up -d db-practica1
```

### 2. Ejecutar la Auditoría en Terminal (Python & Pandas)
```bash
make encargo-p1-pandas
# O alternativamente:
bash practica1/ejecutar_encargo_pandas.sh
```

### 3. Abrir el Jupyter Notebook Interactivo
```bash
make notebook-p1
```
El cuaderno se abrirá en Jupyter Lab con todas las celdas, explicaciones markdown, ecuaciones KaTeX, salidas precalculadas y visualizaciones de Matplotlib / Seaborn.

---

## 📊 Conciliación Contable Oficial ($3,863.80)

| Categoría Contable | Monto ($) | % del Total | Justificación Forense |
| :--- | :---: | :---: | :--- |
| **1. Ventas Asignadas a Autores** | **$2,893.50** | 74.89% | Facturación atribuible a los autores registrados ponderada por `royaltyper`. |
| **2. Ventas Huérfanas (Sin Autor)** | **$199.75** | 5.17% | Libro `PS7777` vendido sin autor registrado en `titleauthor`. |
| **3. Remanente Editorial no Asignado** | **$770.55** | 19.94% | Porcentajes contractuales retenidos por la editorial (`BU1111` y `PS2091`). |
| **>>> TOTAL GENERAL AUDITADO <<<** | **$3,863.80** | **100.00%** | **Cuadratura perfecta con la caja registradora de la empresa.** |

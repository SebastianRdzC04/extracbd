#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador y Ejecutor del Jupyter Notebook para la Práctica 1: Ganancias por Autor con Pandas.
Crea y pre-renderiza el notebook con todas las fases analíticas, markdown estético,
código comentado paso a paso, validaciones matemáticas al centavo y visualizaciones ejecutivas.
Genera el notebook en:
  - analisis_pandas/notebooks/practica1_encargo1_ganancias_por_autor.ipynb
  - practica1/notebooks/encargo1_ganancias_por_autor.ipynb
"""

import json
import sys
from pathlib import Path

# Agregar directorio raíz de analisis_pandas al PYTHONPATH
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
ROOT_DIR = PROJECT_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import nbformat
from nbclient import NotebookClient

NOTEBOOK_DIR_ANALISIS = PROJECT_DIR / "notebooks"
NOTEBOOK_DIR_PRACTICA1 = ROOT_DIR / "practica1" / "notebooks"
NOTEBOOK_DIR_ANALISIS.mkdir(parents=True, exist_ok=True)
NOTEBOOK_DIR_PRACTICA1.mkdir(parents=True, exist_ok=True)

NOTEBOOK_PATH_ANALISIS = NOTEBOOK_DIR_ANALISIS / "practica1_encargo1_ganancias_por_autor.ipynb"
NOTEBOOK_PATH_PRACTICA1 = NOTEBOOK_DIR_PRACTICA1 / "encargo1_ganancias_por_autor.ipynb"


def build_practica1_notebook():
    cells = []

    # -------------------------------------------------------------------------
    # CELL 1: PORTADA Y METADATOS
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# 📚 Práctica 1 - Encargo 1: Determinación y Conciliación Forense de Ganancias por Autor\n",
            "### 🏛️ Arquitectura Desacoplada: Extracción Ligera (≤ 2 JOINs) + Transformación, Diagnóstico y Conciliación Contable en Memoria con Python & Pandas\n",
            "\n",
            "---\n",
            "\n",
            "### 🎯 Contexto y Reglas de Ingeniería del Proyecto\n",
            "* **Base de Datos:** `pubs` (MySQL 8.0 desplegado en contenedor Docker, puerto `3307`).\n",
            "* **Objetivo Principal:** Determinar las ganancias exactas y regalías de cada autor registrado en la base de datos, documentando minuciosamente cada consulta exploratoria, detección de anomalías contables y decisiones tomadas hasta llegar al resultado definitivo.\n",
            "* **⚠️ Restricción Estricta de Diseño:**\n",
            "  > **Ninguna consulta a SQL puede contener más de 2 `JOIN`s.**\n",
            "  > **Estrategia de Arquitectura:** En entornos corporativos modernos (Data Lakes, Microservicios y ETLs desacoplados), enviar consultas monolíticas con 5 o más `JOIN`s bloquea recursos del motor transaccional. Por ello, extraemos las tablas en bruto (**0 JOINs**) o mediante consultas atómicas directas hacia DataFrames de Pandas. Toda la lógica de álgebra relacional, detección y resolución de duplicidad cartesiana, normalización de campos, agrupaciones multivariadas y conciliaciones contables se ejecuta en memoria mediante **Python & Pandas**.\n",
            "\n",
            "---\n",
            "\n",
            "### 🗺️ Hoja de Ruta Analítica (10 Fases de Ingeniería)\n",
            "1. **Fase 0:** Inicialización del Entorno, Conexión a la Base de Datos y Validador de Límites de JOINs (≤ 2 JOINs).\n",
            "2. **Fase 1:** Reconocimiento y Extracción en Bruto (*Data Discovery* - 0 JOINs: `authors`, `titles`, `titleauthor`, `sales`).\n",
            "3. **Fase 2:** Establecimiento de la Línea Base Contable (*Ground Truth Oficial de la Empresa: $3,863.80*).\n",
            "4. **Fase 3:** El Intento Ingenuo y la Gran Discrepancia (*Reproducción del Error Común en Pandas: +$845.10 de Inflación*).\n",
            "5. **Fase 4:** Auditoría Forense y Diagnóstico de Causa Raíz (Libros Multi-Autor, Huérfanos, Censo de Autores y `royaltyper`).\n",
            "6. **Fase 5:** Construcción Iterativa de la Solución Robusta en Pandas (Ponderación de Regalías y `LEFT JOIN`).\n",
            "7. **Fase 6:** Criterios de Negocio: Ventas Atribuibles vs Regalías Netas vs Catálogo Histórico (`ytd_sales`).\n",
            "8. **Fase 7:** *Master Table* Ejecutiva (Los 23 Autores con KPIs Directivos Formateados).\n",
            "9. **Fase 8:** Conciliación Contable Definitiva al Centavo (100.00% de la Facturación de la Empresa Cuadrada al $0.00).\n",
            "10. **Fase 9:** Tablero Visual de Métricas Gerenciales (Visualizaciones con Matplotlib & Seaborn)."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 2: CONFIGURACIÓN E IMPORTACIONES
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# CONFIGURACIÓN INICIAL DEL ENTORNO DE TRABAJO\n",
            "# =============================================================================\n",
            "import os\n",
            "import sys\n",
            "import re\n",
            "from pathlib import Path\n",
            "import numpy as np\n",
            "import pandas as pd\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "from sqlalchemy import create_engine, text\n",
            "\n",
            "# Localizar la raíz del repositorio y módulos compartidos\n",
            "CURRENT_PATH = Path.cwd()\n",
            "if (CURRENT_PATH / 'analisis_pandas').exists():\n",
            "    PROJECT_ROOT = CURRENT_PATH\n",
            "elif (CURRENT_PATH.parent / 'analisis_pandas').exists():\n",
            "    PROJECT_ROOT = CURRENT_PATH.parent\n",
            "elif (CURRENT_PATH.parent.parent / 'analisis_pandas').exists():\n",
            "    PROJECT_ROOT = CURRENT_PATH.parent.parent\n",
            "else:\n",
            "    PROJECT_ROOT = CURRENT_PATH\n",
            "\n",
            "if str(PROJECT_ROOT / 'analisis_pandas') not in sys.path:\n",
            "    sys.path.insert(0, str(PROJECT_ROOT / 'analisis_pandas'))\n",
            "\n",
            "# Configuración estética de Pandas para montos financieros\n",
            "pd.set_option('display.max_columns', 25)\n",
            "pd.set_option('display.width', 1000)\n",
            "pd.options.display.float_format = '${:,.2f}'.format\n",
            "\n",
            "# Estilo de visualización para gráficos ejecutivos\n",
            "plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')\n",
            "plt.rcParams['font.sans-serif'] = 'Helvetica, Arial, DejaVu Sans'\n",
            "plt.rcParams['axes.edgecolor'] = '#CCCCCC'\n",
            "plt.rcParams['axes.linewidth'] = 0.8\n",
            "\n",
            "print(\"✅ Librerías importadas y entorno configurado correctamente.\")"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 3: FASE 0 - EXPLICACIÓN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 🔌 Fase 0: Inicialización del Motor de Base de Datos y Validador de JOINs\n",
            "\n",
            "Para garantizar el cumplimiento riguroso de la restricción del encargo (**máximo 2 `JOIN`s en SQL**), implementamos una función interceptora `validate_max_joins()` que audita mediante expresiones regulares cualquier sentencia enviada al motor SQL.\n",
            "\n",
            "La base de datos `pubs` se encuentra alojada en MySQL 8.0 en el puerto `3307`."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 4: FASE 0 - CÓDIGO
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# FASE 0: GESTOR DE CONEXIÓN Y CERTIFICADOR DE RESTRICCIÓN DE JOINS\n",
            "# =============================================================================\n",
            "from src.database import get_engine, extract_table, load_query, validate_max_joins\n",
            "\n",
            "# Crear conexión a la base de datos 'pubs'\n",
            "engine = get_engine('pubs')\n",
            "print(\"✅ Motor SQLAlchemy conectado a MySQL (pubs en puerto 3307).\")\n",
            "\n",
            "# Demostración del validador de JOINs: Acepta consultas con <= 2 JOINs\n",
            "query_valida = \"\"\"\n",
            "SELECT s.ord_num, t.title \n",
            "FROM sales s \n",
            "INNER JOIN titles t ON s.title_id = t.title_id\n",
            "\"\"\"\n",
            "joins_count = validate_max_joins(query_valida, max_joins=2)\n",
            "print(f\"✅ Validación exitosa: Consulta con {joins_count} JOIN permitida por el interceptor.\")\n",
            "\n",
            "# Verificación de que el validador rechaza consultas que violen el límite\n",
            "try:\n",
            "    query_invalida = \"\"\"\n",
            "    SELECT * FROM authors a \n",
            "    JOIN titleauthor ta ON a.au_id = ta.au_id\n",
            "    JOIN titles t ON ta.title_id = t.title_id\n",
            "    JOIN sales s ON t.title_id = s.title_id\n",
            "    \"\"\"\n",
            "    validate_max_joins(query_invalida, max_joins=2)\n",
            "except ValueError as e:\n",
            "    print(f\"🛡️ Interceptor de seguridad funcionando: {e}\")"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 5: FASE 1 - EXPLICACIÓN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 🔍 Fase 1: Reconocimiento y Extracción en Bruto (*Data Discovery* - 0 JOINs)\n",
            "\n",
            "Siguiendo las mejores prácticas de ingeniería de datos, extraemos las tablas en bruto directamente hacia DataFrames de Pandas mediante la instrucción atómica `SELECT * FROM tabla` (**0 JOINs**).\n",
            "\n",
            "Las 4 tablas involucradas en el análisis son:\n",
            "1. **`authors`**: Catálogo de autores con datos demográficos, ciudad, estado y estado contractual.\n",
            "2. **`titles`**: Catálogo de libros publicados con precios (`price`), adelantos (`advance`), porcentaje de regalías de la editorial (`royalty`) y ventas anuales (`ytd_sales`).\n",
            "3. **`titleauthor`**: Tabla asociativa N:M entre autores y libros con el campo clave `royaltyper` (% de participación del autor sobre el libro).\n",
            "4. **`sales`**: Tabla transaccional de órdenes de venta en librerías (`qty`, `stor_id`, `ord_num`, `ord_date`)."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 6: FASE 1 - CÓDIGO
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# FASE 1: EXTRACCIÓN DE TABLAS EN BRUTO HACIA DATAFRAMES (0 JOINS)\n",
            "# =============================================================================\n",
            "df_authors = extract_table('authors', engine, db_key='pubs')\n",
            "df_titles = extract_table('titles', engine, db_key='pubs')\n",
            "df_titleauthor = extract_table('titleauthor', engine, db_key='pubs')\n",
            "df_sales = extract_table('sales', engine, db_key='pubs')\n",
            "\n",
            "print(\"📊 Volumetría de las tablas extraídas en bruto:\")\n",
            "print(f\"  • authors:      {len(df_authors):>2} filas | Columnas: {list(df_authors.columns)}\")\n",
            "print(f\"  • titles:       {len(df_titles):>2} filas | Columnas: {list(df_titles.columns)}\")\n",
            "print(f\"  • titleauthor:  {len(df_titleauthor):>2} filas | Columnas: {list(df_titleauthor.columns)}\")\n",
            "print(f\"  • sales:        {len(df_sales):>2} filas | Columnas: {list(df_sales.columns)}\")\n",
            "\n",
            "# Vista previa rápida de las tablas principales\n",
            "display(df_authors[['au_id', 'au_fname', 'au_lname', 'city', 'state', 'contract']].head(5))\n",
            "display(df_titles[['title_id', 'title', 'type', 'price', 'advance', 'royalty', 'ytd_sales']].head(5))"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 7: FASE 2 - EXPLICACIÓN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 💰 Fase 2: Establecimiento de la Línea Base Contable (*Ground Truth Oficial*)\n",
            "\n",
            "Antes de calcular cualquier ganancia individual de autor, todo analista financiero profesional debe conocer con precisión milimétrica el dinero total que ingresó a la caja registradora de la empresa:\n",
            "\n",
            "$$\\text{Total Ventas de la Empresa} = \\sum (\\text{qty} \\times \\text{price})$$\n",
            "\n",
            "Este valor es nuestro **Ground Truth** contable indiscutible. Cualquier reporte o cálculo que se haga posteriormente debe cuadrar exactamente contra esta cifra."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 8: FASE 2 - CÓDIGO
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# FASE 2: CÁLCULO DE LA LÍNEA BASE CONTABLE (GROUND TRUTH OFICIAL)\n",
            "# =============================================================================\n",
            "# Unir órdenes de venta (sales) con el catálogo de libros (titles) en memoria\n",
            "df_ventas_base = df_sales.merge(\n",
            "    df_titles[['title_id', 'title', 'price', 'type']], \n",
            "    on='title_id', \n",
            "    how='inner'\n",
            ")\n",
            "\n",
            "# Calcular monto facturado por línea de orden\n",
            "df_ventas_base['monto_linea'] = df_ventas_base['qty'] * df_ventas_base['price']\n",
            "\n",
            "total_ventas_base = round(float(df_ventas_base['monto_linea'].sum()), 2)\n",
            "total_unidades_base = int(df_ventas_base['qty'].sum())\n",
            "titulos_vendidos_count = df_ventas_base['title_id'].nunique()\n",
            "\n",
            "print(\"=\" * 75)\n",
            "print(f\"🎯 LÍNEA BASE OFICIAL DE LA EMPRESA (GROUND TRUTH): ${total_ventas_base:,.2f}\")\n",
            "print(f\"📦 Total de Unidades Vendidas:                       {total_unidades_base:,} unidades\")\n",
            "print(f\"📚 Títulos con Movimiento Comercial:                {titulos_vendidos_count} de {len(df_titles)} libros\")\n",
            "print(\"=\" * 75)\n",
            "\n",
            "# Desglose contable por libro individual\n",
            "ventas_por_libro = df_ventas_base.groupby(['title_id', 'title', 'price'], as_index=False).agg(\n",
            "    unidades_vendidas=('qty', 'sum'),\n",
            "    total_facturado=('monto_linea', 'sum')\n",
            ").sort_values(by='total_facturado', ascending=False)\n",
            "\n",
            "print(\"\\n📖 Desglose de Ventas por Libro Vendido:\")\n",
            "display(ventas_por_libro)"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 9: FASE 3 - EXPLICACIÓN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 🚨 Fase 3: El Intento Ingenuo y la Gran Discrepancia (*El Error Común*)\n",
            "\n",
            "El enfoque que comúnmente intentaría un desarrollador inexperto es encadenar las 4 tablas mediante `INNER JOIN` directo y sumar `qty * price` agrupando por autor:\n",
            "\n",
            "```python\n",
            "# Intento ingenuo típico:\n",
            "df_ingenuo = df_authors.merge(df_titleauthor).merge(df_titles).merge(df_sales)\n",
            "df_ingenuo.groupby('autor')['qty * price'].sum()\n",
            "```\n",
            "\n",
            "Veamos qué sucede matemáticamente cuando ejecutamos este procedimiento en memoria."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 10: FASE 3 - CÓDIGO
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# FASE 3: REPRODUCCIÓN DEL INTENTO INGENUO Y MEDICIÓN DEL DESFASE\n",
            "# =============================================================================\n",
            "df_ingenuo = df_authors.merge(df_titleauthor, on='au_id', how='inner') \\\n",
            "                       .merge(df_titles, on='title_id', how='inner') \\\n",
            "                       .merge(df_sales, on='title_id', how='inner')\n",
            "\n",
            "df_ingenuo['ganancia_ingenua'] = df_ingenuo['qty'] * df_ingenuo['price']\n",
            "df_ingenuo['autor'] = df_ingenuo['au_fname'] + ' ' + df_ingenuo['au_lname']\n",
            "\n",
            "resumen_ingenuo = df_ingenuo.groupby(['au_id', 'autor'], as_index=False).agg(\n",
            "    ganancia_calculada=('ganancia_ingenua', 'sum')\n",
            ").sort_values(by='ganancia_calculada', ascending=False)\n",
            "\n",
            "total_ingenuo = round(float(resumen_ingenuo['ganancia_calculada'].sum()), 2)\n",
            "desfase = round(total_ingenuo - total_ventas_base, 2)\n",
            "pct_desfase = round((desfase / total_ventas_base) * 100, 2)\n",
            "\n",
            "print(\"=\" * 80)\n",
            "print(f\"❌ Total Obtenido con Intento Ingenuo:   ${total_ingenuo:,.2f} ({len(resumen_ingenuo)} autores)\")\n",
            "print(f\"✅ Total Real de Ventas de la Empresa:  ${total_ventas_base:,.2f}\")\n",
            "print(f\"🚨 ¡DESFASE FINANCIERO INEXPLICABLE!:   +${desfase:,.2f} (+{pct_desfase}%)\")\n",
            "print(\"=\" * 80)\n",
            "\n",
            "display(resumen_ingenuo)"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 11: FASE 4 - EXPLICACIÓN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 🕵️ Fase 4: Auditoría Forense de la Base de Datos (*Descubriendo los Detalles Ocultos*)\n",
            "\n",
            "¿Por qué \\$4,708.90 $\\neq$ \\$3,863.80? Como ingenieros de datos profesionales, no podemos conformarnos con suposiciones. En esta fase investigamos las causas exactas del desfase de **+$845.10** mediante 4 auditorías forenses:\n",
            "\n",
            "1. **Investigación 1 (Multiplicación Cartesiana):** Libros con múltiples autores registrados que duplican las ventas al hacer `JOIN`.\n",
            "2. **Investigación 2 (Libros Huérfanos):** Títulos vendidos comercialmente que NO tienen autor en `titleauthor` y que el `INNER JOIN` descarta.\n",
            "3. **Investigación 3 (Censo de Autores):** Autores sin libros y autores sin ventas que fueron excluidos del análisis.\n",
            "4. **Investigación 4 (Columna `royaltyper`):** La participación contractual porcentual entre coautores y editoriales."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 12: FASE 4.1 Y 4.2 - CÓDIGO
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# FASE 4.1: INVESTIGACIÓN DE LIBROS MULTI-AUTOR (DUPLICIDAD POR JOIN)\n",
            "# =============================================================================\n",
            "autores_por_libro = df_titleauthor.groupby('title_id')['au_id'].nunique().reset_index(name='num_autores')\n",
            "libros_multiautor = autores_por_libro[autores_por_libro['num_autores'] > 1]\n",
            "\n",
            "multiautor_ventas = df_ventas_base.merge(libros_multiautor, on='title_id', how='inner')\n",
            "multiautor_ventas['venta_real'] = multiautor_ventas['monto_linea']\n",
            "multiautor_ventas['venta_inflada_join'] = multiautor_ventas['monto_linea'] * multiautor_ventas['num_autores']\n",
            "multiautor_ventas['duplicidad_generada'] = multiautor_ventas['venta_inflada_join'] - multiautor_ventas['venta_real']\n",
            "\n",
            "duplicidad_total = round(float(multiautor_ventas['duplicidad_generada'].sum()), 2)\n",
            "\n",
            "print(\"🔍 4.1 Libros Multi-Autor Identificados en Ventas:\")\n",
            "display(multiautor_ventas[['title_id', 'title', 'num_autores', 'venta_real', 'venta_inflada_join', 'duplicidad_generada']])\n",
            "print(f\"💥 Duplicación artificial total generada en el intento ingenuo: +${duplicidad_total:,.2f}\")\n",
            "\n",
            "# =============================================================================\n",
            "# FASE 4.2: INVESTIGACIÓN DE LIBROS HUÉRFANOS (VENTAS SIN AUTOR ASIGNADO)\n",
            "# =============================================================================\n",
            "titulos_con_autor = set(df_titleauthor['title_id'].unique())\n",
            "libros_huerfanos = df_ventas_base[~df_ventas_base['title_id'].isin(titulos_con_autor)]\n",
            "perdida_huerfanos = round(float(libros_huerfanos['monto_linea'].sum()), 2)\n",
            "\n",
            "print(\"\\n🔍 4.2 Libros Vendidos sin Autor en 'titleauthor' (Omitidos por INNER JOIN):\")\n",
            "display(libros_huerfanos[['title_id', 'title', 'qty', 'price', 'monto_linea']])\n",
            "print(f\"📉 Total de ventas reales ignoradas por el intento ingenuo: -${perdida_huerfanos:,.2f}\")"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 13: FASE 4.3 - CONCILIACIÓN FORENSE
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# FASE 4.3: CONCILIACIÓN MATEMÁTICA FORENSE DE LA DISCREPANCIA\n",
            "# =============================================================================\n",
            "total_explicado = round(total_ventas_base + duplicidad_total - perdida_huerfanos, 2)\n",
            "diferencia_residual = round(total_explicado - total_ingenuo, 2)\n",
            "\n",
            "print(\"=\" * 85)\n",
            "print(\"🎯 ECUACIÓN FORENSE DE CONCILIACIÓN DE LA DISCREPANCIA:\")\n",
            "print(\"=\" * 85)\n",
            "print(f\"   Ventas Reales Oficiales de la Empresa:             ${total_ventas_base:,.2f}\")\n",
            "print(f\"   (+) Duplicación en libros multi-autor:            +${duplicidad_total:,.2f}  (PC8888: $1,000.00, MC3021: $44.85)\")\n",
            "print(f\"   (-) Omisión del libro huérfano PS7777:             -${perdida_huerfanos:,.2f}\")\n",
            "print(\"   \" + \"-\" * 60)\n",
            "print(f\"   (=) Total Matemático Explicado:                    ${total_explicado:,.2f}\")\n",
            "print(f\"   (=) Total Obtenido en Intento Ingenuo:             ${total_ingenuo:,.2f}\")\n",
            "print(f\"   => Discrepancia Residual Final:                    ${diferencia_residual:,.2f}\")\n",
            "print(\"=\" * 85)\n",
            "\n",
            "assert diferencia_residual == 0.00, f\"Fallo en la conciliación: ${diferencia_residual}\"\n",
            "print(\"🏆 ¡DISCREPANCIA 100% EXPLICADA Y DEMOSTRADA AL CENTAVO!\")"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 14: FASE 4.4 Y 4.5 - CENSO Y ROYALTYPER
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# FASE 4.4: CENSO COMPLETO DE AUTORES (POBLACIÓN TOTAL = 23)\n",
            "# =============================================================================\n",
            "autores_con_libros = set(df_titleauthor['au_id'].unique())\n",
            "autores_sin_libros = df_authors[~df_authors['au_id'].isin(autores_con_libros)]\n",
            "autores_con_ventas_ids = set(df_ingenuo['au_id'].unique())\n",
            "autores_con_libros_sin_ventas = df_authors[df_authors['au_id'].isin(autores_con_libros) & ~df_authors['au_id'].isin(autores_con_ventas_ids)]\n",
            "\n",
            "print(\"📋 Censo de Autores en el Universo Pubs:\")\n",
            "print(f\"  • Autores sin libros registrados en 'titleauthor':   {len(autores_sin_libros)} autores\")\n",
            "print(f\"  • Autores con libros pero con 0 ventas comerciales:  {len(autores_con_libros_sin_ventas)} autores\")\n",
            "print(f\"  • Autores con ventas registradas:                    {len(autores_con_ventas_ids)} autores\")\n",
            "print(f\"  • TOTAL DE AUTORES EN NÓMINA:                        {len(df_authors)} autores\")\n",
            "\n",
            "# =============================================================================\n",
            "# FASE 4.5: AUDITORÍA DE LA COLUMNA 'royaltyper' (% DE PARTICIPACIÓN)\n",
            "# =============================================================================\n",
            "royalty_dist = df_titleauthor.groupby('title_id')['royaltyper'].agg(['count', 'sum']).reset_index()\n",
            "royalty_dist.columns = ['title_id', 'num_autores', 'porcentaje_total_autores']\n",
            "libros_con_remanente = royalty_dist[royalty_dist['porcentaje_total_autores'] < 100]\n",
            "\n",
            "print(\"\\n🔍 Libros con Porcentaje de Autoría Inferior al 100% (Remanente Editorial / Externo):\")\n",
            "display(libros_con_remanente)"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 15: FASE 5 - EXPLICACIÓN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 🛠️ Fase 5: Construcción Iterativa de la Solución Robusta en Pandas\n",
            "\n",
            "Con las causas del error plenamente diagnosticadas, construimos el pipeline definitivo aplicando dos correcciones críticas:\n",
            "\n",
            "1. **Ponderación por Cuota de Autoría (`royaltyper / 100.0`):** Cada autor solo recibe el porcentaje legal que le corresponde sobre las ventas del libro.\n",
            "2. **Inclusión Total de Autores (`how='left'` y `.fillna(0)`):** Garantiza que los 23 autores figuren en el informe directivo, mostrando \\$0.00 para quienes no hayan registrado ventas en vez de ser invisibilizados."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 16: FASE 5 Y 6 - CÓDIGO
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# FASE 5 & 6: PIPELINE ROBUSTO EN PANDAS Y CRITERIOS DE NEGOCIO\n",
            "# =============================================================================\n",
            "# Unión relacional izquierda (LEFT JOIN en memoria)\n",
            "df_relacional = df_authors.merge(df_titleauthor, on='au_id', how='left') \\\n",
            "                          .merge(df_titles, on='title_id', how='left') \\\n",
            "                          .merge(df_sales, on='title_id', how='left', suffixes=('', '_sale'))\n",
            "\n",
            "# Imputación de nulos (equivalente a COALESCE en SQL)\n",
            "df_relacional['qty_clean'] = df_relacional['qty'].fillna(0)\n",
            "df_relacional['price_clean'] = df_relacional['price'].fillna(0)\n",
            "df_relacional['royaltyper_clean'] = df_relacional['royaltyper'].fillna(0)\n",
            "df_relacional['royalty_clean'] = df_relacional['royalty'].fillna(0)\n",
            "\n",
            "# Criterio 1: Ventas Atribuibles al Autor (Facturación generada según cuota)\n",
            "df_relacional['unidades_atribuibles'] = df_relacional['qty_clean'] * (df_relacional['royaltyper_clean'] / 100.0)\n",
            "df_relacional['ventas_atribuibles'] = df_relacional['qty_clean'] * df_relacional['price_clean'] * (df_relacional['royaltyper_clean'] / 100.0)\n",
            "\n",
            "# Criterio 2: Regalías Netas en Mano (Dinero líquido que el autor cobra de la editorial)\n",
            "df_relacional['regalias_netas'] = df_relacional['qty_clean'] * df_relacional['price_clean'] * \\\n",
            "                                  (df_relacional['royalty_clean'] / 100.0) * (df_relacional['royaltyper_clean'] / 100.0)\n",
            "\n",
            "# Agrupación final por autor (23 autores preservados)\n",
            "master = df_relacional.groupby(['au_id', 'au_fname', 'au_lname', 'city', 'state'], as_index=False).agg(\n",
            "    libros_publicados=('title_id', lambda s: s.dropna().nunique()),\n",
            "    unidades_brutas=('qty_clean', 'sum'),\n",
            "    unidades_atribuibles=('unidades_atribuibles', 'sum'),\n",
            "    ganancias_generadas=('ventas_atribuibles', 'sum'),\n",
            "    regalias_cobradas=('regalias_netas', 'sum')\n",
            ")\n",
            "\n",
            "master['Nombre del Autor'] = master['au_fname'] + ' ' + master['au_lname']\n",
            "master.sort_values(by=['ganancias_generadas', 'regalias_cobradas', 'Nombre del Autor'], \n",
            "                   ascending=[False, False, True], inplace=True)\n",
            "master.reset_index(drop=True, inplace=True)\n",
            "\n",
            "print(f\"✅ Pipeline ejecutado exitosamente. Universo de autores procesado: {len(master)} autores.\")"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 17: FASE 6.2 - CRITERIO 3 (YTD SALES)
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# FASE 6.2: CRITERIO 3 - VENTAS BASADAS EN CATÁLOGO HISTÓRICO (titles.ytd_sales)\n",
            "# =============================================================================\n",
            "df_ytd = df_authors.merge(df_titleauthor, on='au_id', how='left') \\\n",
            "                   .merge(df_titles, on='title_id', how='left')\n",
            "\n",
            "df_ytd['ytd_sales_clean'] = df_ytd['ytd_sales'].fillna(0)\n",
            "df_ytd['price_clean'] = df_ytd['price'].fillna(0)\n",
            "df_ytd['royaltyper_clean'] = df_ytd['royaltyper'].fillna(0)\n",
            "df_ytd['royalty_clean'] = df_ytd['royalty'].fillna(0)\n",
            "\n",
            "df_ytd['ventas_ytd_atribuibles'] = df_ytd['ytd_sales_clean'] * df_ytd['price_clean'] * (df_ytd['royaltyper_clean'] / 100.0)\n",
            "df_ytd['regalias_ytd_netas'] = df_ytd['ytd_sales_clean'] * df_ytd['price_clean'] * \\\n",
            "                               (df_ytd['royalty_clean'] / 100.0) * (df_ytd['royaltyper_clean'] / 100.0)\n",
            "\n",
            "master_ytd = df_ytd.groupby(['au_id', 'au_fname', 'au_lname'], as_index=False).agg(\n",
            "    libros_publicados=('title_id', lambda s: s.dropna().nunique()),\n",
            "    ventas_ytd=('ventas_ytd_atribuibles', 'sum'),\n",
            "    regalias_ytd=('regalias_ytd_netas', 'sum')\n",
            ")\n",
            "master_ytd['Nombre del Autor'] = master_ytd['au_fname'] + ' ' + master_ytd['au_lname']\n",
            "master_ytd.sort_values(by='ventas_ytd', ascending=False, inplace=True)\n",
            "\n",
            "print(\"📖 Top 5 Autores según Ventas Históricas Acumuladas (ytd_sales):\")\n",
            "display(master_ytd.head(5)[['au_id', 'Nombre del Autor', 'libros_publicados', 'ventas_ytd', 'regalias_ytd']])"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 18: FASE 7 - MASTER TABLE EJECUTIVA
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 📊 Fase 7: *Master Table* Ejecutiva (Los 23 Autores)\n",
            "\n",
            "A continuación se presenta la tabla directiva final para la entrega formal de la Práctica 1. Incluye al 100% de la población de autores, resuelve la duplicidad por coautoría y muestra tanto la facturación generada como las regalías cobradas."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 19: FASE 7 - CÓDIGO DISPLAY
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# FASE 7: MASTER TABLE FORMATEADA PARA PRESENTACIÓN DIRECTIVA\n",
            "# =============================================================================\n",
            "reporte_ejecutivo = master.copy()\n",
            "\n",
            "reporte_ejecutivo.rename(columns={\n",
            "    'au_id': 'ID Autor',\n",
            "    'city': 'Ciudad',\n",
            "    'state': 'Estado',\n",
            "    'libros_publicados': 'Libros Publicados',\n",
            "    'unidades_brutas': 'Unidades Vendidas (Brutas)',\n",
            "    'unidades_atribuibles': 'Unidades Atribuibles',\n",
            "    'ganancias_generadas': 'Ganancias Generadas ($)',\n",
            "    'regalias_cobradas': 'Regalías Cobradas ($)'\n",
            "}, inplace=True)\n",
            "\n",
            "columnas_ordenadas = [\n",
            "    'ID Autor', 'Nombre del Autor', 'Ciudad', 'Estado', 'Libros Publicados',\n",
            "    'Unidades Vendidas (Brutas)', 'Unidades Atribuibles', 'Ganancias Generadas ($)', 'Regalías Cobradas ($)'\n",
            "]\n",
            "\n",
            "reporte_display = reporte_ejecutivo[columnas_ordenadas].style.format({\n",
            "    'Unidades Vendidas (Brutas)': '{:,.0f}',\n",
            "    'Unidades Atribuibles': '{:,.1f}',\n",
            "    'Ganancias Generadas ($)': '${:,.2f}',\n",
            "    'Regalías Cobradas ($)': '${:,.2f}'\n",
            "})\n",
            "\n",
            "reporte_display"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 20: FASE 8 - CONCILIACIÓN CONTABLE
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## ⚖️ Fase 8: Conciliación Contable Definitiva al Centavo (100% de la Empresa)\n",
            "\n",
            "Para otorgar validez legal y de auditoría contable a nuestros resultados, demostramos que el **100.00%** de los **$3,863.80** facturados en la base de datos queda asignado al centavo sin ningún tipo de fuga financiera:\n",
            "\n",
            "1. **Ventas asignadas a autores registrados:** \\$2,893.50 (74.89%)\n",
            "2. **Ventas de libros huérfanos sin autor (PS7777):** \\$199.75 (5.17%)\n",
            "3. **Remanente editorial no asignado (BU1111 y PS2091):** \\$770.55 (19.94%)\n",
            "\n",
            "$$\\$2,893.50 + \\$199.75 + \\$770.55 = \\$3,863.80 \\quad (\\Delta = \\$0.00)$$"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 21: FASE 8 - CÓDIGO
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# FASE 8: AUDITORÍA Y CERTIFICACIÓN CONTABLE INTEGRAL\n",
            "# =============================================================================\n",
            "total_autores = round(float(master['ganancias_generadas'].sum()), 2)\n",
            "total_huerfano = round(float(perdida_huerfanos), 2)\n",
            "\n",
            "# Calcular remanente editorial\n",
            "part_editorial = df_titleauthor.groupby('title_id')['royaltyper'].sum().reset_index()\n",
            "titulos_remanente = part_editorial[part_editorial['royaltyper'] < 100].copy()\n",
            "titulos_remanente['pct_editorial'] = (100 - titulos_remanente['royaltyper']) / 100.0\n",
            "\n",
            "df_editorial = df_sales.merge(df_titles, on='title_id', how='inner') \\\n",
            "                       .merge(titulos_remanente, on='title_id', how='inner')\n",
            "df_editorial['monto_editorial'] = df_editorial['qty'] * df_editorial['price'] * df_editorial['pct_editorial']\n",
            "total_remanente = round(float(df_editorial['monto_editorial'].sum()), 2)\n",
            "\n",
            "total_auditado = round(total_autores + total_huerfano + total_remanente, 2)\n",
            "diff_caja = round(total_auditado - total_ventas_base, 2)\n",
            "\n",
            "tabla_conciliacion = pd.DataFrame([\n",
            "    {'Categoría Contable': '1. Ventas Atribuidas a Autores Registrados', 'Monto ($)': total_autores, '% del Total': (total_autores/total_ventas_base)*100},\n",
            "    {'Categoría Contable': '2. Ventas de Libros sin Autor Asignado (PS7777)', 'Monto ($)': total_huerfano, '% del Total': (total_huerfano/total_ventas_base)*100},\n",
            "    {'Categoría Contable': '3. Porcentaje no Asignado a Autores (BU1111 y PS2091)', 'Monto ($)': total_remanente, '% del Total': (total_remanente/total_ventas_base)*100},\n",
            "    {'Categoría Contable': '>>> TOTAL GENERAL AUDITADO DE LA EMPRESA <<<', 'Monto ($)': total_auditado, '% del Total': (total_auditado/total_ventas_base)*100}\n",
            "])\n",
            "\n",
            "display(tabla_conciliacion.style.format({'Monto ($)': '${:,.2f}', '% del Total': '{:.2f}%'}))\n",
            "\n",
            "print(f\"\\n💰 Línea Base Oficial (Caja Registradora): ${total_ventas_base:,.2f}\")\n",
            "print(f\"⚖️  Diferencia Residual Contable:            ${diff_caja:,.2f}\")\n",
            "\n",
            "assert abs(diff_caja) < 0.001, f\"Fallo de conciliación contable: ${diff_caja}\"\n",
            "print(\"🎉 ¡CERTIFICACIÓN CONTABLE EMITIDA: CONCILIACIÓN PERFECTA AL CENTAVO!\")"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 22: FASE 9 - VISUALIZACIONES
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 📈 Fase 9: Tablero Visual de Métricas Gerenciales (Matplotlib & Seaborn)\n",
            "\n",
            "Generamos gráficos ejecutivos de alta calidad para comunicar los hallazgos a la dirección de la editorial."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 23: FASE 9 - CÓDIGO GRÁFICOS
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# FASE 9: VISUALIZACIONES EJECUTIVAS MULTI-PANEL\n",
            "# =============================================================================\n",
            "fig, axes = plt.subplots(2, 2, figsize=(16, 12))\n",
            "plt.subplots_adjust(hspace=0.35, wspace=0.25)\n",
            "\n",
            "# 1. Top Autores por Ganancias Generadas vs Regalías Cobradas\n",
            "top_autores = master[master['ganancias_generadas'] > 0].copy()\n",
            "y = np.arange(len(top_autores))\n",
            "height = 0.35\n",
            "\n",
            "ax1 = axes[0, 0]\n",
            "ax1.barh(y - height/2, top_autores['ganancias_generadas'], height, label='Ganancias Generadas ($)', color='#1f77b4', alpha=0.9)\n",
            "ax1.barh(y + height/2, top_autores['regalias_cobradas'], height, label='Regalías Cobradas ($)', color='#2ca02c', alpha=0.9)\n",
            "ax1.set_yticks(y)\n",
            "ax1.set_yticklabels(top_autores['Nombre del Autor'], fontsize=10)\n",
            "ax1.invert_yaxis()\n",
            "ax1.set_xlabel('Monto en USD ($)', fontsize=11, fontweight='bold')\n",
            "ax1.set_title('Top Autores: Ganancias Atribuibles vs Regalías Netas', fontsize=12, fontweight='bold', pad=12)\n",
            "ax1.legend(loc='lower right', frameon=True)\n",
            "for i, v in enumerate(top_autores['ganancias_generadas']):\n",
            "    ax1.text(v + 10, i - height/2, f'${v:,.2f}', va='center', fontsize=9, fontweight='bold', color='#1f77b4')\n",
            "\n",
            "# 2. Conciliación Integral del 100% de Ventas (Gráfico Donut)\n",
            "ax2 = axes[0, 1]\n",
            "pie_labels = ['Autores Registrados', 'Libro Huérfano (PS7777)', 'Remanente Editorial']\n",
            "pie_values = [total_autores, total_huerfano, total_remanente]\n",
            "colors = ['#1f77b4', '#d62728', '#ff7f0e']\n",
            "wedges, texts, autotexts = ax2.pie(\n",
            "    pie_values, labels=pie_labels, autopct='%1.1f%%', startangle=140,\n",
            "    colors=colors, pctdistance=0.75, wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)\n",
            ")\n",
            "for at in autotexts:\n",
            "    at.set_fontsize(10)\n",
            "    at.set_fontweight('bold')\n",
            "    at.set_color('white')\n",
            "ax2.set_title('Conciliación Contable del 100% de Ventas ($3,863.80)', fontsize=12, fontweight='bold', pad=12)\n",
            "\n",
            "# 3. Distribución Geográfica de Autores por Estado\n",
            "ax3 = axes[1, 0]\n",
            "autores_por_estado = df_authors.groupby('state')['au_id'].count().sort_values(ascending=False)\n",
            "sns.barplot(x=autores_por_estado.index, y=autores_por_estado.values, ax=ax3, palette='Blues_r')\n",
            "ax3.set_title('Distribución Geográfica de Autores por Estado', fontsize=12, fontweight='bold', pad=12)\n",
            "ax3.set_xlabel('Estado', fontsize=11, fontweight='bold')\n",
            "ax3.set_ylabel('Número de Autores', fontsize=11, fontweight='bold')\n",
            "for i, v in enumerate(autores_por_estado.values):\n",
            "    ax3.text(i, v + 0.3, str(v), ha='center', fontsize=10, fontweight='bold')\n",
            "\n",
            "# 4. Comparativa: Ventas en Órdenes (sales) vs Ventas Históricas (ytd_sales)\n",
            "ax4 = axes[1, 1]\n",
            "comparativa_ventas = df_titles.copy()\n",
            "comparativa_ventas = comparativa_ventas.merge(\n",
            "    df_sales.groupby('title_id')['qty'].sum().reset_index(name='sales_qty'), \n",
            "    on='title_id', \n",
            "    how='left'\n",
            ").fillna(0)\n",
            "comparativa_ventas['sales_monto'] = comparativa_ventas['sales_qty'] * comparativa_ventas['price']\n",
            "comparativa_ventas['ytd_monto'] = comparativa_ventas['ytd_sales'] * comparativa_ventas['price']\n",
            "top_libros = comparativa_ventas.sort_values(by='ytd_monto', ascending=False).head(7)\n",
            "\n",
            "x = np.arange(len(top_libros))\n",
            "ax4.bar(x - height/2, top_libros['sales_monto'], height, label='Órdenes (sales)', color='#17becf')\n",
            "ax4.bar(x + height/2, top_libros['ytd_monto'], height, label='Catálogo Anual (ytd_sales)', color='#9467bd')\n",
            "ax4.set_xticks(x)\n",
            "ax4.set_xticklabels(top_libros['title_id'], rotation=45, fontsize=10)\n",
            "ax4.set_title('Comparativa: Ventas en Órdenes vs Ventas Históricas (YTD)', fontsize=12, fontweight='bold', pad=12)\n",
            "ax4.set_ylabel('Monto en USD ($)', fontsize=11, fontweight='bold')\n",
            "ax4.legend(loc='upper right', frameon=True)\n",
            "\n",
            "plt.show()"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 24: CONCLUSIÓN Y RESUMEN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 🎯 Conclusiones del Proyecto y Hallazgos de Ingeniería\n",
            "\n",
            "1. **Cumplimiento de la Restricción de JOINs:** Se demostró que es posible construir un pipeline analítico y contable empresarial de la más alta precisión extrayendo tablas en bruto con **0 JOINs** y delegando el álgebra relacional a **Pandas**.\n",
            "2. **Resolución de Anomalías Relacionales:** El intento ingenuo produjo un desfase de **+$845.10** debido a la duplicidad cartesiana de libros multi-autor (\\$1,044.85) y la exclusión de libros huérfanos (\\$199.75). Ambas anomalías fueron corregidas y conciliadas con **\\$0.00 de discrepancia residual**.\n",
            "3. **Inclusión Integral de la Población:** Al utilizar uniones izquierdas (`LEFT JOIN` en Pandas), se garantizó que los 23 autores figuren en el informe directivo, distinguiendo formalmente entre facturación generada (\\$2,893.50) y regalías cobradas (\\$307.45).\n",
            "4. **Certificación Contable al 100%:** La empresa facturó exactamente **\\$3,863.80**, monto que quedó auditado y distribuido entre autores (74.89%), libros huérfanos (5.17%) y remanente editorial (19.94%)."
        ]
    })

    # Construir estructura de notebook JSON
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    # Guardar archivo sin ejecutar
    print(f"💾 Guardando notebook base en: {NOTEBOOK_PATH_ANALISIS}")
    with open(NOTEBOOK_PATH_ANALISIS, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)

    # Ejecutar notebook con nbclient para pre-renderizar todas las salidas
    print("⚙️ Pre-renderizando todas las celdas con NotebookClient...")
    with open(NOTEBOOK_PATH_ANALISIS, "r", encoding="utf-8") as f:
        nb_obj = nbformat.read(f, as_version=4)

    client = NotebookClient(nb_obj, timeout=300, kernel_name="python3")
    client.execute()

    print(f"💾 Guardando notebook pre-renderizado en: {NOTEBOOK_PATH_ANALISIS}")
    with open(NOTEBOOK_PATH_ANALISIS, "w", encoding="utf-8") as f:
        nbformat.write(nb_obj, f)

    print(f"💾 Guardando copia pre-renderizada en: {NOTEBOOK_PATH_PRACTICA1}")
    with open(NOTEBOOK_PATH_PRACTICA1, "w", encoding="utf-8") as f:
        nbformat.write(nb_obj, f)

    print("🎉 ¡Notebooks generados y pre-renderizados con éxito!")


if __name__ == "__main__":
    build_practica1_notebook()

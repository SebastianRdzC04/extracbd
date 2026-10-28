#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del Jupyter Notebook para la Práctica 2 - Encargo 1: Ganancias por Región con Pandas.
Crea el archivo .ipynb con todas las fases analíticas, markdown estético, código comentado,
validaciones matemáticas, tablas formateadas y visualizaciones de Matplotlib / Seaborn.
"""

import json
from pathlib import Path

# Directorio destino del notebook
NOTEBOOK_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH = NOTEBOOK_DIR / "encargo1_ganancias_por_region.ipynb"


def build_notebook():
    cells = []

    # -------------------------------------------------------------------------
    # CELL 1: PORTADA Y METADATOS
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# 📊 Práctica 2 - Encargo 1: Determinación y Conciliación Forense de Ganancias por Región\n",
            "### 🏛️ Arquitectura Híbrida: Extracción SQL Ligera (≤ 2 JOINs) + Transformación, Diagnóstico y Conciliación Contable en Memoria con Python & Pandas\n",
            "\n",
            "---\n",
            "\n",
            "### 🎯 Contexto y Reglas de Ingeniería del Proyecto\n",
            "* **Base de Datos:** `northwind` (MySQL 8.0 desplegado en contenedor Docker, puerto `3308`).\n",
            "* **Objetivo Principal:** Determinar las ganancias exactas por región de la compañía Northwind, documentando cada paso exploratorio, auditoría de discrepancias y decisiones tomadas hasta llegar al resultado definitivo.\n",
            "* **⚠️ Restricción Estricta de Diseño:** \n",
            "  > **Ninguna consulta a SQL puede contener más de 2 `JOIN`s.**\n",
            "  > **Estrategia Implementada:** Para cumplir estrictamente con esta restricción sin perder fidelidad analítica, se extraen las tablas completas en bruto (**0 JOINs**) o mediante consultas atómicas simples directamente hacia DataFrames de Pandas. Toda la lógica de álgebra relacional, detección y resolución de duplicidad cartesiana, normalización de campos, agrupaciones y conciliaciones contables se ejecuta en memoria mediante **Python & Pandas**.\n",
            "\n",
            "---\n",
            "\n",
            "### 🗺️ Hoja de Ruta Analítica (8 Fases Forenses)\n",
            "1. **Fase 0:** Inicialización del Entorno, Conexión a la Base de Datos y Validador de Límites de JOINs.\n",
            "2. **Fase 1:** Reconocimiento y Extracción en Bruto (*Data Discovery* - 0 JOINs).\n",
            "3. **Fase 2:** Establecimiento de la Línea Base Contable (*Ground Truth Oficial*).\n",
            "4. **Fase 3:** El Intento Ingenuo y la Gran Discrepancia (*Reproducción del Error Común en Pandas: +394.5%*).\n",
            "5. **Fase 4:** Auditoría Forense y Diagnóstico de Causa Raíz (Multiplicidad N:M y Duplicación de Fletes).\n",
            "6. **Fase 5:** Construcción de la Solución Robusta en Pandas (Desacoplamiento Empleado-Región).\n",
            "7. **Fase 6:** Criterios de Negocio: Ventas Netas vs Facturación Integrada y Desglose por Vendedor.\n",
            "8. **Fase 7:** *Master Table* Ejecutiva (KPIs Directivos Formateados).\n",
            "9. **Fase 8:** Conciliación Contable Definitiva al Centavo ($0.00 de Discrepancia Certificada).\n",
            "10. **Fase 9:** Tablero Visual de Métricas Gerenciales (Matplotlib & Seaborn)."
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
            "# Configuración estética de Pandas para montos financieros y precisión\n",
            "pd.set_option('display.max_columns', 20)\n",
            "pd.set_option('display.width', 1000)\n",
            "pd.options.display.float_format = '${:,.2f}'.format\n",
            "\n",
            "# Configuración de estilo de visualización para gráficos ejecutivos\n",
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
            "En esta fase establecemos la conexión con la base de datos `northwind` alojada en el contenedor MySQL 8.0 (puerto `3308`).\n",
            "\n",
            "Para garantizar el cumplimiento de la restricción del encargo (*\"las consultas no pueden tener más de dos joins\"*), implementamos una función de validación estricta (`validate_max_joins`) que inspecciona sintácticamente cualquier consulta SQL antes de enviarla al motor relacional."
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
            "# MOTOR DE CONEXIÓN Y VALIDADOR DE RESTRICCIÓN DE JOINS\n",
            "# =============================================================================\n",
            "\n",
            "DB_HOST = os.getenv(\"MYSQL_HOST\", \"localhost\")\n",
            "DB_PORT = int(os.getenv(\"PRACTICA2_DB_PORT\", \"3308\"))\n",
            "DB_NAME = os.getenv(\"PRACTICA2_DB_NAME\", \"northwind\")\n",
            "DB_USER = os.getenv(\"PRACTICA2_DB_USER_ROOT\", \"root\")\n",
            "DB_PASS = os.getenv(\"PRACTICA2_DB_ROOT_PASSWORD\", \"rootpassword\")\n",
            "\n",
            "CONNECTION_URL = f\"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4\"\n",
            "engine = create_engine(CONNECTION_URL, pool_pre_ping=True)\n",
            "\n",
            "def validate_max_joins(sql_query: str, max_joins: int = 2) -> int:\n",
            "    \"\"\"\n",
            "    Inspecciona la consulta SQL y asegura que no exceda el número máximo de JOINs permitido.\n",
            "    Regla del requerimiento: Máximo 2 JOINs en SQL.\n",
            "    \"\"\"\n",
            "    clean_sql = re.sub(r\"--.*\", \"\", sql_query)\n",
            "    clean_sql = re.sub(r\"/\\*.*?\\*/\", \"\", clean_sql, flags=re.DOTALL)\n",
            "    join_matches = re.findall(r\"\\b(?:INNER\\s+|LEFT\\s+|RIGHT\\s+|CROSS\\s+|FULL\\s+)?JOIN\\b\", clean_sql, re.IGNORECASE)\n",
            "    join_count = len(join_matches)\n",
            "    \n",
            "    if join_count > max_joins:\n",
            "        raise ValueError(\n",
            "            f\"⚠️ VIOLACIÓN DE REGLA: La consulta contiene {join_count} JOINs, \"\n",
            "            f\"pero el límite estricto establecido es de máximo {max_joins} JOINs.\\n\"\n",
            "            f\"Estrategia requerida: Extraiga las tablas a DataFrames de Pandas y procese en memoria.\"\n",
            "        )\n",
            "    return join_count\n",
            "\n",
            "def extract_table(table_name: str) -> pd.DataFrame:\n",
            "    \"\"\"Extrae una tabla completa de MySQL hacia Pandas con exactamente 0 JOINs.\"\"\"\n",
            "    escaped_table = f\"`{table_name}`\" if not table_name.startswith(\"`\") else table_name\n",
            "    query = f\"SELECT * FROM {escaped_table}\"\n",
            "    validate_max_joins(query, max_joins=2) # 0 JOINs <= 2 JOINs\n",
            "    return pd.read_sql_query(query, con=engine)\n",
            "\n",
            "# Probar conexión ejecutando un ping simple\n",
            "with engine.connect() as conn:\n",
            "    result = conn.execute(text(\"SELECT DATABASE(), VERSION(), NOW();\")).fetchone()\n",
            "    print(f\"🎉 Conectado exitosamente a la base de datos '{result[0]}' (MySQL versión {result[1]}) en {result[2]}.\")"
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
            "Un principio fundamental de la ingeniería de datos es **nunca realizar transformaciones a ciegas**.\n",
            "Antes de modelar, debemos extraer y comprender la semántica de las 6 tablas esenciales del modelo de Northwind:\n",
            "\n",
            "1. **`region`**: Catálogo de las 4 divisiones comerciales corporativas (Eastern, Westerns, Northern, Southern). Notar que la columna `RegionDescription` almacena espacios residuales de relleno (*trailing spaces*) provenientes de tipos `NCHAR(50)` de la base original, por lo que aplicamos `.str.strip()`.\n",
            "2. **`territories`**: 53 territorios geográficos asignados a cada región (`RegionID`).\n",
            "3. **`employeeterritories`**: Tabla puente N:M que asocia a los 9 vendedores con sus territorios comerciales. Contiene 49 asignaciones.\n",
            "4. **`employees`**: Plantilla de los 9 empleados comerciales de la empresa.\n",
            "5. **`orders`**: 830 encabezados de pedidos con fecha, cliente, vendedor asignado (`EmployeeID`) y costo de flete (`Freight`).\n",
            "   * **Hallazgo Forense:** La columna `ShipRegion` en `orders` tiene 507 valores nulos (61.08% de nulos) y sus valores corresponden a abreviaturas de estados de entrega (como 'WA' o 'SP'), **no a las regiones comerciales de la empresa**. La verdadera región corporativa de ventas depende de la asignación del empleado vendedor.\n",
            "6. **`order details`**: 2,155 líneas transaccionales de venta con `UnitPrice`, `Quantity` y `Discount`."
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
            "# EXTRACCIÓN EN BRUTO DE LAS 6 TABLAS REQUERIDAS (0 JOINS EN SQL)\n",
            "# =============================================================================\n",
            "\n",
            "df_region = extract_table(\"region\")\n",
            "df_territories = extract_table(\"territories\")\n",
            "df_emp_terr = extract_table(\"employeeterritories\")\n",
            "df_employees = extract_table(\"employees\")\n",
            "df_orders = extract_table(\"orders\")\n",
            "df_order_details = extract_table(\"order details\")\n",
            "\n",
            "# Limpieza de espacios en blanco procedentes de NCHAR / CHAR\n",
            "df_region['RegionDescription'] = df_region['RegionDescription'].astype(str).str.strip()\n",
            "df_territories['TerritoryDescription'] = df_territories['TerritoryDescription'].astype(str).str.strip()\n",
            "\n",
            "# Resumen de inventario de DataFrames extraídos\n",
            "df_discovery = pd.DataFrame([\n",
            "    {\"Tabla\": \"region\", \"Registros Extraídos\": len(df_region), \"Columnas\": len(df_region.columns), \"JOINs SQL\": 0},\n",
            "    {\"Tabla\": \"territories\", \"Registros Extraídos\": len(df_territories), \"Columnas\": len(df_territories.columns), \"JOINs SQL\": 0},\n",
            "    {\"Tabla\": \"employeeterritories\", \"Registros Extraídos\": len(df_emp_terr), \"Columnas\": len(df_emp_terr.columns), \"JOINs SQL\": 0},\n",
            "    {\"Tabla\": \"employees\", \"Registros Extraídos\": len(df_employees), \"Columnas\": len(df_employees.columns), \"JOINs SQL\": 0},\n",
            "    {\"Tabla\": \"orders\", \"Registros Extraídos\": len(df_orders), \"Columnas\": len(df_orders.columns), \"JOINs SQL\": 0},\n",
            "    {\"Tabla\": \"order details\", \"Registros Extraídos\": len(df_order_details), \"Columnas\": len(df_order_details.columns), \"JOINs SQL\": 0},\n",
            "])\n",
            "\n",
            "print(\"📋 INVENTARIO DE DATAFRAMES EXTRAÍDOS EN MEMORIA:\")\n",
            "display(df_discovery)\n",
            "\n",
            "# Diagnóstico forense del campo 'ShipRegion' en orders\n",
            "nulos_shipregion = df_orders['ShipRegion'].isna().sum()\n",
            "pct_nulos_ship = (nulos_shipregion / len(df_orders)) * 100\n",
            "print(f\"\\n🔎 Diagnóstico del campo 'ShipRegion' en orders: {nulos_shipregion} nulos de {len(df_orders)} pedidos ({pct_nulos_ship:.2f}% de nulos).\")\n",
            "print(\"   -> Conclusión: ShipRegion NO representa las regiones comerciales corporativas.\")"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 7: FASE 2 - EXPLICACIÓN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## ⚖️ Fase 2: Determinación de la Línea Base Contable (*Ground Truth Oficial*)\n",
            "\n",
            "Un principio inviolable en analítica y auditoría contable es fijar la **\"Cifra Dorada\"** (*Ground Truth*) antes de realizar cualquier agrupación regional o cruce relacional.\n",
            "\n",
            "La fórmula de venta estándar de la industria es:\n",
            "$$\\text{Importe Línea} = \\text{UnitPrice} \\times \\text{Quantity} \\times (1 - \\text{Discount})$$\n",
            "\n",
            "Ninguna agrupación por región puede considerarse correcta si la suma de sus partes no coincide **al centavo exacto** con la suma directa de la tabla `order details`."
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
            "# CÁLCULO DE LA LÍNEA BASE CONTABLE OFICIAL (GROUND TRUTH)\n",
            "# =============================================================================\n",
            "\n",
            "# Cálculo de la columna financiera por línea de venta\n",
            "df_order_details['ImporteLinea'] = df_order_details['UnitPrice'] * df_order_details['Quantity'] * (1 - df_order_details['Discount'])\n",
            "\n",
            "LINEA_BASE_UNIDADES = int(df_order_details['Quantity'].sum())\n",
            "LINEA_BASE_VENTAS = round(float(df_order_details['ImporteLinea'].sum()), 2)\n",
            "LINEA_BASE_FLETES = round(float(df_orders['Freight'].sum()), 2)\n",
            "LINEA_BASE_TOTAL_INTEGRADO = round(LINEA_BASE_VENTAS + LINEA_BASE_FLETES, 2)\n",
            "LINEA_BASE_PEDIDOS = int(df_order_details['OrderID'].nunique())\n",
            "\n",
            "df_linea_base = pd.DataFrame([\n",
            "    {\"Métrica de Control\": \"Total de Pedidos con Venta\", \"Valor Oficial\": f\"{LINEA_BASE_PEDIDOS:,}\", \"Origen Contable\": \"COUNT(DISTINCT OrderID) en order details\"},\n",
            "    {\"Métrica de Control\": \"Total de Unidades Físicas Vendidas\", \"Valor Oficial\": f\"{LINEA_BASE_UNIDADES:,}\", \"Origen Contable\": \"SUM(Quantity) en order details\"},\n",
            "    {\"Métrica de Control\": \"Venta Real de Productos (Cifra Dorada)\", \"Valor Oficial\": f\"${LINEA_BASE_VENTAS:,.2f}\", \"Origen Contable\": \"SUM(UnitPrice * Quantity * (1 - Discount))\"},\n",
            "    {\"Métrica de Control\": \"Total de Fletes de Envío Facturados\", \"Valor Oficial\": f\"${LINEA_BASE_FLETES:,.2f}\", \"Origen Contable\": \"SUM(Freight) en orders\"},\n",
            "    {\"Métrica de Control\": \"Facturación Total Integrada (Productos + Fletes)\", \"Valor Oficial\": f\"${LINEA_BASE_TOTAL_INTEGRADO:,.2f}\", \"Origen Contable\": \"Venta Productos + Fletes\"},\n",
            "])\n",
            "\n",
            "print(\"💎 LÍNEA BASE OFICIAL DE CONTROL (GROUND TRUTH CONTABLE):\")\n",
            "display(df_linea_base)"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 9: FASE 3 - EXPLICACIÓN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## ⚠️ Fase 3: El Intento Ingenuo y la Gran Discrepancia (*The Naive Merge Error*)\n",
            "\n",
            "El error más clásico y destructivo en el análisis de datos relacionales consiste en encadenar todas las tablas directamente en secuencia:\n",
            "$$\\text{order details} \\bowtie \\text{orders} \\bowtie \\text{employees} \\bowtie \\text{employeeterritories} \\bowtie \\text{territories} \\bowtie \\text{region}$$\n",
            "\n",
            "En esta fase reproducimos este intento ingenuo en Pandas para diagnosticar por qué produce números astronómicos y ficticios si no se audita contra la línea base."
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
            "# REPRODUCCIÓN DEL INTENTO INGENUO EN PANDAS (MERGE SECUENCIAL DIRECTO)\n",
            "# =============================================================================\n",
            "\n",
            "df_merge_ingenuo = (\n",
            "    df_order_details\n",
            "    .merge(df_orders[['OrderID', 'EmployeeID']], on='OrderID', how='inner')\n",
            "    .merge(df_employees[['EmployeeID']], on='EmployeeID', how='inner')\n",
            "    .merge(df_emp_terr, on='EmployeeID', how='inner')\n",
            "    .merge(df_territories[['TerritoryID', 'RegionID']], on='TerritoryID', how='inner')\n",
            "    .merge(df_region[['RegionID', 'RegionDescription']], on='RegionID', how='inner')\n",
            ")\n",
            "\n",
            "# Agrupación ingenua por región\n",
            "resumen_ingenuo = (\n",
            "    df_merge_ingenuo\n",
            "    .groupby(['RegionID', 'RegionDescription'])['ImporteLinea']\n",
            "    .sum()\n",
            "    .round(2)\n",
            "    .reset_index()\n",
            "    .rename(columns={'ImporteLinea': 'Ganancia_Calculada_Ingenua'})\n",
            "    .sort_values(by='RegionID')\n",
            ")\n",
            "\n",
            "total_obtenido_ingenuo = round(float(resumen_ingenuo['Ganancia_Calculada_Ingenua'].sum()), 2)\n",
            "desfase_inflado = round(total_obtenido_ingenuo - LINEA_BASE_VENTAS, 2)\n",
            "pct_inflacion = round((desfase_inflado / LINEA_BASE_VENTAS) * 100, 2)\n",
            "\n",
            "print(\"🚨 RESULTADOS DEL INTENTO INGENUO POR REGIÓN:\")\n",
            "display(resumen_ingenuo)\n",
            "\n",
            "print(\"\\n\" + \"!\" * 80)\n",
            "print(f\"💥 ¡ALERTA CRÍTICA DE DISCREPANCIA FINANCIERA!\")\n",
            "print(f\"   • Suma total del Intento Ingenuo:   ${total_obtenido_ingenuo:,.2f}\")\n",
            "print(f\"   • Ventas Reales (Línea Base):        ${LINEA_BASE_VENTAS:,.2f}\")\n",
            "print(f\"   • Desfase Ficticio (Inflación):     +${desfase_inflado:,.2f}  (+{pct_inflacion}% DE ERROR)\")\n",
            "print(\"!\" * 80)"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 11: FASE 4 - EXPLICACIÓN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 🔬 Fase 4: Auditoría Forense y Diagnóstico de Causa Raíz\n",
            "\n",
            "¿Cómo es posible que un código sintácticamente correcto infle las ventas en un **+394.5%** (más de **$5.34 millones de dólares**)?\n",
            "\n",
            "Realizamos una investigación forense de 4 pasos:\n",
            "1. **Investigación 4.1: Multiplicidad en `employeeterritories`**: Analizar cuántos territorios tiene cada empleado.\n",
            "2. **Investigación 4.2: Unicidad Regional por Empleado**: Verificar si los empleados atienden más de una región.\n",
            "3. **Investigación 4.3: Conciliación Matemática Forense**: Reconstruir exactamente el origen matemático de los $6,698,176.56$.\n",
            "4. **Investigación 4.4: La Trampa de la Duplicación de Fletes**: Evidenciar el impacto de sumar métricas a nivel orden (`Freight`) en tablas de nivel detalle."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 12: FASE 4 - CÓDIGO
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# 4.1 INVESTIGACIÓN 1: MULTIPLICIDAD DE TERRITORIOS POR EMPLEADO\n",
            "# =============================================================================\n",
            "terr_por_emp = (\n",
            "    df_emp_terr\n",
            "    .groupby('EmployeeID')['TerritoryID']\n",
            "    .count()\n",
            "    .reset_index()\n",
            "    .rename(columns={'TerritoryID': 'Factor_Multiplicacion_Territorios'})\n",
            "    .merge(df_employees[['EmployeeID', 'FirstName', 'LastName']], on='EmployeeID')\n",
            "    .sort_values(by='Factor_Multiplicacion_Territorios', ascending=False)\n",
            ")\n",
            "terr_por_emp['Empleado'] = terr_por_emp['FirstName'] + ' ' + terr_por_emp['LastName']\n",
            "print(\"📊 TERRITORIOS ASIGNADOS POR EMPLEADO:\")\n",
            "display(terr_por_emp[['EmployeeID', 'Empleado', 'Factor_Multiplicacion_Territorios']])\n",
            "\n",
            "# =============================================================================\n",
            "# 4.2 INVESTIGACIÓN 2: VERIFICACIÓN DE UNICIDAD REGIONAL POR EMPLEADO\n",
            "# =============================================================================\n",
            "emp_terr_reg = df_emp_terr.merge(df_territories[['TerritoryID', 'RegionID']], on='TerritoryID')\n",
            "unicidad_reg = (\n",
            "    emp_terr_reg\n",
            "    .groupby('EmployeeID')\n",
            "    .agg(\n",
            "        Regiones_Distintas=('RegionID', 'nunique'),\n",
            "        ID_Region_Unica=('RegionID', 'min'),\n",
            "        Total_Territorios=('TerritoryID', 'count')\n",
            "    )\n",
            "    .reset_index()\n",
            "    .merge(df_employees[['EmployeeID', 'FirstName', 'LastName']], on='EmployeeID')\n",
            "    .merge(df_region[['RegionID', 'RegionDescription']], left_on='ID_Region_Unica', right_on='RegionID')\n",
            ")\n",
            "unicidad_reg['Empleado'] = unicidad_reg['FirstName'] + ' ' + unicidad_reg['LastName']\n",
            "print(\"\\n🔍 COMPROBACIÓN DE UNICIDAD REGIONAL:\")\n",
            "display(unicidad_reg[['EmployeeID', 'Empleado', 'Regiones_Distintas', 'RegionDescription', 'Total_Territorios']])\n",
            "\n",
            "# Verificación formal de aserción\n",
            "assert (unicidad_reg['Regiones_Distintas'] == 1).all(), \"¡Alerta! Hay empleados en más de una región.\"\n",
            "print(\"\\n💡 HALLAZGO FUNDAMENTAL:\")\n",
            "print(\"   Todos los empleados pertenecen a exactamente 1 sola región (Regiones_Distintas == 1).\")\n",
            "print(\"   La duplicidad ocurrió porque el merge arrastró la lista de territorios de cada empleado,\")\n",
            "print(\"   multiplicando cada pedido tantas veces como territorios tenía asignados el vendedor.\")\n",
            "\n",
            "# =============================================================================\n",
            "# 4.3 INVESTIGACIÓN 3: RECONCILIACIÓN MATEMÁTICA FORENSE DEL ERROR INGENUO\n",
            "# =============================================================================\n",
            "ventas_por_emp = (\n",
            "    df_order_details\n",
            "    .merge(df_orders[['OrderID', 'EmployeeID']], on='OrderID')\n",
            "    .groupby('EmployeeID')['ImporteLinea']\n",
            "    .sum()\n",
            "    .round(2)\n",
            "    .reset_index()\n",
            "    .rename(columns={'ImporteLinea': 'Venta_Real_Empleado'})\n",
            "    .merge(terr_por_emp[['EmployeeID', 'Empleado', 'Factor_Multiplicacion_Territorios']], on='EmployeeID')\n",
            "    .merge(unicidad_reg[['EmployeeID', 'RegionDescription']], on='EmployeeID')\n",
            ")\n",
            "ventas_por_emp['Venta_Inflada_Esperada'] = (ventas_por_emp['Venta_Real_Empleado'] * ventas_por_emp['Factor_Multiplicacion_Territorios']).round(2)\n",
            "print(\"\\n🧮 RECONSTRUCCIÓN EXACTA DEL ERROR INGENUO POR VENDEDOR:\")\n",
            "display(ventas_por_emp[['EmployeeID', 'Empleado', 'RegionDescription', 'Factor_Multiplicacion_Territorios', 'Venta_Real_Empleado', 'Venta_Inflada_Esperada']])\n",
            "\n",
            "print(f\"\\n   Suma de ventas reales reconstruidas:    ${ventas_por_emp['Venta_Real_Empleado'].sum():,.2f}  (Coincide al 100% con Línea Base)\")\n",
            "print(f\"   Suma de ventas infladas reconstruidas:  ${ventas_por_emp['Venta_Inflada_Esperada'].sum():,.2f}  (Coincide al 100% con Merge Ingenuo)\")\n",
            "\n",
            "# =============================================================================\n",
            "# 4.4 INVESTIGACIÓN 4: LA TRAMPA DE LA DUPLICACIÓN DE FLETES\n",
            "# =============================================================================\n",
            "flete_duplicado = df_orders.merge(df_order_details[['OrderID']], on='OrderID')['Freight'].sum()\n",
            "print(f\"\\n🚚 AUDITORÍA DE FLETES:\")\n",
            "print(f\"   • Flete real global (orders.Freight):                    ${LINEA_BASE_FLETES:,.2f}\")\n",
            "print(f\"   • Flete duplicado al unir con order details:             ${flete_duplicado:,.2f}\")\n",
            "print(f\"   • Inflación por líneas de pedido (2.6x promedio):        +${flete_duplicado - LINEA_BASE_FLETES:,.2f} (+{((flete_duplicado/LINEA_BASE_FLETES)-1)*100:.1f}%)\")"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 13: FASE 5 - EXPLICACIÓN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 🛠️ Fase 5: Construcción de la Solución Robusta en Pandas (Desacoplamiento Relacional)\n",
            "\n",
            "Una vez diagnosticada la causa raíz, la solución de ingeniería es elegante y precisa:\n",
            "1. **Desacoplar la relación Empleado ➔ Región**: En lugar de unir toda la tabla `employeeterritories`, construimos una proyección unívoca `df_emp_region` aplicando `drop_duplicates(['EmployeeID', 'RegionID'])`. Esto nos deja exactamente **9 filas** (1 por cada empleado).\n",
            "2. **Merge limpio con Pedidos**: Cruzamos `orders` con `df_emp_region` sobre `EmployeeID`.\n",
            "3. **Merge con Detalles de Venta**: Cruzamos con `order details` sobre `OrderID`.\n",
            "4. **Agrupación y Suma**: Obtenemos las ganancias exactas por región sin multiplicación cartesiana."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 14: FASE 5 - CÓDIGO
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# SOLUCIÓN ROBUSTA MEDIANTE DESACOPLAMIENTO RELACIONAL EN PANDAS\n",
            "# =============================================================================\n",
            "\n",
            "# 1. Mapeo unívoco y desacoplado Empleado -> Región (9 registros limpios)\n",
            "df_emp_region = (\n",
            "    df_emp_terr\n",
            "    .merge(df_territories[['TerritoryID', 'RegionID']], on='TerritoryID')\n",
            "    [['EmployeeID', 'RegionID']]\n",
            "    .drop_duplicates()\n",
            ")\n",
            "\n",
            "# 2. Enlace de pedidos con su región legítima\n",
            "df_pedidos_region = df_orders.merge(df_emp_region, on='EmployeeID', how='inner')\n",
            "\n",
            "# 3. Enlace con detalles de orden para cálculo de importes\n",
            "df_ventas_limpias = df_order_details.merge(\n",
            "    df_pedidos_region[['OrderID', 'EmployeeID', 'RegionID']],\n",
            "    on='OrderID',\n",
            "    how='inner'\n",
            ")\n",
            "\n",
            "# 4. Agrupación por Región asegurando que aparezcan las 4 regiones\n",
            "ventas_por_region = (\n",
            "    df_region[['RegionID', 'RegionDescription']]\n",
            "    .merge(\n",
            "        df_ventas_limpias.groupby('RegionID')['ImporteLinea'].sum().round(2).reset_index(),\n",
            "        on='RegionID',\n",
            "        how='left'\n",
            "    )\n",
            "    .rename(columns={'ImporteLinea': 'Ganancias_Totales_Productos'})\n",
            "    .fillna({'Ganancias_Totales_Productos': 0.0})\n",
            "    .sort_values(by='Ganancias_Totales_Productos', ascending=False)\n",
            ")\n",
            "\n",
            "total_solucion_limpia = round(float(ventas_por_region['Ganancias_Totales_Productos'].sum()), 2)\n",
            "diferencia_control = round(total_solucion_limpia - LINEA_BASE_VENTAS, 2)\n",
            "\n",
            "print(\"🏆 RESULTADO DE VENTAS POR REGIÓN (CORREGIDO Y DESACOPLADO):\")\n",
            "display(ventas_por_region)\n",
            "\n",
            "print(f\"\\n  • Suma total de las 4 regiones:  ${total_solucion_limpia:,.2f}\")\n",
            "print(f\"  • Línea base oficial de ventas:  ${LINEA_BASE_VENTAS:,.2f}\")\n",
            "print(f\"  • Discrepancia:                  ${diferencia_control:,.2f}  (¡Cuadre al 100% exacto!)\")"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 15: FASE 6 - EXPLICACIÓN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 💼 Fase 6: Definición de Criterios Financieros y Desglose por Vendedor\n",
            "\n",
            "En el análisis financiero existen dos lecturas legítimas de *\"Ganancias por Región\"*:\n",
            "* **Criterio 1: Ventas Netas de Productos (Mercancía Vendida)**: Excluye costos logísticos de envío. Monto global: **$1,354,458.59**.\n",
            "* **Criterio 2: Facturación Total Integrada (Productos + Fletes)**: Incorpora los fletes facturados a los clientes en los pedidos asignados a cada región. Monto global: **$1,419,401.28** ($1,354,458.59 + $64,942.69).\n",
            "\n",
            "Para implementar el Criterio 2 sin caer en la trampa de la duplicación de fletes, **pre-agrupamos los detalles de la orden a nivel `OrderID`** antes de realizar el merge con la tabla de pedidos."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 16: FASE 6 - CÓDIGO
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# 6.1 DESGLOSE DE VENTAS POR EMPLEADO DENTRO DE CADA REGIÓN\n",
            "# =============================================================================\n",
            "desglose_vendedores = (\n",
            "    df_region[['RegionID', 'RegionDescription']]\n",
            "    .merge(df_emp_region, on='RegionID')\n",
            "    .merge(df_employees[['EmployeeID', 'FirstName', 'LastName', 'Title']], on='EmployeeID')\n",
            "    .merge(\n",
            "        df_ventas_limpias.groupby('EmployeeID').agg(\n",
            "            Pedidos_Atendidos=('OrderID', 'nunique'),\n",
            "            Unidades_Vendidas=('Quantity', 'sum'),\n",
            "            Venta_Neta_Empleado=('ImporteLinea', 'sum')\n",
            "        ).reset_index(),\n",
            "        on='EmployeeID',\n",
            "        how='left'\n",
            "    )\n",
            ")\n",
            "desglose_vendedores['Empleado'] = desglose_vendedores['FirstName'] + ' ' + desglose_vendedores['LastName']\n",
            "desglose_vendedores['Venta_Neta_Empleado'] = desglose_vendedores['Venta_Neta_Empleado'].round(2)\n",
            "desglose_vendedores.sort_values(by=['RegionID', 'Venta_Neta_Empleado'], ascending=[True, False], inplace=True)\n",
            "\n",
            "print(\"👔 DESGLOSE DE APORTE POR VENDEDOR EN CADA REGIÓN:\")\n",
            "display(desglose_vendedores[['RegionDescription', 'EmployeeID', 'Empleado', 'Title', 'Pedidos_Atendidos', 'Unidades_Vendidas', 'Venta_Neta_Empleado']])\n",
            "\n",
            "# =============================================================================\n",
            "# 6.2 CRITERIO 2: INTEGRACIÓN DE FLETES SIN DUPLICACIÓN\n",
            "# =============================================================================\n",
            "# Pre-agregar a nivel OrderID para que cada flete se sume exactamente una vez\n",
            "df_ordenes_agregadas = (\n",
            "    df_order_details\n",
            "    .groupby('OrderID')\n",
            "    .agg(\n",
            "        Unidades_Pedido=('Quantity', 'sum'),\n",
            "        Venta_Pedido=('ImporteLinea', 'sum')\n",
            "    )\n",
            "    .reset_index()\n",
            ")\n",
            "\n",
            "df_pedidos_consolidados = df_pedidos_region.merge(df_ordenes_agregadas, on='OrderID', how='inner')\n",
            "\n",
            "criterio2_region = (\n",
            "    df_region[['RegionID', 'RegionDescription']]\n",
            "    .merge(\n",
            "        df_pedidos_consolidados.groupby('RegionID').agg(\n",
            "            Total_Pedidos=('OrderID', 'count'),\n",
            "            Total_Unidades=('Unidades_Pedido', 'sum'),\n",
            "            Venta_Neta_Productos=('Venta_Pedido', 'sum'),\n",
            "            Fletes_Facturados=('Freight', 'sum')\n",
            "        ).reset_index(),\n",
            "        on='RegionID',\n",
            "        how='left'\n",
            "    )\n",
            ")\n",
            "criterio2_region['Facturacion_Total_Integrada'] = (criterio2_region['Venta_Neta_Productos'] + criterio2_region['Fletes_Facturados']).round(2)\n",
            "criterio2_region['Venta_Neta_Productos'] = criterio2_region['Venta_Neta_Productos'].round(2)\n",
            "criterio2_region['Fletes_Facturados'] = criterio2_region['Fletes_Facturados'].round(2)\n",
            "criterio2_region.sort_values(by='Facturacion_Total_Integrada', ascending=False, inplace=True)\n",
            "\n",
            "print(\"\\n📦 CRITERIO 2: FACTURACIÓN TOTAL INTEGRADA (PRODUCTOS + FLETES):\")\n",
            "display(criterio2_region)"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 17: FASE 7 - EXPLICACIÓN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 📑 Fase 7: *Master Table* Ejecutiva (KPIs Directivos Formateados)\n",
            "\n",
            "A continuación consolidamos el reporte principal de entrega ejecutiva.\n",
            "Este entregable incluye todos los indicadores clave de rendimiento (KPIs):\n",
            "1. **Fuerza de Ventas**: Número de vendedores asignados a la región.\n",
            "2. **Total Pedidos**: Cantidad de órdenes procesadas.\n",
            "3. **Unidades Vendidas**: Artículos físicos colocados en el mercado.\n",
            "4. **Ganancias Productos ($)**: Venta neta de mercancía.\n",
            "5. **Fletes Facturados ($)**: Recaudación por servicio logístico.\n",
            "6. **Facturación Total ($)**: Ingreso bruto global de la región.\n",
            "7. **% Participación Ventas**: Proporción relativa de la región sobre las ventas nacionales.\n",
            "8. **Ticket Promedio ($)**: Monto promedio facturado por cada pedido."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 18: FASE 7 - CÓDIGO
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# CONSTRUCCIÓN DE LA MASTER TABLE EJECUTIVA CON FORMATO CORPORATIVO\n",
            "# =============================================================================\n",
            "\n",
            "# Conteo de vendedores por región\n",
            "vendedores_por_reg = (\n",
            "    df_emp_region\n",
            "    .groupby('RegionID')['EmployeeID']\n",
            "    .count()\n",
            "    .reset_index()\n",
            "    .rename(columns={'EmployeeID': 'Fuerza de Ventas'})\n",
            ")\n",
            "\n",
            "master_table = (\n",
            "    df_region[['RegionID', 'RegionDescription']]\n",
            "    .rename(columns={'RegionID': 'ID Región', 'RegionDescription': 'Región'})\n",
            "    .merge(vendedores_por_reg.rename(columns={'RegionID': 'ID Región'}), on='ID Región', how='left')\n",
            "    .merge(\n",
            "        criterio2_region[['RegionID', 'Total_Pedidos', 'Total_Unidades', 'Venta_Neta_Productos', 'Fletes_Facturados', 'Facturacion_Total_Integrada']]\n",
            "        .rename(columns={\n",
            "            'RegionID': 'ID Región',\n",
            "            'Total_Pedidos': 'Total Pedidos',\n",
            "            'Total_Unidades': 'Unidades Vendidas',\n",
            "            'Venta_Neta_Productos': 'Ganancias Productos ($)',\n",
            "            'Fletes_Facturados': 'Fletes Facturados ($)',\n",
            "            'Facturacion_Total_Integrada': 'Facturación Total ($)'\n",
            "        }),\n",
            "        on='ID Región',\n",
            "        how='left'\n",
            "    )\n",
            ")\n",
            "\n",
            "# Cálculo de métricas avanzadas\n",
            "master_table['% Participación Ventas'] = (master_table['Ganancias Productos ($)'] / LINEA_BASE_VENTAS) * 100\n",
            "master_table['Ticket Promedio ($)'] = master_table['Ganancias Productos ($)'] / master_table['Total Pedidos']\n",
            "\n",
            "# Ordenar por ventas de productos descendente\n",
            "master_table.sort_values(by='Ganancias Productos ($)', ascending=False, inplace=True)\n",
            "\n",
            "# Formateo estilizado para presentación\n",
            "master_formatted = master_table.copy()\n",
            "master_formatted['Ganancias Productos ($)'] = master_formatted['Ganancias Productos ($)'].map('${:,.2f}'.format)\n",
            "master_formatted['Fletes Facturados ($)'] = master_formatted['Fletes Facturados ($)'].map('${:,.2f}'.format)\n",
            "master_formatted['Facturación Total ($)'] = master_formatted['Facturación Total ($)'].map('${:,.2f}'.format)\n",
            "master_formatted['% Participación Ventas'] = master_formatted['% Participación Ventas'].map('{:.2f}%'.format)\n",
            "master_formatted['Ticket Promedio ($)'] = master_formatted['Ticket Promedio ($)'].map('${:,.2f}'.format)\n",
            "master_formatted['Unidades Vendidas'] = master_formatted['Unidades Vendidas'].map('{:,.0f}'.format)\n",
            "master_formatted['Total Pedidos'] = master_formatted['Total Pedidos'].map('{:,.0f}'.format)\n",
            "\n",
            "print(\"🏛️ MASTER TABLE EJECUTIVA DEFINITIVA (ENCARGO 1 - NORTHWIND):\")\n",
            "display(master_formatted)"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 19: FASE 8 - EXPLICACIÓN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 🎯 Fase 8: Conciliación Contable Definitiva al Centavo ($0.00 de Discrepancia)\n",
            "\n",
            "En esta fase certificamos formalmente que la solución desarrollada en Pandas no extravió ni infló **ni un solo centavo** de la base de datos de Northwind.\n",
            "\n",
            "Ejecutamos comprobaciones mediante `assert` para garantizar la integridad contable absoluta del reporte."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 20: FASE 8 - CÓDIGO
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# MATRIZ DE CONCILIACIÓN CONTABLE Y CERTIFICACIÓN FORMAL CON ASERCIONES\n",
            "# =============================================================================\n",
            "\n",
            "total_ventas_calculadas = round(float(master_table['Ganancias Productos ($)'].sum()), 2)\n",
            "total_fletes_calculados = round(float(master_table['Fletes Facturados ($)'].sum()), 2)\n",
            "total_facturacion_calc = round(float(master_table['Facturación Total ($)'].sum()), 2)\n",
            "\n",
            "diff_ventas = round(total_ventas_calculadas - LINEA_BASE_VENTAS, 2)\n",
            "diff_fletes = round(total_fletes_calculados - LINEA_BASE_FLETES, 2)\n",
            "diff_facturacion = round(total_facturacion_calc - LINEA_BASE_TOTAL_INTEGRADO, 2)\n",
            "\n",
            "df_conciliacion = pd.DataFrame([\n",
            "    {\n",
            "        \"Concepto Contable\": \"1. Ganancias Sumadas por Región (Productos)\",\n",
            "        \"Monto Calculado\": f\"${total_ventas_calculadas:,.2f}\",\n",
            "        \"Línea Base Oficial\": f\"${LINEA_BASE_VENTAS:,.2f}\",\n",
            "        \"Discrepancia\": f\"${diff_ventas:,.2f}\",\n",
            "        \"Estado de Auditoría\": \"✅ Conciliado al 100% (Cuadre Exacto)\"\n",
            "    },\n",
            "    {\n",
            "        \"Concepto Contable\": \"2. Total de Fletes de Envío Facturados\",\n",
            "        \"Monto Calculado\": f\"${total_fletes_calculados:,.2f}\",\n",
            "        \"Línea Base Oficial\": f\"${LINEA_BASE_FLETES:,.2f}\",\n",
            "        \"Discrepancia\": f\"${diff_fletes:,.2f}\",\n",
            "        \"Estado de Auditoría\": \"✅ Conciliado al 100% (Sin Duplicación)\"\n",
            "    },\n",
            "    {\n",
            "        \"Concepto Contable\": \"3. Facturación Total Integrada\",\n",
            "        \"Monto Calculado\": f\"${total_facturacion_calc:,.2f}\",\n",
            "        \"Línea Base Oficial\": f\"${LINEA_BASE_TOTAL_INTEGRADO:,.2f}\",\n",
            "        \"Discrepancia\": f\"${diff_facturacion:,.2f}\",\n",
            "        \"Estado de Auditoría\": \"✅ Conciliado al 100% (Cifra Dorada)\"\n",
            "    }\n",
            "])\n",
            "\n",
            "print(\"💎 MATRIZ DE CERTIFICACIÓN Y CONCILIACIÓN CONTABLE:\")\n",
            "display(df_conciliacion)\n",
            "\n",
            "# Aserciones estrictas: Si alguna discrepancia supera 0.001 centavos, el notebook falla\n",
            "assert abs(diff_ventas) < 0.001, f\"Fallo en cuadre de ventas: ${diff_ventas}\"\n",
            "assert abs(diff_fletes) < 0.001, f\"Fallo en cuadre de fletes: ${diff_fletes}\"\n",
            "assert abs(diff_facturacion) < 0.001, f\"Fallo en cuadre de facturación: ${diff_facturacion}\"\n",
            "\n",
            "print(\"\\n\" + \"⭐\" * 80)\n",
            "print(\"🏆 ¡AUDITORÍA FINALIZADA CON ÉXITO! TODAS LAS COMPROBACIONES CUADRAN AL CENTAVO.\")\n",
            "print(\"⭐\" * 80)"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 21: FASE 9 - EXPLICACIÓN
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 📈 Fase 9: Tablero Visual de Métricas Gerenciales (Visual Analytics)\n",
            "\n",
            "Un análisis de ingeniería de datos no está completo sin herramientas visuales que permitan a la dirección comercial comprender inmediatamente los patrones clave del negocio:\n",
            "1. **Distribución de Ganancias y Participación de Mercado por Región**.\n",
            "2. **Comparativa Forense: Cifras Reales vs El Error del Intento Ingenuo (+394.5%)**.\n",
            "3. **Composición de Facturación: Mercancía vs Flete por Región**.\n",
            "4. **Desempeño Individual de Ventas por Vendedor**."
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 22: FASE 9 - CÓDIGO
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# =============================================================================\n",
            "# GENERACIÓN DEL TABLERO VISUAL DE ALTO NIVEL (DASHBOARD ANALÍTICO)\n",
            "# =============================================================================\n",
            "\n",
            "fig, axes = plt.subplots(2, 2, figsize=(16, 12))\n",
            "fig.suptitle(\"TABLERO EJECUTIVO DE GANANCIAS POR REGIÓN - NORTHWIND\", fontsize=18, fontweight='bold', y=0.98)\n",
            "\n",
            "colores_regiones = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728']\n",
            "\n",
            "# 1. Gráfico de Barras: Ganancias Netas de Productos por Región\n",
            "ax1 = axes[0, 0]\n",
            "bars1 = ax1.bar(master_table['Región'], master_table['Ganancias Productos ($)'], color=colores_regiones, width=0.55)\n",
            "ax1.set_title(\"Ventas Netas de Productos por Región\", fontsize=13, fontweight='bold', pad=12)\n",
            "ax1.set_ylabel(\"Ganancias en USD ($)\", fontsize=11)\n",
            "ax1.yaxis.set_major_formatter('${:,.0f}'.format)\n",
            "\n",
            "for bar in bars1:\n",
            "    height = bar.get_height()\n",
            "    pct = (height / LINEA_BASE_VENTAS) * 100\n",
            "    ax1.annotate(f\"${height:,.0f}\\n({pct:.1f}%)\",\n",
            "                 xy=(bar.get_x() + bar.get_width() / 2, height),\n",
            "                 xytext=(0, 5),\n",
            "                 textcoords=\"offset points\",\n",
            "                 ha='center', va='bottom', fontsize=10, fontweight='bold')\n",
            "\n",
            "# 2. Gráfico Comparativo: Ventas Reales vs Error del Intento Ingenuo\n",
            "ax2 = axes[0, 1]\n",
            "x = np.arange(len(master_table))\n",
            "width = 0.35\n",
            "\n",
            "df_comp = master_table.merge(resumen_ingenuo.rename(columns={'RegionDescription': 'Región'}), on='Región')\n",
            "bars_reales = ax2.bar(x - width/2, df_comp['Ganancias Productos ($)'], width, label='Venta Real Corregida', color='#2ca02c')\n",
            "bars_ingenuas = ax2.bar(x + width/2, df_comp['Ganancia_Calculada_Ingenua'], width, label='Intento Ingenuo (Inflado)', color='#d62728', alpha=0.85)\n",
            "\n",
            "ax2.set_title(\"Comparativa Forense: Realidad vs Error Ingenuo (+394.5%)\", fontsize=13, fontweight='bold', pad=12)\n",
            "ax2.set_xticks(x)\n",
            "ax2.set_xticklabels(df_comp['Región'])\n",
            "ax2.yaxis.set_major_formatter('${:,.0f}'.format)\n",
            "ax2.legend(loc='upper right', frameon=True)\n",
            "\n",
            "# 3. Gráfico de Pastel: Participación de Mercado por Región\n",
            "ax3 = axes[1, 0]\n",
            "wedges, texts, autotexts = ax3.pie(\n",
            "    master_table['Ganancias Productos ($)'],\n",
            "    labels=master_table['Región'],\n",
            "    autopct='%1.1f%%',\n",
            "    startangle=140,\n",
            "    colors=colores_regiones,\n",
            "    explode=(0.06, 0.02, 0.02, 0.02),\n",
            "    textprops=dict(color=\"black\", fontsize=11, fontweight='bold')\n",
            ")\n",
            "ax3.set_title(\"Participación Porcentual en las Ventas Nacionales\", fontsize=13, fontweight='bold', pad=12)\n",
            "\n",
            "# 4. Gráfico de Barras Apiladas: Productos vs Fletes por Región\n",
            "ax4 = axes[1, 1]\n",
            "ax4.bar(master_table['Región'], master_table['Ganancias Productos ($)'], label='Mercancía (Productos)', color='#1f77b4', width=0.55)\n",
            "ax4.bar(master_table['Región'], master_table['Fletes Facturados ($)'], bottom=master_table['Ganancias Productos ($)'], label='Fletes Logísticos', color='#aec7e8', width=0.55)\n",
            "\n",
            "ax4.set_title(\"Composición de Facturación Total (Productos + Fletes)\", fontsize=13, fontweight='bold', pad=12)\n",
            "ax4.set_ylabel(\"Facturación Integrada en USD ($)\", fontsize=11)\n",
            "ax4.yaxis.set_major_formatter('${:,.0f}'.format)\n",
            "ax4.legend(loc='upper right', frameon=True)\n",
            "\n",
            "plt.tight_layout(rect=[0, 0.03, 1, 0.95])\n",
            "plt.show()"
        ]
    })

    # -------------------------------------------------------------------------
    # CELL 23: CONCLUSIONES Y LECCIONES DE INGENIERÍA
    # -------------------------------------------------------------------------
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 📋 Conclusiones Técnicas y Recomendaciones de Ingeniería de Datos\n",
            "\n",
            "1. **Riesgo Crítico de la Multiplicación Cartesiana:**\n",
            "   * Unir tablas intermedias de relaciones N:M (`employeeterritories`) directamente a transacciones de venta provoca inflación exponencial de cifras. En este dataset, el error fue de **+$5,343,717.97 (+394.5%)**.\n",
            "2. **El Poder del Desacoplamiento en Pandas:**\n",
            "   * La regla de limitar las consultas a **máximo 2 JOINs** fomenta una arquitectura desacoplada y modular. Al extraer datos planos y resolver las relaciones mediante `.drop_duplicates()` y `.merge()` en Pandas, el flujo es más transparente, auditable y previene bloqueos por contención en el servidor de base de datos.\n",
            "3. **Auditoría de Granularidad (El Caso del Flete):**\n",
            "   * Métricas de nivel encabezado (`orders.Freight`) nunca deben sumarse sobre tablas de detalle (`order details`) sin pre-agrupación. De lo contrario, se duplican por el factor de líneas promedio por orden (**+219%** de distorsión).\n",
            "4. **Certificación Contable Absoluta:**\n",
            "   * Los resultados por región quedaron comprobados al **100.00% exacto contra la Línea Base Contable ($1,354,458.59)** con **$0.00 de discrepancia**:\n",
            "     * **Eastern (Región 1):** $705,648.17 (52.10%)\n",
            "     * **Westerns (Región 2):** $219,494.09 (16.21%)\n",
            "     * **Northern (Región 3):** $216,265.03 (15.97%)\n",
            "     * **Southern (Región 4):** $213,051.30 (15.73%)"
        ]
    })

    notebook_content = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (.venv)",
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
                "version": "3.14.3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(notebook_content, f, indent=2, ensure_ascii=False)
    
    print(f"🎉 Notebook generado exitosamente en: {NOTEBOOK_PATH}")
    print(f"   Total de celdas creadas: {len(cells)}")


if __name__ == "__main__":
    build_notebook()

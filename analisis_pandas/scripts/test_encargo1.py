#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Auditoría y Verificación Técnica para el Encargo 1 con Pandas.
Ejecuta de principio a fin todo el pipeline analítico, validando la lógica,
las discrepancias y las cifras contables al centavo contra Northwind.
"""

import sys
from pathlib import Path

# Agregar directorio raíz de analisis_pandas al PYTHONPATH
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import pandas as pd
import numpy as np
from src.database import get_engine, extract_table, load_query, validate_max_joins


def run_encargo1_audit():
    print("=" * 80)
    print("🚀 INICIANDO AUDITORÍA FORENSE - ENCARGO 1 (PANDAS & PYTHON)")
    print("=" * 80)

    # 1. Conexión a Base de Datos
    print("\n[FASE 0] Conectando a MySQL (Northwind en puerto 3308)...")
    engine = get_engine("northwind")
    print("✅ Conexión establecida exitosamente.")

    # 2. Extracción en Bruto (Sin JOINs en SQL - Restricción del Encargo)
    print("\n[FASE 1] Extrayendo tablas en bruto a DataFrames de Pandas (0 JOINs)...")
    df_region = extract_table("region", engine)
    df_territories = extract_table("territories", engine)
    df_emp_terr = extract_table("employeeterritories", engine)
    df_employees = extract_table("employees", engine)
    df_orders = extract_table("orders", engine)
    df_order_details = extract_table("order details", engine)

    # Limpieza de espacios en blanco procedentes de NCHAR
    df_region['RegionDescription'] = df_region['RegionDescription'].astype(str).str.strip()
    df_territories['TerritoryDescription'] = df_territories['TerritoryDescription'].astype(str).str.strip()

    print(f"  • region: {len(df_region)} filas")
    print(f"  • territories: {len(df_territories)} filas")
    print(f"  • employeeterritories: {len(df_emp_terr)} filas")
    print(f"  • employees: {len(df_employees)} filas")
    print(f"  • orders: {len(df_orders)} filas")
    print(f"  • order details: {len(df_order_details)} filas")

    # 3. Línea Base Contable (Ground Truth)
    print("\n[FASE 2] Estableciendo la Línea Base Contable Oficial...")
    df_order_details['ImporteLinea'] = df_order_details['UnitPrice'] * df_order_details['Quantity'] * (1 - df_order_details['Discount'])
    
    total_unidades_base = int(df_order_details['Quantity'].sum())
    total_ventas_base = round(float(df_order_details['ImporteLinea'].sum()), 2)
    total_fletes_base = round(float(df_orders['Freight'].sum()), 2)
    total_facturacion_base = round(total_ventas_base + total_fletes_base, 2)

    print(f"  📌 Unidades vendidas (Línea Base): {total_unidades_base:,}")
    print(f"  📌 Ventas Reales Productos:       ${total_ventas_base:,.2f}")
    print(f"  📌 Fletes Reales Cobrados:        ${total_fletes_base:,.2f}")
    print(f"  📌 Facturación Total Integrada:   ${total_facturacion_base:,.2f}")

    # 4. El Intento Ingenuo (Reproducción del Error Común en Pandas)
    print("\n[FASE 3] Reproduciendo el Intento Ingenuo (Merge secuencial directo)...")
    df_ingenuo = (
        df_order_details
        .merge(df_orders[['OrderID', 'EmployeeID']], on='OrderID', how='inner')
        .merge(df_employees[['EmployeeID']], on='EmployeeID', how='inner')
        .merge(df_emp_terr, on='EmployeeID', how='inner')
        .merge(df_territories[['TerritoryID', 'RegionID']], on='TerritoryID', how='inner')
        .merge(df_region[['RegionID', 'RegionDescription']], on='RegionID', how='inner')
    )
    
    resumen_ingenuo = df_ingenuo.groupby(['RegionID', 'RegionDescription'])['ImporteLinea'].sum().round(2).reset_index()
    total_ingenuo = round(float(resumen_ingenuo['ImporteLinea'].sum()), 2)
    desfase = round(total_ingenuo - total_ventas_base, 2)
    pct_error = round((desfase / total_ventas_base) * 100, 2)

    print(f"  ⚠️ Suma Total Obtenida con Merge Ingenuo: ${total_ingenuo:,.2f}")
    print(f"  ⚠️ Desfase inflado:                      +${desfase:,.2f} (+{pct_error}%)")

    # 5. Auditoría Forense y Causa Raíz
    print("\n[FASE 4] Diagnóstico Forense de Causa Raíz...")
    # Multiplicidad por empleado
    terr_por_emp = df_emp_terr.groupby('EmployeeID')['TerritoryID'].count().reset_index()
    terr_por_emp.rename(columns={'TerritoryID': 'num_territorios'}, inplace=True)
    
    # Comprobar si algún empleado atiende más de 1 región
    emp_terr_region = df_emp_terr.merge(df_territories[['TerritoryID', 'RegionID']], on='TerritoryID')
    regiones_por_emp = emp_terr_region.groupby('EmployeeID')['RegionID'].nunique()
    max_regiones = regiones_por_emp.max()
    min_regiones = regiones_por_emp.min()
    print(f"  🔍 Comprobación de Unicidad Regional por Empleado: Min={min_regiones}, Max={max_regiones}")
    assert max_regiones == 1 and min_regiones == 1, "Error: Existen empleados con múltiples regiones"
    print("  ✅ Conclusión arquitectónica: Cada empleado pertenece unívocamente a exactamente 1 región.")
    print("     La multiplicación se produce exclusivamente porque cada empleado tiene múltiples territorios dentro de su región.")

    # 6. Solución Robusta en Pandas (Desacoplamiento)
    print("\n[FASE 5] Construcción de la Solución Robusta con Desacoplamiento...")
    df_emp_region_unicos = emp_terr_region[['EmployeeID', 'RegionID']].drop_duplicates()
    print(f"  • Mapeo Empleado -> Región limpio: exactamente {len(df_emp_region_unicos)} registros (1 por empleado).")

    # Merge limpio sin multiplicación cartesiana
    df_pedidos_region = df_orders.merge(df_emp_region_unicos, on='EmployeeID', how='inner')
    df_ventas_completas = df_order_details.merge(
        df_pedidos_region[['OrderID', 'EmployeeID', 'RegionID']], 
        on='OrderID', 
        how='inner'
    )

    # 7. Pre-agrupación de órdenes para fletes (Evitar duplicación de flete)
    df_ordenes_totales = df_order_details.groupby('OrderID').agg(
        unidades_orden=('Quantity', 'sum'),
        venta_orden=('ImporteLinea', 'sum')
    ).reset_index()

    df_pedidos_metricas = df_pedidos_region.merge(df_ordenes_totales, on='OrderID', how='left')

    # 8. Master Table Ejecutiva (KPIs Directivos)
    print("\n[FASE 6 & 7] Generando Master Table Ejecutiva por Región...")
    master = df_region.copy()

    # Agregar métricas de empleados
    empleados_por_reg = df_emp_region_unicos.groupby('RegionID')['EmployeeID'].count().reset_index()
    empleados_por_reg.rename(columns={'EmployeeID': 'Fuerza de Ventas (Vendedores)'}, inplace=True)
    master = master.merge(empleados_por_reg, on='RegionID', how='left')

    # Agregar métricas de pedidos y fletes
    kpis_pedidos = df_pedidos_metricas.groupby('RegionID').agg(
        Total_Pedidos=('OrderID', 'nunique'),
        Unidades_Vendidas=('unidades_orden', 'sum'),
        Ganancias_Productos=('venta_orden', 'sum'),
        Fletes_Facturados=('Freight', 'sum')
    ).reset_index()

    master = master.merge(kpis_pedidos, on='RegionID', how='left')
    master['Facturacion_Total'] = master['Ganancias_Productos'] + master['Fletes_Facturados']
    master['Pct_Participacion'] = (master['Ganancias_Productos'] / total_ventas_base) * 100
    master['Ticket_Promedio'] = master['Ganancias_Productos'] / master['Total_Pedidos']

    # Ordenar y formatear
    master.sort_values(by='Ganancias_Productos', ascending=False, inplace=True)

    print("\n" + "=" * 110)
    print("📊 MASTER TABLE EJECUTIVA - GANANCIAS POR REGIÓN (NORTHWIND)")
    print("=" * 110)
    
    tabla_display = master.copy()
    tabla_display['Ganancias Productos ($)'] = tabla_display['Ganancias_Productos'].map('${:,.2f}'.format)
    tabla_display['Fletes Facturados ($)'] = tabla_display['Fletes_Facturados'].map('${:,.2f}'.format)
    tabla_display['Facturación Total ($)'] = tabla_display['Facturacion_Total'].map('${:,.2f}'.format)
    tabla_display['% Participación Ventas'] = tabla_display['Pct_Participacion'].map('{:.2f}%'.format)
    tabla_display['Ticket Promedio ($)'] = tabla_display['Ticket_Promedio'].map('${:,.2f}'.format)
    tabla_display['Unidades Vendidas'] = tabla_display['Unidades_Vendidas'].map('{:,.0f}'.format)

    columnas_mostrar = [
        'RegionID', 'RegionDescription', 'Fuerza de Ventas (Vendedores)',
        'Total_Pedidos', 'Unidades Vendidas', 'Ganancias Productos ($)',
        'Fletes Facturados ($)', 'Facturación Total ($)', '% Participación Ventas',
        'Ticket Promedio ($)'
    ]
    print(tabla_display[columnas_mostrar].to_string(index=False))

    # 9. Conciliación Contable Definitiva
    print("\n[FASE 8] Conciliación y Certificación Contable...")
    total_ventas_pandas = round(float(master['Ganancias_Productos'].sum()), 2)
    total_fletes_pandas = round(float(master['Fletes_Facturados'].sum()), 2)
    total_facturacion_pandas = round(float(master['Facturacion_Total'].sum()), 2)

    diff_ventas = round(total_ventas_pandas - total_ventas_base, 2)
    diff_fletes = round(total_fletes_pandas - total_fletes_base, 2)
    diff_facturacion = round(total_facturacion_pandas - total_facturacion_base, 2)

    print(f"  • Total Ventas Obtenido:     ${total_ventas_pandas:,.2f}  |  Línea Base: ${total_ventas_base:,.2f}  |  Diferencia: ${diff_ventas:,.2f}")
    print(f"  • Total Fletes Obtenido:     ${total_fletes_pandas:,.2f}   |  Línea Base: ${total_fletes_base:,.2f}   |  Diferencia: ${diff_fletes:,.2f}")
    print(f"  • Facturación Integrada:     ${total_facturacion_pandas:,.2f}  |  Línea Base: ${total_facturacion_base:,.2f}  |  Diferencia: ${diff_facturacion:,.2f}")

    assert abs(diff_ventas) < 0.001, f"Fallo de conciliación en ventas: ${diff_ventas}"
    assert abs(diff_fletes) < 0.001, f"Fallo de conciliación en fletes: ${diff_fletes}"
    assert abs(diff_facturacion) < 0.001, f"Fallo de conciliación en facturación: ${diff_facturacion}"

    print("\n" + "⭐" * 40)
    print("🏆 ¡CONCILIACIÓN MATEMÁTICA AL 100.00% EXACTA! (DIFERENCIA = $0.00)")
    print("⭐" * 40 + "\n")


if __name__ == "__main__":
    run_encargo1_audit()

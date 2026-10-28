#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Auditoría Forense y Verificación Contable - Práctica 1 (Pubs: Ganancias por Autor).
Ejecuta de principio a fin todo el pipeline analítico en Python & Pandas cumpliendo con la regla:
  - Máximo 2 JOINs en SQL (implementado mediante extracción en bruto con 0 JOINs).
  - Toda la auditoría, detección de duplicidades, resolución de huérfanos y conciliación
    se desarrolla en memoria mediante Pandas.
"""

import sys
from pathlib import Path

# Agregar directorio raíz de analisis_pandas al PYTHONPATH
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import numpy as np
import pandas as pd
from src.database import get_engine, extract_table, load_query, validate_max_joins


def run_practica1_audit():
    print("=" * 95)
    print("🚀 INICIANDO AUDITORÍA FORENSE - PRÁCTICA 1: GANANCIAS POR AUTOR (PANDAS & PYTHON)")
    print("   Base de Datos: pubs (MySQL 8.0 en Docker, puerto 3307)")
    print("   Regla de Ingeniería: Extracción en bruto (0 JOINs) + Álgebra Relacional en Pandas")
    print("=" * 95)

    # -------------------------------------------------------------------------
    # FASE 0: CONEXIÓN Y CERTIFICACIÓN DE LÍMITES DE JOINS
    # -------------------------------------------------------------------------
    print("\n[FASE 0] Conectando a MySQL (pubs en puerto 3307)...")
    engine = get_engine("pubs")
    print("✅ Conexión establecida exitosamente.")

    # Validar que el interceptor de JOINs funciona según la restricción
    test_sql_valido = "SELECT COUNT(*) FROM sales s INNER JOIN titles t ON s.title_id = t.title_id"
    joins_detectados = validate_max_joins(test_sql_valido, max_joins=2)
    print(f"✅ Validador de JOINs activo: Consulta de prueba con {joins_detectados} JOIN aprobada (≤ 2).")

    # -------------------------------------------------------------------------
    # FASE 1: RECONOCIMIENTO Y EXTRACCIÓN EN BRUTO (Data Discovery - 0 JOINs)
    # -------------------------------------------------------------------------
    print("\n[FASE 1] Extrayendo tablas maestras en bruto hacia DataFrames de Pandas (0 JOINs)...")
    df_authors = extract_table("authors", engine, db_key="pubs")
    df_titles = extract_table("titles", engine, db_key="pubs")
    df_titleauthor = extract_table("titleauthor", engine, db_key="pubs")
    df_sales = extract_table("sales", engine, db_key="pubs")

    print(f"  • authors (autores registrados):        {len(df_authors)} filas")
    print(f"  • titles (catálogo de libros):          {len(df_titles)} filas")
    print(f"  • titleauthor (relación autor-libro):   {len(df_titleauthor)} filas")
    print(f"  • sales (órdenes de venta en tiendas):  {len(df_sales)} filas")

    assert len(df_authors) == 23, f"Se esperaban 23 autores, se obtuvieron {len(df_authors)}"
    assert len(df_titles) == 17, f"Se esperaban 17 títulos, se obtuvieron {len(df_titles)}"
    assert len(df_titleauthor) == 20, f"Se esperaban 20 relaciones, se obtuvieron {len(df_titleauthor)}"
    assert len(df_sales) == 10, f"Se esperaban 10 registros de ventas, se obtuvieron {len(df_sales)}"

    # -------------------------------------------------------------------------
    # FASE 2: LÍNEA BASE CONTABLE (Ground Truth Oficial de la Empresa)
    # -------------------------------------------------------------------------
    print("\n[FASE 2] Estableciendo la Línea Base Contable (Ground Truth Oficial)...")
    # Merge atómico de 2 DataFrames en Pandas: sales x titles
    df_ventas_base = df_sales.merge(df_titles[['title_id', 'title', 'price']], on='title_id', how='inner')
    df_ventas_base['monto_linea'] = df_ventas_base['qty'] * df_ventas_base['price']
    
    total_ventas_base = round(float(df_ventas_base['monto_linea'].sum()), 2)
    titulos_con_ventas = df_ventas_base['title_id'].nunique()
    total_unidades_base = int(df_ventas_base['qty'].sum())

    print(f"  • 💰 Total Oficial de Ventas Reales (Caja Registradora): ${total_ventas_base:,.2f}")
    print(f"  • 📦 Total Unidades Físicas Vendidas:                    {total_unidades_base:,} unidades")
    print(f"  • 📚 Títulos con Movimiento Comercial:                   {titulos_con_ventas} de {len(df_titles)} libros")
    print(f"  • ⚠️  Hallazgo: {len(df_titles) - titulos_con_ventas} libros del catálogo tienen 0 ventas en la tabla 'sales'.")

    assert total_ventas_base == 3863.80, f"Error en Ground Truth: ${total_ventas_base} != $3863.80"

    # -------------------------------------------------------------------------
    # FASE 3: EL INTENTO INGENUO Y LA GRAN DISCREPANCIA (El Error Común)
    # -------------------------------------------------------------------------
    print("\n[FASE 3] Reproduciendo el Intento Ingenuo (INNER JOIN directo de 4 entidades)...")
    # Simulación del error de principiante en Pandas: merge encadenado con inner join
    df_ingenuo = df_authors.merge(df_titleauthor, on='au_id', how='inner') \
                           .merge(df_titles, on='title_id', how='inner') \
                           .merge(df_sales, on='title_id', how='inner')

    df_ingenuo['monto_ingenuo'] = df_ingenuo['qty'] * df_ingenuo['price']
    resumen_ingenuo = df_ingenuo.groupby(['au_id', 'au_fname', 'au_lname'], as_index=False)['monto_ingenuo'].sum()
    total_ingenuo = round(float(resumen_ingenuo['monto_ingenuo'].sum()), 2)
    autores_ingenuo = len(resumen_ingenuo)

    desfase = round(total_ingenuo - total_ventas_base, 2)
    pct_desfase = round((desfase / total_ventas_base) * 100, 2)

    print(f"  • Total Obtenido en Intento Ingenuo:   ${total_ingenuo:,.2f} ({autores_ingenuo} autores)")
    print(f"  • Línea Base Real de la Empresa:       ${total_ventas_base:,.2f}")
    print(f"  • 🚨 ¡ALERTA DE DESFASE FINANCIERO!:   +${desfase:,.2f} (+{pct_desfase}%)")
    print("  • Diagnóstico Preliminar: ¡Las cuentas contables NO cuadran! Hay inflación y omisiones.")

    assert total_ingenuo == 4708.90, f"Error en total ingenuo: ${total_ingenuo} != $4708.90"
    assert desfase == 845.10, f"Error en desfase: ${desfase} != $845.10"

    # -------------------------------------------------------------------------
    # FASE 4: AUDITORÍA FORENSE Y DIAGNÓSTICO DE CAUSA RAÍZ
    # -------------------------------------------------------------------------
    print("\n[FASE 4] Auditoría Forense: Descomponiendo las anomalías matemáticas...")

    # 4.1 Libros Multi-Autor y Duplicidad Cartesiana
    conteo_autores = df_titleauthor.groupby('title_id')['au_id'].nunique().reset_index(name='num_autores')
    libros_multiautor = conteo_autores[conteo_autores['num_autores'] > 1]
    
    # Calcular cuánto infló el join ingenuo por cada libro multi-autor
    ventas_multiautor = df_ventas_base.merge(libros_multiautor, on='title_id', how='inner')
    ventas_multiautor['duplicidad_generada'] = ventas_multiautor['monto_linea'] * (ventas_multiautor['num_autores'] - 1)
    duplicidad_total = round(float(ventas_multiautor['duplicidad_generada'].sum()), 2)

    print("  ▶ 4.1 Libros con Múltiples Autores (Duplicidad por INNER JOIN):")
    for _, r in ventas_multiautor.groupby(['title_id', 'title', 'num_autores'])['duplicidad_generada'].sum().reset_index().iterrows():
        print(f"      - [{r['title_id']}] {r['title'][:32]}: {r['num_autores']} autoras -> Inflado artificial: +${r['duplicidad_generada']:,.2f}")
    print(f"      => Duplicidad Total Generada: +${duplicidad_total:,.2f}")

    assert duplicidad_total == 1044.85, f"Error en duplicidad: ${duplicidad_total} != $1044.85"

    # 4.2 Libros Huérfanos sin Autor Asignado
    titulos_con_autor = set(df_titleauthor['title_id'].unique())
    libros_huerfanos = df_ventas_base[~df_ventas_base['title_id'].isin(titulos_con_autor)]
    perdida_huerfanos = round(float(libros_huerfanos['monto_linea'].sum()), 2)

    print("  ▶ 4.2 Libros Huérfanos (Vendidos comercialmente pero SIN autor registrado):")
    for _, r in libros_huerfanos.groupby(['title_id', 'title'])['monto_linea'].sum().reset_index().iterrows():
        print(f"      - [{r['title_id']}] {r['title'][:32]}: Descartado por INNER JOIN -> Ventas perdidas: -${r['monto_linea']:,.2f}")
    print(f"      => Total Ventas Huérfanas Omitidas: -${perdida_huerfanos:,.2f}")

    assert perdida_huerfanos == 199.75, f"Error en huérfanos: ${perdida_huerfanos} != $199.75"

    # 4.3 Conciliación Matemática Forense de la Discrepancia
    print("  ▶ 4.3 Ecuación de Conciliación Matemática:")
    print(f"      Línea Base Oficial:                      ${total_ventas_base:,.2f}")
    print(f"      (+) Duplicidad libros multi-autor:      +${duplicidad_total:,.2f}")
    print(f"      (-) Omisión libros huérfanos:            -${perdida_huerfanos:,.2f}")
    print("      " + "-" * 50)
    total_conciliado_ingenuo = round(total_ventas_base + duplicidad_total - perdida_huerfanos, 2)
    print(f"      (=) Total Exacto Explicado:              ${total_conciliado_ingenuo:,.2f}")
    print(f"      (=) Total Obtenido en Intento Ingenuo:   ${total_ingenuo:,.2f}")
    diff_conciliacion = round(total_conciliado_ingenuo - total_ingenuo, 2)
    print(f"      => Discrepancia Residual:                ${diff_conciliacion:,.2f}")
    
    assert diff_conciliacion == 0.00, f"Conciliación falló: ${diff_conciliacion}"
    print("      🎯 ¡La discrepancia de +$845.10 queda explicada al 100.00% al centavo!")

    # 4.4 Censo de Población de Autores (23 en total)
    autores_con_libros = set(df_titleauthor['au_id'].unique())
    autores_sin_libros = df_authors[~df_authors['au_id'].isin(autores_con_libros)]
    autores_con_ventas_ids = set(df_ingenuo['au_id'].unique())
    autores_con_libros_sin_ventas = df_authors[df_authors['au_id'].isin(autores_con_libros) & ~df_authors['au_id'].isin(autores_con_ventas_ids)]

    print(f"  ▶ 4.4 Auditoría de Población de Autores:")
    print(f"      - Autores sin libros registrados:            {len(autores_sin_libros)} autores")
    print(f"      - Autores con libros pero con 0 ventas:      {len(autores_con_libros_sin_ventas)} autores")
    print(f"      - Autores con ventas registradas:            {len(autores_con_ventas_ids)} autores")
    print(f"      - Censo Total de la Empresa:                 {len(df_authors)} autores")
    assert len(autores_sin_libros) + len(autores_con_libros_sin_ventas) + len(autores_con_ventas_ids) == 23

    # -------------------------------------------------------------------------
    # FASE 5 & 6: CONSTRUCCIÓN ITERATIVA DE LA SOLUCIÓN Y CRITERIOS DE NEGOCIO
    # -------------------------------------------------------------------------
    print("\n[FASE 5 & 6] Construcción de la Solución Robusta en Pandas (LEFT JOIN + Ponderación)...")
    # Construcción de la cadena relacional en memoria
    df_relacional = df_authors.merge(df_titleauthor, on='au_id', how='left') \
                              .merge(df_titles, on='title_id', how='left') \
                              .merge(df_sales, on='title_id', how='left', suffixes=('', '_sale'))

    # Imputación de nulos (equivalente a COALESCE en SQL)
    df_relacional['qty_clean'] = df_relacional['qty'].fillna(0)
    df_relacional['price_clean'] = df_relacional['price'].fillna(0)
    df_relacional['royaltyper_clean'] = df_relacional['royaltyper'].fillna(0)
    df_relacional['royalty_clean'] = df_relacional['royalty'].fillna(0)

    # Criterio 1: Ventas Atribuibles (facturación bruta ponderada por cuota de autoría)
    df_relacional['unidades_atribuibles'] = df_relacional['qty_clean'] * (df_relacional['royaltyper_clean'] / 100.0)
    df_relacional['ventas_atribuibles'] = df_relacional['qty_clean'] * df_relacional['price_clean'] * (df_relacional['royaltyper_clean'] / 100.0)

    # Criterio 2: Regalías Netas en Mano (lo que la editorial paga contractualmente al autor)
    df_relacional['regalias_netas'] = df_relacional['qty_clean'] * df_relacional['price_clean'] * \
                                      (df_relacional['royalty_clean'] / 100.0) * (df_relacional['royaltyper_clean'] / 100.0)

    # Agrupación directiva por autor preservando a los 23 autores
    master = df_relacional.groupby(['au_id', 'au_fname', 'au_lname', 'city', 'state'], as_index=False).agg(
        Libros_Publicados=('title_id', lambda s: s.dropna().nunique()),
        Unidades_Brutas=('qty_clean', 'sum'),
        Unidades_Atribuibles=('unidades_atribuibles', 'sum'),
        Ganancias_Generadas=('ventas_atribuibles', 'sum'),
        Regalias_Cobradas=('regalias_netas', 'sum')
    )

    master['Nombre del Autor'] = master['au_fname'] + ' ' + master['au_lname']
    master.sort_values(by=['Ganancias_Generadas', 'Regalias_Cobradas', 'Nombre del Autor'], 
                       ascending=[False, False, True], inplace=True)
    master.reset_index(drop=True, inplace=True)

    assert len(master) == 23, f"Se esperaban 23 autores en la tabla final, se obtuvieron {len(master)}"

    # -------------------------------------------------------------------------
    # FASE 7: MASTER TABLE EJECUTIVA (Reporte Gerencial Formateado)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 115)
    print("📊 MASTER TABLE EJECUTIVA - GANANCIAS POR AUTOR (PUBS - PANDAS)")
    print("=" * 115)

    display_df = master.copy()
    display_df['Ganancias Generadas ($)'] = display_df['Ganancias_Generadas'].map('${:,.2f}'.format)
    display_df['Regalías Cobradas ($)'] = display_df['Regalias_Cobradas'].map('${:,.2f}'.format)
    display_df['Unidades Brutas'] = display_df['Unidades_Brutas'].map('{:,.0f}'.format)
    display_df['Unidades Atribuibles'] = display_df['Unidades_Atribuibles'].map('{:,.1f}'.format)

    columnas_mostrar = [
        'au_id', 'Nombre del Autor', 'city', 'state', 'Libros_Publicados',
        'Unidades Brutas', 'Unidades Atribuibles', 'Ganancias Generadas ($)', 'Regalías Cobradas ($)'
    ]
    display_df.rename(columns={'au_id': 'ID Autor', 'city': 'Ciudad', 'state': 'Estado'}, inplace=True)
    columnas_mostrar_renombradas = [
        'ID Autor', 'Nombre del Autor', 'Ciudad', 'Estado', 'Libros_Publicados',
        'Unidades Brutas', 'Unidades Atribuibles', 'Ganancias Generadas ($)', 'Regalías Cobradas ($)'
    ]
    print(display_df[columnas_mostrar_renombradas].to_string(index=False))

    # -------------------------------------------------------------------------
    # FASE 8: CONCILIACIÓN CONTABLE DEFINITIVA AL CENTAVO (100% de la Empresa)
    # -------------------------------------------------------------------------
    print("\n[FASE 8] Conciliación y Certificación Contable Integral del 100% de Ventas...")
    
    # 1. Ventas asignadas a autores
    total_autores_asignado = round(float(master['Ganancias_Generadas'].sum()), 2)
    total_regalias_autores = round(float(master['Regalias_Cobradas'].sum()), 2)

    # 2. Ventas huérfanas sin autor (PS7777)
    total_huerfano = round(float(perdida_huerfanos), 2)

    # 3. Remanente editorial no asignado a autores (porcentajes de BU1111 y PS2091)
    participacion_editorial = df_titleauthor.groupby('title_id')['royaltyper'].sum().reset_index()
    titulos_con_remanente = participacion_editorial[participacion_editorial['royaltyper'] < 100].copy()
    titulos_con_remanente['pct_editorial'] = (100 - titulos_con_remanente['royaltyper']) / 100.0

    df_editorial = df_sales.merge(df_titles, on='title_id', how='inner') \
                           .merge(titulos_con_remanente, on='title_id', how='inner')
    df_editorial['monto_editorial'] = df_editorial['qty'] * df_editorial['price'] * df_editorial['pct_editorial']
    total_remanente_editorial = round(float(df_editorial['monto_editorial'].sum()), 2)

    # Suma Total Auditoría
    total_auditado_empresa = round(total_autores_asignado + total_huerfano + total_remanente_editorial, 2)
    diff_final = round(total_auditado_empresa - total_ventas_base, 2)

    print(f"  • 1. Ventas Atribuidas a Autores Registrados:            ${total_autores_asignado:,.2f}  ({(total_autores_asignado/total_ventas_base)*100:.2f}%)")
    print(f"  • 2. Ventas de Libros sin Autor Asignado (PS7777):        ${total_huerfano:,.2f}  ({(total_huerfano/total_ventas_base)*100:.2f}%)")
    print(f"  • 3. Remanente Editorial no Asignado (BU1111 y PS2091):   ${total_remanente_editorial:,.2f}  ({(total_remanente_editorial/total_ventas_base)*100:.2f}%)")
    print("  " + "-" * 75)
    print(f"  • >>> TOTAL GENERAL AUDITADO DE LA EMPRESA <<<:           ${total_auditado_empresa:,.2f}  (100.00%)")
    print(f"  • 💰 Línea Base Oficial (Caja Registradora):             ${total_ventas_base:,.2f}")
    print(f"  • ⚖️  Diferencia Residual Contable:                        ${diff_final:,.2f}")

    assert abs(diff_final) < 0.001, f"Fallo en la conciliación final: ${diff_final}"
    assert total_autores_asignado == 2893.50, f"Error en asignado a autores: ${total_autores_asignado}"
    assert total_huerfano == 199.75, f"Error en huérfanos: ${total_huerfano}"
    assert total_remanente_editorial == 770.55, f"Error en remanente editorial: ${total_remanente_editorial}"

    print("\n" + "⭐" * 45)
    print("🏆 ¡CONCILIACIÓN MATEMÁTICA AL 100.00% EXACTA! (DIFERENCIA = $0.00)")
    print("   Total Facturado: $3,863.80 | Auditado: $3,863.80 | Cero Fuga Contable")
    print("⭐" * 45 + "\n")


if __name__ == "__main__":
    run_practica1_audit()

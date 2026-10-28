#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Auditoría Forense y Verificación Técnica para el Encargo 1 de la Práctica 1 con Pandas.
Punto de entrada directo dentro del módulo practica1/.
"""

import sys
from pathlib import Path

# Localizar la raíz del repositorio y analisis_pandas
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent
ANALISIS_DIR = ROOT_DIR / "analisis_pandas"

if str(ANALISIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALISIS_DIR))

from scripts.test_practica1_encargo1 import run_practica1_audit

if __name__ == "__main__":
    run_practica1_audit()

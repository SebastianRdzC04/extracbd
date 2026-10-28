#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del Jupyter Notebook para la Práctica 1 - Encargo 1: Ganancias por Autor.
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

from scripts.generate_notebook_practica1 import build_practica1_notebook

if __name__ == "__main__":
    build_practica1_notebook()

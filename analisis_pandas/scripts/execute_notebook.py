#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecutor Headless del Notebook de Encargo 1.
Ejecuta todas las celdas del notebook y almacena las salidas pre-renderizadas
(tablas, gráficos, alertas y aserciones) dentro del archivo .ipynb.
"""

import sys
from pathlib import Path
import nbformat
from nbclient import NotebookClient

NOTEBOOK_DIR = Path(__file__).resolve().parent.parent / "notebooks"


def run_and_save_notebook(notebook_filename="practica1_encargo_ganancias_por_autor.ipynb"):
    notebook_path = NOTEBOOK_DIR / notebook_filename
    print(f"📖 Leyendo notebook desde: {notebook_path}")
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    print("⚙️ Ejecutando celdas del notebook...")
    client = NotebookClient(nb, timeout=300, kernel_name="python3")
    client.execute()

    print(f"💾 Guardando notebook con salidas pre-renderizadas en: {notebook_path}")
    with open(notebook_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    print(f"🎉 ¡Notebook {notebook_filename} ejecutado y persistido con éxito!")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "practica1_encargo_ganancias_por_autor.ipynb"
    run_and_save_notebook(target)

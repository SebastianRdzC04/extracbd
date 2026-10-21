#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Runner estético para Prácticas de Base de Datos.
Ejecuta consultas en contenedores Docker y estiliza la salida en terminal con colores y marcos ANSI.
"""

import os
import sys
import time
import argparse
import subprocess
import shutil

# Códigos de color ANSI
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
ITALIC  = "\033[3m"

# Colores estándar
BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"

# Colores brillantes
B_RED     = "\033[91m"
B_GREEN   = "\033[92m"
B_YELLOW  = "\033[93m"
B_BLUE    = "\033[94m"
B_MAGENTA = "\033[95m"
B_CYAN    = "\033[96m"
B_WHITE   = "\033[97m"

# Fondos
BG_BLUE    = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN    = "\033[46m"
BG_DARK    = "\033[48;5;236m"

def get_terminal_width():
    try:
        width = shutil.get_terminal_size((100, 24)).columns
        return min(max(width, 80), 120)
    except Exception:
        return 100

def print_header(title, subtitle, db_name, service_name, port):
    w = get_terminal_width()
    inner = w - 4
    
    print("\n" + B_CYAN + "╔" + "═" * (w - 2) + "╗" + RESET)
    title_str = f"  🏛️  {title}".center(inner)
    sub_str   = f"📂 {subtitle}".center(inner)
    info_str  = f"🗄️  Base de Datos: {db_name}  |  🐳 Servicio: {service_name}  |  🔌 Puerto: {port}".center(inner)
    
    print(B_CYAN + "║" + BOLD + B_WHITE + title_str + RESET + B_CYAN + "║" + RESET)
    print(B_CYAN + "║" + DIM + B_CYAN + sub_str + RESET + B_CYAN + "║" + RESET)
    print(B_CYAN + "║" + B_MAGENTA + info_str + RESET + B_CYAN + "║" + RESET)
    print(B_CYAN + "╚" + "═" * (w - 2) + "╝" + RESET + "\n")

def print_phase(phase_text):
    w = get_terminal_width()
    line_len = max(w - len(phase_text) - 10, 5)
    print("\n" + B_YELLOW + "╭" + "─" * (w - 2) + "╮" + RESET)
    print(B_YELLOW + "│" + BOLD + B_YELLOW + f"  📌 {phase_text}".ljust(w - 2) + RESET + B_YELLOW + "│" + RESET)
    print(B_YELLOW + "╰" + "─" * (w - 2) + "╯" + RESET)

def print_step(title, notes, is_final=False):
    w = get_terminal_width()
    if is_final:
        print("\n" + B_GREEN + "╔" + "═" * (w - 2) + "╗" + RESET)
        final_title = f"  ⭐ {title.upper()} ⭐  "
        print(B_GREEN + "║" + BOLD + B_GREEN + final_title.center(w - 2) + RESET + B_GREEN + "║" + RESET)
        print(B_GREEN + "╚" + "═" * (w - 2) + "╝" + RESET)
    else:
        print("\n" + BOLD + B_CYAN + f"  ▶ {title}" + RESET)
    
    for note in notes:
        if note.lower().startswith("propósito:") or note.lower().startswith("proposito:"):
            print(B_WHITE + f"     💡 {BOLD}{note[:10]}{RESET}{DIM}{note[10:]}{RESET}")
        elif note.lower().startswith("hallazgo"):
            print(B_MAGENTA + f"     🔍 {BOLD}{note[:9]}{RESET}{B_WHITE}{note[9:]}{RESET}")
        elif note.lower().startswith("resultado"):
            print(B_GREEN + f"     📊 {BOLD}{note[:10]}{RESET}{B_GREEN}{note[10:]}{RESET}")
        elif note.lower().startswith("alerta"):
            print(B_RED + f"     ⚠️  {BOLD}{note[:7]}{RESET}{B_RED}{note[7:]}{RESET}")
        elif note.lower().startswith("nota"):
            print(DIM + f"     📝 {note}" + RESET)
        else:
            print(DIM + f"     • {note}" + RESET)
    print()

def style_mysql_table(output):
    """Aplica formato ANSI y resaltado de encabezados a la salida ASCII de MySQL."""
    lines = output.strip().splitlines()
    if not lines:
        return ""
    
    formatted = []
    is_first_border = True
    is_header_row = False
    
    for line in lines:
        if line.startswith("+"):
            # Línea divisoria de tabla
            formatted.append(DIM + CYAN + line + RESET)
            if is_first_border:
                is_header_row = True
                is_first_border = False
            else:
                is_header_row = False
        elif line.startswith("|"):
            if is_header_row:
                # Fila de encabezado con columnas destacadas
                formatted.append(BOLD + B_YELLOW + line + RESET)
            else:
                # Filas de datos
                # Resaltar bordes '|' en dim y texto en blanco brillante
                colored_row = line.replace("|", DIM + CYAN + "|" + RESET + B_WHITE)
                formatted.append(colored_row + RESET)
        else:
            formatted.append(DIM + line + RESET)
            
    return "\n".join(formatted)

def parse_sql_file(filepath):
    """
    Parsea un archivo SQL preservando comentarios precedentes para cada sentencia.
    Maneja cadenas de texto ('...', \"...\", `...`) para no romper en punto y coma internos.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    statements = []
    current_stmt = []
    current_comments = []
    
    in_single_quote = False
    in_double_quote = False
    in_backtick = False
    in_line_comment = False
    in_block_comment = False
    
    i = 0
    n = len(content)
    line_comment_buffer = []
    
    while i < n:
        c = content[i]
        c2 = content[i:i+2] if i + 1 < n else ""
        
        # Manejo de comentarios de línea (-- ...)
        if in_line_comment:
            if c == '\n':
                in_line_comment = False
                comment_text = "".join(line_comment_buffer).strip()
                if comment_text:
                    current_comments.append(comment_text)
                line_comment_buffer = []
            else:
                line_comment_buffer.append(c)
            i += 1
            continue
            
        # Manejo de comentarios de bloque (/* ... */)
        if in_block_comment:
            if c2 == '*/':
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue
            
        # Comprobar inicio de comentarios (fuera de comillas)
        if not in_single_quote and not in_double_quote and not in_backtick:
            if c2 == '--':
                in_line_comment = True
                line_comment_buffer = []
                i += 2
                continue
            elif c2 == '/*':
                in_block_comment = True
                i += 2
                continue
                
        # Manejo de comillas
        if c == "'" and not in_double_quote and not in_backtick:
            # Comprobar escape de comilla \' o ''
            if in_single_quote and i + 1 < n and content[i+1] == "'":
                current_stmt.append("''")
                i += 2
                continue
            in_single_quote = not in_single_quote
            current_stmt.append(c)
            i += 1
            continue
            
        if c == '"' and not in_single_quote and not in_backtick:
            if in_double_quote and i + 1 < n and content[i+1] == '"':
                current_stmt.append('""')
                i += 2
                continue
            in_double_quote = not in_double_quote
            current_stmt.append(c)
            i += 1
            continue
            
        if c == '`' and not in_single_quote and not in_double_quote:
            in_backtick = not in_backtick
            current_stmt.append(c)
            i += 1
            continue
            
        # Semicolon fuera de comillas finaliza sentencia
        if c == ';' and not in_single_quote and not in_double_quote and not in_backtick:
            stmt_sql = "".join(current_stmt).strip()
            if stmt_sql:
                statements.append({
                    "sql": stmt_sql,
                    "comments": list(current_comments)
                })
            current_stmt = []
            current_comments = []
            i += 1
            continue
            
        current_stmt.append(c)
        i += 1
        
    # Última sentencia si no terminó con ';'
    stmt_sql = "".join(current_stmt).strip()
    if stmt_sql:
        statements.append({
            "sql": stmt_sql,
            "comments": list(current_comments)
        })
        
    return statements

def ensure_container_running(service_name):
    """Verifica si el contenedor de Docker Compose está corriendo, si no, lo levanta."""
    try:
        check = subprocess.run(
            ["docker", "compose", "ps", "--services", "--filter", "status=running"],
            capture_output=True, text=True, check=True
        )
        running = check.stdout.strip().splitlines()
        if service_name not in running:
            print(B_YELLOW + f"⚠️  El contenedor para '{service_name}' no está iniciado. Levantándolo..." + RESET)
            subprocess.run(["docker", "compose", "up", "-d", service_name], check=True)
            print(B_GREEN + f"✔ Contenedor '{service_name}' iniciado correctamente." + RESET)
            time.sleep(2)
    except Exception as e:
        print(B_RED + f"❌ Error al comprobar contenedor Docker '{service_name}': {e}" + RESET)
        print(B_YELLOW + "Asegúrate de que Docker Desktop esté encendido." + RESET)
        sys.exit(1)

def run_query(service_name, database, password, sql):
    """Ejecuta una consulta SQL en MySQL dentro del contenedor Docker y retorna la tabla formateada."""
    env = os.environ.copy()
    env["MYSQL_PWD"] = password
    
    cmd = [
        "docker", "compose", "exec", "-T",
        "-e", f"MYSQL_PWD={password}",
        service_name,
        "mysql", "-u", "root", "-t", database, "-e", sql
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return None, res.stderr.strip()
    return res.stdout.strip(), None

def main():
    parser = argparse.ArgumentParser(description="SQL Aesthetic Runner")
    parser.add_argument("--file", required=True, help="Ruta al archivo .sql")
    parser.add_argument("--service", required=True, help="Servicio Docker Compose (db-practica1 / db-practica2)")
    parser.add_argument("--database", required=True, help="Nombre de la base de datos (pubs / northwind)")
    parser.add_argument("--port", default="3306", help="Puerto de host mapeado")
    parser.add_argument("--title", default="Reporte de Análisis", help="Título del reporte")
    parser.add_argument("--password", default="rootpassword", help="Contraseña root de MySQL")
    args = parser.parse_args()

    # Cargar variables de entorno si existe .env
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if k == "PRACTICA1_DB_ROOT_PASSWORD" and args.service == "db-practica1":
                        args.password = v
                    elif k == "PRACTICA2_DB_ROOT_PASSWORD" and args.service == "db-practica2":
                        args.password = v

    print_header(args.title, args.file, args.database, args.service, args.port)
    ensure_container_running(args.service)
    
    statements = parse_sql_file(args.file)
    print(DIM + f"🚀 Procesando {len(statements)} bloques de consulta desde {args.file}..." + RESET)
    
    current_phase = None
    executed_count = 0
    start_time = time.time()
    
    for item in statements:
        sql = item["sql"].strip()
        comments = item["comments"]
        
        # Ignorar USE db; directo si coincide
        if sql.upper().startswith("USE "):
            continue
            
        step_title = None
        notes = []
        is_final = False
        
        for c in comments:
            c_clean = c.lstrip("-=").strip()
            if not c_clean:
                continue
            if "FASE " in c_clean.upper() or "ANEXO " in c_clean.upper():
                phase_title = c_clean
                if phase_title != current_phase:
                    current_phase = phase_title
                    print_phase(current_phase)
            elif any(c_clean.startswith(f"{x}.") for x in range(1, 10)) or "CONSULTA FINAL" in c_clean.upper() or "INVESTIGACIÓN" in c_clean.upper():
                step_title = c_clean
                if "CONSULTA FINAL" in c_clean.upper() or "MASTER QUERY" in c_clean.upper():
                    is_final = True
            elif c_clean.lower().startswith(("propósito:", "proposito:", "hallazgo", "resultado", "alerta", "nota", "criterio")):
                notes.append(c_clean)
                
        if not step_title:
            # Resumen de las primeras palabras del SQL
            first_line = sql.splitlines()[0]
            step_title = (first_line[:70] + "...") if len(first_line) > 70 else first_line

        print_step(step_title, notes, is_final=is_final)
        
        stdout, stderr = run_query(args.service, args.database, args.password, sql)
        if stderr:
            print(B_RED + f"     ❌ Error en consulta: {stderr}" + RESET)
        elif stdout:
            print(style_mysql_table(stdout))
            executed_count += 1
        else:
            print(DIM + "     ✔ Consulta ejecutada sin registros devueltos." + RESET)
        print()
        
    elapsed = time.time() - start_time
    w = get_terminal_width()
    print(B_GREEN + "╔" + "═" * (w - 2) + "╗" + RESET)
    summary_text = f"  ✨ EJECUCIÓN COMPLETADA EXITOSAMENTE  |  {executed_count} consultas ejecutadas  |  ⏱️  {elapsed:.2f}s  "
    print(B_GREEN + "║" + BOLD + B_GREEN + summary_text.center(w - 2) + RESET + B_GREEN + "║" + RESET)
    print(B_GREEN + "╚" + "═" * (w - 2) + "╝" + RESET + "\n")

if __name__ == "__main__":
    main()

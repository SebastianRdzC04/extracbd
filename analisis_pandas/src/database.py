"""
Módulo de Gestión de Conexiones a Bases de Datos y Extracción para Pandas.
Diseñado para la arquitectura de prácticas en Docker (MySQL 8.0: Northwind y Pubs).

Regla de Ingeniería:
- Extracción de datos en bruto o mediante consultas simples con como máximo 2 JOINs.
- Todo el procesamiento relacional, álgebra relacional, filtrado y comprobaciones
  se delega a Pandas en Python.
"""

import os
import re
import socket
from pathlib import Path
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Localizar la raíz del repositorio y cargar .env si existe
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"

if ENV_FILE.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_FILE)
    except ImportError:
        # Fallback manual para leer .env sin dependencias externas
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

# Parámetros predeterminados seguros (alineados con docker-compose.yml)
DB_CONFIGS = {
    "northwind": {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("PRACTICA2_DB_PORT", "3308")),
        "database": os.getenv("PRACTICA2_DB_NAME", "northwind"),
        "user": os.getenv("PRACTICA2_DB_USER_ROOT", "root"),
        "password": os.getenv("PRACTICA2_DB_ROOT_PASSWORD", "rootpassword"),
    },
    "pubs": {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("PRACTICA1_DB_PORT", "3307")),
        "database": os.getenv("PRACTICA1_DB_NAME", "pubs"),
        "user": os.getenv("PRACTICA1_DB_USER_ROOT", "root"),
        "password": os.getenv("PRACTICA1_DB_ROOT_PASSWORD", "rootpassword"),
    }
}


def is_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """Verifica si el puerto del contenedor está escuchando."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def get_engine(db_key: str = "northwind") -> Engine:
    """
    Crea y retorna un motor de SQLAlchemy configurado con PyMySQL.
    """
    if db_key not in DB_CONFIGS:
        raise ValueError(f"Base de datos desconocida: '{db_key}'. Opciones válidas: {list(DB_CONFIGS.keys())}")
    
    cfg = DB_CONFIGS[db_key]
    host = cfg["host"]
    port = cfg["port"]
    user = cfg["user"]
    pwd = cfg["password"]
    db = cfg["database"]

    if not is_port_open(host, port):
        raise ConnectionError(
            f"❌ No se puede conectar a MySQL en {host}:{port} ({db_key}).\n"
            f"Asegúrate de que el contenedor Docker esté levantado con: 'make db-practica2' o 'docker compose up -d db-practica2'"
        )

    # Conexión con charset utf8mb4 para preservar acentos y caracteres especiales
    connection_url = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}?charset=utf8mb4"
    return create_engine(connection_url, pool_pre_ping=True)


def validate_max_joins(sql_query: str, max_joins: int = 2) -> int:
    """
    Inspecciona la consulta SQL y asegura que no exceda el número máximo de JOINs permitido.
    Regla del requerimiento: Máximo 2 JOINs en SQL.
    """
    clean_sql = re.sub(r"--.*", "", sql_query)
    clean_sql = re.sub(r"/\*.*?\*/", "", clean_sql, flags=re.DOTALL)
    join_matches = re.findall(r"\b(?:INNER\s+|LEFT\s+|RIGHT\s+|CROSS\s+|FULL\s+)?JOIN\b", clean_sql, re.IGNORECASE)
    join_count = len(join_matches)
    
    if join_count > max_joins:
        raise ValueError(
            f"⚠️ VIOLACIÓN DE REGLA: La consulta contiene {join_count} JOINs, "
            f"pero el límite estricto establecido es de máximo {max_joins} JOINs.\n"
            f"Estrategia requerida: Extraiga las tablas a DataFrames de Pandas y realice los merges en Python."
        )
    return join_count


def extract_table(table_name: str, engine: Optional[Engine] = None, db_key: str = "northwind") -> pd.DataFrame:
    """
    Extrae una tabla completa de MySQL hacia un DataFrame de Pandas (0 JOINs).
    """
    if engine is None:
        engine = get_engine(db_key)
    
    # Manejar nombres de tablas con espacios (ej. `order details`)
    escaped_table = f"`{table_name}`" if not table_name.startswith("`") else table_name
    query = f"SELECT * FROM {escaped_table}"
    return pd.read_sql_query(query, con=engine)


def load_query(sql_query: str, engine: Optional[Engine] = None, db_key: str = "northwind", enforce_join_limit: bool = True) -> pd.DataFrame:
    """
    Ejecuta una consulta SQL hacia un DataFrame, validando opcionalmente el límite de JOINs.
    """
    if enforce_join_limit:
        validate_max_joins(sql_query, max_joins=2)
    
    if engine is None:
        engine = get_engine(db_key)
        
    return pd.read_sql_query(sql_query, con=engine)

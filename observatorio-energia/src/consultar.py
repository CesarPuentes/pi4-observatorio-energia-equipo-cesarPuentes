"""
Ejecuta las consultas SQL de negocio sobre la Capa Oro (data/gold/observatorio.duckdb)
y/o sobre la Capa Bronce (consultas/*.sql).

Uso:
    python -m src.consultar            # ejecuta las consultas de la capa oro (y bronce si se pide --bronce)
    python -m src.consultar --bronce   # ejecuta las consultas de bronce
"""
import os
import sys

import duckdb

from src import config
from src.utils import log


def ejecutar_consultas_oro() -> None:
    """Ejecuta las consultas analiticas de `consultas/oro/*.sql` contra el esquema estrella en DuckDB."""
    if not config.DUCKDB_ORO.exists():
        raise FileNotFoundError(
            f"No existe {config.DUCKDB_ORO}. Ejecute primero: python -m src.transformar"
        )
    con = duckdb.connect(str(config.DUCKDB_ORO), read_only=True)
    for archivo in sorted(config.DIR_CONSULTAS_ORO.glob("*.sql")):
        log(f"[ORO] Consulta: {archivo.name}")
        sql = archivo.read_text(encoding="utf-8")
        print(con.sql(sql).df().to_string(index=False))
        print()
    con.close()


def ejecutar_consultas_bronce() -> None:
    """Ejecuta las consultas exploratorias iniciales sobre los Parquet de la capa bronce."""
    os.chdir(config.RAIZ)
    con = duckdb.connect()
    for archivo in sorted((config.RAIZ / "consultas").glob("*.sql")):
        log(f"[BRONCE] Consulta: {archivo.name}")
        sql = archivo.read_text(encoding="utf-8")
        print(con.sql(sql).df().to_string(index=False))
        print()
    con.close()


def main() -> None:
    if "--bronce" in sys.argv:
        ejecutar_consultas_bronce()
    else:
        ejecutar_consultas_oro()


if __name__ == "__main__":
    main()

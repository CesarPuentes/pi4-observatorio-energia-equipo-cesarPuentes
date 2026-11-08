"""
Orquestador unico de transformacion reproducible (Capa Plata + Reporte de Calidad + Capa Oro con dbt).

Uso:
    python -m src.transformar
"""
import shutil
import subprocess
import sys
import time
from pathlib import Path

import duckdb
import pandas as pd

from src import config
from src.quality.reporte import generar_reporte_calidad
from src.silver import divipola, enerandes, ideam, noaa, xm
from src.utils import log


def resumen_plata() -> None:
    """Muestra en consola el resumen de los archivos Parquet generados en data/silver/."""
    log("Resumen de la Capa Plata (data/silver/):")
    print(f"   {'archivo':<36}{'filas':>12}{'columnas':>10}{'KB':>10}")
    for archivo in sorted(config.DIR_SILVER.glob("*.parquet")):
        df = pd.read_parquet(archivo)
        kb = max(1, archivo.stat().st_size // 1024)
        print(f"   {archivo.name:<36}{len(df):>12,}{df.shape[1]:>10}{kb:>10,}")


def ejecutar_dbt_build() -> None:
    """Ejecuta `dbt build --project-dir dbt --profiles-dir dbt` desde la raiz del proyecto."""
    log("Construyendo y probando el Esquema Estrella en Capa Oro con `dbt build`...")
    config.DUCKDB_ORO.parent.mkdir(parents=True, exist_ok=True)

    # Buscar el ejecutable dbt en el mismo entorno virtual de Python o en el PATH
    candidato_venv = Path(sys.executable).resolve().parent / "dbt"
    if candidato_venv.exists():
        cmd_dbt = [str(candidato_venv)]
    elif shutil.which("dbt"):
        cmd_dbt = [shutil.which("dbt")]
    else:
        cmd_dbt = [sys.executable, "-m", "dbt.cli.main"]

    comando = cmd_dbt + [
        "build",
        "--project-dir",
        "dbt",
        "--profiles-dir",
        "dbt",
    ]

    resultado = subprocess.run(comando, cwd=str(config.RAIZ), check=False)
    if resultado.returncode != 0:
        raise RuntimeError(f"El comando `dbt build` fallo con codigo {resultado.returncode}")


def resumen_oro() -> None:
    """Muestra las tablas del esquema estrella construidas en data/observatorio.duckdb."""
    if not config.DUCKDB_ORO.exists():
        return
    log("Resumen del Esquema Estrella en Capa Oro (data/observatorio.duckdb):")
    con = duckdb.connect(str(config.DUCKDB_ORO), read_only=True)
    filas_info = con.execute(
        """
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = 'main'
        ORDER BY table_type, table_name
        """
    ).fetchall()
    print(f"   {'modelo_dbt (capa oro)':<36}{'tipo':<16}{'filas':>14}{'columnas':>10}")
    for tabla, table_type in filas_info:
        filas = con.execute(f'SELECT COUNT(*) FROM "{tabla}"').fetchone()[0]
        cols = len(con.execute(f'DESCRIBE "{tabla}"').fetchall())
        if table_type == "VIEW":
            tipo = "Vista (staging)"
        elif tabla.startswith("dim_"):
            tipo = "Dimension"
        else:
            tipo = "Hecho"
        print(f"   {tabla:<36}{tipo:<16}{filas:>14,}{cols:>10}")
    con.close()


def main() -> None:
    inicio = time.time()
    log("=== Inicio de transformacion: Bronce -> Plata (Pandera) -> Oro (dbt + DuckDB) ===")

    # 1. Limpieza y validacion Pandera de la fuente propia DIVIPOLA (base para municipios)
    df_divipola, met_divipola = divipola.limpiar()
    catalogo_ant = divipola.construir_catalogo_antioquia(df_divipola)

    # 2. Limpieza y validacion Pandera de las 4 hojas del Excel de EnerAndes (2023 a 2026)
    res_ener = enerandes.limpiar_enerandes()
    met_ener = res_ener["metricas"]
    df_cuarentena_ener = res_ener["cuarentena_df"]

    # 3. Limpieza y validacion Pandera de las 6 tablas de XM
    _tablas_xm, met_xm = xm.limpiar()

    # 4. Limpieza y validacion Pandera de las 2 tablas del IDEAM
    tablas_ideam, met_ideam = ideam.limpiar(catalogo_ant)

    # 5. Limpieza y validacion Pandera del indice ONI de NOAA
    _df_noaa, met_noaa = noaa.limpiar()

    # 6. Generar reporte automatico de calidad (docs/reporte_calidad.md)
    todas_metricas = met_ener + met_xm + met_ideam + met_noaa + met_divipola
    generar_reporte_calidad(
        todas_metricas,
        df_cuarentena_enerandes=df_cuarentena_ener,
        df_cuarentena_ideam=tablas_ideam.get("ideam_cuarentena"),
    )

    resumen_plata()

    # 7. Construir y validar la Capa Oro (esquema estrella) con dbt build
    ejecutar_dbt_build()
    resumen_oro()

    log(f"=== Transformacion Plata + Oro completada sin errores en {time.time() - inicio:.1f} s ===")


if __name__ == "__main__":
    main()

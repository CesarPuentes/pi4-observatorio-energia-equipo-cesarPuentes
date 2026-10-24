"""
Punto de entrada unico del pipeline de extraccion (capa BRONCE).

Uso:
    python -m src.pipeline              # descarga lo que falte
    python -m src.pipeline --forzar     # vuelve a descargar todo
"""
# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
import sys      # sys.argv: lista con lo que se escribio en el comando (ej. --forzar)
import time     # time.time(): segundos actuales, para medir cuanto tarda

import pandas as pd     # pandas: para abrir cada Parquet y contar filas y columnas

from src import config                                        # configuracion central
from src.extract import divipola, enerandes, ideam, noaa, xm  # los 5 extractores (src/extract/*.py)
from src.utils import log                                     # mensajes con hora


def exportar_muestras() -> None:
    """Guarda en data/sample/ una muestra CSV con las primeras 200 filas de cada archivo de bronce."""
    config.DIR_SAMPLE.mkdir(parents=True, exist_ok=True)
    archivos = sorted(config.DIR_BRONZE.glob("*.parquet"))
    for archivo in archivos:
        df = pd.read_parquet(archivo)
        ruta_csv = config.DIR_SAMPLE / f"{archivo.stem}.csv"
        df.head(config.SAMPLE_FILAS).to_csv(ruta_csv, index=False)
    log(f"Muestras CSV actualizadas en data/sample/ ({len(archivos)} archivos, max {config.SAMPLE_FILAS} filas c/u)")


def resumen() -> None:
    """Muestra una tabla con los archivos de la capa bronce."""
    log("Resumen de la capa bronce:")
    # :<36 alinea a la izquierda en 36 espacios; :>10 a la derecha en 10.
    print(f"   {'archivo':<36}{'filas':>10}{'columnas':>10}{'KB':>8}")
    for archivo in sorted(config.DIR_BRONZE.glob("*.parquet")):    # cada .parquet, en orden
        df = pd.read_parquet(archivo)
        # len(df) = filas; df.shape[1] = columnas; st_size // 1024 = tamano en KB
        print(f"   {archivo.name:<36}{len(df):>10,}{df.shape[1]:>10}{archivo.stat().st_size // 1024:>8}")


def main() -> None:
    forzar = "--forzar" in sys.argv       # True si el comando trae --forzar
    inicio = time.time()                  # hora de inicio, para medir
    log(f"Pipeline bronce | rango {config.FECHA_INICIO} a {config.FECHA_FIN} | forzar={forzar}")
    for extractor in (xm, ideam, noaa, enerandes, divipola):   # los 5 extractores, EN ORDEN
        extractor.extraer(forzar)                              # todos tienen la funcion extraer()
    exportar_muestras()
    resumen()
    log(f"Listo en {time.time() - inicio:.0f} s")    # :.0f = sin decimales


# Este bloque solo se ejecuta cuando se corre el archivo directamente
# (python -m src.pipeline), no cuando otro archivo lo importa.
if __name__ == "__main__":
    main()

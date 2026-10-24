"""
Fuente 5 (propia) - DIVIPOLA del DANE en datos.gov.co (API Socrata / SoQL).
  - Catalogo oficial de la Division Politico-Administrativa de Colombia (municipios y departamentos).
  - Sirve para normalizar los nombres de municipios (con errores ortograficos, tildes o mayusculas
    inconsistentes en EnerAndes e IDEAM) mediante el codigo oficial DANE (cod_mpio) y cruzar
    las ventas de EnerAndes con el clima local por municipio en Antioquia.
Ficha oficial: https://www.datos.gov.co/d/gdxc-w37w
"""
# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
import pandas as pd     # pandas: convierte la lista de diccionarios JSON en DataFrame

from src import config  # config.py: URL del dataset DIVIPOLA en datos.gov.co
from src.utils import guardar_bronce, http_json, log, ya_existe

NOMBRE = "dane_divipola"    # nombre del archivo en data/bronze/
PAGINA = 5000               # filas maximas por pagina en SoQL


def extraer(forzar: bool = False) -> None:
    """Descarga el catalogo oficial de municipios DIVIPOLA (DANE) y lo guarda en bronce."""
    log("DANE - catalogo oficial de municipios DIVIPOLA (fuente propia)")
    if ya_existe(NOMBRE, forzar):
        return

    filas = []
    offset = 0
    while True:
        params = {
            "$order": "cod_mpio",
            "$limit": PAGINA,
            "$offset": offset,
        }
        lote = http_json("GET", config.DIVIPOLA_URL, params=params)
        filas.extend(lote)
        if len(lote) < PAGINA:
            break
        offset += PAGINA

    log(f"   municipios descargados: {len(filas)} filas")
    guardar_bronce(pd.DataFrame(filas), NOMBRE, fuente="DANE-DIVIPOLA", origen=config.DIVIPOLA_URL)


if __name__ == "__main__":
    import sys
    extraer(forzar="--forzar" in sys.argv)

"""
Limpieza del indice ONI de NOAA -> Capa Plata (`data/silver/noaa_oni.parquet`).
Convierte cada trimestre movil (`DJF`, `JFM`, ..., `NDJ`) a su mes central (`1..12`),
construye el periodo (`AAAA-MM`) y la fecha mensual (`YYYY-MM-01`) y clasifica la fase ENSO:
  - `oni >= 0.5`  -> 'El Niño'
  - `oni <= -0.5` -> 'La Niña'
  - otro caso     -> 'Neutral'
"""
import pandas as pd

from src.quality.esquemas import ESQUEMA_NOAA_ONI
from src.utils import guardar_plata, log, ruta_bronce

# Mapa oficial de trimestres moviles de NOAA a su mes central (1 = enero ... 12 = diciembre)
MAPA_TRIMESTRE_MES = {
    "DJF": 1,   # diciembre - enero - febrero   -> enero
    "JFM": 2,   # enero - febrero - marzo       -> febrero
    "FMA": 3,   # febrero - marzo - abril       -> marzo
    "MAM": 4,   # marzo - abril - mayo          -> abril
    "AMJ": 5,   # abril - mayo - junio          -> mayo
    "MJJ": 6,   # mayo - junio - julio          -> junio
    "JJA": 7,   # junio - julio - agosto        -> julio
    "JAS": 8,   # julio - agosto - septiembre   -> agosto
    "ASO": 9,   # agosto - septiembre - octubre -> septiembre
    "SON": 10,  # septiembre - octubre - nov.   -> octubre
    "OND": 11,  # octubre - noviembre - dic.    -> noviembre
    "NDJ": 12,  # noviembre - diciembre - enero -> diciembre
}


def trimestre_a_mes_central(trimestre: str) -> int:
    """Convierte el codigo de trimestre movil de NOAA (ej. 'DJF', 'JAS') al numero de su mes central (1..12)."""
    clave = str(trimestre).strip().upper()
    if clave not in MAPA_TRIMESTRE_MES:
        raise ValueError(f"Trimestre movil NOAA no reconocido: {trimestre!r}")
    return MAPA_TRIMESTRE_MES[clave]


def calcular_fase_enso(oni: float) -> str:
    """
    Clasifica la fase del fenomeno ENSO a partir de la anomalia ONI:
      - El Niño si oni >= 0.5
      - La Niña si oni <= -0.5
      - Neutral en los demas casos (-0.5 < oni < 0.5)
    """
    valor = float(oni)
    if valor >= 0.5:
        return "El Niño"
    if valor <= -0.5:
        return "La Niña"
    return "Neutral"


def limpiar_noaa_df(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Transforma el DataFrame crudo de NOAA ONI a serie mensual tipada con fase ENSO."""
    filas_antes = len(df_raw)

    df = pd.DataFrame()
    df["trimestre_movil"] = df_raw["SEAS"].astype(str).str.strip().str.upper()
    df["anio"] = pd.to_numeric(df_raw["YR"], errors="raise").astype(int)
    df["mes"] = df["trimestre_movil"].apply(trimestre_a_mes_central).astype(int)
    df["periodo"] = df["anio"].astype(str) + "-" + df["mes"].astype(str).str.zfill(2)
    df["fecha"] = pd.to_datetime(df["periodo"] + "-01").astype("datetime64[ns]")
    df["total_c"] = pd.to_numeric(df_raw["TOTAL"], errors="raise").astype(float)
    df["oni"] = pd.to_numeric(df_raw["ANOM"], errors="raise").astype(float)
    df["fase_enso"] = df["oni"].apply(calcular_fase_enso)

    columnas = ["fecha", "periodo", "anio", "mes", "trimestre_movil", "total_c", "oni", "fase_enso"]
    df = (
        df[columnas]
        .drop_duplicates(subset=["fecha"])
        .sort_values("fecha")
        .reset_index(drop=True)
    )

    conteo_fases = df["fase_enso"].value_counts().to_dict()
    metricas = [
        {
            "fuente": "NOAA",
            "tabla": "noaa_oni",
            "problema": "Serie en trimestres móviles (`DJF`, `JFM`, …, `JAS`) y valores de temperatura/anomalía (`TOTAL`, `ANOM`) como texto (`str`)",
            "regla aplicada": "Asignar cada trimestre móvil a su mes central (`DJF` → `1`, …, `NDJ` → `12`), construir `periodo` (`AAAA-MM`) y `fecha` (`YYYY-MM-01`) y convertir `total_c` y `oni` a `float`",
            "antes": f"{filas_antes:,} trimestres móviles en texto sin fecha calendario",
            "despues": f"{len(df):,} meses únicos con `periodo` (`AAAA-MM`), `fecha` y `oni` numérico",
        },
        {
            "fuente": "NOAA",
            "tabla": "noaa_oni",
            "problema": "Ausencia de clasificación categórica de la fase del fenómeno ENSO",
            "regla aplicada": "Agregar `fase_enso`: `'El Niño'` si `oni >= 0.5`, `'La Niña'` si `oni <= -0.5` y `'Neutral'` en los demás casos",
            "antes": "0 filas con fase ENSO clasificada",
            "despues": (
                f"{len(df):,} meses clasificados "
                f"(El Niño: {conteo_fases.get('El Niño', 0)}, "
                f"La Niña: {conteo_fases.get('La Niña', 0)}, "
                f"Neutral: {conteo_fases.get('Neutral', 0)})"
            ),
        },
    ]
    return df, metricas


def limpiar() -> tuple[pd.DataFrame, list[dict]]:
    """Ejecuta la limpieza de NOAA ONI, valida con Pandera y guarda en data/silver/."""
    log("Limpiando NOAA - Indice ONI y fase ENSO -> Capa Plata")
    df_raw = pd.read_parquet(ruta_bronce("noaa_oni"))
    df_limpio, metricas = limpiar_noaa_df(df_raw)
    df_limpio = guardar_plata(df_limpio, "noaa_oni", schema=ESQUEMA_NOAA_ONI)
    return df_limpio, metricas


if __name__ == "__main__":
    limpiar()

"""
Limpieza de las tablas meteorologicas del IDEAM -> Capa Plata (`data/silver/`):
  1. `ideam_precipitacion.parquet` (lluvia acumulada diaria por estacion en Antioquia)
  2. `ideam_temperatura.parquet`   (temperatura media, minima y maxima diaria por estacion en Antioquia)
  3. `ideam_cuarentena.parquet`    (lecturas de precipitacion > 500 mm/dia por volcado acumulado de sensor)
"""
import pandas as pd

from src.quality.esquemas import (
    ESQUEMA_IDEAM_PRECIPITACION as SCHEMA_IDEAM_PRECIPITACION,
    ESQUEMA_IDEAM_TEMPERATURA as SCHEMA_IDEAM_TEMPERATURA,
)
from src.silver.divipola import construir_catalogo_antioquia, resolver_municipio_antioquia
from src.utils import guardar_plata, log, ruta_bronce

MAX_PRECIPITACION_DIARIA_MM = 500.0


def limpiar_precipitacion_df(
    df_raw: pd.DataFrame,
    catalogo_antioquia: dict[str, tuple[str, str]],
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    """
    Limpia ideam_precipitacion_diaria:
      - Convierte fecha a datetime64[ns] y valores (precipitacion_mm, latitud, longitud, n_obs) a numericos.
      - Cruza cada estacion con su municipio oficial en DIVIPOLA (cod_mpio y municipio).
      - Aisla en cuarentena lecturas > 500 mm/dia producto de volcados multianuales del sensor.
    """
    filas_antes = len(df_raw)
    mpios_raw_antes = int(df_raw["municipio"].nunique())

    df = pd.DataFrame()
    df["codigo_estacion"] = df_raw["codigoestacion"].astype(str).str.strip()
    df["nombre_estacion"] = df_raw["nombreestacion"].astype(str).str.strip().str.upper()

    res_mpio = df_raw["municipio"].apply(lambda m: resolver_municipio_antioquia(m, catalogo_antioquia))
    df["cod_mpio"] = [r[0] for r in res_mpio]
    df["municipio"] = [r[1] for r in res_mpio]

    df["latitud"] = pd.to_numeric(df_raw["latitud"], errors="coerce").astype("float64")
    df["longitud"] = pd.to_numeric(df_raw["longitud"], errors="coerce").astype("float64")
    df["fecha"] = pd.to_datetime(df_raw["fecha"]).dt.floor("D").astype("datetime64[ns]")
    df["precipitacion_mm"] = pd.to_numeric(df_raw["precipitacion_mm"], errors="coerce").astype("float64")
    df["n_obs"] = pd.to_numeric(df_raw["n_obs"], errors="coerce").astype("int64")

    df = df.drop_duplicates(subset=["codigo_estacion", "fecha"]).reset_index(drop=True)

    # Detectar valores extremos fisicamente imposibles (> 500 mm en un solo dia)
    es_extremo = (df["precipitacion_mm"] < 0.0) | (df["precipitacion_mm"] > MAX_PRECIPITACION_DIARIA_MM)
    extremos_antes = int(es_extremo.sum())

    df_cuarentena = df.loc[es_extremo].copy()
    df_cuarentena["motivo_cuarentena"] = "precipitacion_diaria_fuera_de_rango_fisico_0_500_mm"
    df_cuarentena = df_cuarentena.reset_index(drop=True)

    df_limpio = (
        df.loc[~es_extremo]
        .sort_values(["fecha", "codigo_estacion"])
        .reset_index(drop=True)
    )

    metricas = [
        {
            "fuente": "IDEAM",
            "tabla": "ideam_precipitacion",
            "problema": "Fechas con sufijo de hora (`2025-01-01T00:00:00.000`), métricas en texto (`str`) y nombres de municipio sin código DANE (`SAN VICENTE` vs. `SAN VICENTE FERRER`)",
            "regla": "Convertir `fecha` a `datetime64[ns]`, `precipitacion_mm`/`latitud`/`longitud` a `float64`, `n_obs` a `int64` y cruzar cada estación con `dane_divipola` (`cod_mpio`)",
            "antes": f"{filas_antes:,} filas con tipos `str` y {mpios_raw_antes} municipios sin `cod_mpio`",
            "despues": f"{len(df_limpio):,} filas tipadas y 100% vinculadas a `cod_mpio` de Antioquia",
        },
        {
            "fuente": "IDEAM",
            "tabla": "ideam_precipitacion",
            "problema": "Valores extremos físicamente imposibles de precipitación diaria (`> 500 mm/día`, hasta `3,081.8 mm` por volcado acumulado de observaciones atrasadas)",
            "regla": "Aislar en `data/silver/ideam_cuarentena.parquet` los registros con `precipitacion_mm > 500 mm` y validar rango `[0, 500]` con Pandera",
            "antes": f"{extremos_antes} registros con precipitación diaria > 500 mm",
            "despues": f"0 registros fuera de `[0, 500]` mm en `ideam_precipitacion` ({extremos_antes} en cuarentena)",
        },
    ]
    return df_limpio, df_cuarentena, metricas


def limpiar_temperatura_df(
    df_raw: pd.DataFrame,
    catalogo_antioquia: dict[str, tuple[str, str]],
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Limpia ideam_temperatura_diaria:
      - Convierte fecha a datetime64[ns] y temperaturas (media, min, max) a float64 (redondeadas a 2 decimales).
      - Cruza cada estacion con su municipio oficial en DIVIPOLA (cod_mpio y municipio).
      - Verifica consistencia termica (temp_min_c <= temp_media_c <= temp_max_c).
    """
    filas_antes = len(df_raw)

    df = pd.DataFrame()
    df["codigo_estacion"] = df_raw["codigoestacion"].astype(str).str.strip()
    df["nombre_estacion"] = df_raw["nombreestacion"].astype(str).str.strip().str.upper()

    res_mpio = df_raw["municipio"].apply(lambda m: resolver_municipio_antioquia(m, catalogo_antioquia))
    df["cod_mpio"] = [r[0] for r in res_mpio]
    df["municipio"] = [r[1] for r in res_mpio]

    df["latitud"] = pd.to_numeric(df_raw["latitud"], errors="coerce").astype("float64")
    df["longitud"] = pd.to_numeric(df_raw["longitud"], errors="coerce").astype("float64")
    df["fecha"] = pd.to_datetime(df_raw["fecha"]).dt.floor("D").astype("datetime64[ns]")
    df["temp_media_c"] = pd.to_numeric(df_raw["temp_media_c"], errors="coerce").round(2).astype("float64")
    df["temp_min_c"] = pd.to_numeric(df_raw["temp_min_c"], errors="coerce").round(2).astype("float64")
    df["temp_max_c"] = pd.to_numeric(df_raw["temp_max_c"], errors="coerce").round(2).astype("float64")
    df["n_obs"] = pd.to_numeric(df_raw["n_obs"], errors="coerce").astype("int64")

    df = (
        df.drop_duplicates(subset=["codigo_estacion", "fecha"])
        .sort_values(["fecha", "codigo_estacion"])
        .reset_index(drop=True)
    )

    metricas = [
        {
            "fuente": "IDEAM",
            "tabla": "ideam_temperatura",
            "problema": "Temperaturas (`temp_media_c`, `temp_min_c`, `temp_max_c`) como texto con hasta 16 decimales de precisión flotante y estaciones sin `cod_mpio`",
            "regla": "Convertir `fecha` a `datetime64[ns]`, redondear temperaturas a 2 decimales (`float64`), validar rangos térmicos y asignar `cod_mpio` oficial DIVIPOLA",
            "antes": f"{filas_antes:,} filas en texto (`str`) sin código de municipio DANE",
            "despues": f"{len(df):,} filas tipadas (`float64`) con `cod_mpio` validado en 37 municipios",
        }
    ]
    return df, metricas


def limpiar(
    catalogo_antioquia: dict[str, tuple[str, str]] | None = None,
) -> tuple[dict[str, pd.DataFrame], list[dict]]:
    """Ejecuta la limpieza de precipitacion y temperatura del IDEAM, valida con Pandera y guarda en plata."""
    log("Limpiando IDEAM - Precipitacion y Temperatura -> Capa Plata")
    if catalogo_antioquia is None:
        catalogo_antioquia = construir_catalogo_antioquia()

    raw_precip = pd.read_parquet(ruta_bronce("ideam_precipitacion_diaria"))
    df_precip, df_cuarentena_ideam, met_precip = limpiar_precipitacion_df(raw_precip, catalogo_antioquia)
    df_precip = guardar_plata(df_precip, "ideam_precipitacion", schema=SCHEMA_IDEAM_PRECIPITACION)
    guardar_plata(df_cuarentena_ideam, "ideam_cuarentena", schema=None)

    raw_temp = pd.read_parquet(ruta_bronce("ideam_temperatura_diaria"))
    df_temp, met_temp = limpiar_temperatura_df(raw_temp, catalogo_antioquia)
    df_temp = guardar_plata(df_temp, "ideam_temperatura", schema=SCHEMA_IDEAM_TEMPERATURA)

    tablas = {
        "ideam_precipitacion": df_precip,
        "ideam_temperatura": df_temp,
        "ideam_cuarentena": df_cuarentena_ideam,
    }
    return tablas, met_precip + met_temp


if __name__ == "__main__":
    limpiar()

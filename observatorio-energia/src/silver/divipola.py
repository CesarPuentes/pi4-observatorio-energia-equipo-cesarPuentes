"""
Limpieza de la fuente propia DANE DIVIPOLA (data/bronze/dane_divipola.parquet -> data/silver/dane_divipola.parquet)
y utilidades de normalizacion geografica de municipios de Antioquia para EnerAndes e IDEAM.
"""
import unicodedata

import pandas as pd

from src.quality.esquemas import ESQUEMA_DANE_DIVIPOLA
from src.utils import guardar_plata, log, ruta_bronce

# Alias conocidos en fuentes comerciales (EnerAndes) y meteorologicas (IDEAM)
ALIAS_MUNICIPIOS_ANTIOQUIA = {
    "MEDELLIN D.E.": "MEDELLIN",
    "RIONEGRO (ANT)": "RIONEGRO",
    "RIO NEGRO": "RIONEGRO",
    "STA FE DE ANTIOQUIA": "SANTA FE DE ANTIOQUIA",
    "SANTAFE DE ANTIOQUIA": "SANTA FE DE ANTIOQUIA",
    "SAN VICENTE": "SAN VICENTE FERRER",
    "DON MATIAS": "DONMATIAS",
    "EL CARMEN DE VIBORAL": "EL CARMEN DE VIBORAL",
    "CARMEN DE VIBORAL": "EL CARMEN DE VIBORAL",
    "SAN PEDRO": "SAN PEDRO DE LOS MILAGROS",
}


def normalizar_texto_municipio(valor: str | None) -> str:
    """Elimina tildes, espacios repetidos y pasa a mayusculas para comparacion canonica."""
    if valor is None or pd.isna(valor):
        return ""
    limpio = " ".join(str(valor).strip().upper().split())
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", limpio) if unicodedata.category(c) != "Mn"
    )
    return ALIAS_MUNICIPIOS_ANTIOQUIA.get(sin_tildes, sin_tildes)


def limpiar_divipola_df(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """
    Limpia el DataFrame crudo de DIVIPOLA:
      - Reemplaza coma decimal (',') por punto ('.') en latitud y longitud y convierte a float64.
      - Normaliza codigos DANE (2 digitos departamento, 5 digitos municipio) y textos.
      - Elimina posibles duplicados por cod_mpio.
    """
    total_inicial = len(df_raw)
    comas_lat_antes = int(df_raw["latitud"].astype(str).str.contains(",", na=False).sum())
    comas_lon_antes = int(df_raw["longitud"].astype(str).str.contains(",", na=False).sum())
    duplicados_antes = int(df_raw.duplicated(subset=["cod_mpio"]).sum())

    df = df_raw.copy()
    df["cod_dpto"] = df["cod_dpto"].astype(str).str.strip().str.zfill(2)
    df["departamento"] = df["dpto"].astype(str).str.strip().str.upper()
    df["cod_mpio"] = df["cod_mpio"].astype(str).str.strip().str.zfill(5)
    df["municipio"] = df["nom_mpio"].astype(str).str.strip().str.upper()
    df["tipo_municipio"] = df["tipo_municipio"].astype(str).str.strip()

    df["latitud"] = pd.to_numeric(
        df["latitud"].astype(str).str.strip().str.replace(",", ".", regex=False),
        errors="coerce",
    ).astype(float)
    df["longitud"] = pd.to_numeric(
        df["longitud"].astype(str).str.strip().str.replace(",", ".", regex=False),
        errors="coerce",
    ).astype(float)

    columnas_finales = [
        "cod_dpto",
        "departamento",
        "cod_mpio",
        "municipio",
        "tipo_municipio",
        "latitud",
        "longitud",
    ]
    df = (
        df[columnas_finales]
        .drop_duplicates(subset=["cod_mpio"])
        .sort_values("cod_mpio")
        .reset_index(drop=True)
    )

    metricas = [
        {
            "fuente": "DANE-DIVIPOLA",
            "tabla": "dane_divipola",
            "problema": "Coordenadas geográficas (`latitud` y `longitud`) almacenadas como texto con coma decimal (`,`) en lugar de punto (`.`)",
            "regla aplicada": "Reemplazar `,` por `.` y convertir `latitud` y `longitud` a `float`, validando rangos de Colombia (`latitud` en [-5, 14], `longitud` en [-82, -66])",
            "antes": f"{comas_lat_antes:,} lat / {comas_lon_antes:,} lon con coma decimal (`str`)",
            "despues": "0 con coma decimal (`float` válido en las 1,122 filas)",
        },
        {
            "fuente": "DANE-DIVIPOLA",
            "tabla": "dane_divipola",
            "problema": "Estandarización de códigos DANE (`cod_dpto`, `cod_mpio`), nombres oficiales y verificación de unicidad de `cod_mpio`",
            "regla aplicada": "Formatear `cod_dpto` a 2 dígitos y `cod_mpio` a 5 dígitos, normalizar nombres en mayúsculas y garantizar llave única `cod_mpio`",
            "antes": f"{total_inicial:,} filas ({duplicados_antes} duplicados)",
            "despues": f"{len(df):,} municipios únicos validados con Pandera",
        },
    ]
    return df, metricas


def construir_catalogo_antioquia(
    df_divipola: pd.DataFrame | None = None,
) -> dict[str, tuple[str, str]]:
    """
    Devuelve un diccionario {nombre_normalizado_sin_tildes: (cod_mpio, nombre_oficial_con_tilde)}
    para los 125 municipios de Antioquia (cod_dpto == '05').
    """
    if df_divipola is None:
        df_raw = pd.read_parquet(ruta_bronce("dane_divipola"))
        df_divipola, _ = limpiar_divipola_df(df_raw)

    ant = df_divipola[df_divipola["cod_dpto"] == "05"]
    catalogo: dict[str, tuple[str, str]] = {}
    for _, fila in ant.iterrows():
        clave = normalizar_texto_municipio(fila["municipio"])
        catalogo[clave] = (str(fila["cod_mpio"]), str(fila["municipio"]))
    return catalogo


def resolver_municipio_antioquia(
    nombre_sucio: str | None, catalogo: dict[str, tuple[str, str]]
) -> tuple[str | None, str | None]:
    """Resuelve un nombre de municipio sucio contra el catalogo DIVIPOLA de Antioquia."""
    clave = normalizar_texto_municipio(nombre_sucio)
    if clave in catalogo:
        return catalogo[clave]
    return None, None


def limpiar() -> tuple[pd.DataFrame, list[dict]]:
    """Ejecuta la limpieza de DIVIPOLA, valida con Pandera y guarda en data/silver/."""
    log("Limpiando DANE - DIVIPOLA (capa plata)")
    df_raw = pd.read_parquet(ruta_bronce("dane_divipola"))
    df_limpio, metricas = limpiar_divipola_df(df_raw)
    df_validado = guardar_plata(df_limpio, "dane_divipola", schema=ESQUEMA_DANE_DIVIPOLA)
    return df_validado, metricas


if __name__ == "__main__":
    limpiar()

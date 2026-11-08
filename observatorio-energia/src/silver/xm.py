"""
Limpieza de las 6 tablas de XM Sinergox -> Capa Plata (`data/silver/`):
  1. `xm_precio_bolsa.parquet`        (de 24 columnas Hour01..Hour24 a formato largo fecha-hora)
  2. `xm_demanda.parquet`             (de 24 columnas Hour01..Hour24 a formato largo fecha-hora)
  3. `xm_generacion_recurso.parquet`  (de 24 columnas Hour01..Hour24 a formato largo fecha-hora-recurso)
  4. `xm_embalses.parquet`            (fecha y porcentaje de volumen util 0-100 %)
  5. `xm_aportes.parquet`             (fecha y aportes hidricos en kWh)
  6. `xm_listado_recursos.parquet`    (catalogo maestro de plantas sin duplicados y con integridad referencial)
"""
import pandas as pd

from src.quality.esquemas import (
    ESQUEMA_XM_APORTES as SCHEMA_XM_APORTES,
    ESQUEMA_XM_DEMANDA as SCHEMA_XM_DEMANDA,
    ESQUEMA_XM_EMBALSES as SCHEMA_XM_EMBALSES,
    ESQUEMA_XM_GENERACION_RECURSO as SCHEMA_XM_GENERACION_RECURSO,
    ESQUEMA_XM_LISTADO_RECURSOS as SCHEMA_XM_LISTADO_RECURSOS,
    ESQUEMA_XM_PRECIO_BOLSA as SCHEMA_XM_PRECIO_BOLSA,
)
from src.utils import guardar_plata, log, ruta_bronce

COLUMNAS_HORA = [f"Hour{i:02d}" for i in range(1, 25)]


def despivotar_horario_xm(
    df_raw: pd.DataFrame,
    nombre_valor: str,
    incluir_recurso: bool = False,
) -> tuple[pd.DataFrame, dict]:
    """
    Convierte una tabla horaria de XM en formato ancho (24 columnas Hour01..Hour24 como texto)
    a formato largo (una fila por fecha y hora, o fecha, hora y codigo_recurso) con valores numericos.
    """
    filas_anchas_antes = len(df_raw)
    cols_hora_presentes = [c for c in COLUMNAS_HORA if c in df_raw.columns]
    id_vars = ["Date", "code"] if incluir_recurso else ["Date"]

    largo = df_raw.melt(
        id_vars=id_vars,
        value_vars=cols_hora_presentes,
        var_name="hora_txt",
        value_name="valor_txt",
    )
    celdas_totales = len(largo)
    largo[nombre_valor] = pd.to_numeric(largo["valor_txt"], errors="coerce")
    celdas_nulas_o_vacias = int(largo[nombre_valor].isna().sum())
    celdas_no_positivas = int((largo[nombre_valor] <= 0).sum())

    largo = largo.dropna(subset=[nombre_valor])
    largo = largo[largo[nombre_valor] > 0].copy()

    largo["fecha"] = pd.to_datetime(largo["Date"]).astype("datetime64[ns]")
    largo["hora"] = largo["hora_txt"].str.slice(4, 6).astype("int64")
    largo[nombre_valor] = largo[nombre_valor].astype("float64")

    if incluir_recurso:
        largo["codigo_recurso"] = largo["code"].astype(str).str.strip().str.upper()
        cols_llave = ["fecha", "hora", "codigo_recurso"]
        cols_salida = ["fecha", "hora", "codigo_recurso", nombre_valor]
    else:
        cols_llave = ["fecha", "hora"]
        cols_salida = ["fecha", "hora", nombre_valor]

    duplicados = int(largo.duplicated(subset=cols_llave).sum())
    largo = (
        largo[cols_salida]
        .drop_duplicates(subset=cols_llave)
        .sort_values(cols_llave)
        .reset_index(drop=True)
    )

    info = {
        "filas_anchas_antes": filas_anchas_antes,
        "columnas_hora_antes": len(cols_hora_presentes),
        "celdas_totales": celdas_totales,
        "celdas_nulas_o_vacias": celdas_nulas_o_vacias,
        "celdas_no_positivas": celdas_no_positivas,
        "duplicados": duplicados,
        "filas_largas_despues": len(largo),
    }
    return largo, info


def limpiar_embalses_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Limpia xm_embalses: tipa fecha y convierte Value (fraccion 0..1) a porcentaje (0..100 %)."""
    df = pd.DataFrame()
    df["fecha"] = pd.to_datetime(df_raw["Date"]).astype("datetime64[ns]")
    valores = pd.to_numeric(df_raw["Value"], errors="coerce").astype("float64")
    # En XM PorcVoluUtilDiar viene en fraccion (ej. 0.70058 = 70.058 %)
    es_fraccion = valores.max() <= 1.5
    df["volumen_util_pct"] = (valores * 100.0 if es_fraccion else valores).round(4)
    df = df.dropna(subset=["fecha", "volumen_util_pct"])
    df = df[(df["volumen_util_pct"] >= 0.0) & (df["volumen_util_pct"] <= 100.0)]
    return df.drop_duplicates(subset=["fecha"]).sort_values("fecha").reset_index(drop=True)


def limpiar_aportes_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Limpia xm_aportes: tipa fecha y convierte Value a aportes_energia_kwh (float64 > 0)."""
    df = pd.DataFrame()
    df["fecha"] = pd.to_datetime(df_raw["Date"]).astype("datetime64[ns]")
    df["aportes_energia_kwh"] = pd.to_numeric(df_raw["Value"], errors="coerce").astype("float64")
    df = df.dropna(subset=["fecha", "aportes_energia_kwh"])
    df = df[df["aportes_energia_kwh"] > 0]
    return df.drop_duplicates(subset=["fecha"]).sort_values("fecha").reset_index(drop=True)


def limpiar_listado_recursos_df(
    df_raw: pd.DataFrame,
    codigos_generacion: set[str] | None = None,
) -> tuple[pd.DataFrame, dict]:
    """
    Limpia el catalogo de plantas (ListadoRecursos):
      - Elimina duplicados por codigo_recurso (ej. 5J8H y 5PUN).
      - Normaliza mayusculas/minusculas en tipo_generacion ('Solar' -> 'SOLAR') y estado ('Operacion' -> 'OPERACION').
      - Agrega registros historicos para codigos presentes en generacion pero retirados del corte actual.
    """
    filas_antes = len(df_raw)
    tipos_antes = int(df_raw["Type"].nunique())
    estados_antes = int(df_raw["State"].nunique())
    duplicados_antes = int(df_raw.duplicated(subset=["Code"]).sum())

    df = pd.DataFrame()
    df["codigo_recurso"] = df_raw["Code"].astype(str).str.strip().str.upper()
    df["nombre_recurso"] = df_raw["Name"].astype(str).str.strip().str.upper()
    df["tipo_generacion"] = df_raw["Type"].astype(str).str.strip().str.upper()
    df["fuente_energia"] = df_raw["EnerSource"].astype(str).str.strip().str.upper()
    df["tipo_despacho"] = df_raw["Disp"].astype(str).str.strip().str.upper()
    df["tipo_recurso"] = df_raw["RecType"].astype(str).str.strip().str.upper()
    df["codigo_agente"] = df_raw["CompanyCode"].astype(str).str.strip().str.upper()
    df["fecha_operacion"] = pd.to_datetime(
        df_raw["OperStartdate"], errors="coerce"
    ).fillna(pd.Timestamp("2000-01-01")).astype("datetime64[ns]")
    df["estado"] = df_raw["State"].astype(str).str.strip().str.upper()

    df = df.drop_duplicates(subset=["codigo_recurso"]).reset_index(drop=True)

    # Integridad referencial: si en xm_generacion_recurso hay plantas historicas retiradas del listado actual
    codigos_faltantes = set()
    if codigos_generacion:
        codigos_faltantes = {str(c).strip().upper() for c in codigos_generacion} - set(df["codigo_recurso"])
        if codigos_faltantes:
            filas_hist = pd.DataFrame(
                [
                    {
                        "codigo_recurso": cod,
                        "nombre_recurso": f"RECURSO HISTORICO {cod}",
                        "tipo_generacion": "NO ESPECIFICADO",
                        "fuente_energia": "NO ESPECIFICADO",
                        "tipo_despacho": "NO ESPECIFICADO",
                        "tipo_recurso": "HISTORICO",
                        "codigo_agente": "SIN_AGENTE",
                        "fecha_operacion": pd.Timestamp("2000-01-01"),
                        "estado": "HISTORICO",
                    }
                    for cod in sorted(codigos_faltantes)
                ]
            )
            filas_hist["fecha_operacion"] = filas_hist["fecha_operacion"].astype("datetime64[ns]")
            df = pd.concat([df, filas_hist], ignore_index=True)

    df = df.sort_values("codigo_recurso").reset_index(drop=True)
    info = {
        "filas_antes": filas_antes,
        "duplicados_antes": duplicados_antes,
        "tipos_antes": tipos_antes,
        "estados_antes": estados_antes,
        "historicos_agregados": len(codigos_faltantes),
        "filas_despues": len(df),
    }
    return df, info


def limpiar() -> tuple[dict[str, pd.DataFrame], list[dict]]:
    """Ejecuta la limpieza de las 6 tablas de XM, valida con Pandera y guarda en data/silver/."""
    log("Limpiando XM - 6 tablas del mercado mayorista -> Capa Plata")

    # 1. Precio de bolsa
    raw_precio = pd.read_parquet(ruta_bronce("xm_precio_bolsa"))
    df_precio, info_precio = despivotar_horario_xm(raw_precio, "precio_bolsa_cop_kwh", incluir_recurso=False)
    df_precio = guardar_plata(df_precio, "xm_precio_bolsa", schema=SCHEMA_XM_PRECIO_BOLSA)

    # 2. Demanda real
    raw_demanda = pd.read_parquet(ruta_bronce("xm_demanda"))
    df_demanda, info_demanda = despivotar_horario_xm(raw_demanda, "demanda_real_kwh", incluir_recurso=False)
    df_demanda = guardar_plata(df_demanda, "xm_demanda", schema=SCHEMA_XM_DEMANDA)

    # 3. Generacion por recurso
    raw_gen = pd.read_parquet(ruta_bronce("xm_generacion_recurso"))
    df_gen, info_gen = despivotar_horario_xm(raw_gen, "generacion_kwh", incluir_recurso=True)
    df_gen = guardar_plata(df_gen, "xm_generacion_recurso", schema=SCHEMA_XM_GENERACION_RECURSO)

    # 4. Embalses
    raw_emb = pd.read_parquet(ruta_bronce("xm_embalses"))
    df_emb = limpiar_embalses_df(raw_emb)
    df_emb = guardar_plata(df_emb, "xm_embalses", schema=SCHEMA_XM_EMBALSES)

    # 5. Aportes
    raw_apo = pd.read_parquet(ruta_bronce("xm_aportes"))
    df_apo = limpiar_aportes_df(raw_apo)
    df_apo = guardar_plata(df_apo, "xm_aportes", schema=SCHEMA_XM_APORTES)

    # 6. Listado de recursos
    raw_rec = pd.read_parquet(ruta_bronce("xm_listado_recursos"))
    df_rec, info_rec = limpiar_listado_recursos_df(raw_rec, set(df_gen["codigo_recurso"].unique()))
    df_rec = guardar_plata(df_rec, "xm_listado_recursos", schema=SCHEMA_XM_LISTADO_RECURSOS)

    metricas = [
        {
            "fuente": "XM",
            "tabla": "xm_precio_bolsa",
            "problema": "Estructura ancha de 24 columnas horarias (`Hour01`..`Hour24`) almacenadas como texto (`str`)",
            "regla": "Despivotar (`melt`) a una fila por `fecha` (`datetime64[ns]`) y `hora` (`1..24`, `int64`) con `precio_bolsa_cop_kwh` en `float64`",
            "antes": f"{info_precio['filas_anchas_antes']:,} filas x 24 columnas `str`",
            "despues": f"{info_precio['filas_largas_despues']:,} filas horarias (`fecha`, `hora`) tipadas",
        },
        {
            "fuente": "XM",
            "tabla": "xm_demanda",
            "problema": "Estructura ancha de 24 columnas horarias (`Hour01`..`Hour24`) almacenadas como texto (`str`)",
            "regla": "Despivotar (`melt`) a una fila por `fecha` y `hora` (`1..24`) con `demanda_real_kwh` en `float64 > 0`",
            "antes": f"{info_demanda['filas_anchas_antes']:,} filas x 24 columnas `str`",
            "despues": f"{info_demanda['filas_largas_despues']:,} filas horarias (`fecha`, `hora`) tipadas",
        },
        {
            "fuente": "XM",
            "tabla": "xm_generacion_recurso",
            "problema": "Estructura ancha (`Hour01`..`Hour24` en texto) y 2.47 millones de celdas horarias vacías/nulas (plantas solares/térmicas en horas sin generación)",
            "regla": "Despivotar a (`fecha`, `hora`, `codigo_recurso`), convertir a `float64` y filtrar celdas nulas o sin generación (`<= 0`)",
            "antes": f"{info_gen['filas_anchas_antes']:,} filas anchas ({info_gen['celdas_nulas_o_vacias']:,} celdas horarias nulas)",
            "despues": f"{info_gen['filas_largas_despues']:,} registros horarios válidos con 0 nulos",
        },
        {
            "fuente": "XM",
            "tabla": "xm_embalses / xm_aportes",
            "problema": "Fechas y métricas hidrológicas (`PorcVoluUtilDiar` en fracción `0..1` y `AporEner`) almacenadas como texto (`str`)",
            "regla": "Tipar `fecha` a `datetime64[ns]`, escalar `volumen_util_pct` a porcentaje `[0, 100]` (`float64`) y convertir `aportes_energia_kwh` a `float64 > 0`",
            "antes": f"{len(raw_emb):,} + {len(raw_apo):,} filas en texto y fracción `0..1`",
            "despues": f"{len(df_emb):,} + {len(df_apo):,} filas diarias tipadas y en escala porcentual `0..100 %`",
        },
        {
            "fuente": "XM",
            "tabla": "xm_listado_recursos",
            "problema": "Registros duplicados en el catálogo (`5J8H`, `5PUN`), inconsistencia de mayúsculas (`Solar`/`SOLAR`, `Operacion`/`OPERACION`) y 10 códigos históricos de generación ausentes del corte actual",
            "regla": "Eliminar duplicados por `codigo_recurso`, normalizar textos en mayúsculas e incorporar los recursos históricos (`estado = 'HISTORICO'`) para preservar integridad referencial",
            "antes": f"{info_rec['duplicados_antes']} duplicados, {info_rec['tipos_antes']} tipos, {info_rec['historicos_agregados']} recursos huérfanos en generación",
            "despues": f"0 duplicados, catálogo normalizado y 0 recursos huérfanos ({info_rec['filas_despues']:,} plantas únicas)",
        },
    ]

    tablas = {
        "xm_precio_bolsa": df_precio,
        "xm_demanda": df_demanda,
        "xm_generacion_recurso": df_gen,
        "xm_embalses": df_emb,
        "xm_aportes": df_apo,
        "xm_listado_recursos": df_rec,
    }
    return tablas, metricas


if __name__ == "__main__":
    limpiar()

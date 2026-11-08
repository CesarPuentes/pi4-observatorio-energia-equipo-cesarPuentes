"""
Reglas de calidad de la capa plata, escritas con pandera.

Un ESQUEMA es la lista de condiciones que una tabla limpia DEBE cumplir:
que columnas tiene, de que tipo es cada una y que valores acepta.
Si una sola fila no cumple, pandera detiene el programa y dice cual fila
y cual regla fallo. Asi, ningun dato sucio llega a la capa oro.

Este archivo SOLO GUARDA las reglas: no revisa nada por si solo.
Quien las usa son los programas de limpieza en src/silver/ y las pruebas en tests/.
"""
# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Check, Column

# ---------------------------------------------------------------------------
# 1. ENERANDES - Ventas mensuales limpias (2023 a 2026)
# ---------------------------------------------------------------------------
# Los unicos 4 valores que puede tener la columna segmento
SEGMENTOS = ["Residencial", "Comercial", "Industrial", "No informado"]
# Los unicos 2 valores que puede tener la columna tipo_compra
TIPOS_COMPRA = ["Bolsa", "Contrato"]

# El esquema de la tabla limpia de EnerAndes (base de la clase ampliada a 2023-2026)
ESQUEMA_VENTAS = pa.DataFrameSchema(
    {
        # periodo: texto (str) que cumpla el patron AAAA-MM con un mes de 01 a 12.
        "periodo": Column(str, Check.str_matches(r"^\d{4}-(0[1-9]|1[0-2])$")),
        # divipola: texto de exactamente 5 digitos (^\d{5}$). '05001' cumple; '5001' no
        "divipola": Column(str, Check.str_matches(r"^\d{5}$")),
        # municipio: texto, sin condicion extra (el nombre oficial ya viene de MUNICIPIOS)
        "municipio": Column(str),
        # segmento: texto que este en la lista SEGMENTOS (.isin = "esta en")
        "segmento": Column(str, Check.isin(SEGMENTOS)),
        # tipo_compra: texto que este en la lista TIPOS_COMPRA: solo Bolsa o Contrato
        "tipo_compra": Column(str, Check.isin(TIPOS_COMPRA)),
        # energia_kwh: numero con decimales (float) mayor o igual a 0 (ge = greater or equal)
        "energia_kwh": Column(float, Check.ge(0)),
        # valor_cop: numero >= 0; nullable=True permite celdas vacias (regla 9 de la limpieza)
        "valor_cop": Column(float, Check.ge(0), nullable=True),
        # clientes: numero entero (int) mayor o igual a 0
        "clientes": Column(int, Check.ge(0)),
    },
    # unique: no puede haber dos filas con el mismo periodo, municipio, segmento y tipo de compra
    unique=["periodo", "divipola", "segmento", "tipo_compra"],
    # strict=True: la tabla no puede traer columnas que no esten en este esquema
    strict=True,
)

# ---------------------------------------------------------------------------
# 2. XM - Mercado de Energia Mayorista (horarios, diarios y catalogo)
# ---------------------------------------------------------------------------
ESQUEMA_XM_PRECIO_BOLSA = pa.DataFrameSchema(
    {
        "fecha": Column(
            "datetime64[ns]",
            [Check.ge(pd.Timestamp("2024-01-01")), Check.le(pd.Timestamp("2026-12-31"))],
        ),
        "hora": Column(int, Check.between(1, 24)),
        "precio_bolsa_cop_kwh": Column(float, Check.between(0.0, 20000.0)),
    },
    unique=["fecha", "hora"],
    strict=True,
)

ESQUEMA_XM_DEMANDA = pa.DataFrameSchema(
    {
        "fecha": Column(
            "datetime64[ns]",
            [Check.ge(pd.Timestamp("2024-01-01")), Check.le(pd.Timestamp("2026-12-31"))],
        ),
        "hora": Column(int, Check.between(1, 24)),
        "demanda_real_kwh": Column(float, Check.gt(0.0)),
    },
    unique=["fecha", "hora"],
    strict=True,
)

ESQUEMA_XM_GENERACION_RECURSO = pa.DataFrameSchema(
    {
        "fecha": Column(
            "datetime64[ns]",
            [Check.ge(pd.Timestamp("2024-01-01")), Check.le(pd.Timestamp("2026-12-31"))],
        ),
        "hora": Column(int, Check.between(1, 24)),
        "codigo_recurso": Column(str, Check.str_length(min_value=2, max_value=10)),
        "generacion_kwh": Column(float, Check.gt(0.0)),
    },
    unique=["fecha", "hora", "codigo_recurso"],
    strict=True,
)

ESQUEMA_XM_EMBALSES = pa.DataFrameSchema(
    {
        "fecha": Column(
            "datetime64[ns]",
            [Check.ge(pd.Timestamp("2024-01-01")), Check.le(pd.Timestamp("2026-12-31"))],
        ),
        "volumen_util_pct": Column(float, Check.between(0.0, 100.0)),
    },
    unique=["fecha"],
    strict=True,
)

ESQUEMA_XM_APORTES = pa.DataFrameSchema(
    {
        "fecha": Column(
            "datetime64[ns]",
            [Check.ge(pd.Timestamp("2024-01-01")), Check.le(pd.Timestamp("2026-12-31"))],
        ),
        "aportes_energia_kwh": Column(float, Check.gt(0.0)),
    },
    unique=["fecha"],
    strict=True,
)

TIPOS_GENERACION_XM = [
    "HIDRAULICA",
    "TERMICA",
    "SOLAR",
    "EOLICA",
    "COGENERADOR",
    "NO ESPECIFICADO",
]
TIPOS_DESPACHO_XM = [
    "DESPACHADO CENTRALMENTE",
    "NO DESPACHADO CENTRALMENTE",
    "NO ESPECIFICADO",
]
ESTADOS_RECURSO_XM = ["OPERACION", "PRUEBAS", "INACTIVO", "HISTORICO"]

ESQUEMA_XM_LISTADO_RECURSOS = pa.DataFrameSchema(
    {
        "codigo_recurso": Column(str, Check.str_length(min_value=2, max_value=10)),
        "nombre_recurso": Column(str, Check.str_length(min_value=2)),
        "tipo_generacion": Column(str, Check.isin(TIPOS_GENERACION_XM)),
        "fuente_energia": Column(str, Check.str_length(min_value=2)),
        "tipo_despacho": Column(str, Check.isin(TIPOS_DESPACHO_XM)),
        "tipo_recurso": Column(str, Check.str_length(min_value=2)),
        "codigo_agente": Column(str, Check.str_length(min_value=2)),
        "fecha_operacion": Column("datetime64[ns]"),
        "estado": Column(str, Check.isin(ESTADOS_RECURSO_XM)),
    },
    unique=["codigo_recurso"],
    strict=True,
)

# ---------------------------------------------------------------------------
# 3. IDEAM - Precipitacion y Temperatura diaria en Antioquia
# ---------------------------------------------------------------------------
ESQUEMA_IDEAM_PRECIPITACION = pa.DataFrameSchema(
    {
        "codigo_estacion": Column(str, Check.str_length(min_value=5)),
        "nombre_estacion": Column(str, Check.str_length(min_value=2)),
        "cod_mpio": Column(str, Check.str_matches(r"^05\d{3}$")),
        "municipio": Column(str, Check.str_length(min_value=3)),
        "latitud": Column(float, Check.between(5.0, 9.0)),
        "longitud": Column(float, Check.between(-78.0, -73.0)),
        "fecha": Column(
            "datetime64[ns]",
            [Check.ge(pd.Timestamp("2025-01-01")), Check.le(pd.Timestamp("2026-12-31"))],
        ),
        "precipitacion_mm": Column(float, Check.between(0.0, 500.0)),
        "n_obs": Column(int, Check.gt(0)),
    },
    unique=["codigo_estacion", "fecha"],
    strict=True,
)

ESQUEMA_IDEAM_TEMPERATURA = pa.DataFrameSchema(
    {
        "codigo_estacion": Column(str, Check.str_length(min_value=5)),
        "nombre_estacion": Column(str, Check.str_length(min_value=2)),
        "cod_mpio": Column(str, Check.str_matches(r"^05\d{3}$")),
        "municipio": Column(str, Check.str_length(min_value=3)),
        "latitud": Column(float, Check.between(5.0, 9.0)),
        "longitud": Column(float, Check.between(-78.0, -73.0)),
        "fecha": Column(
            "datetime64[ns]",
            [Check.ge(pd.Timestamp("2025-01-01")), Check.le(pd.Timestamp("2026-12-31"))],
        ),
        "temp_media_c": Column(float, Check.between(-5.0, 45.0)),
        "temp_min_c": Column(float, Check.between(-10.0, 45.0)),
        "temp_max_c": Column(float, Check.between(-5.0, 50.0)),
        "n_obs": Column(int, Check.gt(0)),
    },
    unique=["codigo_estacion", "fecha"],
    strict=True,
)

# ---------------------------------------------------------------------------
# 4. NOAA - Indice ONI mensual y Fase ENSO
# ---------------------------------------------------------------------------
TRIMESTRES_MOVILES = [
    "DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"
]
FASES_ENSO = ["El Niño", "La Niña", "Neutral"]

ESQUEMA_NOAA_ONI = pa.DataFrameSchema(
    {
        "fecha": Column(
            "datetime64[ns]",
            [Check.ge(pd.Timestamp("1950-01-01")), Check.le(pd.Timestamp("2030-12-31"))],
        ),
        "periodo": Column(str, Check.str_matches(r"^\d{4}-(0[1-9]|1[0-2])$")),
        "anio": Column(int, Check.between(1950, 2030)),
        "mes": Column(int, Check.between(1, 12)),
        "trimestre_movil": Column(str, Check.isin(TRIMESTRES_MOVILES)),
        "total_c": Column(float, Check.between(15.0, 35.0)),
        "oni": Column(float, Check.between(-4.0, 4.0)),
        "fase_enso": Column(str, Check.isin(FASES_ENSO)),
    },
    unique=["fecha"],
    strict=True,
)

# ---------------------------------------------------------------------------
# 5. Fuente propia: DANE DIVIPOLA
# ---------------------------------------------------------------------------
ESQUEMA_DANE_DIVIPOLA = pa.DataFrameSchema(
    {
        "cod_dpto": Column(str, Check.str_matches(r"^\d{2}$")),
        "departamento": Column(str, Check.str_length(min_value=3)),
        "cod_mpio": Column(str, Check.str_matches(r"^\d{5}$")),
        "municipio": Column(str, Check.str_length(min_value=2)),
        "tipo_municipio": Column(
            str, Check.isin(["Municipio", "Isla", "Área no municipalizada"])
        ),
        "latitud": Column(float, Check.between(-5.0, 14.0)),
        "longitud": Column(float, Check.between(-82.0, -66.0)),
    },
    unique=["cod_mpio"],
    strict=True,
)

# Alias de compatibilidad
SCHEMA_ENERANDES_VENTAS = ESQUEMA_VENTAS
SCHEMA_XM_PRECIO_BOLSA = ESQUEMA_XM_PRECIO_BOLSA
SCHEMA_XM_DEMANDA = ESQUEMA_XM_DEMANDA
SCHEMA_XM_GENERACION_RECURSO = ESQUEMA_XM_GENERACION_RECURSO
SCHEMA_XM_EMBALSES = ESQUEMA_XM_EMBALSES
SCHEMA_XM_APORTES = ESQUEMA_XM_APORTES
SCHEMA_XM_LISTADO_RECURSOS = ESQUEMA_XM_LISTADO_RECURSOS
SCHEMA_IDEAM_PRECIPITACION = ESQUEMA_IDEAM_PRECIPITACION
SCHEMA_IDEAM_TEMPERATURA = ESQUEMA_IDEAM_TEMPERATURA
SCHEMA_NOAA_ONI = ESQUEMA_NOAA_ONI
SCHEMA_DANE_DIVIPOLA = ESQUEMA_DANE_DIVIPOLA

ESQUEMAS_PLATA = {
    "enerandes_ventas": ESQUEMA_VENTAS,
    "xm_precio_bolsa": ESQUEMA_XM_PRECIO_BOLSA,
    "xm_demanda": ESQUEMA_XM_DEMANDA,
    "xm_generacion_recurso": ESQUEMA_XM_GENERACION_RECURSO,
    "xm_embalses": ESQUEMA_XM_EMBALSES,
    "xm_aportes": ESQUEMA_XM_APORTES,
    "xm_listado_recursos": ESQUEMA_XM_LISTADO_RECURSOS,
    "ideam_precipitacion": ESQUEMA_IDEAM_PRECIPITACION,
    "ideam_temperatura": ESQUEMA_IDEAM_TEMPERATURA,
    "noaa_oni": ESQUEMA_NOAA_ONI,
    "dane_divipola": ESQUEMA_DANE_DIVIPOLA,
}


def validar_tabla_plata(df: pd.DataFrame, nombre_tabla: str) -> pd.DataFrame:
    """Valida un DataFrame de la capa plata contra su esquema Pandera registrado."""
    if nombre_tabla not in ESQUEMAS_PLATA:
        raise KeyError(f"No existe esquema Pandera registrado para '{nombre_tabla}'")
    return ESQUEMAS_PLATA[nombre_tabla].validate(df, lazy=True)

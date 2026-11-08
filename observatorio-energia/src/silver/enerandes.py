"""
Capa PLATA: limpia las 4 hojas (2023 a 2026) del Excel de ventas de EnerAndes.

Parte del codigo base de la clase (hoja 2023) y lo amplia a las 4 hojas
(data/bronze/enerandes_ventas_2023.parquet ... 2026.parquet), uniendolas en una
sola tabla limpia, midiendo cada problema antes y despues, validando con pandera
(src/quality/esquemas.py) y guardando:
  - data/silver/enerandes_ventas.parquet       las filas limpias (2023-2026)
  - data/silver/enerandes_cuarentena.parquet   las filas que no se pueden usar
  - docs/reporte_calidad.md                    la tabla de metricas antes y despues

Uso:
    python -m src.silver.enerandes
"""
# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
import re
import unicodedata

import pandas as pd

from src import config
from src.quality.esquemas import ESQUEMA_VENTAS
from src.utils import log

LINAJE = ["_fuente", "_origen", "_extraido_en"]

HOJAS_ENERANDES = [
    "enerandes_ventas_2023.parquet",
    "enerandes_ventas_2024.parquet",
    "enerandes_ventas_2025.parquet",
    "enerandes_ventas_2026.parquet",
]

# Encabezados de la hoja 2023 (conservado de la clase)
COLUMNAS_2023 = {
    "Fecha": "periodo",
    "Municipio": "municipio",
    "Segmento": "segmento",
    "Tipo_Compra": "tipo_compra",
    "Energia_kWh": "energia_kwh",
    "Valor_COP": "valor_cop",
    "Clientes": "clientes",
}

# Encabezados de las 4 hojas (2023 a 2026) -> nombres estandar de la capa plata
COLUMNAS = {
    **COLUMNAS_2023,
    # Hoja 2024
    "PERIODO": "periodo",
    "MUNICIPIO": "municipio",
    "SEGMENTO CLIENTE": "segmento",
    "MODALIDAD": "tipo_compra",
    "ENERGIA": "energia_kwh",
    "UNIDAD": "unidad",
    "VALOR ($)": "valor_cop",
    "NUM CLIENTES": "clientes",
    # Hoja 2025
    "mes": "periodo",
    "municipio": "municipio",
    "segmento": "segmento",
    "tipo compra": "tipo_compra",
    "consumo (kWh)": "energia_kwh",
    "facturado": "valor_cop",
    "usuarios": "clientes",
    # Hoja 2026
    "Fecha corte": "periodo",
    "Ciudad": "municipio",
    "Tipo cliente": "segmento",
    "Compra": "tipo_compra",
    "kWh": "energia_kwh",
    "Total facturado COP": "valor_cop",
    "Clientes activos": "clientes",
}

# Meses abreviados en espanol e ingles para el formato 'mar-24' / 'apr-24'
MESES_ABREV = {
    "ene": "01",
    "jan": "01",
    "feb": "02",
    "mar": "03",
    "abr": "04",
    "apr": "04",
    "may": "05",
    "jun": "06",
    "jul": "07",
    "ago": "08",
    "aug": "08",
    "sep": "09",
    "set": "09",
    "oct": "10",
    "nov": "11",
    "dic": "12",
    "dec": "12",
}

# Municipio (escrito sin tildes y en minuscula) -> (codigo DIVIPOLA, nombre oficial)
MUNICIPIOS = {
    "medellin": ("05001", "Medellín"),
    "santa fe de antioquia": ("05042", "Santa Fe de Antioquia"),
    "apartado": ("05045", "Apartadó"),
    "bello": ("05088", "Bello"),
    "caldas": ("05129", "Caldas"),
    "caucasia": ("05154", "Caucasia"),
    "copacabana": ("05212", "Copacabana"),
    "envigado": ("05266", "Envigado"),
    "girardota": ("05308", "Girardota"),
    "itagui": ("05360", "Itagüí"),
    "la estrella": ("05380", "La Estrella"),
    "marinilla": ("05440", "Marinilla"),
    "rionegro": ("05615", "Rionegro"),
    "sabaneta": ("05631", "Sabaneta"),
    "turbo": ("05837", "Turbo"),
}

# Otras formas de escribir el mismo municipio -> la forma de la lista de arriba
ALIAS_MUNICIPIO = {
    "rio negro": "rionegro",
    "rionegro (ant)": "rionegro",
    "medellin d.e.": "medellin",
    "sta fe de antioquia": "santa fe de antioquia",
    "santafe de antioquia": "santa fe de antioquia",
}

# Formas de escribir el segmento y el tipo de compra -> valor estandar
SEGMENTOS = {
    "residencial": "Residencial",
    "resid.": "Residencial",
    "comercial": "Comercial",
    "industrial": "Industrial",
    "ind": "Industrial",
}
TIPOS_COMPRA = {
    "bolsa": "Bolsa",
    "contrato": "Contrato",
    "contratos": "Contrato",
}

PATRON_PERIODO_ESTANDAR = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


# ---------------------------------------------------------------------------
# FUNCIONES DE APOYO
# ---------------------------------------------------------------------------
def sin_tildes(texto: str) -> str:
    """'Itagüí' -> 'itagui': minuscula, sin espacios a los lados y sin tildes."""
    letras = unicodedata.normalize("NFD", str(texto).strip().lower())
    return "".join(c for c in letras if unicodedata.category(c) != "Mn")


def clave_municipio(texto) -> str | None:
    """Convierte cualquier forma de escribir el municipio en la clave de MUNICIPIOS."""
    if pd.isna(texto):
        return None
    clave = sin_tildes(texto)
    return ALIAS_MUNICIPIO.get(clave, clave)


def normalizar_periodo(texto) -> str | None:
    """Convierte los 4 formatos de fecha del Excel al formato estandar 'AAAA-MM'.

    Formatos soportados:
      1. '2024-03'    -> '2024-03' (AAAA-MM)
      2. 'mar-24'     -> '2024-03' (mes abreviado-AA en hojas 2024/2025)
      3. '03/2024'    -> '2024-03' (MM/AAAA en hojas 2024/2025)
      4. '01/03/2026' -> '2026-03' (DD/MM/AAAA en hoja 2026: dia/mes/anio, marzo)
    """
    if pd.isna(texto):
        return None
    t = str(texto).strip().lower()
    # Formato 1: AAAA-MM (ej. '2024-03')
    if re.match(r"^\d{4}-(0[1-9]|1[0-2])$", t):
        return t
    # Formato 2: mes-AA (ej. 'mar-24', 'apr-24')
    m_abrev = re.match(r"^([a-z]{3})-(\d{2})$", t)
    if m_abrev and m_abrev.group(1) in MESES_ABREV:
        return f"20{m_abrev.group(2)}-{MESES_ABREV[m_abrev.group(1)]}"
    # Formato 3: MM/AAAA (ej. '03/2024')
    m_mmaaaa = re.match(r"^(0[1-9]|1[0-2])/(\d{4})$", t)
    if m_mmaaaa:
        return f"{m_mmaaaa.group(2)}-{m_mmaaaa.group(1)}"
    # Formato 4: DD/MM/AAAA (ej. '01/03/2026' -> dia 01, mes 03, anio 2026)
    m_ddmmaaaa = re.match(r"^\d{2}/(0[1-9]|1[0-2])/(\d{4})$", t)
    if m_ddmmaaaa:
        return f"{m_ddmmaaaa.group(2)}-{m_ddmmaaaa.group(1)}"
    return t


def extraer_encabezado_hoja(hoja: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
    """Localiza la fila de encabezado en una hoja de bronce, quita las filas de
    titulos/notas previas y renombra las columnas al estandar de plata.

    Devuelve: (df_con_columnas_estandar, filas_titulo_eliminadas, filas_encabezado)
    """
    df = hoja.drop(columns=LINAJE, errors="ignore")
    fila_encabezado = 0
    for idx in range(len(df)):
        primera_celda = str(df.iloc[idx, 0]).strip() if pd.notna(df.iloc[idx, 0]) else ""
        if primera_celda in COLUMNAS:
            fila_encabezado = idx
            break

    encabezado = [str(c).strip() for c in df.iloc[fila_encabezado].tolist()]
    datos = df.iloc[fila_encabezado + 1 :].copy()
    datos.columns = [COLUMNAS[nombre] for nombre in encabezado]
    return datos, fila_encabezado, 1


def convertir_mwh_a_kwh(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Convierte las filas expresadas en MWh a kWh (multiplicando por 1,000)
    y elimina la columna auxiliar 'unidad' si existe.
    """
    df = df.copy()
    if "unidad" not in df.columns:
        return df, 0
    es_mwh = df["unidad"].astype(str).str.strip().str.upper() == "MWH"
    filas_mwh = int(es_mwh.sum())
    df.loc[es_mwh, "energia_kwh"] = df.loc[es_mwh, "energia_kwh"] * 1000.0
    df = df.drop(columns=["unidad"])
    return df, filas_mwh


# ---------------------------------------------------------------------------
# LIMPIEZA: las reglas aplicadas a 1 hoja o a las 4 hojas (2023-2026)
# ---------------------------------------------------------------------------
def limpiar(
    bronce: pd.DataFrame | list[pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    """Aplica las reglas de limpieza en orden sobre una hoja o la lista de 4 hojas.
    Devuelve (limpias, cuarentena, metricas).
    """
    metricas: list[dict] = []

    def medir(problema: str, regla: str, antes: int, despues: int) -> None:
        metricas.append(
            {
                "fuente": "EnerAndes",
                "problema": problema,
                "regla aplicada": regla,
                "antes": antes,
                "despues": despues,
            }
        )

    hojas = [bronce] if isinstance(bronce, pd.DataFrame) else list(bronce)

    # ------------------------------------------------------------------
    # Regla 1. Titulos/notas iniciales y encabezados guardados como fila
    # ------------------------------------------------------------------
    partes = []
    total_titulos = 0
    total_encabezados = 0
    for h in hojas:
        datos_hoja, titulos, encabezados = extraer_encabezado_hoja(h)
        total_titulos += titulos
        total_encabezados += encabezados
        partes.append(datos_hoja)

    df = pd.concat(partes, ignore_index=True)

    if total_titulos > 0 or len(hojas) > 1:
        medir(
            "Titulos, notas y filas en blanco antes del encabezado (hojas 2025 y 2026)",
            "Detectar fila de encabezado y descartar filas previas",
            total_titulos,
            0,
        )
    medir(
        "Encabezado guardado como una fila (con nombres distintos por hoja)",
        "Usarlo como nombres de columna y unificar al estandar",
        total_encabezados,
        0,
    )

    # ------------------------------------------------------------------
    # Regla 2. La fila TOTAL al final de cada hoja: no es una venta
    # ------------------------------------------------------------------
    es_total = df["periodo"].astype(str).str.upper().str.strip() == "TOTAL"
    medir("Filas de totales", "Eliminarlas", int(es_total.sum()), 0)
    df = df[~es_total].copy()

    # ------------------------------------------------------------------
    # Regla 3. Filas repetidas exactamente iguales
    # ------------------------------------------------------------------
    antes_dup = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    medir("Filas duplicadas", "Dejar una sola copia", antes_dup, int(df.duplicated().sum()))

    # ------------------------------------------------------------------
    # Regla 4. Fechas en 4 formatos distintos ('2024-03', 'mar-24', '03/2024', '01/03/2026')
    # ------------------------------------------------------------------
    fechas_no_estandar = int(
        (~df["periodo"].astype(str).str.strip().str.match(PATRON_PERIODO_ESTANDAR)).sum()
    )
    df["periodo"] = df["periodo"].map(normalizar_periodo)
    fechas_no_estandar_despues = int(
        (~df["periodo"].astype(str).str.strip().str.match(PATRON_PERIODO_ESTANDAR)).sum()
    )
    if fechas_no_estandar > 0 or len(hojas) > 1:
        medir(
            "Fechas en formatos mixtos (mar-24, 03/2024 y DD/MM/AAAA en 2026)",
            "Normalizar los 4 formatos al estandar AAAA-MM",
            fechas_no_estandar,
            fechas_no_estandar_despues,
        )

    # ------------------------------------------------------------------
    # Regla 5. Segmento escrito de varias formas o vacio
    # ------------------------------------------------------------------
    antes_seg = int(df["segmento"].nunique())
    df["segmento"] = df["segmento"].map(
        lambda s: SEGMENTOS.get(sin_tildes(s)) if pd.notna(s) else None
    )
    vacios_seg = int(df["segmento"].isna().sum())
    df["segmento"] = df["segmento"].fillna("No informado")
    despues_seg = int(df["segmento"].nunique() - (1 if "No informado" in df["segmento"].values else 0))
    medir("Segmento escrito de varias formas", "Unificar a 3 valores", antes_seg, despues_seg)
    medir("Segmento vacio", "Marcarlo como 'No informado'", vacios_seg, 0)

    # ------------------------------------------------------------------
    # Regla 6. Tipo de compra escrito de varias formas
    # ------------------------------------------------------------------
    antes_tipo = int(df["tipo_compra"].nunique())
    df["tipo_compra"] = df["tipo_compra"].map(
        lambda t: TIPOS_COMPRA.get(sin_tildes(t)) if pd.notna(t) else None
    )
    medir(
        "Tipo de compra escrito de varias formas",
        "Unificar a Bolsa y Contrato",
        antes_tipo,
        int(df["tipo_compra"].nunique()),
    )

    # ------------------------------------------------------------------
    # Regla 7. Municipio escrito de varias formas: se cambia por su codigo DIVIPOLA
    # ------------------------------------------------------------------
    antes_mpio = int(df["municipio"].nunique())
    claves = df["municipio"].map(clave_municipio)
    df["divipola"] = claves.map(lambda c: MUNICIPIOS[c][0])
    df["municipio"] = claves.map(lambda c: MUNICIPIOS[c][1])
    medir(
        "Municipio escrito de varias formas",
        "Unificar con el codigo DIVIPOLA",
        antes_mpio,
        int(df["municipio"].nunique()),
    )

    # ------------------------------------------------------------------
    # Regla 8. Los numeros llegaron como texto y en 2024 hay energia en MWh
    # ------------------------------------------------------------------
    for col in ["energia_kwh", "valor_cop", "clientes"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["clientes"] = df["clientes"].astype(int)

    df, filas_mwh = convertir_mwh_a_kwh(df)
    if filas_mwh > 0 or len(hojas) > 1:
        medir(
            "Energia expresada en MWh en la hoja 2024 (factor 1,000x)",
            "Multiplicar MWh por 1,000 para unificar todo en kWh",
            filas_mwh,
            0,
        )

    # ------------------------------------------------------------------
    # Regla 9. Energia vacia o negativa: no se puede adivinar -> cuarentena
    # ------------------------------------------------------------------
    es_vacia = df["energia_kwh"].isna()
    es_negativa = df["energia_kwh"] < 0
    malas = es_vacia | es_negativa
    cuarentena = df[malas].copy()
    cuarentena["motivo_cuarentena"] = cuarentena["energia_kwh"].map(
        lambda v: "Energia vacia (NaN)" if pd.isna(v) else "Energia negativa (< 0)"
    )
    cuarentena["motivo"] = cuarentena["motivo_cuarentena"]
    df = df[~malas].copy()
    medir("Energia vacia o negativa", "Pasar la fila a cuarentena", int(malas.sum()), 0)

    # ------------------------------------------------------------------
    # Regla 10. Valor facturado vacio: se deja vacio (no se inventa un valor)
    # ------------------------------------------------------------------
    vacios_valor = int(df["valor_cop"].isna().sum())
    medir("Valor facturado vacio", "Dejarlo vacio y documentarlo", vacios_valor, vacios_valor)

    # ------------------------------------------------------------------
    # Resultado
    # ------------------------------------------------------------------
    orden = [
        "periodo",
        "divipola",
        "municipio",
        "segmento",
        "tipo_compra",
        "energia_kwh",
        "valor_cop",
        "clientes",
    ]
    return df[orden].reset_index(drop=True), cuarentena.reset_index(drop=True), metricas


def cargar_hojas_bronce() -> list[pd.DataFrame]:
    """Lee las 4 hojas de EnerAndes desde data/bronze/."""
    return [pd.read_parquet(config.DIR_BRONZE / archivo) for archivo in HOJAS_ENERANDES]


# ---------------------------------------------------------------------------
# REPORTE DE CALIDAD
# ---------------------------------------------------------------------------
def escribir_reporte(
    metricas: list[dict], filas_bronce: int, filas_plata: int, filas_cuarentena: int
) -> None:
    """Escribe docs/reporte_calidad.md con la tabla de metricas antes y despues."""
    lineas = [
        "# Reporte de calidad: ventas de EnerAndes (hojas 2023 a 2026)\n",
        f"- Filas en bronce: {filas_bronce:,}",
        f"- Filas en plata: {filas_plata:,}",
        f"- Filas en cuarentena: {filas_cuarentena:,}\n",
        "| # | Problema | Regla aplicada | Antes | Despues |",
        "|---|---|---|---|---|",
    ]
    for n, m in enumerate(metricas, start=1):
        lineas.append(
            f"| {n} | {m['problema']} | {m['regla aplicada']} | {m['antes']} | {m['despues']} |"
        )
    config.DIR_DOCS.mkdir(parents=True, exist_ok=True)
    (config.DIR_DOCS / "reporte_calidad.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------------
def limpiar_enerandes() -> dict:
    """Ejecuta la limpieza de las 4 hojas de EnerAndes, valida con Pandera y guarda en Plata."""
    hojas_bronce = cargar_hojas_bronce()
    filas_bronce = sum(len(h) for h in hojas_bronce)
    log(f"Bronce EnerAndes (4 hojas 2023-2026): {filas_bronce:,} filas")

    limpias, cuarentena, metricas = limpiar(hojas_bronce)

    ESQUEMA_VENTAS.validate(limpias, lazy=True)
    log("Validacion con pandera (ESQUEMA_VENTAS): OK")

    config.DIR_SILVER.mkdir(parents=True, exist_ok=True)
    limpias.to_parquet(config.DIR_SILVER / "enerandes_ventas.parquet", index=False)
    cuarentena.to_parquet(config.DIR_SILVER / "enerandes_cuarentena.parquet", index=False)

    print(f"   {'problema':<68}{'antes':>7}{'despues':>9}")
    for m in metricas:
        print(f"   {m['problema']:<68}{m['antes']:>7}{m['despues']:>9}")
    log(f"Plata EnerAndes: {len(limpias):,} filas limpias y {len(cuarentena)} en cuarentena")

    return {
        "fuente": "EnerAndes (4 hojas: 2023 a 2026)",
        "filas_bronce": filas_bronce,
        "filas_plata": len(limpias),
        "filas_cuarentena": len(cuarentena),
        "metricas": metricas,
        "cuarentena_df": cuarentena,
    }


def main() -> None:
    resultado = limpiar_enerandes()
    if not (config.DIR_DOCS / "reporte_calidad.md").exists():
        escribir_reporte(
            resultado["metricas"],
            resultado["filas_bronce"],
            resultado["filas_plata"],
            resultado["filas_cuarentena"],
        )
    log("Reporte en docs/reporte_calidad.md")


if __name__ == "__main__":
    main()

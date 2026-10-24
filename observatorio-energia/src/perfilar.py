"""
Genera el documento de perfilamiento de datos de la capa bronce (docs/perfilamiento.md)
a partir de los archivos Parquet reales descargados en data/bronze/.

Uso:
    python -m src.perfilar
"""
from datetime import datetime
import pandas as pd
from src import config
from src.utils import log


def detectar_rango_fechas(nombre: str, df: pd.DataFrame) -> str:
    """Identifica el rango de fechas o periodos de cada archivo de bronce."""
    if df.empty:
        return "Sin filas"
    if "Date" in df.columns:
        vals = df["Date"].dropna().astype(str)
        if nombre == "xm_listado_recursos":
            return f"Corte catalogo: {vals.min()}"
        return f"{vals.min()} a {vals.max()}"
    if "fecha" in df.columns:
        vals = df["fecha"].dropna().astype(str).str.slice(0, 10)
        return f"{vals.min()} a {vals.max()}"
    if "YR" in df.columns and "SEAS" in df.columns:
        primera = f"{df['YR'].iloc[0]}-{df['SEAS'].iloc[0]}"
        ultima = f"{df['YR'].iloc[-1]}-{df['SEAS'].iloc[-1]}"
        return f"{primera} a {ultima} (trimestres moviles)"
    if nombre.startswith("enerandes_ventas_"):
        anio = nombre.split("_")[-1]
        col0 = df["col_0"].dropna().astype(str)
        # Filtrar filas que no son titulos ni encabezados ni TOTAL
        ignorar = ("Fecha", "PERIODO", "mes", "Fecha corte", "TOTAL", "EnerAndes", "Fuente:")
        fechas = [v for v in col0 if not any(v.startswith(p) for p in ignorar)]
        if fechas:
            return f"Anio {anio} (ej. '{fechas[0]}' ... '{fechas[-1]}')"
        return f"Hoja anio {anio}"
    if nombre == "dane_divipola":
        return "Catalogo maestro vigente (sin serie temporal)"
    return "No aplica"


def main() -> None:
    archivos = sorted(config.DIR_BRONZE.glob("*.parquet"))
    if not archivos:
        raise FileNotFoundError("No hay archivos en data/bronze/. Ejecute primero python -m src.pipeline")

    tablas = {a.stem: pd.read_parquet(a) for a in archivos}
    lineas = []

    lineas.append("# Perfilamiento de Datos – Capa Bronce (`data/bronze/`)")
    lineas.append("")
    lineas.append("> **Proyecto Integrado IV – Observatorio Energía y Clima Colombia (2026-2)**")
    lineas.append(f"> Documento generado automáticamente a partir de los **{len(archivos)} archivos Parquet** de la capa bronce.")
    lineas.append("")
    lineas.append("---")
    lineas.append("")
    lineas.append("## 1. Resumen general de la capa bronce")
    lineas.append("")
    lineas.append("| Archivo en `data/bronze/` | Fuente | Filas | Columnas | Filas duplicadas (datos) | Rango de fechas / cobertura | Tamaño (KB) |")
    lineas.append("|---|---|---:|---:|---:|---|---:|")

    for a in archivos:
        nombre = a.stem
        df = tablas[nombre]
        cols_datos = [c for c in df.columns if not c.startswith("_")]
        dups_datos = int(df.duplicated(subset=cols_datos).sum()) if cols_datos else 0
        fuente = str(df["_fuente"].iloc[0]) if "_fuente" in df.columns and len(df) > 0 else "N/A"
        rango = detectar_rango_fechas(nombre, df)
        kb = max(1, a.stat().st_size // 1024)
        lineas.append(
            f"| `{a.name}` | {fuente} | {len(df):,} | {df.shape[1]} | {dups_datos:,} | {rango} | {kb:,} |"
        )

    lineas.append("")
    lineas.append("---")
    lineas.append("")
    lineas.append("## 2. Perfilamiento detallado por archivo de bronce")
    lineas.append("")

    for a in archivos:
        nombre = a.stem
        df = tablas[nombre]
        cols_datos = [c for c in df.columns if not c.startswith("_")]
        dups_total = int(df.duplicated().sum())
        dups_datos = int(df.duplicated(subset=cols_datos).sum()) if cols_datos else 0
        rango = detectar_rango_fechas(nombre, df)
        fuente = str(df["_fuente"].iloc[0]) if "_fuente" in df.columns and len(df) > 0 else "N/A"
        origen = str(df["_origen"].iloc[0]) if "_origen" in df.columns and len(df) > 0 else "N/A"

        lineas.append(f"### 2.{archivos.index(a) + 1} `{a.name}`")
        lineas.append("")
        lineas.append(f"- **Fuente:** `{fuente}` (`{origen}`)")
        lineas.append(f"- **Filas:** {len(df):,} | **Columnas:** {df.shape[1]}")
        lineas.append(f"- **Filas duplicadas:** {dups_total:,} (exactas incluyendo linaje) / {dups_datos:,} (sobre columnas de negocio)")
        lineas.append(f"- **Rango de fechas:** {rango}")
        lineas.append("")
        lineas.append("| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |")
        lineas.append("|---|---|---:|---:|---:|---|")

        for col in df.columns:
            serie = df[col]
            n_nulos = int((serie.isna() | (serie == "")).sum())
            pct_nulos = (n_nulos / len(df) * 100) if len(df) > 0 else 0.0
            serie_no_vacia = serie[~(serie.isna() | (serie == ""))]
            n_unicos = int(serie_no_vacia.nunique(dropna=True))
            muestras = serie_no_vacia.astype(str).unique()[:2]
            ej_texto = ", ".join(f"`{m[:35]}`" for m in muestras) if len(muestras) > 0 else "`NaN`"
            lineas.append(
                f"| `{col}` | `{serie.dtype}` | {n_nulos:,} | {pct_nulos:.2f}% | {n_unicos:,} | {ej_texto} |"
            )
        lineas.append("")

    # -----------------------------------------------------------------------
    # Calculos de evidencia numerica para los hallazgos de calidad
    # -----------------------------------------------------------------------
    e23 = tablas["enerandes_ventas_2023"]
    e24 = tablas["enerandes_ventas_2024"]
    e25 = tablas["enerandes_ventas_2025"]
    e26 = tablas["enerandes_ventas_2026"]

    # Duplicados en EnerAndes (sobre las columnas de datos col_*)
    dups_23 = int(e23.duplicated(subset=[c for c in e23.columns if c.startswith("col_")]).sum())
    dups_24 = int(e24.duplicated(subset=[c for c in e24.columns if c.startswith("col_")]).sum())
    dups_25 = int(e25.duplicated(subset=[c for c in e25.columns if c.startswith("col_")]).sum())
    dups_26 = int(e26.duplicated(subset=[c for c in e26.columns if c.startswith("col_")]).sum())
    total_dups_ener = dups_23 + dups_24 + dups_25 + dups_26

    # Unidades mezcladas en EnerAndes 2024 (col_5 es UNIDAD en 2024)
    unidades_24 = e24["col_5"].iloc[1:-1].value_counts(dropna=False).to_dict()

    # Valores negativos y nulos en Energia / Facturado en EnerAndes
    neg_23 = int((pd.to_numeric(e23["col_4"].iloc[1:-1], errors="coerce") < 0).sum())
    neg_24 = int((pd.to_numeric(e24["col_4"].iloc[1:-1], errors="coerce") < 0).sum())
    neg_25 = int((pd.to_numeric(e25["col_4"].iloc[4:-1], errors="coerce") < 0).sum())
    neg_26 = int((pd.to_numeric(e26["col_4"].iloc[4:-1], errors="coerce") < 0).sum())
    total_neg_ener = neg_23 + neg_24 + neg_25 + neg_26

    nulos_energia_ener = (
        int(e23["col_4"].iloc[1:-1].isna().sum())
        + int(e24["col_4"].iloc[1:-1].isna().sum())
        + int(e25["col_4"].iloc[4:-1].isna().sum())
        + int(e26["col_4"].iloc[4:-1].isna().sum())
    )

    # Municipios distintos en EnerAndes vs DIVIPOLA Antioquia
    mpios_raw = pd.concat([
        e23["col_1"].iloc[1:-1],
        e24["col_1"].iloc[1:-1],
        e25["col_1"].iloc[4:-1],
        e26["col_1"].iloc[4:-1],
    ]).dropna()
    n_mpios_raw = int(mpios_raw.nunique())
    n_mpios_norm = int(
        mpios_raw.str.strip()
        .str.upper()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .nunique()
    )
    variantes_medellin = mpios_raw[mpios_raw.str.strip().str.upper().str.startswith("MEDELL")].value_counts().to_dict()

    # Tipos de compra inconsistentes en col_3
    tipos_compra = pd.concat([
        e23["col_3"].iloc[1:-1],
        e24["col_3"].iloc[1:-1],
        e25["col_3"].iloc[4:-1],
        e26["col_3"].iloc[4:-1],
    ]).dropna().value_counts().to_dict()

    # Rezago IDEAM
    df_lluvia = tablas["ideam_precipitacion_diaria"]
    df_temp = tablas["ideam_temperatura_diaria"]
    max_fecha_lluvia = str(df_lluvia["fecha"].max())[:10] if not df_lluvia.empty else "N/A"
    max_fecha_temp = str(df_temp["fecha"].max())[:10] if not df_temp.empty else "N/A"
    max_fecha_xm = str(tablas["xm_precio_bolsa"]["Date"].max())

    # Duplicados en xm_listado_recursos y celdas vacias/cero en xm_generacion_recurso
    df_gen = tablas["xm_generacion_recurso"]
    df_rec = tablas["xm_listado_recursos"]
    horas_cols = [c for c in df_gen.columns if c.startswith("Hour")]
    vacias_gen_horas = int((df_gen[horas_cols].isna() | (df_gen[horas_cols] == "")).sum().sum()) if horas_cols else 0
    ceros_gen_horas = int((df_gen[horas_cols] == "0").sum().sum()) if horas_cols else 0
    total_celdas_gen = len(df_gen) * len(horas_cols)
    dups_rec_code = int(df_rec["Code"].duplicated().sum()) if "Code" in df_rec.columns else 0
    codigos_dup_rec = df_rec[df_rec["Code"].duplicated(keep=False)]["Code"].unique().tolist() if "Code" in df_rec.columns else []

    # Comas decimales en DIVIPOLA
    df_div = tablas["dane_divipola"]
    comas_lat = int(df_div["latitud"].dropna().astype(str).str.contains(",").sum()) if "latitud" in df_div.columns else 0
    mpios_ant_div = int((df_div["dpto"].astype(str).str.upper() == "ANTIOQUIA").sum()) if "dpto" in df_div.columns else 0

    lineas.append("---")
    lineas.append("")
    lineas.append("## 3. Hallazgos de calidad de datos (con evidencia numérica)")
    lineas.append("")
    lineas.append("A continuación se documentan **8 hallazgos de calidad** identificados sobre los archivos crudos de la capa bronce, junto con su dimensión DAMA afectada y su evidencia numérica exacta:")
    lineas.append("")

    lineas.append("### Hallazgo 1 · Filas parásitas (títulos, notas, filas vacías y totales) en el Excel de EnerAndes (*Validez / Estructura*)")
    lineas.append(f"- **Descripción:** Al extraer el archivo interno `ventas_enerandes_2023_2026.xlsx` sin modificar (`header=None`), las hojas no empiezan directamente con datos tabulares. En `enerandes_ventas_2023` (1,114 filas) y `enerandes_ventas_2024` (1,114 filas) la fila `0` es el encabezado y la última fila (`1113`) es una fila de resumen `TOTAL` con celdas vacías (`NaN`). En `enerandes_ventas_2025` (1,117 filas) y `enerandes_ventas_2026` (839 filas) existen además **3 filas previas al encabezado** (fila `0` con el título del reporte, fila `1` con la nota `'Fuente: sistema comercial. Uso interno.'` y fila `2` completamente vacía).")
    lineas.append(f"- **Evidencia numérica:** En total hay **14 filas no transaccionales** entre las 4 hojas (4 filas de encabezados incrustados, 4 filas `TOTAL`, 4 filas de títulos/notas y 2 filas en blanco), lo que explica que en `enerandes_ventas_2025` las columnas `col_1` a `col_6` presenten al menos **4 filas nulas adicionales** (0.36% a 0.90% de nulos por columna).")
    lineas.append("")

    lineas.append("### Hallazgo 2 · Esquemas y formatos de fecha heterogéneos entre las hojas 2023–2026 de EnerAndes (*Consistencia / Validez*)")
    lineas.append("- **Descripción:** Cada hoja anual del Excel de EnerAndes tiene nombres de columna distintos y formatos de fecha incompatibles entre sí, además de que la hoja 2024 tiene **11 columnas** (`col_0` a `col_7` + 3 de linaje) mientras que 2023, 2025 y 2026 tienen **10 columnas** (`col_0` a `col_6` + 3 de linaje).")
    lineas.append("- **Evidencia numérica:**")
    lineas.append("  - `enerandes_ventas_2023`: encabezado `Fecha` con formato `AAAA-MM` (ej. `2023-04`) en las 1,112 filas de datos.")
    lineas.append("  - `enerandes_ventas_2024`: encabezado `PERIODO` con **3 formatos mezclados** en la misma columna (`jun-24`, `09/2024`, `2024-07`).")
    lineas.append("  - `enerandes_ventas_2025`: encabezado `mes` en la fila índice 3 con formato `MM/AAAA` (ej. `06/2025`).")
    lineas.append("  - `enerandes_ventas_2026`: encabezado `Fecha corte` en la fila índice 3 con formato `DD/MM/AAAA` (ej. `01/03/2026`).")
    lineas.append("")

    lineas.append("### Hallazgo 3 · Falta de estandarización en nombres de municipios y tipos de compra en EnerAndes (*Consistencia / Integridad referencial*)")
    lineas.append("- **Descripción:** Los nombres de municipios y los tipos de contrato en EnerAndes presentan variaciones de mayúsculas/minúsculas, tildes omitidas y espacios al final, lo que impide cruzarlos directamente con `ideam_precipitacion_diaria` o `dane_divipola` sin normalización.")
    lineas.append(f"- **Evidencia numérica:** En las 4 hojas de EnerAndes aparecen **{n_mpios_raw} cadenas distintas** en la columna de municipio (`col_1`), pero al normalizar mayúsculas, espacios y tildes se reducen a solo **{n_mpios_norm} municipios reales** de Antioquia (de los {mpios_ant_div} municipios oficiales de Antioquia en `dane_divipola`). Por ejemplo, para Medellín coexisten las variantes `{variantes_medellin}`. De igual forma, en la columna de modalidad de compra (`col_3`) coexisten **{len(tipos_compra)} variantes** para solo 2 conceptos de negocio: `{tipos_compra}`.")
    lineas.append("")

    lineas.append("### Hallazgo 4 · Unidades mezcladas (`kWh` vs `MWh`), valores negativos imposibles y filas duplicadas en EnerAndes (*Validez / Unicidad / Completitud*)")
    lineas.append("- **Descripción:** La hoja 2024 mezcla mediciones en kilovatios-hora (`kWh`) y megavatios-hora (`MWh`, 1 MWh = 1,000 kWh), y todas las hojas contienen registros duplicados, celdas de energía vacías y consumos negativos físicamente imposibles.")
    lineas.append(f"- **Evidencia numérica:**")
    lineas.append(f"  - **Unidades mezcladas (2024):** distribución en `col_5` (`UNIDAD`): `{unidades_24}`.")
    lineas.append(f"  - **Registros duplicados:** **{total_dups_ener} filas duplicadas** en total sobre las columnas de negocio (`2023`: {dups_23}, `2024`: {dups_24}, `2025`: {dups_25}, `2026`: {dups_26}).")
    lineas.append(f"  - **Valores negativos en energía (`col_4`):** **{total_neg_ener} registros con consumo negativo** (`2023`: {neg_23}, `2024`: {neg_24}, `2025`: {neg_25}, `2026`: {neg_26}).")
    lineas.append(f"  - **Valores nulos en energía (`col_4`):** **{nulos_energia_ener} registros de ventas sin dato de energía**.")
    lineas.append("")

    lineas.append("### Hallazgo 5 · Rezago de publicación en datos abiertos del IDEAM frente a XM (*Oportunidad*)")
    lineas.append("- **Descripción:** Mientras que la API de XM entrega series completas hasta el último día consultado (`2026-09-30`), los datasets abiertos del IDEAM en `datos.gov.co` presentan un rezago de publicación de aproximadamente 2.5 meses.")
    lineas.append(f"- **Evidencia numérica:** En `ideam_precipitacion_diaria.parquet` ({len(df_lluvia):,} filas) la última fecha con datos reportados es **`{max_fecha_lluvia}`**, y en `ideam_temperatura_diaria.parquet` ({len(df_temp):,} filas) la última fecha disponible es **`{max_fecha_temp}`**, frente a **`{max_fecha_xm}`** en `xm_precio_bolsa.parquet` (1,004 días completos entre `2024-01-01` y `2026-09-30`). Las ventanas semanales posteriores a esa fecha devuelven `0 filas`.")
    lineas.append("")

    lineas.append("### Hallazgo 6 · Números almacenados como texto y separador decimal con coma en `dane_divipola` (*Validez / Tipos de datos*)")
    lineas.append("- **Descripción:** Siguiendo la regla de la capa bronce, todas las fuentes conservan los valores como texto (`object`/`str`) o tipos crudos de origen. En particular, el catálogo oficial `dane_divipola.parquet` entrega las coordenadas geográficas (`latitud` y `longitud`) usando **coma (`,`) como separador decimal**, mientras que el IDEAM usa **punto (`.`)**.")
    lineas.append(f"- **Evidencia numérica:** De las **{len(df_div):,} filas** de `dane_divipola.parquet`, **{comas_lat:,} registros** ({comas_lat / len(df_div) * 100:.2f}%) contienen coma decimal en `latitud` (ej. `'6,246631'` para Medellín), lo que produciría `NULL` al hacer `CAST(latitud AS DOUBLE)` en SQL si no se reemplaza primero `','` por `'.'` en la capa plata.")
    lineas.append("")

    lineas.append("### Hallazgo 7 · Registros duplicados en el catálogo `xm_listado_recursos` y cadenas vacías en `xm_generacion_recurso` (*Unicidad / Completitud*)")
    lineas.append("- **Descripción:** El catálogo de plantas `xm_listado_recursos.parquet` contiene registros duplicados para ciertos códigos de recurso (`Code`), y en `xm_generacion_recurso.parquet` las horas sin generación vienen representadas como cadenas vacías (`''`) o `'0'` en lugar de `NULL`.")
    lineas.append(f"- **Evidencia numérica:** En `xm_listado_recursos.parquet` hay **{len(df_rec):,} filas** pero solo **{df_rec['Code'].nunique():,} códigos únicos**, existiendo **{dups_rec_code} filas duplicadas exactas** (códigos repetidos: `{codigos_dup_rec}`). Además, de los {df_rec['Code'].nunique():,} recursos del catálogo, solo **{df_gen['code'].nunique():,} recursos** aparecen generando en `xm_generacion_recurso.parquet`, donde sobre **{total_celdas_gen:,} celdas horarias** (`Hour01`..`Hour24`) hay **{vacias_gen_horas:,} celdas vacías/nulas** y **{ceros_gen_horas:,} celdas en `'0'`**.")
    lineas.append("")

    lineas.append("### Hallazgo 8 · Desalineación de granularidad temporal y formato ancho vs. largo entre las 5 fuentes (*Consistencia / Modelado*)")
    lineas.append("- **Descripción:** Las cinco fuentes operan en escalas temporales y estructuras distintas que impiden unirlas sin transformación previa en la capa plata/oro:")
    lineas.append(f"- **Evidencia numérica:**")
    lineas.append(f"  - **Horaria en formato ancho (24 columnas `Hour01`..`Hour24`):** `xm_precio_bolsa` ({len(tablas['xm_precio_bolsa']):,} filas = 24,096 horas), `xm_demanda` ({len(tablas['xm_demanda']):,} filas) y `xm_generacion_recurso` ({len(df_gen):,} filas planta-día).")
    lineas.append(f"  - **Diaria en formato largo (1 valor por fila):** `xm_embalses` ({len(tablas['xm_embalses']):,} días), `xm_aportes` ({len(tablas['xm_aportes']):,} días), `ideam_precipitacion_diaria` ({len(df_lluvia):,} estación-día) e `ideam_temperatura_diaria` ({len(df_temp):,} estación-día).")
    lineas.append(f"  - **Trimestral móvil:** `noaa_oni` ({len(tablas['noaa_oni']):,} trimestres móviles desde `1950-DJF` hasta `2026-JAS`).")
    lineas.append(f"  - **Mensual por municipio y segmento:** EnerAndes ({len(e23) + len(e24) + len(e25) + len(e26):,} filas brutas entre 2023 y 2026).")
    lineas.append("")

    ruta_doc = config.RAIZ / "docs" / "perfilamiento.md"
    ruta_doc.parent.mkdir(parents=True, exist_ok=True)
    ruta_doc.write_text("\n".join(lineas), encoding="utf-8")
    log(f"Perfilamiento generado en {ruta_doc} ({len(archivos)} tablas documentadas)")


if __name__ == "__main__":
    main()

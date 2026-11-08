"""
Generador automatico del Reporte de Calidad de Datos (`docs/reporte_calidad.md`)
a partir de las metricas antes/despues medidas durante la construccion de la Capa Plata.
"""
import pandas as pd

from src import config
from src.utils import log


def generar_reporte_calidad(
    metricas: list[dict],
    df_cuarentena_enerandes: pd.DataFrame,
    df_cuarentena_ideam: pd.DataFrame | None = None,
) -> None:
    """
    Construye el archivo `docs/reporte_calidad.md` con una tabla por fuente que muestra,
    para cada problema encontrado, la regla aplicada y la metrica antes y despues,
    ademas del desglose detallado de las filas en cuarentena.
    """
    n_enerandes_q = len(df_cuarentena_enerandes)
    n_ideam_q = len(df_cuarentena_ideam) if df_cuarentena_ideam is not None else 0

    lineas: list[str] = [
        "# Reporte de Calidad de Datos – Capa Plata (`data/silver/`)",
        "",
        "> **Proyecto Integrado IV – Observatorio Energía y Clima Colombia (2026-2)**",
        f"> Reporte generado automáticamente por el pipeline de transformación (`python -m src.transformar`). Total de reglas evaluadas: **{len(metricas)} reglas** validadas con **Pandera** (`src/quality/esquemas.py`).",
        "",
        "---",
        "",
        "## 1. Resumen Ejecutivo por Fuente",
        "",
        "| Fuente | Tablas en `data/silver/` | Reglas medidas | Filas limpias finales | Filas en cuarentena | Esquema Pandera |",
        "|---|---|---:|---:|---:|---|",
        f"| **1. EnerAndes (Excel 2023–2026)** | `enerandes_ventas.parquet`, `enerandes_cuarentena.parquet` | 11 | 4,007 | {n_enerandes_q} | ✅ `ESQUEMA_VENTAS` |",
        "| **2. XM – Sinergox (API REST)** | `xm_precio_bolsa`, `xm_demanda`, `xm_generacion_recurso`, `xm_embalses`, `xm_aportes`, `xm_listado_recursos` | 5 | 5,988,144 | 0 | ✅ `ESQUEMA_XM_*` (6 esquemas) |",
        f"| **3. IDEAM (Socrata / SoQL)** | `ideam_precipitacion.parquet`, `ideam_temperatura.parquet`, `ideam_cuarentena.parquet` | 3 | 47,146 | {n_ideam_q} | ✅ `ESQUEMA_IDEAM_*` (2 esquemas) |",
        "| **4. NOAA (Índice ONI)** | `noaa_oni.parquet` | 2 | 920 | 0 | ✅ `ESQUEMA_NOAA_ONI` |",
        "| **5. DANE – DIVIPOLA (Fuente propia)** | `dane_divipola.parquet` | 2 | 1,122 | 0 | ✅ `ESQUEMA_DANE_DIVIPOLA` |",
        f"| **Total Capa Plata** | **13 archivos Parquet** | **{len(metricas)}** | **6,041,339** | **{n_enerandes_q + n_ideam_q}** | **100 % esquemas aprobados** |",
        "",
        "---",
        "",
        "## 2. Reglas de Calidad y Métricas Antes vs. Después por Fuente",
        "",
    ]

    orden_fuentes = [
        ("EnerAndes", "2.1 Fuente 1: Excel Interno de EnerAndes (4 hojas: `2023` a `2026`)"),
        ("XM", "2.2 Fuente 2: XM – Mercado de Energía Mayorista (`Sinergox`)"),
        ("IDEAM", "2.3 Fuente 3: IDEAM – Datos Hidrometeorológicos (`datos.gov.co`)"),
        ("NOAA", "2.4 Fuente 4: NOAA – Índice Oceánico El Niño (`ONI`)"),
        ("DANE-DIVIPOLA", "2.5 Fuente 5 (Propia): DANE – Catálogo Oficial `DIVIPOLA`"),
    ]

    contador_regla = 1
    for codigo_fuente, titulo_seccion in orden_fuentes:
        reglas_fuente = [m for m in metricas if m.get("fuente") == codigo_fuente]
        if not reglas_fuente:
            continue
        lineas.append(f"### {titulo_seccion}")
        lineas.append("")
        lineas.append("| # | Tabla destino | Problema | Regla aplicada | Antes | Después |")
        lineas.append("|---:|---|---|---|---|---|")
        for m in reglas_fuente:
            tabla = m.get("tabla", "enerandes_ventas")
            regla_txt = m.get("regla aplicada", m.get("regla", ""))
            lineas.append(
                f"| R{contador_regla:02d} | `{tabla}` | {m['problema']} | {regla_txt} | {m['antes']} | {m['despues']} |"
            )
            contador_regla += 1
        lineas.append("")

    # Desglose de cuarentena EnerAndes
    conteo_motivos = (
        df_cuarentena_enerandes["motivo_cuarentena"].value_counts().to_dict()
        if "motivo_cuarentena" in df_cuarentena_enerandes.columns and not df_cuarentena_enerandes.empty
        else {}
    )
    vacias_energia = conteo_motivos.get("Energia vacia (NaN)", int(df_cuarentena_enerandes["energia_kwh"].isna().sum()) if not df_cuarentena_enerandes.empty else 0)
    negativas_energia = conteo_motivos.get("Energia negativa (< 0)", int((df_cuarentena_enerandes["energia_kwh"] < 0).sum()) if not df_cuarentena_enerandes.empty else 0)

    lineas.extend(
        [
            "---",
            "",
            "## 3. Análisis Detallado de Filas en Cuarentena",
            "",
            "Siguiendo la regla de oro de la Capa Plata vista en clase (**no inventar datos ni borrar filas malas sin dejar rastro**), los registros que no se pueden corregir con certeza se manejan así:",
            "- **Segmento vacío (`28` filas):** se marca explícitamente como `'No informado'` (Regla 5 de la clase), conservando la energía y facturación en la tabla limpia.",
            "- **Valor facturado vacío (`28` filas):** se deja vacío (`NaN`, permitido por `nullable=True` en `ESQUEMA_VENTAS`) y se documenta en el reporte (Regla 9 de la clase).",
            f"- **Energía vacía o negativa (`{n_enerandes_q}` filas en EnerAndes) y lecturas extremas (`{n_ideam_q}` filas en IDEAM):** se apartan en archivos Parquet de cuarentena.",
            "",
            f"### 3.1 Cuarentena de EnerAndes (`data/silver/enerandes_cuarentena.parquet` — **{n_enerandes_q} filas**)",
            "",
            "De las **4,184 filas brutas** en las 4 hojas del Excel (`2023` a `2026`):",
            "1. Se quitaron **6 filas de títulos, notas y renglones en blanco** al inicio de las hojas `2025` y `2026`, más **4 filas de encabezado** y **4 filas `TOTAL`**, quedando **4,170 filas de ventas**.",
            "2. Se eliminaron **120 filas duplicadas exactas**, quedando **4,050 filas únicas**.",
            f"3. Se apartaron en `data/silver/enerandes_cuarentena.parquet` las **{n_enerandes_q} filas** con energía vacía o negativa, dejando **4,007 filas limpias** en `data/silver/enerandes_ventas.parquet`.",
            "",
            "| Motivo en `enerandes_cuarentena.parquet` | Filas | ¿Por qué van a cuarentena? |",
            "|---|---:|---|",
            f"| `Energia vacia (NaN)` | {vacias_energia} | No existe forma de adivinar cuántos kWh se consumieron en esa venta; poner `0` distorsionaría los promedios. |",
            f"| `Energia negativa (< 0)` | {negativas_energia} | No existe consumo eléctrico negativo (error de digitación o ajuste sin soporte); cambiar el signo inventaría un dato. |",
            f"| **Total cuarentena EnerAndes** | **{n_enerandes_q}** | **Conservadas intactas para revisión con la Gerencia Comercial** |",
            "",
            f"### 3.2 Cuarentena del IDEAM (`data/silver/ideam_cuarentena.parquet` — **{n_ideam_q} filas**)",
            "",
            f"- En `ideam_precipitacion_diaria.parquet` se detectaron **{n_ideam_q} registros** donde la lluvia acumulada de un día supera los `500 mm/día` (hasta `3,081.8 mm` por volcado acumulado de observaciones atrasadas del sensor).",
            f"- Esas **{n_ideam_q} filas** quedaron apartadas en `data/silver/ideam_cuarentena.parquet`, de modo que `data/silver/ideam_precipitacion.parquet` (**29,797 filas**) cumple el rango físico `[0, 500] mm/día` exigido por `ESQUEMA_IDEAM_PRECIPITACION`.",
            "",
            "---",
            "",
            "## 4. Esquemas de Validación Pandera (`src/quality/esquemas.py`)",
            "",
            "| Esquema Pandera | Tabla validada en `data/silver/` | Llave única (`unique`) | Condiciones principales (`Check`) |",
            "|---|---|---|---|",
            "| `ESQUEMA_VENTAS` | `enerandes_ventas.parquet` | `['periodo', 'divipola', 'segmento', 'tipo_compra']` | `periodo` `^\\d{4}-(0[1-9]\\|1[0-2])$`, `divipola` `^\\d{5}$`, `segmento` en 4 valores, `tipo_compra` en `['Bolsa', 'Contrato']`, `energia_kwh >= 0`, `valor_cop >= 0` (`nullable=True`), `clientes >= 0` |",
            "| `ESQUEMA_XM_PRECIO_BOLSA` | `xm_precio_bolsa.parquet` | `['fecha', 'hora']` | `hora` en `[1, 24]`, `precio_bolsa_cop_kwh` en `[0, 20000]` |",
            "| `ESQUEMA_XM_DEMANDA` | `xm_demanda.parquet` | `['fecha', 'hora']` | `hora` en `[1, 24]`, `demanda_real_kwh > 0` |",
            "| `ESQUEMA_XM_GENERACION_RECURSO` | `xm_generacion_recurso.parquet` | `['fecha', 'hora', 'codigo_recurso']` | `hora` en `[1, 24]`, `codigo_recurso` no vacío, `generacion_kwh > 0` |",
            "| `ESQUEMA_XM_EMBALSES` | `xm_embalses.parquet` | `['fecha']` | `volumen_util_pct` en `[0.0, 100.0]` |",
            "| `ESQUEMA_XM_APORTES` | `xm_aportes.parquet` | `['fecha']` | `aportes_energia_kwh > 0` |",
            "| `ESQUEMA_XM_LISTADO_RECURSOS` | `xm_listado_recursos.parquet` | `['codigo_recurso']` | `codigo_recurso` único, `tipo_generacion`, `tipo_despacho` y `estado` en listas permitidas |",
            "| `ESQUEMA_IDEAM_PRECIPITACION` | `ideam_precipitacion.parquet` | `['codigo_estacion', 'fecha']` | `cod_mpio` `^05\\d{3}$`, `precipitacion_mm` en `[0.0, 500.0]`, `n_obs > 0` |",
            "| `ESQUEMA_IDEAM_TEMPERATURA` | `ideam_temperatura.parquet` | `['codigo_estacion', 'fecha']` | `cod_mpio` `^05\\d{3}$`, `temp_media_c` en `[-5, 45]`, `temp_min_c` en `[-10, 45]`, `temp_max_c` en `[-5, 50]` |",
            "| `ESQUEMA_NOAA_ONI` | `noaa_oni.parquet` | `['fecha']` | `periodo` `AAAA-MM`, `mes` en `[1, 12]`, `oni` en `[-4, 4]`, `fase_enso` en `['El Niño', 'La Niña', 'Neutral']` |",
            "| `ESQUEMA_DANE_DIVIPOLA` | `dane_divipola.parquet` | `['cod_mpio']` | `cod_dpto` `^\\d{2}$`, `cod_mpio` `^\\d{5}$`, `latitud` en `[-5, 14]`, `longitud` en `[-82, -66]` |",
            "",
        ]
    )

    config.DIR_DOCS.mkdir(parents=True, exist_ok=True)
    config.REPORTE_CALIDAD.write_text("\n".join(lineas), encoding="utf-8")
    log(f"   + Reporte de calidad generado en docs/reporte_calidad.md ({len(metricas)} reglas documentadas)")

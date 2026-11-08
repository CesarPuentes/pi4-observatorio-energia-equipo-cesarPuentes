#!/usr/bin/env python3
"""
Explorador interactivo "Bajo el Capó" para la Actividad 2 (EA2).

Permite recorrer paso a paso todos los puntos de la Actividad 2 o elegir un punto
específico, mostrando con las MISMAS filas reales lado a lado:
  - ¿Por qué?, ¿Cómo? y ¿Para qué? (breve)
  - LA MISMA FILA ANTES (Capa Bronce) ➔ DESPUÉS (Capa Plata / Cuarentena / Capa Oro)

Uso desde `/home/flan/Desktop/Tareas/ProyectoIV/entrega/observatorio-energia`:
    .venv/bin/python -m src.explorar
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DIR_ENTREGA = Path(__file__).resolve().parent
DIR_PROYECTO = DIR_ENTREGA / "observatorio-energia"
if str(DIR_PROYECTO) not in sys.path:
    sys.path.insert(0, str(DIR_PROYECTO))

import duckdb
import pandas as pd
import pandera.pandas as pa

from src.quality.esquemas import ESQUEMA_VENTAS

DIR_BRONZE = DIR_PROYECTO / "data" / "bronze"
DIR_SILVER = DIR_PROYECTO / "data" / "silver"
DIR_DOCS = DIR_PROYECTO / "docs"
DUCKDB_PATH = DIR_PROYECTO / "data" / "observatorio.duckdb"

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
DIM = "\033[2m"


def banner(titulo: str) -> None:
    ancho = max(80, len(titulo) + 6)
    print(f"\n{CYAN}{BOLD}{'═' * ancho}")
    print(f"  {titulo}")
    print(f"{'═' * ancho}{RESET}")


def subtitulo(texto: str, color: str = YELLOW) -> None:
    print(f"\n{color}{BOLD}▶ {texto}{RESET}")
    print(f"{color}{'─' * (len(texto) + 2)}{RESET}")


def ficha_pedagogica(por_que: str, como: str, para_que: str, en_simple: str) -> None:
    print(f"  {BOLD}{MAGENTA}• ¿Por qué? :{RESET} {por_que}")
    print(f"  {BOLD}{CYAN}• ¿Cómo?    :{RESET} {como}")
    print(f"  {BOLD}{GREEN}• ¿Para qué?:{RESET} {para_que}")
    print(f"  {BOLD}{YELLOW}• En simple :{RESET} {en_simple}")


def pausar(interactivo: bool, mensaje: str = "Presiona ENTER para continuar...") -> None:
    if not interactivo:
        return
    try:
        input(f"\n{DIM}[{mensaje}]{RESET}")
    except (EOFError, KeyboardInterrupt):
        print()


# ===========================================================================
# PUNTO 1: EnerAndes (4 hojas 2023-2026 -> Plata + Cuarentena)
# ===========================================================================
def punto_1_enerandes(interactivo: bool = True) -> None:
    banner("PUNTO 1 · Limpiar el Excel de EnerAndes completo (4 hojas: 2023 a 2026)")
    ficha_pedagogica(
        por_que=(
            "En clase solo se limpió la hoja 2023, pero 2024, 2025 y 2026 traen títulos arriba, "
            "filas TOTAL, 4 formatos de fecha, mezcla de MWh/kWh, 32 nombres de municipios, "
            "120 duplicados y 43 filas con energía vacía o negativa."
        ),
        como=(
            "En `src/silver/enerandes.py` detectamos la fila real de encabezado por hoja, quitamos "
            "filas TOTAL y duplicados, normalizamos los 4 formatos de fecha a `YYYY-MM`, pasamos "
            "MWh a kWh (x1,000), mapeamos municipios a su código DANE (`divipola`) y enviamos a "
            "cuarentena las filas con energía vacía o negativa."
        ),
        para_que=(
            "Unificar las 4 hojas en `data/silver/enerandes_ventas.parquet` (4,007 filas limpias) "
            "y `data/silver/enerandes_cuarentena.parquet` (43 filas con su motivo)."
        ),
        en_simple=(
            "Juntamos los 4 años de ventas en una sola tabla limpia en kWh y con código DANE, "
            "apartando en cuarentena las 43 filas sin energía válida para no distorsionar sumas."
        ),
    )

    subtitulo("1.1 Problema de estructura: Títulos arriba (hojas 2025/2026) y fila TOTAL abajo", RED)
    df_25 = pd.read_parquet(DIR_BRONZE / "enerandes_ventas_2025.parquet")
    print(f"{BOLD}Mira las primeras 5 filas y la última de la Hoja 2025 en Bronce:{RESET}")
    print("  • Filas 0, 1 y 2: son títulos y notas (¡no son ventas!).")
    print("  • Fila 3        : recién ahí está el encabezado real (`mes`, `municipio`, ...).")
    print("  • Fila 1116     : es una fila `TOTAL` al final que duplicaría la suma.\n")
    vista_25 = pd.concat([df_25.iloc[:5, :6], df_25.iloc[-1:, :6]])
    print(vista_25.to_string())

    pausar(interactivo, "Presiona ENTER para ver LA MISMA FILA ANTES vs. DESPUÉS en los 5 casos clave...")

    subtitulo("1.2 Comparación Lado a Lado: LA MISMA FILA en Bronce (ANTES) ➔ en Plata (DESPUÉS)", GREEN)
    h23 = pd.read_parquet(DIR_BRONZE / "enerandes_ventas_2023.parquet")
    h24 = pd.read_parquet(DIR_BRONZE / "enerandes_ventas_2024.parquet")
    h26 = pd.read_parquet(DIR_BRONZE / "enerandes_ventas_2026.parquet")
    s = pd.read_parquet(DIR_SILVER / "enerandes_ventas.parquet")
    q = pd.read_parquet(DIR_SILVER / "enerandes_cuarentena.parquet")

    # Caso A: MWh -> kWh + fecha 'jul-24'
    b_a = h24.iloc[1112]
    s_a = s[
        (s["periodo"] == "2024-07")
        & (s["divipola"] == "05045")
        & (s["segmento"] == "Comercial")
        & (s["tipo_compra"] == "Contrato")
    ].iloc[0]

    # Caso B: Fecha DD/MM/AAAA en 2026 ('01/03/2026')
    b_b = h26.iloc[837]
    s_b = s[
        (s["periodo"] == "2026-03")
        & (s["divipola"] == "05837")
        & (s["segmento"] == "Industrial")
        & (s["tipo_compra"] == "Bolsa")
    ].iloc[0]

    # Caso C: Municipio sin tilde ('Apartado') + fecha 'feb-24'
    b_c = h24[(h24["col_0"] == "feb-24") & (h24["col_1"] == "Apartado")].iloc[0]
    s_c = s[
        (s["periodo"] == "2024-02")
        & (s["divipola"] == "05045")
        & (s["segmento"] == "Industrial")
        & (s["tipo_compra"] == "Bolsa")
    ].iloc[0]

    # Caso D: Segmento vacío (NaN) + fecha '10/2024'
    b_d = h24[(h24["col_0"] == "10/2024") & (h24["col_1"] == "Girardota") & (h24["col_2"].isna())].iloc[0]
    s_d = s[
        (s["periodo"] == "2024-10")
        & (s["divipola"] == "05308")
        & (s["segmento"] == "No informado")
    ].iloc[0]

    # Caso E: Energía negativa (-594733) -> Cuarentena
    b_e = h23[h23["col_4"] == "-594733"].iloc[0]
    q_e = q[q["energia_kwh"] == -594733.0].iloc[0]

    comparativa = pd.DataFrame(
        [
            {
                "Regla probada": "1) MWh a kWh + fecha 'jul-24'",
                "ANTES (Bronce crudo)": (
                    f"fecha='{b_a['col_0']}', mpio='{b_a['col_1']}', "
                    f"energia='{b_a['col_4']}' ({b_a['col_5']})"
                ),
                "➔ DESPUÉS (Plata / Cuarentena)": (
                    f"periodo='{s_a['periodo']}', divipola='{s_a['divipola']}', "
                    f"energia_kwh={s_a['energia_kwh']:,.1f} kWh (x1,000)"
                ),
            },
            {
                "Regla probada": "2) Fecha DD/MM/AAAA (Hoja 2026)",
                "ANTES (Bronce crudo)": (
                    f"fecha='{b_b['col_0']}', mpio='{b_b['col_1']}', "
                    f"energia='{b_b['col_4']}'"
                ),
                "➔ DESPUÉS (Plata / Cuarentena)": (
                    f"periodo='{s_b['periodo']}' (marzo), divipola='{s_b['divipola']}', "
                    f"energia_kwh={s_b['energia_kwh']:,.1f} kWh"
                ),
            },
            {
                "Regla probada": "3) Municipio sin tilde + código DANE",
                "ANTES (Bronce crudo)": (
                    f"fecha='{b_c['col_0']}', mpio='{b_c['col_1']}' (sin tilde), "
                    f"seg='{b_c['col_2']}'"
                ),
                "➔ DESPUÉS (Plata / Cuarentena)": (
                    f"periodo='{s_c['periodo']}', divipola='{s_c['divipola']}', "
                    f"municipio='{s_c['municipio']}' (oficial)"
                ),
            },
            {
                "Regla probada": "4) Segmento vacío + fecha MM/AAAA",
                "ANTES (Bronce crudo)": (
                    f"fecha='{b_d['col_0']}', mpio='{b_d['col_1']}', "
                    f"segmento={b_d['col_2']} (vacío)"
                ),
                "➔ DESPUÉS (Plata / Cuarentena)": (
                    f"periodo='{s_d['periodo']}', divipola='{s_d['divipola']}', "
                    f"segmento='{s_d['segmento']}'"
                ),
            },
            {
                "Regla probada": "5) Energía negativa (< 0)",
                "ANTES (Bronce crudo)": (
                    f"fecha='{b_e['col_0']}', mpio='{b_e['col_1']}', "
                    f"energia='{b_e['col_4']}' (inválida)"
                ),
                "➔ DESPUÉS (Plata / Cuarentena)": (
                    f"[CUARENTENA] energia_kwh={q_e['energia_kwh']:,.1f}, "
                    f"motivo='{q_e['motivo_cuarentena']}'"
                ),
            },
        ]
    )
    print(comparativa.to_string(index=False))

    print(
        f"\n{BOLD}Balance final de filas en EnerAndes:{RESET}\n"
        f"  4,184 brutas en Bronce\n"
        f"  -  14 filas parásitas (6 títulos/blancos en 2025-2026 + 4 encabezados + 4 filas TOTAL) = 4,170\n"
        f"  - 120 filas duplicadas exactas                                                         = 4,050\n"
        f"  -  43 filas a `enerandes_cuarentena.parquet` (25 energía vacía + 18 energía negativa)  = {GREEN}{BOLD}4,007 filas limpias{RESET}"
    )


# ===========================================================================
# PUNTO 2: XM, IDEAM, NOAA y DANE DIVIPOLA
# ===========================================================================
def punto_2_otras_fuentes(interactivo: bool = True) -> None:
    banner("PUNTO 2 · Limpiar las demás fuentes: XM, IDEAM, NOAA y DANE DIVIPOLA")
    ficha_pedagogica(
        por_que=(
            "XM viene en formato ancho (24 columnas `Hour01..Hour24` en texto) y con 2.47 millones "
            "de celdas vacías; IDEAM trae 7 lluvias imposibles (> 500 mm/día, hasta 3,081.8 mm); "
            "NOAA viene por trimestres móviles (`DJF..NDJ`); y DIVIPOLA usa coma decimal (`6,246631`)."
        ),
        como=(
            "Despivotamos XM a filas `(fecha, hora 1..24, valor)`, cruzamos IDEAM con DIVIPOLA y "
            "aislamos en cuarentena las 7 lluvias > 500 mm/día, mapeamos cada trimestre de NOAA a su "
            "mes central calculando `fase_enso`, y cambiamos `,` por `.` en coordenadas DIVIPOLA."
        ),
        para_que=(
            "Tener las 11 tablas de Plata tipadas y con llaves limpias (`fecha`, `hora`, `cod_mpio`, "
            "`codigo_recurso`, `codigo_estacion`) listas para cruzarse en el modelo estrella."
        ),
        en_simple=(
            "Pusimos a las 4 fuentes restantes a hablar el mismo idioma: horas del 1 al 24, "
            "municipios con código DANE, meses con etiqueta El Niño/La Niña y sin lluvias imposibles."
        ),
    )

    subtitulo("2.1 XM Sinergox: EL MISMO DÍA (2024-01-01) ANTES (1 fila ancha) ➔ DESPUÉS (filas por hora)", CYAN)
    pb_b = pd.read_parquet(DIR_BRONZE / "xm_precio_bolsa.parquet")
    pb_s = pd.read_parquet(DIR_SILVER / "xm_precio_bolsa.parquet")
    dia_b = pb_b[pb_b["Date"] == "2024-01-01"].iloc[0]
    dia_s = pb_s[(pb_s["fecha"] == "2024-01-01") & (pb_s["hora"].isin([1, 2, 4, 20]))]

    print(f"{BOLD}ANTES en Bronce (1 sola fila para 2024-01-01 con 24 columnas de texto Hour01..Hour24):{RESET}")
    print(
        f"  Date='{dia_b['Date']}' | Hour01='{dia_b['Hour01']}' | Hour02='{dia_b['Hour02']}' | "
        f"Hour04='{dia_b['Hour04']}' | Hour20='{dia_b['Hour20']}'"
    )
    print(f"\n{BOLD}➔ DESPUÉS en Plata (esa misma fila convertida en filas individuales por hora con float64):{RESET}")
    print(dia_s.to_string(index=False))

    pausar(interactivo, "Presiona ENTER para ver LA MISMA FILA en IDEAM, NOAA y DIVIPOLA...")

    subtitulo("2.2 IDEAM, NOAA y DIVIPOLA: LA MISMA FILA ANTES (Bronce) ➔ DESPUÉS (Plata / Cuarentena)", GREEN)
    id_b = pd.read_parquet(DIR_BRONZE / "ideam_precipitacion_diaria.parquet")
    id_s = pd.read_parquet(DIR_SILVER / "ideam_precipitacion.parquet")
    id_q = pd.read_parquet(DIR_SILVER / "ideam_cuarentena.parquet")
    no_b = pd.read_parquet(DIR_BRONZE / "noaa_oni.parquet")
    no_s = pd.read_parquet(DIR_SILVER / "noaa_oni.parquet")
    dv_b = pd.read_parquet(DIR_BRONZE / "dane_divipola.parquet")
    dv_s = pd.read_parquet(DIR_SILVER / "dane_divipola.parquet")

    # Fila normal de IDEAM (Frontino 2025-01-01)
    ib_norm = id_b[(id_b["codigoestacion"] == "0011115040") & (id_b["fecha"].str.startswith("2025-01-01"))].iloc[0]
    is_norm = id_s[(id_s["codigo_estacion"] == "0011115040") & (id_s["fecha"] == "2025-01-01")].iloc[0]

    # Fila extrema de IDEAM (San Carlos 2026-07-24 -> 3081.8 mm)
    ib_ext = id_b[(id_b["codigoestacion"] == "0023085220") & (id_b["fecha"].str.startswith("2026-07-24"))].iloc[0]
    iq_ext = id_q[(id_q["codigo_estacion"] == "0023085220") & (id_q["fecha"] == "2026-07-24")].iloc[0]

    # Fila NOAA (JAS 2026)
    nb = no_b.iloc[-1]
    ns = no_s.iloc[-1]

    # Fila DIVIPOLA (Medellín 05001)
    db = dv_b[dv_b["cod_mpio"] == "05001"].iloc[0]
    ds = dv_s[dv_s["cod_mpio"] == "05001"].iloc[0]

    comp_2 = pd.DataFrame(
        [
            {
                "Fuente / Caso": "IDEAM (lectura normal)",
                "ANTES (Bronce crudo)": (
                    f"fecha='{ib_norm['fecha'][:10]}', mpio='{ib_norm['municipio']}' (sin cod_mpio), "
                    f"lluvia='{ib_norm['precipitacion_mm']}' (str)"
                ),
                "➔ DESPUÉS (Plata / Cuarentena)": (
                    f"fecha={str(is_norm['fecha'])[:10]}, cod_mpio='{is_norm['cod_mpio']}', "
                    f"precipitacion_mm={is_norm['precipitacion_mm']} (float)"
                ),
            },
            {
                "Fuente / Caso": "IDEAM (extremo >500 mm)",
                "ANTES (Bronce crudo)": (
                    f"fecha='{ib_ext['fecha'][:10]}', mpio='{ib_ext['municipio']}', "
                    f"lluvia='{ib_ext['precipitacion_mm']}' (¡imposible!)"
                ),
                "➔ DESPUÉS (Plata / Cuarentena)": (
                    f"[CUARENTENA] precipitacion_mm={iq_ext['precipitacion_mm']}, "
                    f"motivo='{iq_ext['motivo_cuarentena']}'"
                ),
            },
            {
                "Fuente / Caso": "NOAA (trimestre a mes)",
                "ANTES (Bronce crudo)": (
                    f"YR='{nb['YR']}', SEAS='{nb['SEAS']}' (trimestre), ANOM='{nb['ANOM']}'"
                ),
                "➔ DESPUÉS (Plata / Cuarentena)": (
                    f"periodo='{ns['periodo']}' (mes 8), oni={ns['oni']}, "
                    f"fase_enso='{ns['fase_enso']}' (>= 0.5)"
                ),
            },
            {
                "Fuente / Caso": "DIVIPOLA (coordenadas)",
                "ANTES (Bronce crudo)": (
                    f"cod='{db['cod_mpio']}', latitud='{db['latitud']}' (con coma), "
                    f"longitud='{db['longitud']}'"
                ),
                "➔ DESPUÉS (Plata / Cuarentena)": (
                    f"cod_mpio='{ds['cod_mpio']}', latitud={ds['latitud']} (float64), "
                    f"longitud={ds['longitud']}"
                ),
            },
        ]
    )
    print(comp_2.to_string(index=False))


# ===========================================================================
# PUNTO 3: Validación con Pandera y pruebas con pytest
# ===========================================================================
def punto_3_pandera_y_pytest(interactivo: bool = True) -> None:
    banner("PUNTO 3 · Validar la calidad con Pandera y probar las reglas con pytest")
    ficha_pedagogica(
        por_que=(
            "Si mañana cambia una hoja de Excel o la API e introduce un nulo o un negativo, "
            "necesitamos que el pipeline falle de inmediato antes de dañar la Capa Plata."
        ),
        como=(
            "Definimos esquemas `pa.DataFrameSchema` en `src/quality/esquemas.py` y creamos "
            "17 pruebas unitarias en `tests/test_limpieza.py` (7 de la clase + 10 nuevas del equipo) "
            "más 8 de extracción en `tests/test_pipeline.py` (25 tests en total)."
        ),
        para_que=(
            "Bloquear automáticamente cualquier tabla que incumpla tipos, rangos o dominios "
            "y verificar todas las reglas en ~1.3 segundos con `pytest`."
        ),
        en_simple=(
            "Pusimos un inspector automático (Pandera) a la salida de cada tabla y 25 pruebas "
            "rápidas (pytest) que comprueban cada regla con datos pequeños."
        ),
    )

    subtitulo("3.1 Demostración en vivo: ¿Qué pasa cuando Pandera detecta datos corruptos?", RED)
    df_corrupto = pd.DataFrame(
        {
            "periodo": ["2024-03"],
            "divipola": ["9999999"],  # Inválido: debe tener 5 dígitos
            "municipio": ["Medellín"],
            "segmento": ["Residencial"],
            "tipo_compra": ["ModalidadInventada"],  # Inválido: solo Bolsa o Contrato
            "energia_kwh": [-250.0],  # Inválido: debe ser > 0
            "valor_cop": [100000.0],
            "clientes": [5],
        }
    )
    print(f"{BOLD}Intentando validar un DataFrame con 3 errores intencionales:{RESET}")
    print(df_corrupto.to_string(index=False))
    try:
        ESQUEMA_VENTAS.validate(df_corrupto, lazy=True)
    except pa.errors.SchemaErrors as err:
        print(f"\n{GREEN}{BOLD}✔ Pandera bloqueó el DataFrame (lanzó SchemaErrors) y reportó las 3 fallas:{RESET}")
        print(err.failure_cases[["column", "check", "failure_case"]].to_string(index=False))

    subtitulo("3.2 ¿Por qué los 25 tests de `pytest` dicen `PASSED` (en verde) y no `FAILED`?", YELLOW)
    print(
        f"  En `pytest`, {GREEN}{BOLD}PASSED{RESET} significa: {BOLD}'El experimento funcionó como esperábamos'{RESET}.\n"
        f"  Por ejemplo, en `test_pandera_rechaza_un_tipo_de_compra_invalido` escribimos:\n\n"
        f"      {CYAN}with pytest.raises(pa.errors.SchemaError):{RESET}\n"
        f"          {CYAN}ESQUEMA_VENTAS.validate(tabla_con_dato_malo){RESET}\n\n"
        f"  • Si el inspector (`Pandera`) {BOLD}hace bien su trabajo y lanza error{RESET} ante el dato malo ➔ el test dice {GREEN}{BOLD}PASSED{RESET}.\n"
        f"  • El test solo diría {RED}{BOLD}FAILED{RESET} si el inspector {BOLD}se quedara callado y dejara pasar el dato malo{RESET}."
    )

    pausar(interactivo, "Presiona ENTER para ejecutar la suite de 25 pruebas con pytest...")

    subtitulo("Ejecutando `pytest -v` sobre las 25 pruebas unitarias", GREEN)
    subprocess.run(
        [sys.executable, "-m", "pytest", "-v"],
        cwd=str(DIR_PROYECTO),
        check=False,
    )


# ===========================================================================
# PUNTO 4: Reporte automático de calidad (docs/reporte_calidad.md)
# ===========================================================================
def punto_4_reporte_calidad(interactivo: bool = True) -> None:
    banner("PUNTO 4 · Reporte de calidad antes y después (docs/reporte_calidad.md)")
    ficha_pedagogica(
        por_que=(
            "En ingeniería de datos no basta con decir 'limpiamos los datos': hay que demostrar "
            "cuántos registros tenían cada problema ANTES y cuántos quedaron DESPUÉS."
        ),
        como=(
            "Cada módulo de `src/silver/` mide sus reglas antes y después, y `src/quality/reporte.py` "
            "genera automáticamente `docs/reporte_calidad.md` con 24 reglas y el detalle de cuarentena."
        ),
        para_que=(
            "Tener auditoría transparente y reproducible de las 5 fuentes sin escribir cifras a mano."
        ),
        en_simple=(
            "El código escribe solo el informe de auditoría comparando el Antes y el Después de cada regla."
        ),
    )

    subtitulo("Contenido generado en `docs/reporte_calidad.md` (tabla principal)", GREEN)
    ruta_rep = DIR_DOCS / "reporte_calidad.md"
    if ruta_rep.exists():
        lineas = ruta_rep.read_text(encoding="utf-8").splitlines()
        for linea in lineas[:43]:
            print(linea)
    else:
        print("No se encontró `docs/reporte_calidad.md`. Ejecuta `python -m src.transformar`.")


# ===========================================================================
# PUNTO 5: Esquema Estrella en dbt + DuckDB (Capa Oro)
# ===========================================================================
def punto_5_dbt_esquema_estrella(interactivo: bool = True) -> None:
    banner("PUNTO 5 · Construir el Esquema Estrella con dbt y DuckDB (Capa Oro)")
    ficha_pedagogica(
        por_que=(
            "Las tablas de Plata siguen organizadas según cada proveedor origen. Para cruzarlas "
            "fácilmente en BI necesitamos un modelo estrella (Kimball) con dimensiones y hechos."
        ),
        como=(
            "Configuramos `dbt/` sobre `data/observatorio.duckdb` con 11 vistas en `staging/` "
            "(`stg_*`) y 12 tablas en `marts/` (7 dimensiones `dim_*` y 5 tablas de hechos `fact_*`), "
            "protegidas por 82 pruebas automáticas (`unique`, `not_null`, `relationships`)."
        ),
        para_que=(
            "Garantizar con `dbt build` (`PASS=105`) que todas las tablas analíticas tengan grano "
            "definido y 100 % de integridad referencial."
        ),
        en_simple=(
            "Armamos en DuckDB el esquema estrella con las tablas de 'quién/dónde/cuándo' (dimensiones) "
            "y las tablas de mediciones numéricas (hechos)."
        ),
    )

    subtitulo("Inspección en vivo de `data/observatorio.duckdb` (Staging Views, Dimensiones y Hechos)", GREEN)
    if not DUCKDB_PATH.exists():
        print("No existe `data/observatorio.duckdb`. Ejecuta `python -m src.transformar`.")
        return

    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    tablas = con.execute(
        """
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = 'main'
        ORDER BY table_type, table_name
        """
    ).fetchall()

    print(f"  {'MODELO EN DUCKDB':<32} | {'CAPA / ROL':<20} | {'FILAS':>12} | {'COLUMNAS':>8}")
    print("  " + "─" * 78)
    for nombre, tipo_sql in tablas:
        filas = con.execute(f'SELECT COUNT(*) FROM "{nombre}"').fetchone()[0]
        cols = len(con.execute(f'DESCRIBE "{nombre}"').fetchall())
        if tipo_sql == "VIEW":
            rol = "Staging (VIEW)"
        elif nombre.startswith("dim_"):
            rol = "Dimensión (TABLE)"
        else:
            rol = "Hecho (TABLE)"
        print(f"  {nombre:<32} | {rol:<20} | {filas:>12,} | {cols:>8}")
    con.close()


# ===========================================================================
# PUNTO 6: Documentación del modelo y Consultas SQL de negocio en Capa Oro
# ===========================================================================
def punto_6_consultas_oro(interactivo: bool = True) -> None:
    banner("PUNTO 6 · Documentar el modelo y responder preguntas de negocio en Capa Oro")
    ficha_pedagogica(
        por_que=(
            "El modelo estrella debe demostrar con datos reales que puede responder las preguntas "
            "del reto (cómo impacta El Niño a los embalses, la generación térmica, el precio de "
            "bolsa y las ventas de EnerAndes en Antioquia)."
        ),
        como=(
            "Documentamos el diagrama y grano en `docs/modelo_dimensional.md`, el catálogo en "
            "`docs/diccionario_datos.md`, y creamos 5 consultas SQL en `consultas/oro/*.sql`."
        ),
        para_que=(
            "Comprobar de extremo a extremo la cadena causal climática y energética y dejar listas "
            "las consultas que alimentarán el dashboard de la Entrega 3."
        ),
        en_simple=(
            "Probamos el esquema estrella con 5 preguntas reales de negocio y verificamos que "
            "durante El Niño la generación térmica sube al 30 % y el precio de bolsa casi se triplica."
        ),
    )

    subtitulo("Ejecutando las 5 consultas SQL de negocio sobre `data/observatorio.duckdb`", GREEN)
    subprocess.run(
        [sys.executable, "-m", "src.consultar", "--solo-oro"],
        cwd=str(DIR_PROYECTO),
        check=False,
    )


# ===========================================================================
# PUNTOS 7 Y 8: Orquestación en un solo comando e Higiene de Git
# ===========================================================================
def punto_7_8_reproducibilidad_y_git(interactivo: bool = True) -> None:
    banner("PUNTOS 7 y 8 · Reproducibilidad (`src.transformar`) e Higiene de Git")
    ficha_pedagogica(
        por_que=(
            "Ejecutar 5 scripts sueltos y luego comandos de dbt propicia errores de orden, y subir "
            "`data/silver/` o `*.duckdb` a GitHub contamina el repositorio con archivos binarios pesados."
        ),
        como=(
            "Creamos `src/transformar.py` (`python -m src.transformar`) que ejecuta toda la Capa Plata, "
            "el reporte de calidad y `dbt build` en un solo paso; y configuramos `.gitignore`."
        ),
        para_que=(
            "Permitir que cualquier persona reconstruya Plata + Oro + 82 pruebas de dbt con un "
            "único comando en ~22 segundos manteniendo limpio el repositorio."
        ),
        en_simple=(
            "Un solo comando (`python -m src.transformar`) reconstruye y verifica todo el proyecto."
        ),
    )

    subtitulo("Verificación de `.gitignore` (archivos pesados ignorados por Git)", CYAN)
    subprocess.run(
        ["git", "status", "--ignored", "-s"],
        cwd=str(DIR_PROYECTO),
        check=False,
    )


PUNTOS = {
    1: ("Punto 1 · Limpiar el Excel de EnerAndes completo (4 hojas -> Plata y Cuarentena)", punto_1_enerandes),
    2: ("Punto 2 · Limpiar XM, IDEAM, NOAA y DANE DIVIPOLA (Plata y Cuarentena)", punto_2_otras_fuentes),
    3: ("Punto 3 · Validar con Pandera (demo en vivo) y correr las 25 pruebas pytest", punto_3_pandera_y_pytest),
    4: ("Punto 4 · Inspeccionar el Reporte de Calidad Antes vs. Después (24 reglas)", punto_4_reporte_calidad),
    5: ("Punto 5 · Inspeccionar el Esquema Estrella en DuckDB (11 vistas + 12 tablas)", punto_5_dbt_esquema_estrella),
    6: ("Punto 6 · Ejecutar las 5 consultas SQL de negocio sobre la Capa Oro", punto_6_consultas_oro),
    7: ("Puntos 7 y 8 · Reproducibilidad con un comando e higiene de `.gitignore`", punto_7_8_reproducibilidad_y_git),
}


def recorrer_todo(interactivo: bool = True) -> None:
    for num, (_, funcion) in PUNTOS.items():
        funcion(interactivo=interactivo)
        if num < len(PUNTOS):
            pausar(interactivo, f"Fin del Punto {num}. Presiona ENTER para avanzar al Punto {num + 1}...")


def menu_interactivo() -> None:
    while True:
        banner("EXPLORADOR INTERACTIVO 'BAJO EL CAPÓ' – ACTIVIDAD 2 (EA2)")
        print(f"  {BOLD}0){RESET} {GREEN}Recorrido guiado paso a paso por TODOS los puntos (1 al 7){RESET}")
        for num, (descripcion, _) in PUNTOS.items():
            print(f"  {BOLD}{num}){RESET} {descripcion}")
        print(f"  {BOLD}q){RESET} Salir\n")

        try:
            opcion = input(f"{BOLD}Elige una opción (0-7 o 'q' para salir): {RESET}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n¡Hasta luego!")
            break

        if opcion in {"q", "salir", "exit"}:
            print("¡Hasta luego!")
            break
        if opcion == "0":
            recorrer_todo(interactivo=True)
            pausar(True, "Recorrido completo finalizado. Presiona ENTER para volver al menú...")
        elif opcion.isdigit() and int(opcion) in PUNTOS:
            PUNTOS[int(opcion)][1](interactivo=True)
            pausar(True, "Presiona ENTER para volver al menú principal...")
        else:
            print(f"{RED}Opción no válida. Por favor ingresa un número del 0 al 7 o 'q'.{RESET}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Explorador interactivo de la Actividad 2 (Calidad de Datos y Modelo Dimensional)."
    )
    parser.add_argument(
        "--punto",
        type=int,
        choices=list(PUNTOS.keys()),
        help="Ejecuta directamente un punto específico (1 al 7).",
    )
    parser.add_argument(
        "--todo",
        action="store_true",
        help="Recorre todos los puntos del 1 al 7 en orden.",
    )
    parser.add_argument(
        "--sin-pausa",
        action="store_true",
        help="No espera ENTER entre secciones (útil para vista rápida).",
    )
    args = parser.parse_args()

    interactivo = not args.sin_pausa
    if args.todo:
        recorrer_todo(interactivo=interactivo)
    elif args.punto is not None:
        PUNTOS[args.punto][1](interactivo=interactivo)
    else:
        menu_interactivo()


if __name__ == "__main__":
    main()

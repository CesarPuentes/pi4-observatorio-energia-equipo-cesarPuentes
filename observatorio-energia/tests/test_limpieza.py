"""
Pruebas automaticas de la capa plata (reglas de limpieza de la clase + reglas del equipo).

Incluye:
  - Las 7 pruebas construidas en la clase (04_Clase_26_oct_4_nov_Calidad_Modelo).
  - 10 pruebas nuevas del equipo sobre las reglas de la Evidencia 2 (4 hojas de EnerAndes,
    XM horario y catalogo, IDEAM con cuarentena, NOAA con fase ENSO y DANE DIVIPOLA).

Uso:
    python -m pytest -v
"""
# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
import pandas as pd
import pandera.errors
import pytest

from src.quality.esquemas import (
    ESQUEMA_DANE_DIVIPOLA,
    ESQUEMA_IDEAM_PRECIPITACION,
    ESQUEMA_NOAA_ONI,
    ESQUEMA_VENTAS,
    ESQUEMA_XM_LISTADO_RECURSOS,
    ESQUEMA_XM_PRECIO_BOLSA,
)
from src.silver.divipola import limpiar_divipola_df
from src.silver.enerandes import (
    clave_municipio,
    convertir_mwh_a_kwh,
    limpiar,
    normalizar_periodo,
    sin_tildes,
)
from src.silver.ideam import limpiar_precipitacion_df
from src.silver.noaa import calcular_fase_enso, limpiar_noaa_df, trimestre_a_mes_central
from src.silver.xm import despivotar_horario_xm, limpiar_listado_recursos_df


# ---------------------------------------------------------------------------
# DATOS DE EJEMPLO (de la clase)
# ---------------------------------------------------------------------------
def hoja_de_ejemplo() -> pd.DataFrame:
    """Una hoja 2023 en miniatura, como queda en bronce: encabezado como fila,
    una fila repetida, una energia negativa y la fila TOTAL."""
    filas = [
        ["Fecha", "Municipio", "Segmento", "Tipo_Compra", "Energia_kWh", "Valor_COP", "Clientes"],
        ["2023-01", "Medellín", "Residencial", "Contrato", "1000", "900000", "10"],
        ["2023-01", "Medellín", "Residencial", "Contrato", "1000", "900000", "10"],   # repetida
        ["2023-01", "ITAGUI", "RESID.", "bolsa", "500", "450000", "5"],
        ["2023-02", "Rio Negro", "IND", "CONTRATOS", "-300", "270000", "2"],         # negativa
        ["TOTAL", None, None, None, "1200", "1620000", "17"],                        # total
    ]
    return pd.DataFrame(filas, columns=[f"col_{i}" for i in range(7)])


# ---------------------------------------------------------------------------
# PRUEBAS DE LA CLASE (7 pruebas)
# ---------------------------------------------------------------------------
def test_sin_tildes_quita_tildes_mayusculas_y_espacios():
    # 1. Arrange (Preparar)
    texto1 = " ITAGÜÍ "
    texto2 = "Medellín"
    # 2. Act (Ejecutar)
    resultado1 = sin_tildes(texto1)
    resultado2 = sin_tildes(texto2)
    # 3. Assert (Comprobar)
    assert resultado1 == "itagui"
    assert resultado2 == "medellin"


def test_clave_municipio_resuelve_los_alias():
    # 1. Arrange (Preparar)
    alias1 = "Rio Negro"
    alias2 = "Medellín D.E."
    vacio = None
    # 2. Act (Ejecutar)
    clave1 = clave_municipio(alias1)
    clave2 = clave_municipio(alias2)
    clave3 = clave_municipio(vacio)
    # 3. Assert (Comprobar)
    assert clave1 == "rionegro"
    assert clave2 == "medellin"
    assert clave3 is None


def test_limpiar_quita_encabezado_total_y_duplicados():
    # 1. Arrange (Preparar)
    hoja = hoja_de_ejemplo()
    # 2. Act (Ejecutar)
    limpias, cuarentena, metricas = limpiar(hoja)
    # 3. Assert (Comprobar)
    assert len(limpias) == 2
    assert "TOTAL" not in limpias["periodo"].values


def test_limpiar_unifica_valores_y_pone_divipola():
    # 1. Arrange (Preparar)
    hoja = hoja_de_ejemplo()
    # 2. Act (Ejecutar)
    limpias, _, _ = limpiar(hoja)
    itagui = limpias[limpias["municipio"] == "Itagüí"].iloc[0]
    # 3. Assert (Comprobar)
    assert itagui["divipola"] == "05360"
    assert itagui["segmento"] == "Residencial"
    assert itagui["tipo_compra"] == "Bolsa"


def test_energia_negativa_va_a_cuarentena():
    # 1. Arrange (Preparar)
    hoja = hoja_de_ejemplo()
    # 2. Act (Ejecutar)
    _, cuarentena, _ = limpiar(hoja)
    # 3. Assert (Comprobar)
    assert len(cuarentena) == 1
    assert cuarentena.iloc[0]["energia_kwh"] == -300


def test_pandera_rechaza_un_tipo_de_compra_invalido():
    # 1. Arrange (Preparar)
    limpias, _, _ = limpiar(hoja_de_ejemplo())
    limpias.loc[0, "tipo_compra"] = "CONTRATOS"
    # 2. Act y 3. Assert
    with pytest.raises(pandera.errors.SchemaErrors):
        ESQUEMA_VENTAS.validate(limpias, lazy=True)


def test_total_en_minuscula_tambien_se_elimina():
    # 1. Arrange (Preparar)
    hoja = hoja_de_ejemplo()
    hoja.loc[5, "col_0"] = "total"
    # 2. Act (Ejecutar)
    limpias, _, _ = limpiar(hoja)
    # 3. Assert (Comprobar)
    assert len(limpias) == 2


# ---------------------------------------------------------------------------
# PRUEBAS NUEVAS DEL EQUIPO (10 pruebas sobre la Evidencia 2)
# ---------------------------------------------------------------------------
def test_normalizar_periodo_cuatro_formatos_enerandes():
    # 1. Arrange (Preparar): los 4 formatos de fecha del Excel (2023 a 2026)
    f_iso = "2024-03"
    f_abrev_es = "mar-24"
    f_abrev_en = "apr-24"
    f_slash = "03/2024"
    f_corte_2026 = "01/03/2026"  # dia/mes/anio -> marzo de 2026, no 3 de enero
    # 2. Act (Ejecutar) y 3. Assert (Comprobar)
    assert normalizar_periodo(f_iso) == "2024-03"
    assert normalizar_periodo(f_abrev_es) == "2024-03"
    assert normalizar_periodo(f_abrev_en) == "2024-04"
    assert normalizar_periodo(f_slash) == "2024-03"
    assert normalizar_periodo(f_corte_2026) == "2026-03"


def test_convertir_mwh_a_kwh_hoja_2024():
    # 1. Arrange (Preparar): una tabla en miniatura con una fila en MWh y otra en kWh
    df = pd.DataFrame(
        {
            "energia_kwh": [1.5, 500.0],
            "unidad": ["MWh", "kWh"],
        }
    )
    # 2. Act (Ejecutar)
    resultado, filas_mwh = convertir_mwh_a_kwh(df)
    # 3. Assert (Comprobar): 1.5 MWh pasa a 1500.0 kWh y la columna unidad se quita
    assert filas_mwh == 1
    assert "unidad" not in resultado.columns
    assert resultado.loc[0, "energia_kwh"] == 1500.0
    assert resultado.loc[1, "energia_kwh"] == 500.0


def test_limpiar_quita_titulos_y_notas_hojas_2025_2026():
    # 1. Arrange (Preparar): una hoja estilo 2026 con 3 filas antes del encabezado y fecha DD/MM/AAAA
    filas = [
        ["EnerAndes S.A.S. E.S.P. - Reporte de ventas 2026", None, None, None, None, None, None],
        ["Fuente: sistema comercial. Uso interno.", None, None, None, None, None, None],
        [None, None, None, None, None, None, None],
        ["Fecha corte", "Ciudad", "Tipo cliente", "Compra", "kWh", "Total facturado COP", "Clientes activos"],
        ["01/03/2026", "Santa Fe de Antioquia", "Residencial", "Bolsa", "2500", "2500000", "15"],
        ["TOTAL", None, None, None, "2500", "2500000", "15"],
    ]
    hoja_2026 = pd.DataFrame(filas, columns=[f"col_{i}" for i in range(7)])
    # 2. Act (Ejecutar)
    limpias, cuarentena, _ = limpiar(hoja_2026)
    # 3. Assert (Comprobar)
    assert len(limpias) == 1
    assert len(cuarentena) == 0
    assert limpias.iloc[0]["periodo"] == "2026-03"
    assert limpias.iloc[0]["divipola"] == "05042"


def test_limpiar_une_las_cuatro_hojas_enerandes():
    # 1. Arrange (Preparar): dos hojas con encabezados y formatos distintos (2023 y 2024 con MWh)
    hoja_2023 = hoja_de_ejemplo()
    filas_2024 = [
        ["PERIODO", "MUNICIPIO", "SEGMENTO CLIENTE", "MODALIDAD", "ENERGIA", "UNIDAD", "VALOR ($)", "NUM CLIENTES"],
        ["mar-24", "Bello", "Comercial", "Bolsa", "2.5", "MWh", "2750000", "12"],
        ["09/2024", "Caldas", None, "Contrato", "400", "kWh", None, "4"],
    ]
    hoja_2024 = pd.DataFrame(filas_2024, columns=[f"col_{i}" for i in range(8)])
    # 2. Act (Ejecutar)
    limpias, cuarentena, _ = limpiar([hoja_2023, hoja_2024])
    ESQUEMA_VENTAS.validate(limpias, lazy=True)
    # 3. Assert (Comprobar): 2 limpias de 2023 + 2 limpias de 2024 = 4 filas
    assert len(limpias) == 4
    assert len(cuarentena) == 1
    bello = limpias[limpias["municipio"] == "Bello"].iloc[0]
    assert bello["periodo"] == "2024-03"
    assert bello["energia_kwh"] == 2500.0
    caldas = limpias[limpias["municipio"] == "Caldas"].iloc[0]
    assert caldas["segmento"] == "No informado"
    assert pd.isna(caldas["valor_cop"])


def test_noaa_trimestre_a_mes_central_y_fase_enso():
    # 1. Arrange (Preparar): trimestres moviles de ejemplo con casos borde (0.5 y -0.5)
    df_raw = pd.DataFrame(
        {
            "SEAS": ["DJF", "JAS", "NDJ", "MAM"],
            "YR": ["2024", "2026", "2025", "2025"],
            "TOTAL": ["27.8", "28.9", "25.9", "26.6"],
            "ANOM": ["0.5", "2.16", "-0.5", "0.12"],
        }
    )
    # 2. Act (Ejecutar)
    assert trimestre_a_mes_central("DJF") == 1
    assert trimestre_a_mes_central("JAS") == 8
    assert calcular_fase_enso(0.5) == "El Niño"
    assert calcular_fase_enso(-0.5) == "La Niña"
    assert calcular_fase_enso(0.2) == "Neutral"
    limpias, _ = limpiar_noaa_df(df_raw)
    ESQUEMA_NOAA_ONI.validate(limpias, lazy=True)
    # 3. Assert (Comprobar)
    assert len(limpias) == 4
    assert list(limpias["periodo"]) == ["2024-01", "2025-04", "2025-12", "2026-08"]
    assert list(limpias["fase_enso"]) == ["El Niño", "Neutral", "La Niña", "El Niño"]


def test_xm_despivotar_24_columnas_a_formato_largo():
    # 1. Arrange (Preparar): 1 fila de un dia con Hour01..Hour24 como texto
    fila = {"Date": "2026-08-15"}
    for h in range(1, 25):
        fila[f"Hour{h:02d}"] = str(200.0 + h * 10.0)
    df_raw = pd.DataFrame([fila])
    # 2. Act (Ejecutar)
    largo, info = despivotar_horario_xm(df_raw, "precio_bolsa_cop_kwh", incluir_recurso=False)
    ESQUEMA_XM_PRECIO_BOLSA.validate(largo, lazy=True)
    # 3. Assert (Comprobar): quedan 24 filas, una por hora (1 a 24)
    assert len(largo) == 24
    assert info["columnas_hora_antes"] == 24
    assert list(largo["hora"]) == list(range(1, 25))
    assert largo.loc[largo["hora"] == 1, "precio_bolsa_cop_kwh"].iloc[0] == 210.0
    assert largo.loc[largo["hora"] == 24, "precio_bolsa_cop_kwh"].iloc[0] == 440.0


def test_xm_listado_recursos_deduplica_e_incorpora_historicos():
    # 1. Arrange (Preparar): catalogo con un codigo repetido y una planta historica en generacion
    df_raw = pd.DataFrame(
        {
            "Code": ["2QBW", "2QBW", "3ENA"],
            "Name": ["Guatape", "Guatape Dup", "Celsia Solar"],
            "Type": ["HIDRAULICA", "HIDRAULICA", "Solar"],
            "EnerSource": ["AGUA", "AGUA", "RAD SOLAR"],
            "Disp": ["DESPACHADO CENTRALMENTE", "DESPACHADO CENTRALMENTE", "NO DESPACHADO CENTRALMENTE"],
            "RecType": ["NORMAL", "NORMAL", "AUTOGENERADOR"],
            "CompanyCode": ["EPMG", "EPMG", "CELS"],
            "OperStartdate": ["1979-01-01", "1979-01-01", "2023-05-10"],
            "State": ["OPERACION", "OPERACION", "Operacion"],
        }
    )
    # 2. Act (Ejecutar)
    df_limpio, info = limpiar_listado_recursos_df(df_raw, codigos_generacion={"2QBW", "3ENA", "3PKH"})
    ESQUEMA_XM_LISTADO_RECURSOS.validate(df_limpio, lazy=True)
    # 3. Assert (Comprobar)
    assert info["duplicados_antes"] == 1
    assert info["historicos_agregados"] == 1
    assert len(df_limpio) == 3
    assert set(df_limpio["codigo_recurso"]) == {"2QBW", "3ENA", "3PKH"}


def test_ideam_precipitacion_aisla_extremos_en_cuarentena():
    # 1. Arrange (Preparar): 2 lecturas de lluvia (una normal de 25.4 mm y un extremo de 1250 mm)
    catalogo = {"MEDELLIN": ("05001", "MEDELLÍN"), "SAN VICENTE FERRER": ("05674", "SAN VICENTE FERRER")}
    df_raw = pd.DataFrame(
        {
            "codigoestacion": ["0027015330", "0023085270"],
            "nombreestacion": ["AEROPUERTO OLAYA", "SAN VICENTE"],
            "municipio": ["MEDELLIN", "SAN VICENTE"],
            "latitud": ["6.22", "6.28"],
            "longitud": ["-75.59", "-75.33"],
            "fecha": ["2025-05-10T00:00:00.000", "2025-05-11T00:00:00.000"],
            "precipitacion_mm": ["25.4", "1250.0"],
            "n_obs": ["24", "1440"],
        }
    )
    # 2. Act (Ejecutar)
    limpias, cuarentena, _ = limpiar_precipitacion_df(df_raw, catalogo)
    ESQUEMA_IDEAM_PRECIPITACION.validate(limpias, lazy=True)
    # 3. Assert (Comprobar)
    assert len(limpias) == 1
    assert limpias.iloc[0]["cod_mpio"] == "05001"
    assert len(cuarentena) == 1
    assert cuarentena.iloc[0]["precipitacion_mm"] == 1250.0


def test_divipola_reemplaza_coma_decimal_y_valida_pandera():
    # 1. Arrange (Preparar): coordenadas con coma decimal como llegan de datos.gov.co
    df_raw = pd.DataFrame(
        {
            "cod_dpto": ["5", "05"],
            "dpto": ["Antioquia", "ANTIOQUIA"],
            "cod_mpio": ["5001", "05615"],
            "nom_mpio": ["Medellín", "Rionegro"],
            "tipo_municipio": ["Municipio", "Municipio"],
            "latitud": ["6,246631", "6,154123"],
            "longitud": ["-75,581775", "-75,373821"],
        }
    )
    # 2. Act (Ejecutar)
    limpias, _ = limpiar_divipola_df(df_raw)
    ESQUEMA_DANE_DIVIPOLA.validate(limpias, lazy=True)
    # 3. Assert (Comprobar)
    assert list(limpias["cod_mpio"]) == ["05001", "05615"]
    assert pytest.approx(limpias.iloc[0]["latitud"], rel=1e-5) == 6.246631
    assert pytest.approx(limpias.iloc[0]["longitud"], rel=1e-5) == -75.581775


def test_pandera_rechaza_energia_negativa_y_llave_duplicada():
    # 1. Arrange (Preparar): tabla con llave duplicada y energia negativa
    df_invalido = pd.DataFrame(
        {
            "periodo": ["2025-01", "2025-01"],
            "divipola": ["05001", "05001"],
            "municipio": ["Medellín", "Medellín"],
            "segmento": ["Industrial", "Industrial"],
            "tipo_compra": ["Bolsa", "Bolsa"],
            "energia_kwh": [-100.0, 500.0],
            "valor_cop": [100000.0, 500000.0],
            "clientes": [5, 5],
        }
    )
    # 2. Act y 3. Assert
    with pytest.raises(pandera.errors.SchemaErrors):
        ESQUEMA_VENTAS.validate(df_invalido, lazy=True)

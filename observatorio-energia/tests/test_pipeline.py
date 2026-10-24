"""
Pruebas automaticas del pipeline de extraccion (capa bronce) con pytest.

Ejecucion:
    python -m pytest
"""
from datetime import date

import pandas as pd

from src import config
from src.extract.ideam import consulta_soql
from src.extract.xm import aplanar, extraer_metrica
from src.utils import guardar_bronce, ventanas, ya_existe


def test_ventanas_parte_rango_correctamente():
    """Verifica que ventanas() parta un rango de fechas en bloques sin huecos ni traslapos."""
    inicio = date(2026, 1, 1)
    fin = date(2026, 3, 15)  # 74 dias en total (31 ene + 28 feb + 15 mar)
    bloques = list(ventanas(inicio, fin, dias=30))

    assert len(bloques) == 3
    assert bloques[0] == (date(2026, 1, 1), date(2026, 1, 30))
    assert bloques[1] == (date(2026, 1, 31), date(2026, 3, 1))
    assert bloques[2] == (date(2026, 3, 2), date(2026, 3, 15))


def test_aplanar_xm_hourly():
    """Verifica que aplanar() convierta el JSON horario (HourlyEntities) en filas planas."""
    respuesta_ejemplo = {
        "Items": [
            {
                "Date": "2026-01-01",
                "HourlyEntities": [
                    {
                        "Id": "Sistema",
                        "Values": {"code": "PrecBolsNaci", "Hour01": "327.90", "Hour24": "310.50"},
                    }
                ],
            }
        ]
    }
    filas = aplanar(respuesta_ejemplo, "hourly")

    assert len(filas) == 1
    assert filas[0]["Date"] == "2026-01-01"
    assert filas[0]["Id"] == "Sistema"
    assert filas[0]["Hour01"] == "327.90"
    assert filas[0]["Hour24"] == "310.50"


def test_aplanar_xm_daily():
    """Verifica que aplanar() convierta el JSON diario (DailyEntities) en filas planas."""
    respuesta_ejemplo = {
        "Items": [
            {
                "Date": "2026-09-01",
                "DailyEntities": [{"Id": "Sistema", "Value": "0.79510"}],
            },
            {
                "Date": "2026-09-02",
                "DailyEntities": [{"Id": "Sistema", "Value": "0.79935"}],
            },
        ]
    }
    filas = aplanar(respuesta_ejemplo, "daily")

    assert len(filas) == 2
    assert filas[0] == {"Date": "2026-09-01", "Id": "Sistema", "Value": "0.79510"}
    assert filas[1] == {"Date": "2026-09-02", "Id": "Sistema", "Value": "0.79935"}


def test_aplanar_xm_lists():
    """Verifica que aplanar() resuelva el endpoint lists (ListEntities) para ListadoRecursos."""
    respuesta_lists = {
        "Items": [
            {
                "Date": "2026-10-01",
                "ListEntities": [
                    {
                        "Id": "Recurso",
                        "Values": {
                            "Code": "2QBW",
                            "Name": "GUATAPE",
                            "Type": "HIDRAULICA",
                            "Disp": "DESPACHADO CENTRALMENTE",
                        },
                    }
                ],
            }
        ]
    }
    filas = aplanar(respuesta_lists, "lists")

    assert len(filas) == 1
    assert filas[0]["Date"] == "2026-10-01"
    assert filas[0]["Id"] == "Recurso"
    assert filas[0]["Code"] == "2QBW"
    assert filas[0]["Name"] == "GUATAPE"
    assert filas[0]["Type"] == "HIDRAULICA"


def test_ya_existe_idempotencia(tmp_path, monkeypatch):
    """Verifica que ya_existe() omita archivos que ya estan en bronce salvo con forzar=True."""
    monkeypatch.setattr(config, "DIR_BRONZE", tmp_path)

    # Si no existe el archivo, devuelve False
    assert ya_existe("archivo_prueba", forzar=False) is False

    # Creamos un archivo simulado en bronce
    (tmp_path / "archivo_prueba.parquet").write_bytes(b"parquet_dummy")

    # Ahora ya existe: debe devolver True si forzar=False, y False si forzar=True
    assert ya_existe("archivo_prueba", forzar=False) is True
    assert ya_existe("archivo_prueba", forzar=True) is False


def test_guardar_bronce_agrega_linaje(tmp_path, monkeypatch):
    """Verifica que guardar_bronce() conserve los datos crudos y agregue las 3 columnas de linaje."""
    monkeypatch.setattr(config, "DIR_BRONZE", tmp_path)
    df_original = pd.DataFrame([{"col_a": "10.5", "col_b": "MEDELLIN"}])

    guardar_bronce(df_original, "prueba_linaje", fuente="TEST", origen="https://ejemplo.org")

    archivo = tmp_path / "prueba_linaje.parquet"
    assert archivo.exists()

    df_leido = pd.read_parquet(archivo)
    assert len(df_leido) == 1
    assert list(df_leido.columns) == ["col_a", "col_b", "_fuente", "_origen", "_extraido_en"]
    assert df_leido.loc[0, "col_a"] == "10.5"
    assert df_leido.loc[0, "_fuente"] == "TEST"
    assert df_leido.loc[0, "_origen"] == "https://ejemplo.org"


def test_consulta_soql_precipitacion_y_temperatura():
    """Verifica que consulta_soql() filtre y agregue en el servidor para lluvia y temperatura."""
    params_lluvia = consulta_soql(date(2025, 1, 1), date(2025, 1, 7), offset=0, variable="precipitacion")
    assert "sum(valorobservado) AS precipitacion_mm" in params_lluvia["$select"]
    assert "ANTIOQUIA" in params_lluvia["$where"]
    assert "$group" in params_lluvia

    params_temp = consulta_soql(date(2025, 1, 1), date(2025, 1, 7), offset=0, variable="temperatura")
    assert "avg(valorobservado) AS temp_media_c" in params_temp["$select"]
    assert "min(valorobservado) AS temp_min_c" in params_temp["$select"]
    assert "max(valorobservado) AS temp_max_c" in params_temp["$select"]


def test_xm_extraer_metrica_omite_existente(tmp_path, monkeypatch):
    """Verifica que extraer_metrica() no haga peticiones HTTP si el Parquet ya existe."""
    monkeypatch.setattr(config, "DIR_BRONZE", tmp_path)
    (tmp_path / "xm_precio_bolsa.parquet").write_bytes(b"parquet_dummy")

    llamadas_http = []
    monkeypatch.setattr("src.extract.xm.http_json", lambda *args, **kwargs: llamadas_http.append(args))

    extraer_metrica("PrecBolsNaci", "Sistema", "hourly", "xm_precio_bolsa", forzar=False)
    assert len(llamadas_http) == 0

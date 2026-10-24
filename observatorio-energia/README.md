# Observatorio Energía y Clima – Equipo <nombre>

> Proyecto Integrado IV – Integración de Información · IU Digital de Antioquia · 2026-2

## 👥 Integrantes

| Nombre | Usuario GitHub | Rol |
|---|---|---|
| | | Líder técnico / Data Engineer |
| | | Data Quality Analyst |
| | | Analytics Engineer |
| | | BI Analyst / Storyteller |

## 🎯 Objetivo

Integrar datos del mercado eléctrico (XM), del clima (IDEAM y NOAA) y de ventas internas (EnerAndes) para analizar el riesgo energético de Colombia ante El Niño 2026.

## 📦 Fuentes de datos (capa bronce)

| Fuente | Tipo | Archivo en `data/bronze/` |
|---|---|---|
| XM – API Sinergox | API REST (POST, JSON) | `xm_precio_bolsa`, `xm_demanda`, `xm_embalses`, `xm_generacion_recurso`, `xm_aportes`, `xm_listado_recursos` |
| IDEAM – datos.gov.co | API Socrata (SoQL) | `ideam_precipitacion_diaria`, `ideam_temperatura_diaria` |
| NOAA – índice ONI | Archivo de texto | `noaa_oni` |
| EnerAndes | Excel interno | `enerandes_ventas_2023` … `enerandes_ventas_2026` |
| DANE – DIVIPOLA (Propia) | API Socrata (SoQL) | `dane_divipola` |

## 🌎 Fuente propia: DIVIPOLA – DANE (`src/extract/divipola.py`)

- **¿Qué es y de dónde viene?** Es el catálogo oficial de la División Político-Administrativa de Colombia publicado por el DANE en datos abiertos (`https://www.datos.gov.co/resource/gdxc-w37w.json`).
- **¿Para qué se usará?** En el Excel de EnerAndes los municipios vienen sin estandarizar (`Medellin`, `MEDELLÍN`, `Apartado`, etc.). Con `dane_divipola` asignaremos el código oficial DANE (`cod_mpio`) para cruzar las ventas comerciales de EnerAndes con las estaciones meteorológicas del IDEAM por municipio en Antioquia.

## ⚙️ Cómo ejecutar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# copiar ventas_enerandes_2023_2026.xlsx en data/insumos/
python -m src.pipeline          # descarga las 4 fuentes a data/bronze/ (unos 3 minutos)
python -m src.consultar         # consultas SQL de BI con DuckDB
```

Para volver a descargar todo: `python -m src.pipeline --forzar`. El rango de fechas se cambia en `src/config.py`.

## 🏗️ Arquitectura

```
Fuentes -> BRONCE (dato tal cual + linaje) -> PLATA (limpio) -> ORO (modelo estrella) -> Dashboard
```

## 🤖 Uso de IA

(Declarar aquí qué herramientas de IA se usaron y para qué.)

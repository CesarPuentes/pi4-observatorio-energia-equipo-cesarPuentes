# Observatorio Energía y Clima – César Puentes (EA1)

> Proyecto Integrado IV · IU Digital de Antioquia · 2026-2

## 👥 Integrante

| Nombre | Usuario GitHub | Rol | Bitácora |
|---|---|---|---|
| César Puentes | `CesarPuentes` | Data Engineer / Quality / Analytics / BI | [`docs/bitacoras/puentes_cesar.md`](docs/bitacoras/puentes_cesar.md) |

## 🎯 Objetivo

Integrar en la **capa bronce** datos crudos del mercado eléctrico (XM), clima (IDEAM y NOAA), ventas internas (EnerAndes) y municipios (DIVIPOLA) en formato Parquet con linaje.

## 📦 Fuentes de datos (`data/bronze/` y muestras en `data/sample/`)

| Fuente | Método | Rango | Archivos generados |
|---|---|---|---|
| **XM – Sinergox** | API REST (`POST`, JSON) | `2024-01-01` a `2026-09-30` | `xm_precio_bolsa`, `xm_demanda`, `xm_embalses`, `xm_generacion_recurso`, `xm_aportes`, `xm_listado_recursos` (`/lists`) |
| **IDEAM** | API Socrata (SoQL) | Desde `2025-01-01` | `ideam_precipitacion_diaria` (`s54a-sgyg`), `ideam_temperatura_diaria` (`sbwg-7ju4`) |
| **NOAA** | Texto plano (`GET`) | `1950`–`2026` | `noaa_oni` |
| **EnerAndes** | Excel interno | `2023`–`2026` | `enerandes_ventas_2023` … `enerandes_ventas_2026` |
| **DIVIPOLA (DANE)** | API Socrata (SoQL) | Vigente | `dane_divipola` (`gdxc-w37w`) |

## 🌎 Fuente propia: DIVIPOLA (`src/extract/divipola.py`)

- **¿Qué es y de dónde viene?** Catálogo oficial de departamentos y municipios del DANE en datos abiertos (`https://www.datos.gov.co/resource/gdxc-w37w.json`).
- **¿Para qué se usará?** Para normalizar con código DANE (`cod_mpio`) los nombres de municipios sucios del Excel de EnerAndes (`Medellin`, `MEDELLÍN`, etc.) y cruzarlos sin pérdida con las estaciones climáticas del IDEAM en Antioquia.

## ⚙️ Cómo ejecutar desde cero

```bash
uv venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt

uv run python -m src.pipeline      # Descarga bronce y crea muestras en data/sample/
uv run python -m src.consultar     # Consultas SQL con DuckDB
uv run python -m src.perfilar      # Genera docs/perfilamiento.md
uv run python -m pytest            # Ejecuta las 8 pruebas automáticas
```

*(Para forzar la re-descarga: `uv run python -m src.pipeline --forzar`)*

## 🏗️ Arquitectura y Documentación

```text
Fuentes -> BRONCE (Parquet crudo + linaje) -> PLATA (limpio) -> ORO (modelo estrella) -> Dashboard
```

- **Perfilamiento y hallazgos:** [`docs/perfilamiento.md`](docs/perfilamiento.md)
- **Uso de IA:** Se usó asistente de IA en el IDE para apoyo en pruebas con `pytest` y script de perfilamiento.

# Mapa del Proyecto y Reporte de Avance

## ¿Por qué se desarrolló la Actividad 1?

El código provisto en clase era una demostración reducida a la que le faltaban piezas críticas de negocio e ingeniería:

1. **Rango histórico insuficiente:** Solo cubría 2026 (y lluvias desde junio), impidiendo comparar la coyuntura actual con El Niño 2023–2024. Se amplió XM desde enero de 2024 e IDEAM desde enero de 2025.
2. **Falta de variables explicativas del precio:** Faltaban la generación por planta (`Gene` por `Recurso`), los aportes hídricos (`AporEner`) y la temperatura del aire del IDEAM.
3. **Limitación técnica del extractor de XM:** El script base solo consultaba endpoints con fechas (`hourly` y `daily`) y no soportaba el catálogo de plantas (`ListadoRecursos`) en el endpoint `lists` (`ListEntities`, sin fechas).
4. **Calidad y gobernabilidad previas a la Capa Plata:** Se requería auditar los datos crudos (`docs/perfilamiento.md`), publicar muestras livianas (`data/sample/`) y agregar pruebas con `pytest`.

### Enlaces de referencia de las fuentes de datos
- **XM – API Sinergox (`POST`):** `https://servapibi.xm.com.co/hourly`, `https://servapibi.xm.com.co/daily` y `https://servapibi.xm.com.co/lists` ([Documentación](https://github.com/EquipoAnaliticaXM/API_XM))
- **IDEAM – Precipitación (`GET` SoQL):** `https://www.datos.gov.co/resource/s54a-sgyg.json` ([Ficha](https://www.datos.gov.co/d/s54a-sgyg))
- **IDEAM – Temperatura (`GET` SoQL):** `https://www.datos.gov.co/resource/sbwg-7ju4.json` ([Ficha](https://www.datos.gov.co/d/sbwg-7ju4))
- **NOAA – Índice ONI (`GET`):** `https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt`
- **DANE – DIVIPOLA (`GET` SoQL):** `https://www.datos.gov.co/resource/gdxc-w37w.json` ([Ficha](https://www.datos.gov.co/d/gdxc-w37w))

---

## Primer Commit – Ampliación de la extracción de XM (`#1`)

Link PR: https://github.com/CesarPuentes/pi4-observatorio-energia-equipo-cesarPuentes/pull/5

Cambios aplicados sobre el código base:

1. **[`src/config.py`](observatorio-energia/src/config.py):**
   - Se cambió `FECHA_INICIO` de `2026-01-01` a `2024-01-01`.
   - Se agregaron 3 métricas a `XM_METRICAS`: `Gene` (`Recurso`, `hourly`), `AporEner` (`Sistema`, `daily`) y `ListadoRecursos` (`Sistema`, `lists`).

2. **[`src/extract/xm.py`](observatorio-energia/src/extract/xm.py):**
   - Se agregó el soporte para `periodo == "lists"`, enviando el cuerpo JSON sin fechas (`{"MetricId": metrica, "Entity": entidad}`) al endpoint `https://servapibi.xm.com.co/lists` y leyendo la clave `ListEntities` de la respuesta.
   - Se paralelizó la descarga de las ventanas de 30 días con `ThreadPoolExecutor` para acelerar la extracción de los 2+ años de historia.
   - Se regeneraron los 6 archivos Parquet en `data/bronze/` ejecutando `uv run python -m src.extract.xm --forzar`.

---

## Segundo Commit – Ampliación de la extracción del IDEAM (`#2`)

Cambios aplicados sobre el código base:

1. **[`src/config.py`](observatorio-energia/src/config.py):**
   - Se amplió `IDEAM_FECHA_INICIO` de `2026-06-01` a `2025-01-01` (> 1 año de cobertura).
   - Se añadió la URL del dataset de temperatura del aire: `IDEAM_TEMPERATURA_URL = "https://www.datos.gov.co/resource/sbwg-7ju4.json"`.

2. **[`src/extract/ideam.py`](observatorio-energia/src/extract/ideam.py):**
   - Se parametrizó la consulta SoQL para calcular en el servidor tanto la precipitación acumulada diaria (`sum(valorobservado)`) como la temperatura media, mínima y máxima diaria por estación (`avg()`, `min()` y `max()` sobre `valorobservado`).
   - Se extendió la extracción para generar ambos archivos en `data/bronze/`: `ideam_precipitacion_diaria.parquet` e `ideam_temperatura_diaria.parquet`.

---

## Tercer Commit – Incorporación de fuente propia DIVIPOLA (`#2`)

Cambios aplicados sobre el código base:

1. **[`src/config.py`](observatorio-energia/src/config.py):**
   - Se añadió `DIVIPOLA_URL = "https://www.datos.gov.co/resource/gdxc-w37w.json"`.

2. **[`src/extract/divipola.py`](observatorio-energia/src/extract/divipola.py):**
   - Se creó el extractor para descargar mediante paginación SoQL el catálogo oficial de municipios del DANE y almacenarlo en `data/bronze/dane_divipola.parquet`.

3. **[`src/pipeline.py`](observatorio-energia/src/pipeline.py) y [`observatorio-energia/README.md`](observatorio-energia/README.md):**
   - Se integró `divipola` en la secuencia de ejecución del pipeline y se documentó su origen y propósito de negocio (estandarizar nombres de municipios entre EnerAndes e IDEAM mediante `cod_mpio`).

---

## Cuarto Commit – Muestras en `data/sample/` y Perfilamiento de Datos (`#3`)

Cambios aplicados sobre el código base:

1. **[`src/config.py`](observatorio-energia/src/config.py) y [`src/pipeline.py`](observatorio-energia/src/pipeline.py):**
   - Se añadieron `DIR_SAMPLE = RAIZ / "data" / "sample"` y `SAMPLE_FILAS = 200`.
   - Se implementó `exportar_muestras()` dentro del pipeline para exportar automáticamente las primeras 200 filas de cada uno de los 14 archivos Parquet de `data/bronze/` a formato CSV en `data/sample/`, garantizando que `data/bronze/` permanezca excluido por `.gitignore`.

2. **[`src/perfilar.py`](observatorio-energia/src/perfilar.py) y [`docs/perfilamiento.md`](observatorio-energia/docs/perfilamiento.md):**
   - Se creó el módulo `src.perfilar` que audita los 14 archivos Parquet de `data/bronze/` y genera [`docs/perfilamiento.md`](observatorio-energia/docs/perfilamiento.md) con las tablas de filas, columnas, tipos de datos, porcentaje de nulos, duplicados y rangos de fechas.
   - Se documentaron **8 hallazgos de calidad con evidencia numérica** (filas parásitas/TOTAL y esquemas dispares en EnerAndes, 38 variantes de municipios para 20 municipios reales, unidades `kWh`/`MWh` mezcladas, 120 duplicados y valores negativos, rezago del IDEAM al `2026-07-24`, comas decimales en DIVIPOLA y duplicados en `xm_listado_recursos`).
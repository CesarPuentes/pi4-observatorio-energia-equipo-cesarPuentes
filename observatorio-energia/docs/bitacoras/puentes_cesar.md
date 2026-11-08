# Bitácora Individual – César Puentes

> **Curso:** Proyecto Integrado IV – Integración de Información (ISD-44) · IU Digital de Antioquia · 2026-2
> **Proyecto:** Observatorio Energía y Clima Colombia (`pi4-observatorio-energia`)

---

## Semana 1 y 2 (12 – 25 de octubre de 2026) — Evidencia de Aprendizaje 1 (EA1)

- **Rol esta semana:** Líder técnico / Data Engineer
- **Qué hice:**
  1. **Ampliación del extractor de XM (`src/extract/xm.py` y `src/config.py`):**
     - Amplié el rango de extracción a más de 2 años (`2024-01-01` a `2026-09-30`, 1,004 días en ventanas de 30 días).
     - Agregué las métricas `Gene` (entidad `Recurso`, horaria), `AporEner` (entidad `Sistema`, diaria) y `ListadoRecursos` (entidad `Sistema`, endpoint `lists`).
     - Extendí `aplanar()` y `extraer_metrica()` para soportar el endpoint `lists` de XM, el cual no recibe fechas (`StartDate`/`EndDate`) y devuelve la estructura anidada `ListEntities`.
  2. **Ampliación del extractor del IDEAM (`src/extract/ideam.py`):**
     - Amplié el rango de precipitación (`s54a-sgyg`) desde el `2025-01-01` hasta el `2026-09-30`.
     - Integré el dataset de temperatura del aire (`sbwg-7ju4`) calculando temperatura media (`avg`), mínima (`min`) y máxima (`max`) diaria por estación directamente en el servidor mediante consultas SoQL (`$select`, `$where`, `$group`, `$limit`, `$offset`).
  3. **Integración de fuente propia (`src/extract/divipola.py`):**
     - Implementé la extracción paginada del catálogo oficial DIVIPOLA del DANE (`gdxc-w37w`) a `data/bronze/dane_divipola.parquet` e integré el módulo en `src/pipeline.py`, junto con la exportación automática de muestras de 200 filas en `data/sample/*.csv`.
  4. **Perfilamiento y pruebas automáticas (`src/perfilar.py`, `docs/perfilamiento.md`, `tests/test_pipeline.py`):**
     - Desarrollé el perfilamiento completo de los 14 archivos Parquet de la capa bronce, documentando 8 hallazgos de calidad con evidencia numérica.
     - Implementé 8 pruebas unitarias con `pytest` para validar `ventanas()`, `aplanar()` (`hourly`, `daily`, `lists`), `consulta_soql()`, `ya_existe()` y `guardar_bronce()`.
- **Qué aprendí:**
  - Cómo consumir APIs REST heterogéneas (POST con ventanas de fechas en Sinergox XM vs. GET con agregación en el servidor mediante SoQL en Socrata/datos.gov.co).
  - La importancia de las 4 reglas de la capa bronce en la arquitectura Medallion: conservar el dato crudo sin modificarlo, registrar el linaje (`_fuente`, `_origen`, `_extraido_en`), garantizar idempotencia y asegurar reproducibilidad.
- **Bloqueos y cómo los resolví:**
  - *Catálogo de XM (`ListadoRecursos`):* En el catálogo de métricas de XM la URL aparece como `/list` (que devuelve HTTP 404) y la estructura JSON usa `ListEntities` en lugar de `DailyEntities` o `HourlyEntities`. Lo resolví apuntando al endpoint `/lists`, omitiendo los campos de fecha en el cuerpo POST y desempacando `entidad["Values"]` dentro de `ListEntities`.
  - *Tiempos de respuesta en Socrata (IDEAM):* Las consultas de rangos largos pueden generar timeout porque el servidor agrupa millones de mediciones subhorarias. Se mantuvo la consulta por ventanas semanales con reintentos exponenciales (`_con_reintentos`) y paginación `$limit`/`$offset`.
- **Horas dedicadas:** 16 horas

---

## Semana 3 y 4 (26 de octubre – 8 de noviembre de 2026) — Evidencia de Aprendizaje 2 (EA2)

- **Rol esta semana:** Data Quality Analyst & Analytics Engineer
- **Qué hice:**
  1. **Ampliación de la Capa Plata desde el código base de la clase (`src/silver/`):**
     - **`src/silver/enerandes.py`:** Partiendo del código de la clase (`04_Clase_26_oct_4_nov_Calidad_Modelo`, hoja `2023`), amplié `limpiar()` para procesar las **4 hojas del Excel (`2023`, `2024`, `2025`, `2026`)** y unirlas en `data/silver/enerandes_ventas.parquet` (**4,007 filas limpias**). Resolví los títulos y notas en las primeras filas de `2025` y `2026` (`6` filas), los encabezados distintos por hoja (`4` filas), las filas `TOTAL` (`4` filas), las **120 filas duplicadas**, los **4 formatos de fecha** (`2024-03`, `mar-24`/`apr-24`, `03/2024` y `01/03/2026` como `DD/MM/AAAA`: marzo de 2026 y no 3 de enero) llevados al estándar `AAAA-MM`, las **337 filas en `MWh`** de la hoja `2024` convertidas a `kWh` (`× 1,000`), la homologación de municipios con el código DIVIPOLA (`38` variantes → `15` municipios), el segmento vacío marcado como `'No informado'` (`28` filas), el valor facturado vacío dejado en `NaN` (`28` filas, `nullable=True`) y las **43 filas con energía vacía (`25`) o negativa (`18`)** apartadas en `data/silver/enerandes_cuarentena.parquet`.
     - **`src/silver/xm.py`:** Despivoté (`melt`) `xm_precio_bolsa`, `xm_demanda` y `xm_generacion_recurso` de 24 columnas (`Hour01`..`Hour24`) a formato largo por `fecha` y `hora` (`1..24`), filtrando las **2,472,831** celdas horarias vacías de plantas sin generación, escalé `xm_embalses` a porcentaje (`0..100 %`), limpié `xm_aportes` y eliminé los duplicados (`5J8H`, `5PUN`) e inconsistencias de mayúsculas en `xm_listado_recursos`, incorporando los **10 códigos históricos** de generación para garantizar integridad referencial (`2,501` recursos únicos).
     - **`src/silver/ideam.py`, `src/silver/noaa.py` y `src/silver/divipola.py`:** Tipé fechas y variables climáticas del IDEAM vinculando cada estación con su `cod_mpio` DIVIPOLA y aislando en `ideam_cuarentena.parquet` **7 lecturas extremas (`> 500 mm/día`)** por volcado acumulado del sensor; convertí los trimestres móviles de NOAA (`DJF` → `1`, …, `NDJ` → `12`) a mes central y calculé `fase_enso` (`El Niño` si `>= 0.5`, `La Niña` si `<= -0.5`, `Neutral`); y reemplacé la coma decimal por punto en las coordenadas de `dane_divipola`.
  2. **Validación con Pandera, Pruebas con `pytest` y Reporte de Calidad (`src/quality/esquemas.py`, `tests/test_limpieza.py`, `docs/reporte_calidad.md`):**
     - Amplié `src/quality/esquemas.py` conservando intacto `ESQUEMA_VENTAS` de la clase y agregando los esquemas de Pandera para cada tabla de la capa plata (`ESQUEMA_XM_*`, `ESQUEMA_IDEAM_*`, `ESQUEMA_NOAA_ONI`, `ESQUEMA_DANE_DIVIPOLA`).
     - Conservé las **7 pruebas de la clase** en `tests/test_limpieza.py` y escribí **10 pruebas unitarias nuevas** sobre las reglas del equipo (25 pruebas en total junto con `tests/test_pipeline.py`, pasando en `1.5 s`).
     - Automatizé en `src/quality/reporte.py` la generación de `docs/reporte_calidad.md` con **23 reglas medidas antes y después** y el análisis de cuarentena.
  3. **Esquema Estrella en `dbt` + DuckDB y Documentación (`dbt/`, `docs/`, `consultas/oro/`, `src/transformar.py`):**
     - Amplié el proyecto `dbt/` de la clase (`dbt/models/staging/` con 11 vistas y `dbt/models/marts/` con **7 dimensiones** y **5 tablas de hechos** materializadas en `data/observatorio.duckdb`), escribiendo el grano de cada modelo y **82 pruebas de datos** (`unique`, `not_null`, `relationships`, `accepted_values`) en `dbt/models/marts/schema.yml` (`PASS=105 WARN=0 ERROR=0` en `dbt build`).
     - Documenté el diagrama y grano de cada hecho en `docs/modelo_dimensional.md`, el diccionario completo en `docs/diccionario_datos.md`, 5 consultas analíticas en `consultas/oro/` y el orquestador reproducible `python -m src.transformar`.
- **Qué aprendí:**
  - Cómo combinar contratos de datos en Python (`pandera`) en la capa plata con vistas `staging` y tablas `marts` probadas declarativamente (`unique`, `not_null`, `relationships` en `dbt`) en la capa oro para garantizar cero errores de integridad referencial.
  - La importancia de definir explícitamente el grano de cada tabla de hechos (mensual por municipio/segmento, horario del sistema, horario por planta, diario hidrológico y diario por estación) antes de cruzarlos mediante dimensiones conformadas (`dim_fecha`, `dim_mes`, `dim_hora`, `dim_municipio`).
- **Bloqueos y cómo los resolví:**
  - *Recursos históricos en generación vs. catálogo actual (`ListadoRecursos`):* Al ejecutar la prueba `relationships` de `dbt` entre `fact_generacion_recurso` (2024–2026) y `dim_recurso` (corte octubre de 2026), aparecieron 10 códigos de plantas que generaron en 2024–2025 pero ya no figuraban en el corte actual de `ListadoRecursos`. Lo resolví en `src/silver/xm.py` incorporando esos 10 códigos como miembros históricos (`estado = 'HISTORICO'`) en `xm_listado_recursos.parquet`, preservando el 100 % de la generación histórica y cumpliendo la integridad referencial en `dbt build`.
- **Horas dedicadas:** 18 horas

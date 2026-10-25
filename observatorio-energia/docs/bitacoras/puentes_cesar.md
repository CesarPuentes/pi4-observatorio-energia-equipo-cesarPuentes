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

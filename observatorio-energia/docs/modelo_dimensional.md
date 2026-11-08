# Modelo Dimensional (Esquema Estrella – Capa Oro)

> **Proyecto Integrado IV – Observatorio Energía y Clima Colombia (2026-2)**
> Almacén analítico implementado con **dbt-duckdb** en `data/observatorio.duckdb` a partir de la capa plata validada con **Pandera** (`data/silver/*.parquet` y `src/quality/esquemas.py`).

---

## 1. Arquitectura del Esquema Estrella (Kimball)

Partiendo del modelo base construido en clase (`stg_ventas` → `dim_mes`, `dim_municipio`, `dim_segmento` y `fact_ventas_mensual`), el proyecto `dbt/` se amplió siguiendo la arquitectura de dos capas de dbt (**`models/staging/`** como vistas de lectura de `data/silver/*.parquet` y **`models/marts/`** como tablas materializadas en `data/observatorio.duckdb`), conformando un esquema estrella con **7 dimensiones** y **5 tablas de hechos**:

- **11 vistas de entrada (`dbt/models/staging/`):** `stg_ventas`, `stg_xm_precio_bolsa`, `stg_xm_demanda`, `stg_xm_generacion_recurso`, `stg_xm_embalses`, `stg_xm_aportes`, `stg_xm_listado_recursos`, `stg_ideam_precipitacion`, `stg_ideam_temperatura`, `stg_noaa_oni` y `stg_divipola`.
- **7 dimensiones (`dbt/models/marts/`):** `dim_mes`, `dim_fecha`, `dim_hora`, `dim_municipio`, `dim_segmento`, `dim_recurso` y `dim_estacion`.
- **5 tablas de hechos (`dbt/models/marts/`):** `fact_ventas_mensual` (`2023` a `2026`), `fact_mercado_horario`, `fact_generacion_recurso`, `fact_hidrologia_diaria` y `fact_clima_diario`.

### Diagrama Entidad-Relación del Esquema Estrella (Mermaid)

```mermaid
erDiagram
    dim_mes ||--o{ fact_ventas_mensual : "mes_id (AAAAMM)"
    dim_fecha ||--o{ fact_ventas_mensual : "fecha (mes)"
    dim_fecha ||--o{ fact_mercado_horario : "fecha (dia)"
    dim_fecha ||--o{ fact_generacion_recurso : "fecha (dia)"
    dim_fecha ||--o| fact_hidrologia_diaria : "fecha (dia)"
    dim_fecha ||--o{ fact_clima_diario : "fecha (dia)"

    dim_hora ||--o{ fact_mercado_horario : "hora (1..24)"
    dim_hora ||--o{ fact_generacion_recurso : "hora (1..24)"

    dim_municipio ||--o{ fact_ventas_mensual : "municipio_id (divipola)"
    dim_municipio ||--o{ fact_clima_diario : "municipio_id (divipola)"
    dim_municipio ||--o{ dim_estacion : "municipio_id (divipola)"

    dim_segmento ||--o{ fact_ventas_mensual : "segmento_id"
    dim_recurso ||--o{ fact_generacion_recurso : "codigo_recurso"
    dim_estacion ||--o{ fact_clima_diario : "codigo_estacion"

    dim_mes {
        INTEGER mes_id PK
        VARCHAR periodo
        INTEGER anio
        INTEGER mes
        INTEGER trimestre
        DOUBLE oni
        VARCHAR fase_enso
    }

    dim_fecha {
        DATE fecha PK
        INTEGER fecha_id
        INTEGER mes_id
        VARCHAR periodo
        INTEGER anio
        INTEGER trimestre
        INTEGER mes
        VARCHAR nombre_mes
        INTEGER dia_mes
        INTEGER dia_semana_iso
        VARCHAR nombre_dia_semana
        BOOLEAN es_fin_de_semana
        VARCHAR trimestre_movil_oni
        DOUBLE oni
        VARCHAR fase_enso
    }

    dim_hora {
        INTEGER hora PK
        VARCHAR franja_horaria
        VARCHAR periodo_dia
        VARCHAR tipo_franja_demanda
        BOOLEAN es_horario_solar
    }

    dim_municipio {
        VARCHAR municipio_id PK
        VARCHAR cod_mpio
        VARCHAR municipio
        VARCHAR cod_dpto
        VARCHAR departamento
        VARCHAR tipo_municipio
        DOUBLE latitud
        DOUBLE longitud
    }

    dim_segmento {
        BIGINT segmento_id PK
        VARCHAR segmento
    }

    dim_recurso {
        VARCHAR codigo_recurso PK
        VARCHAR nombre_recurso
        VARCHAR tipo_generacion
        VARCHAR fuente_energia
        VARCHAR tipo_despacho
        VARCHAR tipo_recurso
        VARCHAR codigo_agente
        DATE fecha_operacion
        VARCHAR estado
        BOOLEAN es_renovable
    }

    dim_estacion {
        VARCHAR codigo_estacion PK
        VARCHAR nombre_estacion
        VARCHAR municipio_id FK
        VARCHAR cod_mpio
        VARCHAR municipio
        DOUBLE latitud
        DOUBLE longitud
        BOOLEAN mide_precipitacion
        BOOLEAN mide_temperatura
    }

    fact_ventas_mensual {
        VARCHAR venta_id PK
        INTEGER mes_id FK
        DATE fecha FK
        VARCHAR municipio_id FK
        VARCHAR cod_mpio
        BIGINT segmento_id FK
        VARCHAR tipo_compra
        DOUBLE energia_kwh
        DOUBLE valor_cop
        INTEGER clientes
        DOUBLE precio_unitario_cop_kwh
    }

    fact_mercado_horario {
        VARCHAR mercado_horario_id PK
        DATE fecha FK
        INTEGER hora FK
        DOUBLE precio_bolsa_cop_kwh
        DOUBLE demanda_real_kwh
        DOUBLE demanda_real_mwh
        DOUBLE costo_horario_bolsa_cop
    }

    fact_generacion_recurso {
        DATE fecha FK
        INTEGER hora FK
        VARCHAR codigo_recurso FK
        DOUBLE generacion_kwh
    }

    fact_hidrologia_diaria {
        DATE fecha PK_FK
        DOUBLE volumen_util_pct
        DOUBLE aportes_energia_kwh
        DOUBLE aportes_energia_gwh
    }

    fact_clima_diario {
        VARCHAR clima_diario_id PK
        DATE fecha FK
        VARCHAR codigo_estacion FK
        VARCHAR municipio_id FK
        VARCHAR cod_mpio
        DOUBLE precipitacion_mm
        DOUBLE temp_media_c
        DOUBLE temp_min_c
        DOUBLE temp_max_c
    }
```

---

## 2. Explicación del Grano de Cada Tabla de Hechos

### 2.1 `fact_ventas_mensual` (4,007 filas | Cobertura: 2023–2026)
- **Grano:** **Una fila por mes (`mes_id` / `fecha`), municipio (`municipio_id` DIVIPOLA), segmento de cliente (`segmento_id`) y tipo de compra (`tipo_compra`: `Bolsa` o `Contrato`)**.
- **Justificación de diseño:** Conserva exactamente las llaves del modelo de la clase (`mes_id`, `municipio_id`, `segmento_id`, `tipo_compra`, `energia_kwh`, `valor_cop`, `clientes`) sobre las 4 hojas consolidadas del Excel de EnerAndes (`2023` a `2026`), y añade `fecha` (`YYYY-MM-01`) para permitir su unión directa tanto con `dim_mes` como con `dim_fecha`.

### 2.2 `fact_mercado_horario` (24,096 filas | Cobertura: 2024-01-01 a 2026-09-30)
- **Grano:** **Una fila por `fecha` (día calendario) y `hora` del día (`1` a `24`) a nivel del Sistema Interconectado Nacional (SIN)**.
- **Justificación de diseño:** Une el precio de bolsa nacional (`PrecBolsNaci` en `COP/kWh`) y la demanda real (`DemaReal` en `kWh` y `MWh`) despivotados de las 24 columnas horarias de XM (`1,004 días × 24 horas = 24,096 filas`).

### 2.3 `fact_generacion_recurso` (5,935,449 filas | Cobertura: 2024-01-01 a 2026-09-30)
- **Grano:** **Una fila por `fecha` (día calendario), `hora` del día (`1` a `24`) y planta/recurso generador (`codigo_recurso`) con generación positiva (`> 0 kWh`)**.
- **Justificación de diseño:** Al unirse con `dim_recurso` (`ListadoRecursos`) y `dim_fecha` (`fase_enso`), permite cuantificar la sustitución entre generación hidráulica y térmica durante las fases de `El Niño`, `Neutral` y `La Niña`.

### 2.4 `fact_hidrologia_diaria` (1,004 filas | Cobertura: 2024-01-01 a 2026-09-30)
- **Grano:** **Una fila por `fecha` (día calendario) a nivel del SIN**.
- **Justificación de diseño:** Integra las métricas diarias de porcentaje de volumen útil de los embalses (`volumen_util_pct`) y aportes hídricos diarios (`aportes_energia_kwh` y `aportes_energia_gwh`) sin duplicarlas artificialmente por hora.

### 2.5 `fact_clima_diario` (30,271 filas | Cobertura: 2025-01-01 a 2026-07-24)
- **Grano:** **Una fila por `fecha` (día calendario) y estación meteorológica (`codigo_estacion`) del IDEAM en Antioquia**.
- **Justificación de diseño:** Consolida la precipitación acumulada diaria (`precipitacion_mm`) y las temperaturas diarias (`temp_media_c`, `temp_min_c`, `temp_max_c`), enlazadas con `dim_estacion`, `dim_municipio` (`municipio_id`) y `dim_fecha`.

---

## 3. Matriz Bus de Integración (Kimball Bus Matrix)

| Tabla de Hechos | Grano | `dim_mes` | `dim_fecha` (con ENSO) | `dim_hora` | `dim_municipio` (DIVIPOLA) | `dim_segmento` | `dim_recurso` (Plantas XM) | `dim_estacion` (IDEAM) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `fact_ventas_mensual` | Mes × Municipio × Segmento × Tipo Compra | ✅ | ✅ | — | ✅ | ✅ | — | — |
| `fact_mercado_horario` | Día × Hora (Sistema) | — | ✅ | ✅ | — | — | — | — |
| `fact_generacion_recurso` | Día × Hora × Planta | — | ✅ | ✅ | — | — | ✅ | — |
| `fact_hidrologia_diaria` | Día (Sistema) | — | ✅ | — | — | — | — | — |
| `fact_clima_diario` | Día × Estación IDEAM | — | ✅ | — | ✅ | — | — | ✅ |

---

## 4. Validación del Modelo en `dbt` (`dbt build`)

Todos los modelos del esquema estrella están documentados y probados en [`dbt/models/marts/schema.yml`](../dbt/models/marts/schema.yml):
- **`unique` y `not_null`** en las llaves primarias de las 7 dimensiones y de las tablas de hechos.
- **`relationships` (integridad referencial)** en todas las llaves foráneas de las 5 tablas de hechos hacia sus dimensiones.
- **`accepted_values`** en dominios categóricos (`tipo_compra`, `fase_enso`).
- Ejecución verificada con `dbt build --project-dir dbt --profiles-dir dbt`: **11 vistas staging + 12 tablas marts + 82 pruebas de datos = 105/105 PASS (`0 ERROR, 0 WARN`)**.

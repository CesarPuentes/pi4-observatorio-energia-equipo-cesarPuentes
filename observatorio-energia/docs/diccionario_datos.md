# Diccionario de Datos – Capa Oro (`data/observatorio.duckdb`)

> **Proyecto Integrado IV – Observatorio Energía y Clima Colombia (2026-2)**
> Catálogo técnico de las **12 tablas del esquema estrella** (`7 dimensiones` y `5 tablas de hechos` en `dbt/models/marts/`) materializadas con **dbt** en `data/observatorio.duckdb`.

---

## 1. Tablas de Dimensiones (`dbt/models/marts/dim_*.sql`)

### 1.1 `dim_mes` (45 filas — Meses con ventas 2023 a 2026)

| Columna | Tipo de dato (DuckDB) | Rol | Descripción | Origen en Capa Plata (`staging`) |
|---|---|---|---|---|
| `mes_id` | `INTEGER` | **PK** | Identificador numérico del mes en formato `AAAAMM` (`202301`..`202609`). | `stg_ventas.periodo` (`replace(periodo, '-', '')`) |
| `periodo` | `VARCHAR` | Atributo | Cadena del periodo mensual en formato `AAAA-MM`. | `stg_ventas.periodo` |
| `anio` | `INTEGER` | Atributo | Año calendario (`2023` a `2026`). | `stg_ventas.periodo` (`left(periodo, 4)`) |
| `mes` | `INTEGER` | Atributo | Número de mes (`1` a `12`). | `stg_ventas.periodo` (`right(periodo, 2)`) |
| `trimestre` | `INTEGER` | Atributo | Trimestre del año (`1` a `4`). | Calculado `(mes + 2) // 3` |
| `oni` | `DOUBLE` | Atributo | Anomalía térmica del Pacífico ecuatorial (*Oceanic Niño Index*, `°C`). | `stg_noaa_oni.oni` |
| `fase_enso` | `VARCHAR` | Atributo | Fase climática (`'El Niño'`, `'La Niña'`, `'Neutral'`). | `stg_noaa_oni.fase_enso` |

---

### 1.2 `dim_fecha` (1,461 filas — Cobertura: `2023-01-01` a `2026-12-31`)

| Columna | Tipo de dato (DuckDB) | Rol | Descripción | Origen en Capa Plata (`staging`) |
|---|---|---|---|---|
| `fecha` | `DATE` | **PK** | Fecha calendario diaria (`YYYY-MM-DD`). | `generate_series('2023-01-01', '2026-12-31', 1 day)` |
| `fecha_id` | `INTEGER` | Atributo | Llave entera en formato `AAAAMMDD` (`20230101`). | Derivado de `fecha` |
| `mes_id` | `INTEGER` | Atributo | Llave mensual en formato `AAAAMM` (`202301`). | Derivado de `fecha` |
| `periodo` | `VARCHAR` | Atributo | Cadena `AAAA-MM` para cruce mensual. | Derivado de `fecha` |
| `anio` | `INTEGER` | Atributo | Año calendario (`2023` a `2026`). | `EXTRACT(YEAR FROM fecha)` |
| `trimestre` | `INTEGER` | Atributo | Trimestre calendario (`1` a `4`). | `EXTRACT(QUARTER FROM fecha)` |
| `mes` | `INTEGER` | Atributo | Mes del año (`1` a `12`). | `EXTRACT(MONTH FROM fecha)` |
| `nombre_mes` | `VARCHAR` | Atributo | Nombre del mes en español (`Enero`..`Diciembre`). | Derivado de `mes` |
| `dia_mes` | `INTEGER` | Atributo | Día del mes (`1` a `31`). | `EXTRACT(DAY FROM fecha)` |
| `dia_semana_iso` | `INTEGER` | Atributo | Día de la semana ISO (`1` = Lunes .. `7` = Domingo). | `EXTRACT(ISODOW FROM fecha)` |
| `nombre_dia_semana` | `VARCHAR` | Atributo | Nombre del día de la semana en español (`Lunes`..`Domingo`). | Derivado de `dia_semana_iso` |
| `es_fin_de_semana` | `BOOLEAN` | Atributo | `TRUE` si es sábado o domingo (`dia_semana_iso IN (6, 7)`). | Derivado de `dia_semana_iso` |
| `trimestre_movil_oni` | `VARCHAR` | Atributo | Trimestre móvil de la NOAA asignado a ese mes (`DJF`..`NDJ`). | `stg_noaa_oni.trimestre_movil` |
| `oni` | `DOUBLE` | Atributo | Valor del índice ONI (`°C`) del mes correspondiente. | `stg_noaa_oni.oni` |
| `fase_enso` | `VARCHAR` | Atributo | Fase del fenómeno ENSO (`'El Niño'`, `'La Niña'`, `'Neutral'`). | `stg_noaa_oni.fase_enso` |

---

### 1.3 `dim_hora` (24 filas — Horas `1` a `24`)

| Columna | Tipo de dato (DuckDB) | Rol | Descripción | Origen en Capa Plata (`staging`) |
|---|---|---|---|---|
| `hora` | `INTEGER` | **PK** | Hora operativa del SIN (`1` a `24`, correspondiente a `Hour01..Hour24` de XM). | `generate_series(1, 24)` |
| `franja_horaria` | `VARCHAR` | Atributo | Etiqueta del intervalo horario (`00:00 - 01:00` .. `23:00 - 24:00`). | Derivado de `hora` |
| `periodo_dia` | `VARCHAR` | Atributo | Bloque del día (`Madrugada`, `Mañana`, `Tarde`, `Noche`). | Derivado de `hora` |
| `tipo_franja_demanda` | `VARCHAR` | Atributo | Clasificación tarifaria/operativa (`Valle` 1–5, `Pico` 19–22, `Intermedia` resto). | Regla de negocio del SIN |
| `es_horario_solar` | `BOOLEAN` | Atributo | `TRUE` entre las horas `7` y `18` (ventana de radiación solar). | Derivado de `hora` |

---

### 1.4 `dim_municipio` (1,122 filas — Catálogo oficial DANE DIVIPOLA)

| Columna | Tipo de dato (DuckDB) | Rol | Descripción | Origen en Capa Plata (`staging`) |
|---|---|---|---|---|
| `municipio_id` | `VARCHAR` | **PK** | Código oficial DANE DIVIPOLA de 5 dígitos (`05001` = Medellín). | `stg_divipola.cod_mpio` |
| `cod_mpio` | `VARCHAR` | Atributo | Alias del código DANE DIVIPOLA de 5 dígitos (`05001`). | `stg_divipola.cod_mpio` |
| `municipio` | `VARCHAR` | Atributo | Nombre oficial del municipio en mayúsculas. | `stg_divipola.municipio` |
| `cod_dpto` | `VARCHAR` | Atributo | Código DANE del departamento (`05` = Antioquia). | `stg_divipola.cod_dpto` |
| `departamento` | `VARCHAR` | Atributo | Nombre oficial del departamento. | `stg_divipola.departamento` |
| `tipo_municipio` | `VARCHAR` | Atributo | Categoría DANE (`Municipio`, `Isla`, `Área no municipalizada`). | `stg_divipola.tipo_municipio` |
| `latitud` | `DOUBLE` | Atributo | Latitud geográfica en grados decimales (`float64`). | `stg_divipola.latitud` |
| `longitud` | `DOUBLE` | Atributo | Longitud geográfica en grados decimales (`float64`). | `stg_divipola.longitud` |

---

### 1.5 `dim_segmento` (4 filas — Segmentos de cliente de EnerAndes)

| Columna | Tipo de dato (DuckDB) | Rol | Descripción | Origen en Capa Plata (`staging`) |
|---|---|---|---|---|
| `segmento_id` | `BIGINT` | **PK** | Llave sustituta secuencial (`1` a `4`) ordenada alfabéticamente. | `row_number() over (order by segmento)` |
| `segmento` | `VARCHAR` | Atributo | Segmento de cliente (`Comercial`, `Industrial`, `No informado`, `Residencial`). | `stg_ventas.segmento` |

---

### 1.6 `dim_recurso` (2,501 filas — Catálogo de plantas generadoras del SIN)

| Columna | Tipo de dato (DuckDB) | Rol | Descripción | Origen en Capa Plata (`staging`) |
|---|---|---|---|---|
| `codigo_recurso` | `VARCHAR` | **PK** | Código SIC del recurso de generación en XM (ej. `2QBW` = Guatapé). | `stg_xm_listado_recursos.codigo_recurso` |
| `nombre_recurso` | `VARCHAR` | Atributo | Nombre comercial de la planta o unidad generadora. | `stg_xm_listado_recursos.nombre_recurso` |
| `tipo_generacion` | `VARCHAR` | Atributo | Tecnología (`HIDRAULICA`, `TERMICA`, `SOLAR`, `EOLICA`, `COGENERADOR`, `NO ESPECIFICADO`). | `stg_xm_listado_recursos.tipo_generacion` |
| `fuente_energia` | `VARCHAR` | Atributo | Combustible o recurso primario (`AGUA`, `GAS`, `CARBON`, `RAD SOLAR`, etc.). | `stg_xm_listado_recursos.fuente_energia` |
| `tipo_despacho` | `VARCHAR` | Atributo | Condición de despacho (`DESPACHADO CENTRALMENTE` / `NO DESPACHADO CENTRALMENTE`). | `stg_xm_listado_recursos.tipo_despacho` |
| `tipo_recurso` | `VARCHAR` | Atributo | Clasificación regulatoria (`NORMAL`, `AUTOGENERADOR`, `MENOR`, `GD`, `HISTORICO`). | `stg_xm_listado_recursos.tipo_recurso` |
| `codigo_agente` | `VARCHAR` | Atributo | Código SIC de la empresa operadora en XM. | `stg_xm_listado_recursos.codigo_agente` |
| `fecha_operacion` | `DATE` | Atributo | Fecha de entrada en operación comercial. | `stg_xm_listado_recursos.fecha_operacion` |
| `estado` | `VARCHAR` | Atributo | Estado del recurso (`OPERACION`, `PRUEBAS`, `INACTIVO`, `HISTORICO`). | `stg_xm_listado_recursos.estado` |
| `es_renovable` | `BOOLEAN` | Atributo | `TRUE` si `tipo_generacion` es `HIDRAULICA`, `SOLAR` o `EOLICA`. | Derivado de `tipo_generacion` |

---

### 1.7 `dim_estacion` (73 filas — Estaciones meteorológicas del IDEAM en Antioquia)

| Columna | Tipo de dato (DuckDB) | Rol | Descripción | Origen en Capa Plata (`staging`) |
|---|---|---|---|---|
| `codigo_estacion` | `VARCHAR` | **PK** | Código oficial de la estación hidrometeorológica del IDEAM. | `stg_ideam_precipitacion` ∪ `stg_ideam_temperatura` |
| `nombre_estacion` | `VARCHAR` | Atributo | Nombre oficial de la estación del IDEAM. | `stg_ideam_precipitacion` ∪ `stg_ideam_temperatura` |
| `municipio_id` | `VARCHAR` | **FK** | Código DANE DIVIPOLA (`dim_municipio.municipio_id`). | `stg_ideam_*.cod_mpio` |
| `cod_mpio` | `VARCHAR` | Atributo | Código DANE DIVIPOLA de 5 dígitos (`05xxx`). | `stg_ideam_*.cod_mpio` |
| `municipio` | `VARCHAR` | Atributo | Nombre oficial del municipio de Antioquia. | `stg_ideam_*.municipio` |
| `latitud` | `DOUBLE` | Atributo | Latitud geográfica de la estación. | `stg_ideam_*.latitud` |
| `longitud` | `DOUBLE` | Atributo | Longitud geográfica de la estación. | `stg_ideam_*.longitud` |
| `mide_precipitacion` | `BOOLEAN` | Atributo | `TRUE` si reporta precipitación diaria. | Derivado en `dim_estacion.sql` |
| `mide_temperatura` | `BOOLEAN` | Atributo | `TRUE` si reporta temperatura diaria. | Derivado en `dim_estacion.sql` |

---

## 2. Tablas de Hechos (`dbt/models/marts/fact_*.sql`)

### 2.1 `fact_ventas_mensual` (4,007 filas — Ventas de EnerAndes `2023` a `2026`)

| Columna | Tipo de dato (DuckDB) | Rol | Descripción | Origen en Capa Plata (`staging`) |
|---|---|---|---|---|
| `venta_id` | `VARCHAR` | **PK** | Llave única compuesta (`periodo\|divipola\|segmento_id\|tipo_compra`). | Derivado en `fact_ventas_mensual.sql` |
| `mes_id` | `INTEGER` | **FK** | Llave foránea hacia `dim_mes.mes_id` (`AAAAMM`). | `stg_ventas.periodo` |
| `fecha` | `DATE` | **FK** | Primer día del mes (`YYYY-MM-01`), llave foránea hacia `dim_fecha.fecha`. | `stg_ventas.periodo \|\| '-01'` |
| `municipio_id` | `VARCHAR` | **FK** | Código DIVIPOLA (`05xxx`), llave foránea hacia `dim_municipio.municipio_id`. | `stg_ventas.divipola` |
| `cod_mpio` | `VARCHAR` | Atributo | Alias del código DIVIPOLA (`05xxx`). | `stg_ventas.divipola` |
| `segmento_id` | `BIGINT` | **FK** | Llave foránea hacia `dim_segmento.segmento_id`. | `dim_segmento.segmento_id` |
| `tipo_compra` | `VARCHAR` | Atributo | Modalidad de compra (`'Bolsa'` o `'Contrato'`). | `stg_ventas.tipo_compra` |
| `energia_kwh` | `DOUBLE` | Medida | Energía eléctrica vendida en el mes, unificada en `kWh`. | `stg_ventas.energia_kwh` |
| `valor_cop` | `DOUBLE` | Medida | Valor facturado en pesos colombianos (`COP`; admite `NULL` en las 28 filas sin valor). | `stg_ventas.valor_cop` |
| `clientes` | `INTEGER` | Medida | Número de clientes activos facturados (medida semiaditiva). | `stg_ventas.clientes` |
| `precio_unitario_cop_kwh` | `DOUBLE` | Medida | Tarifa media implícita (`valor_cop / energia_kwh`). | Calculado en `fact_ventas_mensual.sql` |

---

### 2.2 `fact_mercado_horario` (24,096 filas — Precio y demanda horaria del SIN)

| Columna | Tipo de dato (DuckDB) | Rol | Descripción | Origen en Capa Plata (`staging`) |
|---|---|---|---|---|
| `mercado_horario_id` | `VARCHAR` | **PK** | Llave única compuesta (`YYYY-MM-DD\|HH`). | Derivado en `fact_mercado_horario.sql` |
| `fecha` | `DATE` | **FK** | Fecha operativa (`dim_fecha.fecha`). | `stg_xm_precio_bolsa.fecha` |
| `hora` | `INTEGER` | **FK** | Hora del día `1..24` (`dim_hora.hora`). | `stg_xm_precio_bolsa.hora` |
| `precio_bolsa_cop_kwh` | `DOUBLE` | Medida | Precio de bolsa nacional en `COP/kWh` (`PrecBolsNaci`). | `stg_xm_precio_bolsa.precio_bolsa_cop_kwh` |
| `demanda_real_kwh` | `DOUBLE` | Medida | Demanda real horaria del SIN en `kWh` (`DemaReal`). | `stg_xm_demanda.demanda_real_kwh` |
| `demanda_real_mwh` | `DOUBLE` | Medida | Demanda real horaria del SIN expresada en `MWh` (`demanda_real_kwh / 1000`). | Calculado en `fact_mercado_horario.sql` |
| `costo_horario_bolsa_cop` | `DOUBLE` | Medida | Valorización horaria de la demanda a precio de bolsa (`COP`). | `precio_bolsa_cop_kwh * demanda_real_kwh` |

---

### 2.3 `fact_generacion_recurso` (5,935,449 filas — Generación horaria por planta)

| Columna | Tipo de dato (DuckDB) | Rol | Descripción | Origen en Capa Plata (`staging`) |
|---|---|---|---|---|
| `fecha` | `DATE` | **FK** | Fecha operativa (`dim_fecha.fecha`). | `stg_xm_generacion_recurso.fecha` |
| `hora` | `INTEGER` | **FK** | Hora del día `1..24` (`dim_hora.hora`). | `stg_xm_generacion_recurso.hora` |
| `codigo_recurso` | `VARCHAR` | **FK** | Código SIC de la planta generadora (`dim_recurso.codigo_recurso`). | `stg_xm_generacion_recurso.codigo_recurso` |
| `generacion_kwh` | `DOUBLE` | Medida | Generación neta horaria inyectada al SIN en `kWh` (`Gene`). | `stg_xm_generacion_recurso.generacion_kwh` |

---

### 2.4 `fact_hidrologia_diaria` (1,004 filas — Embalses y aportes diarios del SIN)

| Columna | Tipo de dato (DuckDB) | Rol | Descripción | Origen en Capa Plata (`staging`) |
|---|---|---|---|---|
| `fecha` | `DATE` | **PK / FK** | Fecha calendario diaria (`dim_fecha.fecha`). | `stg_xm_embalses.fecha` |
| `volumen_util_pct` | `DOUBLE` | Medida | Nivel diario de volumen útil de los embalses del SIN (`0..100 %`). | `stg_xm_embalses.volumen_util_pct` |
| `aportes_energia_kwh` | `DOUBLE` | Medida | Aportes hídricos diarios del SIN expresados en `kWh` (`AporEner`). | `stg_xm_aportes.aportes_energia_kwh` |
| `aportes_energia_gwh` | `DOUBLE` | Medida | Aportes hídricos diarios expresados en `GWh` (`aportes_energia_kwh / 1e6`). | Calculado en `fact_hidrologia_diaria.sql` |

---

### 2.5 `fact_clima_diario` (30,271 filas — Precipitación y temperatura diaria en Antioquia)

| Columna | Tipo de dato (DuckDB) | Rol | Descripción | Origen en Capa Plata (`staging`) |
|---|---|---|---|---|
| `clima_diario_id` | `VARCHAR` | **PK** | Llave única compuesta (`YYYY-MM-DD\|codigo_estacion`). | Derivado en `fact_clima_diario.sql` |
| `fecha` | `DATE` | **FK** | Fecha de observación (`dim_fecha.fecha`). | `stg_ideam_precipitacion.fecha` / `stg_ideam_temperatura.fecha` |
| `codigo_estacion` | `VARCHAR` | **FK** | Estación meteorológica (`dim_estacion.codigo_estacion`). | `stg_ideam_*.codigo_estacion` |
| `municipio_id` | `VARCHAR` | **FK** | Municipio de Antioquia (`dim_municipio.municipio_id`). | `stg_ideam_*.cod_mpio` |
| `cod_mpio` | `VARCHAR` | Atributo | Alias del código DANE DIVIPOLA (`05xxx`). | `stg_ideam_*.cod_mpio` |
| `precipitacion_mm` | `DOUBLE` | Medida | Lluvia acumulada diaria en `mm` (rango validado `[0, 500]`). | `stg_ideam_precipitacion.precipitacion_mm` |
| `temp_media_c` | `DOUBLE` | Medida | Temperatura media diaria del aire en `°C`. | `stg_ideam_temperatura.temp_media_c` |
| `temp_min_c` | `DOUBLE` | Medida | Temperatura mínima diaria del aire en `°C`. | `stg_ideam_temperatura.temp_min_c` |
| `temp_max_c` | `DOUBLE` | Medida | Temperatura máxima diaria del aire en `°C`. | `stg_ideam_temperatura.temp_max_c` |

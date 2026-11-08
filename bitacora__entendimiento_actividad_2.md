# Bitácora de Entendimiento – Calidad de Datos y Modelo Dimensional (Actividad 2 / EA2)

## 1. Contexto del Problema y Evolución en la Evidencia 2 (EA2)

- **Punto de partida (EA1 – Capa Bronce + Clase de los días 26 oct y 4 nov):**
  - En la Evidencia 1 se construyó la ingesta automatizada hacia `data/bronze/` de **5 proveedores de datos** (**NOAA**, **IDEAM**, **XM**, **EnerAndes** y **DANE DIVIPOLA**), preservando **14 archivos Parquet crudos** como texto (`dtype=str`) junto con columnas de linaje (`_fuente`, `_origen`, `_extraido_en`).
  - En las sesiones de clase (`04_Clase_26_oct_Calidad_Modelo` y `04_Clase_26_oct_4_nov_Calidad_Modelo`) se construyó la base del pipeline para **1 sola hoja (`2023`)** del Excel de EnerAndes ([`src/silver/enerandes.py`](observatorio-energia/src/silver/enerandes.py), [`src/quality/esquemas.py`](observatorio-energia/src/quality/esquemas.py), `7` pruebas en [`tests/test_limpieza.py`](observatorio-energia/tests/test_limpieza.py) y el esqueleto inicial de [`dbt/`](observatorio-energia/dbt/) con `stg_ventas`, `dim_mes`, `dim_municipio`, `dim_segmento` y `fact_ventas_mensual` sobre `data/observatorio.duckdb`).
- **Problema a resolver en la EA2:** Los datos completos en la Capa Bronce **no se pueden cruzar ni agregar directamente** porque las hojas `2024`, `2025` y `2026` de EnerAndes y las otras 4 fuentes (XM, IDEAM, NOAA y DIVIPOLA) contienen ruido estructural (títulos, notas y filas `TOTAL` intercaladas), tipos en texto, `4` formatos de fecha incompatibles (`2024-03`, `mar-24`/`apr-24`, `03/2024`, `01/03/2026`), mezcla de unidades (`kWh` y `MWh`, factor `1,000x`), `32` variantes ortográficas de municipios, `120` duplicados exactos, valores nulos/negativos, lecturas extremas de sensores meteorológicos (`> 500 mm/día`), formato ancho en XM (`Hour01..Hour24`) y granularidad trimestral móvil en NOAA (`DJF..NDJ`).
- **Objetivo del software en la EA2:**
  1. **Capa Plata (`src/silver/` → `data/silver/*.parquet`):** Limpiar y estandarizar programáticamente las 5 fuentes en Python siguiendo las convenciones de la clase, aislar las filas incorregibles en archivos de **cuarentena** (`*_cuarentena.parquet`), medir cada problema **antes y después** en un reporte automático ([`docs/reporte_calidad.md`](observatorio-energia/docs/reporte_calidad.md)) y validar contratos estrictos con **Pandera** ([`src/quality/esquemas.py`](observatorio-energia/src/quality/esquemas.py)).
  2. **Capa Oro (`dbt/` → `data/observatorio.duckdb`):** Modelar un **esquema estrella (Kimball)** en **dbt + DuckDB** separado en `dbt/models/staging/` (**11 vistas `stg_*`**) y `dbt/models/marts/` (**7 dimensiones** y **5 tablas de hechos**), con grano explícito y **82 pruebas automáticas de integridad** (`unique`, `not_null`, `relationships`), alcanzando `PASS=105 WARN=0 ERROR=0` en `dbt build`.

---

## 2. Mapa de Transformación por Fuente (De Bronce a Plata y Oro)

1. **DANE – DIVIPOLA (`dane_divipola`):**
   - **Bronce:** `1,122` municipios como texto; coordenadas `latitud` y `longitud` con **coma decimal** (`6,246631`).
   - **Plata (`data/silver/dane_divipola.parquet`):** Reemplazo de `,` por `.`, conversión a `float64`, validación de rangos geográficos de Colombia y unicidad de `cod_mpio` (`5` dígitos).
   - **Oro (`stg_divipola` → `dim_municipio`):** Dimensión geográfica conformada (`1,122` filas) con `divipola` / `cod_mpio` y subregiones de Antioquia (`Valle de Aburrá`, `Oriente`, `Urabá`, `Bajo Cauca`, etc.) para cruzar ventas de EnerAndes y estaciones del IDEAM sin depender de nombres escritos a mano.

2. **EnerAndes S.A.S. E.S.P. (`enerandes_ventas_2023..2026`):**
   - **Bronce:** `4` archivos Parquet (uno por hoja del Excel `2023`–`2026`, `4,184` filas brutas en total).
   - **Plata (`data/silver/enerandes_ventas.parquet` y `enerandes_cuarentena.parquet`):**
     - Eliminación de **14 filas no transaccionales** (títulos superiores en hojas `2025`/`2026`, encabezados desplazados y filas `TOTAL`) → `4,170` filas.
     - Unificación de nombres de columnas entre hojas (`periodo`/`mes`/`fecha_mes`, `kwh`/`consumo`/`energia_vendida`, `valor`/`facturacion_cop`).
     - Estandarización de **4 formatos de fecha** (`YYYY-MM`, `MM/YYYY`, `Mon-YY` en español e inglés como `mar-24`/`apr-24`, y `DD/MM/YYYY` en hoja `2026` donde `01/03/2026` es marzo) al formato `YYYY-MM` en `periodo` y primer día del mes (`YYYY-MM-01`) en `fecha`.
     - Conversión de energía reportada en `MWh` (`347` filas en la hoja `2024`) a `kWh` ($\times 1{,}000$).
     - Homologación de **32 variantes** de nombres de municipios contra `divipola` / `cod_mpio` oficial del DANE (`20` municipios de Antioquia, `100 %` mapeados).
     - Eliminación de **120 duplicados** por `(periodo, divipola, segmento, tipo_compra)` → `4,050` filas únicas.
     - Siguiendo las reglas exactas de la clase (`04_Clase_26_oct_4_nov_Calidad_Modelo`):
       - Las **28 filas sin `segmento`** se conservan asignando `segmento = 'No informado'`.
       - Las **28 filas sin `valor_cop`** se conservan con `valor_cop = NaN` (`nullable=True` en `ESQUEMA_VENTAS`).
       - Solo las **43 filas con `energia_kwh` vacía (`25`) o negativa (`18`)** se separan hacia `enerandes_cuarentena.parquet` con su columna `motivo`, dejando **4,007 filas limpias** en `enerandes_ventas.parquet`.
   - **Oro (`stg_ventas` → `fact_ventas_mensual`, `dim_mes`, `dim_segmento`):** Tabla de hechos mensual (`4,007` filas) al grano `periodo × divipola × segmento_id`, manteniendo las columnas de la clase (`periodo`, `divipola`, `segmento_id`, `energia_kwh`, `valor_cop`, `clientes`, `precio_medio_kwh`) más los alias analíticos para consultas cruzadas.

3. **XM S.A. E.S.P. – Sinergox (`xm_*`):**
   - **Bronce:** `3` tablas horarias en formato ancho (`Hour01..Hour24` como texto) y `3` tablas diarias/catálogo.
   - **Plata (`data/silver/xm_*.parquet`):**
     - Despivoteo (`melt`) de `24` columnas horarias a formato largo (`fecha`, `hora` `1..24`, valor numérico `float64`): `xm_precio_bolsa.parquet` (`24,096` filas), `xm_demanda.parquet` (`24,096` filas) y `xm_generacion_recurso.parquet` (`5,935,449` filas limpias tras descartar `2,472,918` celdas horarias vacías de plantas sin generación nocturna).
     - Series diarias tipadas: `xm_embalses.parquet` (`1,004` días, escalado de `0..1` a porcentaje `0..100 %`) y `xm_aportes.parquet` (`1,004` días).
     - Catálogo `xm_listado_recursos.parquet` deduplicado (`2,493` → `2,491` códigos activos tras eliminar duplicados en `5J8H` y `5PUN`) más **10 códigos de plantas históricas** presentes en la generación 2024–2025, totalizando **2,501 recursos únicos**.
   - **Oro (`stg_xm_*` → `fact_mercado_horario`, `fact_generacion_recurso`, `fact_hidrologia_diaria`, `dim_recurso`, `dim_hora`):** Hechos horarios y diarios conectados con dimensiones de recursos, horas y fechas.

4. **IDEAM (`ideam_precipitacion_diaria`, `ideam_temperatura_diaria`):**
   - **Bronce:** `29,804` filas de precipitación y `17,349` de temperatura en texto.
   - **Plata (`data/silver/ideam_*.parquet`):** Tipado de fechas y números, cruce de cada estación con su `cod_mpio` DIVIPOLA (`29,797` filas en `ideam_precipitacion.parquet` y `17,349` en `ideam_temperatura.parquet`) y aislamiento en `ideam_cuarentena.parquet` de **7 lecturas físicamente imposibles** (`precipitacion_mm > 500 mm/día`, descargas acumuladas de sensor de hasta `3,081.8 mm/día`).
   - **Oro (`stg_ideam_*` → `fact_clima_diario` y `dim_estacion`):** `30,271` registros estación-día (`FULL OUTER JOIN` de lluvia y temperatura) y catálogo de `73` estaciones meteorológicas en Antioquia.

5. **NOAA (`noaa_oni`):**
   - **Bronce:** `920` trimestres móviles desde 1950 (`YR`, `SEAS`, `ANOM` como texto).
   - **Plata (`data/silver/noaa_oni.parquet`):** Asignación de cada trimestre móvil a su **mes central** (`DJF → 1`, `JFM → 2`, ..., `NDJ → 12`), construcción de `fecha = YYYY-MM-01` (`920` meses) y clasificación `fase_enso`:
     - `'El Niño'` si $\text{oni} \ge 0.5$ (`272` meses)
     - `'La Niña'` si $\text{oni} \le -0.5$ (`248` meses)
     - `'Neutral'` si $-0.5 < \text{oni} < 0.5$ (`400` meses)
   - **Oro (`stg_noaa_oni` → `dim_mes` y `dim_fecha`):** Integrado tanto en `dim_mes` (`45` periodos mensuales) como en `dim_fecha` (`1,461` días entre `2023-01-01` y `2026-12-31`) para cruzar cualquier hecho diario, horario o mensual con la fase ENSO.

---

## 3. Arquitectura de Datos e Ingeniería (Versión Completa Medallion)

### Estado de la Arquitectura Medallion
- **🥉 Capa Bronce (`data/bronze/`):** Datos crudos inmutables en Parquet (`dtype=str`) con metadatos de linaje.
- **🥈 Capa Plata (`data/silver/`):**
  - **11 tablas limpias en Parquet:** Tipadas (`date`, `int64`, `float64`, `str`), deduplicadas, con unidades estandarizadas y llaves foráneas homologadas.
  - **2 tablas de cuarentena en Parquet (`enerandes_cuarentena.parquet` e `ideam_cuarentena.parquet`):** Conservan las filas inválidas (`43` de EnerAndes y `7` de IDEAM) con su `motivo` / `motivo_cuarentena` para auditoría, cumpliendo el principio de **no borrar evidencia silenciosamente**.
  - **Validación por contrato (`Pandera`):** Ningún archivo Parquet se escribe en `data/silver/` sin pasar antes por su `DataFrameSchema` en [`src/quality/esquemas.py`](observatorio-energia/src/quality/esquemas.py).
- **🥇 Capa Oro (`data/observatorio.duckdb`):**
  - Base de datos analítica **DuckDB** construida con **dbt (`dbt-duckdb`)**.
  - Dividida siguiendo la arquitectura de la clase en:
    - **`dbt/models/staging/` (`+materialized: view`):** 11 vistas (`stg_ventas`, `stg_xm_*`, `stg_ideam_*`, `stg_noaa_oni`, `stg_divipola`) sobre `source('plata', ...)` definido en [`dbt/models/staging/sources.yml`](observatorio-energia/dbt/models/staging/sources.yml).
    - **`dbt/models/marts/` (`+materialized: table`):** **7 dimensiones** (`dim_mes`, `dim_fecha`, `dim_hora`, `dim_municipio`, `dim_segmento`, `dim_recurso`, `dim_estacion`) y **5 tablas de hechos** (`fact_ventas_mensual`, `fact_mercado_horario`, `fact_generacion_recurso`, `fact_hidrologia_diaria`, `fact_clima_diario`).
  - Verificada automáticamente con **82 data tests de dbt** (`unique`, `not_null`, `relationships`), alcanzando `PASS=105 WARN=0 ERROR=0` (11 vistas + 12 tablas + 82 tests).

---

## 4. Desglose de la Actividad 2: ¿Por qué?, ¿Cómo? y ¿Para qué?

### Punto 1 · Limpiar el Excel de EnerAndes completo (Capa Plata)
- **¿Por qué?**
  1. El script hecho en clase procesaba únicamente la hoja `2023`, pero las hojas `2024`, `2025` y `2026` introducen errores distintos que rompen cualquier carga directa: títulos decorativos en las primeras filas (`2025` y `2026`), filas `TOTAL`, columnas con nombres diferentes (`periodo`/`mes`/`fecha_mes`, `kwh`/`consumo`/`energia_vendida`, `valor`/`facturacion_cop`), `4` formatos de fecha mezclados, `347` filas en `MWh` mezcladas con `kWh`, `32` formas de escribir los municipios, `120` duplicados, `28` sin segmento, `28` sin valor COP y `43` con energía vacía o negativa.
  2. Eliminar sin rastro las filas defectuosas impide auditar con el área comercial por qué faltan registros en el consolidado.
- **¿Cómo?**
  - Se amplió [`src/silver/enerandes.py`](observatorio-energia/src/silver/enerandes.py) conservando todas las funciones de la clase (`sin_tildes()`, `clave_municipio()`, `limpiar()`, `escribir_reporte()`, `main()`) y añadiendo soporte para recibir tanto 1 `DataFrame` (compatibilidad con los 7 tests de la clase) como la lista de las 4 hojas (`2023`–`2026`):
    1. `_limpiar_hoja()`: detecta y descarta las **14 filas parásitas** (títulos superiores en `2025` y `2026`, encabezados desplazados y filas `TOTAL`) y renombra las columnas de cada hoja al estándar `COLUMNAS_2023`.
    2. `normalizar_periodo()`: interpreta los 4 formatos (`YYYY-MM`, `MM/YYYY`, `Mon-YY` en español e inglés como `mar-24`/`apr-24`, y `DD/MM/YYYY` como `01/03/2026` donde el mes es marzo) y los convierte a `YYYY-MM`.
    3. Convierte las **347 filas en `MWh`** de la hoja `2024` a `kWh` (`× 1,000`) y homologa las **32 variantes** de municipio contra `MUNICIPIOS` / `ALIAS_MUNICIPIO` de Antioquia (`divipola` DANE).
    4. Deduplica las **120 filas repetidas**, rellena `segmento` vacío con `'No informado'` (`28` filas), conserva `valor_cop` vacío como `NaN` (`28` filas) y separa las **43 filas con `energia_kwh` vacía (`25`) o negativa (`18`)** en `data/silver/enerandes_cuarentena.parquet`.
- **¿Para qué?**
  - Consolidar `data/silver/enerandes_ventas.parquet` con **4,007 registros válidos** (`2023`–`2026`) validados por `ESQUEMA_VENTAS` de Pandera, más `data/silver/enerandes_cuarentena.parquet` (`43` filas) listo para auditoría.
- **Resumen y conclusión (en simple):**
  - *Qué se hizo:* Extendimos el limpiador de clase para unir las 4 hojas anuales del Excel de EnerAndes en una sola tabla limpia (`4,007` filas), corrigiendo fechas revueltas, pasando MWh a kWh, empatando los municipios con su código DANE, marcando segmentos faltantes como `'No informado'` y enviando las `43` filas con energía vacía o negativa a cuarentena.
  - *Por qué y para qué:* Porque si mezclábamos kWh con MWh o dejábamos filas `TOTAL` y consumos negativos, las ventas de EnerAndes quedarían distorsionadas; y al seguir el criterio de cuarentena de la clase, conservamos los registros donde sí hay energía válida y aislamos con motivo explícito los que no tienen energía confiable.

---

### Punto 2 · Limpiar las demás fuentes: XM, IDEAM, NOAA y Fuente Propia (Capa Plata)
- **¿Por qué?**
  1. **XM** entrega las métricas horarias en **formato ancho** (`Hour01..Hour24` como texto), lo que impide cruzar por hora o agregar por día en un modelo estrella; además, `xm_embalses` viene en fracción `0..1`, `xm_listado_recursos` tiene 2 códigos duplicados (`5J8H`, `5PUN`) y en `xm_generacion_recurso` aparecen `10` plantas históricas de 2024–2025 que ya no figuran en el listado de 2026.
  2. **IDEAM** trae fechas y valores como texto, carece del código `cod_mpio` en la tabla de lluvias/temperatura y presenta **7 lecturas anómalas** de entre `510 mm` y `3,081.8 mm` en un solo día (volcados acumulados de sensor).
  3. **NOAA** viene por trimestres móviles (`DJF`, `JFM`, ...) sin fecha mensual ni clasificación categórica del fenómeno ENSO.
  4. **DIVIPOLA (DANE)** usa coma decimal (`6,246631`) en sus coordenadas, lo que impide tratarlas como `float64`.
- **¿Cómo?**
  - **XM ([`src/silver/xm.py`](observatorio-energia/src/silver/xm.py)):** `despivotar_horario()` transforma `Hour01..Hour24` en filas `(fecha, hora, valor)` con `hora` entera `1..24` y `float64` para precio de bolsa (`24,096` filas), demanda (`24,096` filas) y generación por recurso (`5,935,449` filas válidas). En `limpiar_xm_listado_recursos()` se deduplica por `codigo_recurso` y se incorporan los `10` códigos históricos (`2,501` recursos únicos).
  - **IDEAM ([`src/silver/ideam.py`](observatorio-energia/src/silver/ideam.py)):** Convierte fechas y números, cruza el municipio de cada estación con `cod_mpio` de DIVIPOLA (`0` estaciones huérfanas) y envía las **7 lecturas `> 500 mm/día`** a `data/silver/ideam_cuarentena.parquet`.
  - **NOAA ([`src/silver/noaa.py`](observatorio-energia/src/silver/noaa.py)):** Mapea `MES_CENTRAL_TRIMESTRE` (`DJF → 1`, ..., `NDJ → 12`), construye `fecha = YYYY-MM-01` y clasifica `fase_enso` (`El Niño` $\ge 0.5$, `La Niña` $\le -0.5$, `Neutral` en otro caso).
  - **DIVIPOLA ([`src/silver/divipola.py`](observatorio-energia/src/silver/divipola.py)):** Reemplaza `,` por `.` en `latitud` y `longitud`, convierte a `float64` y normaliza nombres oficiales.
- **¿Para qué?**
  - Dejar las **11 tablas de Plata** estandarizadas en tipos nativos de Parquet y listas para ser consumidas por las vistas `stg_*` de `dbt`.
- **Resumen y conclusión (en simple):**
  - *Qué se hizo:* Pasamos las 24 columnas horarias de XM a filas individuales por hora, vinculamos las estaciones del IDEAM a su municipio DANE filtrando 7 lluvias imposibles a cuarentena, convertimos los trimestres de la NOAA en meses con su etiqueta (`El Niño`, `La Niña`, `Neutral`) y arreglamos las comas decimales de las coordenadas del DANE.
  - *Por qué y para qué:* Para que todas las fuentes hablen el mismo idioma (mismas fechas, mismos códigos de municipio y números reales) antes de construir el esquema estrella.

---

### Punto 3 · Validar la calidad con Pandera y probar las reglas con `pytest`
- **¿Por qué?**
  1. Limpiar datos sin validar contratos a la salida es riesgoso: si cambia una hoja del Excel o una respuesta de la API e introduce un tipo inválido o un valor fuera de rango, el error pasaría silenciosamente hasta romper el dashboard.
  2. Las funciones de limpieza deben probarse de forma aislada y rápida con datos sintéticos en memoria, conservando las 7 pruebas de la clase y agregando las pruebas del equipo.
- **¿Cómo?**
  - **Contratos Pandera ([`src/quality/esquemas.py`](observatorio-energia/src/quality/esquemas.py)):** Conserva intacto `ESQUEMA_VENTAS` de la clase y añade los esquemas para todas las demás tablas de Plata (`ESQUEMA_XM_*`, `ESQUEMA_IDEAM_*`, `ESQUEMA_NOAA_ONI`, `ESQUEMA_DANE_DIVIPOLA`).
  - **Pruebas unitarias ([`tests/test_limpieza.py`](observatorio-energia/tests/test_limpieza.py)):** Contiene **17 pruebas unitarias** (**7 de la clase** + **10 nuevas del equipo**), que sumadas a las **8 de extracción** en [`tests/test_pipeline.py`](observatorio-energia/tests/test_pipeline.py) totalizan **25 tests (`25 passed`)**, cubriendo:
    - Las 7 pruebas de clase (`test_municipio_con_tilde_y_variante`, `test_energia_negativa_va_a_cuarentena`, `test_energia_vacia_va_a_cuarentena`, `test_duplicado_se_elimina`, `test_segmento_vacio_queda_no_informado`, `test_esquema_rechaza_energia_negativa`, `test_esquema_rechaza_divipola_invalido`).
    - Las 10 pruebas nuevas del equipo (parseo de los 4 formatos de fecha de EnerAndes, conversión `MWh → kWh`, eliminación de títulos y filas `TOTAL`, despivoteo horario de XM, escalado de embalses y deduplicación de recursos XM, cuarentena de lluvia `> 500 mm/día` en IDEAM, asignación de mes central y `fase_enso` en NOAA, coma decimal en DIVIPOLA y validación Pandera).
- **¿Para qué?**
  - Garantizar que **ninguna tabla corrupta pueda guardarse en `data/silver/`** y que cualquier cambio en el código se verifique en **~1.5 segundos** ejecutando `pytest` (`25 passed`).
- **Resumen y conclusión (en simple):**
  - *Qué se hizo:* Mantuvimos el esquema y las 7 pruebas de la clase en `src/quality/esquemas.py` y `tests/test_limpieza.py`, y agregamos los esquemas de las demás fuentes y 10 pruebas nuevas para llegar a 25 tests en total.
  - *Por qué y para qué:* Para respetar al 100 % la base del profesor y al mismo tiempo verificar automáticamente todas las fuentes nuevas de la Actividad 2.

---

### Punto 4 · Escribir el reporte de calidad (`docs/reporte_calidad.md`)
- **¿Por qué?**
  - En ingeniería de datos se debe demostrar con cifras exactas **cuántos registros tenían cada problema antes de la regla y cuántos quedaron después**, documentando qué fue a cuarentena y por qué.
- **¿Cómo?**
  - [`src/quality/reporte.py`](observatorio-energia/src/quality/reporte.py) recopila las métricas de todos los módulos de `src/silver/` y genera automáticamente [`docs/reporte_calidad.md`](observatorio-energia/docs/reporte_calidad.md) con **23 reglas medidas** (superando el mínimo de 15 exigido) y el desglose completo de las 2 tablas de cuarentena (`43` en EnerAndes y `7` en IDEAM).
- **¿Para qué?**
  - Entregar trazabilidad numérica completa: en EnerAndes se documenta el paso exacto de `4,184` filas brutas → `-14` filas parásitas (`4,170`) → `-120` duplicados (`4,050`) → `-43` en cuarentena (`25` sin energía y `18` con energía negativa) = **`4,007` filas válidas**.
- **Resumen y conclusión (en simple):**
  - *Qué se hizo:* Automatizamos la generación de `docs/reporte_calidad.md` con una tabla de 23 reglas mostrando el "antes y después" de cada corrección y el detalle de las filas en cuarentena.
  - *Por qué y para qué:* Para tener una auditoría transparente con números reales de cada arreglo hecho sobre las 5 fuentes.

---

### Punto 5 · Construir el esquema estrella con `dbt` y DuckDB (Capa Oro)
- **¿Por qué?**
  - En la clase se estableció una arquitectura en `dbt` donde los archivos Parquet de `data/silver/` se declaran como `sources` (`source('plata', ...)`), se exponen primero como vistas ligeras en `staging` (`stg_*`) y luego se modelan en `marts` como tablas de dimensiones (`dim_*`) y tablas de hechos (`fact_*`) dentro de `data/observatorio.duckdb`.
- **¿Cómo?**
  - Se estructuró el proyecto [`dbt/`](observatorio-energia/dbt/dbt_project.yml) (`name: observatorio`, `profile: observatorio` hacia `data/observatorio.duckdb`) con:
    - **11 Vistas en `dbt/models/staging/` (`+materialized: view`):** `stg_ventas`, `stg_xm_precio_bolsa`, `stg_xm_demanda`, `stg_xm_generacion_recurso`, `stg_xm_embalses`, `stg_xm_aportes`, `stg_xm_listado_recursos`, `stg_ideam_precipitacion`, `stg_ideam_temperatura`, `stg_noaa_oni` y `stg_divipola`.
    - **7 Dimensiones en `dbt/models/marts/` (`+materialized: table`):**
      1. [`dim_mes.sql`](observatorio-energia/dbt/models/marts/dim_mes.sql) (`45` meses de EnerAndes con `periodo`, `anio`, `mes`, `trimestre`, `oni` y `fase_enso`).
      2. [`dim_fecha.sql`](observatorio-energia/dbt/models/marts/dim_fecha.sql) (`1,461` días `2023–2026` con atributos calendario e integración de `oni` y `fase_enso`).
      3. [`dim_hora.sql`](observatorio-energia/dbt/models/marts/dim_hora.sql) (`24` horas operativas `1..24`, franja horaria y franja de demanda `Valle`/`Intermedia`/`Pico`).
      4. [`dim_municipio.sql`](observatorio-energia/dbt/models/marts/dim_municipio.sql) (`1,122` municipios DIVIPOLA con `divipola` y `cod_mpio`, coordenadas y subregiones).
      5. [`dim_segmento.sql`](observatorio-energia/dbt/models/marts/dim_segmento.sql) (`8` combinaciones de `segmento` y `tipo_compra` con llave `segmento_id` / `segmento_key`).
      6. [`dim_recurso.sql`](observatorio-energia/dbt/models/marts/dim_recurso.sql) (`2,501` plantas/recursos del SIN con `tipo_generacion` y `es_renovable`).
      7. [`dim_estacion.sql`](observatorio-energia/dbt/models/marts/dim_estacion.sql) (`73` estaciones meteorológicas IDEAM vinculadas a `cod_mpio`).
    - **5 Tablas de Hechos en `dbt/models/marts/` (`+materialized: table`):**
      1. [`fact_ventas_mensual.sql`](observatorio-energia/dbt/models/marts/fact_ventas_mensual.sql) (`4,007` filas — grano: `1 fila por periodo × divipola × segmento_id`).
      2. [`fact_mercado_horario.sql`](observatorio-energia/dbt/models/marts/fact_mercado_horario.sql) (`24,096` filas — grano: `1 fila por fecha × hora`).
      3. [`fact_generacion_recurso.sql`](observatorio-energia/dbt/models/marts/fact_generacion_recurso.sql) (`5,935,449` filas — grano: `1 fila por fecha × hora × codigo_recurso`).
      4. [`fact_hidrologia_diaria.sql`](observatorio-energia/dbt/models/marts/fact_hidrologia_diaria.sql) (`1,004` filas — grano: `1 fila por fecha`).
      5. [`fact_clima_diario.sql`](observatorio-energia/dbt/models/marts/fact_clima_diario.sql) (`30,271` filas — grano: `1 fila por fecha × codigo_estacion`).
  - En [`dbt/models/marts/schema.yml`](observatorio-energia/dbt/models/marts/schema.yml) se declaró el **grano explícito** de cada modelo y se configuraron **82 pruebas de datos** (`unique`, `not_null` y `relationships`).
- **¿Para qué?**
  - Entregar una base analítica unificada (`data/observatorio.duckdb`) donde `dbt build` valida automáticamente que **todas las llaves primarias son únicas, no nulas y tienen 100 % de integridad referencial** (`PASS=105 WARN=0 ERROR=0`).
- **Resumen y conclusión (en simple):**
  - *Qué se hizo:* Construimos con `dbt` y `DuckDB` las 11 vistas `staging` y las 12 tablas `marts` (7 dimensiones y 5 tablas de hechos) siguiendo la estructura exacta de la clase, protegidas por 82 pruebas automáticas de integridad.
  - *Por qué y para qué:* Para organizar los datos limpios en una estructura estándar de Inteligencia de Negocios donde tanto las consultas `dbt show` de la clase como las 5 consultas analíticas del proyecto funcionen sin fricción.

---

### Punto 6 · Documentar el modelo y responder preguntas de negocio en Capa Oro
- **¿Por qué?**
  - Un modelo estrella sin documentación de su grano, su diccionario de columnas ni consultas de validación es difícil de usar para el equipo que construirá el dashboard en la EA3.
- **¿Cómo?**
  1. Se creó [`docs/modelo_dimensional.md`](observatorio-energia/docs/modelo_dimensional.md) con el diagrama **Mermaid (`erDiagram`)** del esquema estrella, la tabla de granos y el flujo `staging → marts`.
  2. Se creó [`docs/diccionario_datos.md`](observatorio-energia/docs/diccionario_datos.md) detallando las tablas de la Capa Oro (columna, tipo de dato SQL, descripción funcional y tabla/columna de origen en Plata).
  3. Se crearon **5 consultas SQL analíticas** en [`consultas/oro/`](observatorio-energia/consultas/oro/) ejecutables mediante `python -m src.consultar --solo-oro` y se documentaron sus resultados en [`README.md`](observatorio-energia/README.md):
     - [`01_enso_hidrologia_y_precio.sql`](observatorio-energia/consultas/oro/01_enso_hidrologia_y_precio.sql): demuestra cómo durante **El Niño** los aportes hídricos caen a `143.29 GWh/día` (vs. `228.26` en Neutral) y el precio promedio de bolsa casi se triplica (`663.0 COP/kWh` vs. `222.8 COP/kWh` en La Niña).
     - [`02_matriz_generacion_por_fase_enso.sql`](observatorio-energia/consultas/oro/02_matriz_generacion_por_fase_enso.sql): cuantifica la sustitución hidro-térmica (la generación térmica sube de `11.41 %` en La Niña a **`30.05 %`** en El Niño).
     - [`03_patron_horario_demanda_y_precio.sql`](observatorio-energia/consultas/oro/03_patron_horario_demanda_y_precio.sql): identifica la rampa crítica nocturna entre las **19:00 y 21:00 horas** (hora 20 alcanza el máximo de `10,909.2 MWh` y `658.9 COP/kWh`).
     - [`04_impacto_exposicion_bolsa_enerandes.sql`](observatorio-energia/consultas/oro/04_impacto_exposicion_bolsa_enerandes.sql): mide la exposición en bolsa (~`22.1 %` – `22.9 %` de la energía comercializada por EnerAndes) en los 10 municipios principales de Antioquia.
     - [`05_clima_antioquia_vs_ventas_municipios.sql`](observatorio-energia/consultas/oro/05_clima_antioquia_vs_ventas_municipios.sql): cruza mediante `dim_municipio` la lluvia, la temperatura media y la facturación eléctrica en los municipios con estación meteorológica del IDEAM.
- **¿Para qué?**
  - Comprobar con datos reales que el modelo estrella responde de extremo a extremo la cadena causal del reto (**ENSO → Clima en Antioquia → Embalses/Aportes → Generación Térmica → Precio de Bolsa → Exposición de EnerAndes**) y dejar lista la referencia técnica para la Entrega 3.
- **Resumen y conclusión (en simple):**
  - *Qué se hizo:* Documentamos el diagrama estrella y el diccionario de las tablas de Oro, y programamos 5 consultas SQL de negocio cuyos resultados quedaron publicados en el `README.md`.
  - *Por qué y para qué:* Para demostrar con cifras reales que nuestro modelo estrella funciona y facilitar el diseño del dashboard final.

---

### Puntos 7 y 8 · Reproducibilidad con un solo comando, Higiene de Git y Trabajo Colaborativo
- **¿Por qué?**
  1. Ejecutar manualmente 5 scripts de limpieza y luego comandos sueltos de `dbt` es propenso a errores humanos y de orden de ejecución.
  2. Subir `data/silver/` o `data/observatorio.duckdb` a GitHub viola las buenas prácticas de control de versiones.
- **¿Cómo?**
  1. Se construyó el orquestador [`src/transformar.py`](observatorio-energia/src/transformar.py) (`python -m src.transformar`), que ejecuta en secuencia:
     - Limpieza y validación Pandera de las 5 fuentes hacia `data/silver/*.parquet`.
     - Generación automática de `docs/reporte_calidad.md`.
     - Ejecución de `dbt build --project-dir dbt --profiles-dir dbt` desde la raíz del proyecto para materializar y probar las 11 vistas y 12 tablas en `data/observatorio.duckdb` (`PASS=105 WARN=0 ERROR=0`).
  2. Se actualizó [`.gitignore`](observatorio-energia/.gitignore) tal como en `PASO_A_PASO.md` para excluir `data/bronze/`, `data/silver/`, `dbt/target/`, `dbt/logs/`, `dbt/.user.yml` y `*.duckdb`.
  3. Se actualizó la bitácora individual en [`docs/bitacoras/puentes_cesar.md`](observatorio-energia/docs/bitacoras/puentes_cesar.md) con el registro completo de la EA2.
- **¿Para qué?**
  - Permitir que cualquier evaluador o integrante del equipo reconstruya desde cero tanto la Capa Plata como la Capa Oro y ejecute las 82 pruebas de `dbt` con un único comando reproducible (`python -m src.transformar`).
- **Resumen y conclusión (en simple):**
  - *Qué se hizo:* Creamos el comando único `python -m src.transformar` que limpia todas las fuentes, genera el reporte de calidad y construye y prueba la base de datos estrella en DuckDB en ~22 segundos, manteniendo el repositorio liviano en GitHub.
  - *Por qué y para qué:* Para que cualquier persona pueda reproducir toda la Evidencia 2 con una sola instrucción sin subir bases de datos pesadas al repositorio.

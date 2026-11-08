# Reporte de Calidad de Datos – Capa Plata (`data/silver/`)

> **Proyecto Integrado IV – Observatorio Energía y Clima Colombia (2026-2)**
> Reporte generado automáticamente por el pipeline de transformación (`python -m src.transformar`). Total de reglas evaluadas: **24 reglas** validadas con **Pandera** (`src/quality/esquemas.py`).

---

## 1. Resumen Ejecutivo por Fuente

| Fuente | Tablas en `data/silver/` | Reglas medidas | Filas limpias finales | Filas en cuarentena | Esquema Pandera |
|---|---|---:|---:|---:|---|
| **1. EnerAndes (Excel 2023–2026)** | `enerandes_ventas.parquet`, `enerandes_cuarentena.parquet` | 11 | 4,007 | 43 | ✅ `ESQUEMA_VENTAS` |
| **2. XM – Sinergox (API REST)** | `xm_precio_bolsa`, `xm_demanda`, `xm_generacion_recurso`, `xm_embalses`, `xm_aportes`, `xm_listado_recursos` | 5 | 5,988,144 | 0 | ✅ `ESQUEMA_XM_*` (6 esquemas) |
| **3. IDEAM (Socrata / SoQL)** | `ideam_precipitacion.parquet`, `ideam_temperatura.parquet`, `ideam_cuarentena.parquet` | 3 | 47,146 | 7 | ✅ `ESQUEMA_IDEAM_*` (2 esquemas) |
| **4. NOAA (Índice ONI)** | `noaa_oni.parquet` | 2 | 920 | 0 | ✅ `ESQUEMA_NOAA_ONI` |
| **5. DANE – DIVIPOLA (Fuente propia)** | `dane_divipola.parquet` | 2 | 1,122 | 0 | ✅ `ESQUEMA_DANE_DIVIPOLA` |
| **Total Capa Plata** | **13 archivos Parquet** | **24** | **6,041,339** | **50** | **100 % esquemas aprobados** |

---

## 2. Reglas de Calidad y Métricas Antes vs. Después por Fuente

### 2.1 Fuente 1: Excel Interno de EnerAndes (4 hojas: `2023` a `2026`)

| # | Tabla destino | Problema | Regla aplicada | Antes | Después |
|---:|---|---|---|---|---|
| R01 | `enerandes_ventas` | Titulos, notas y filas en blanco antes del encabezado (hojas 2025 y 2026) | Detectar fila de encabezado y descartar filas previas | 6 | 0 |
| R02 | `enerandes_ventas` | Encabezado guardado como una fila (con nombres distintos por hoja) | Usarlo como nombres de columna y unificar al estandar | 4 | 0 |
| R03 | `enerandes_ventas` | Filas de totales | Eliminarlas | 4 | 0 |
| R04 | `enerandes_ventas` | Filas duplicadas | Dejar una sola copia | 120 | 0 |
| R05 | `enerandes_ventas` | Fechas en formatos mixtos (mar-24, 03/2024 y DD/MM/AAAA en 2026) | Normalizar los 4 formatos al estandar AAAA-MM | 2626 | 0 |
| R06 | `enerandes_ventas` | Segmento escrito de varias formas | Unificar a 3 valores | 6 | 3 |
| R07 | `enerandes_ventas` | Segmento vacio | Marcarlo como 'No informado' | 28 | 0 |
| R08 | `enerandes_ventas` | Tipo de compra escrito de varias formas | Unificar a Bolsa y Contrato | 4 | 2 |
| R09 | `enerandes_ventas` | Municipio escrito de varias formas | Unificar con el codigo DIVIPOLA | 32 | 15 |
| R10 | `enerandes_ventas` | Energia expresada en MWh en la hoja 2024 (factor 1,000x) | Multiplicar MWh por 1,000 para unificar todo en kWh | 337 | 0 |
| R11 | `enerandes_ventas` | Energia vacia o negativa | Pasar la fila a cuarentena | 43 | 0 |
| R12 | `enerandes_ventas` | Valor facturado vacio | Dejarlo vacio y documentarlo | 28 | 28 |

### 2.2 Fuente 2: XM – Mercado de Energía Mayorista (`Sinergox`)

| # | Tabla destino | Problema | Regla aplicada | Antes | Después |
|---:|---|---|---|---|---|
| R13 | `xm_precio_bolsa` | Estructura ancha de 24 columnas horarias (`Hour01`..`Hour24`) almacenadas como texto (`str`) | Despivotar (`melt`) a una fila por `fecha` (`datetime64[ns]`) y `hora` (`1..24`, `int64`) con `precio_bolsa_cop_kwh` en `float64` | 1,004 filas x 24 columnas `str` | 24,096 filas horarias (`fecha`, `hora`) tipadas |
| R14 | `xm_demanda` | Estructura ancha de 24 columnas horarias (`Hour01`..`Hour24`) almacenadas como texto (`str`) | Despivotar (`melt`) a una fila por `fecha` y `hora` (`1..24`) con `demanda_real_kwh` en `float64 > 0` | 1,004 filas x 24 columnas `str` | 24,096 filas horarias (`fecha`, `hora`) tipadas |
| R15 | `xm_generacion_recurso` | Estructura ancha (`Hour01`..`Hour24` en texto) y 2.47 millones de celdas horarias vacías/nulas (plantas solares/térmicas en horas sin generación) | Despivotar a (`fecha`, `hora`, `codigo_recurso`), convertir a `float64` y filtrar celdas nulas o sin generación (`<= 0`) | 350,361 filas anchas (2,473,215 celdas horarias nulas) | 5,935,449 registros horarios válidos con 0 nulos |
| R16 | `xm_embalses / xm_aportes` | Fechas y métricas hidrológicas (`PorcVoluUtilDiar` en fracción `0..1` y `AporEner`) almacenadas como texto (`str`) | Tipar `fecha` a `datetime64[ns]`, escalar `volumen_util_pct` a porcentaje `[0, 100]` (`float64`) y convertir `aportes_energia_kwh` a `float64 > 0` | 1,004 + 1,004 filas en texto y fracción `0..1` | 1,004 + 1,004 filas diarias tipadas y en escala porcentual `0..100 %` |
| R17 | `xm_listado_recursos` | Registros duplicados en el catálogo (`5J8H`, `5PUN`), inconsistencia de mayúsculas (`Solar`/`SOLAR`, `Operacion`/`OPERACION`) y 10 códigos históricos de generación ausentes del corte actual | Eliminar duplicados por `codigo_recurso`, normalizar textos en mayúsculas e incorporar los recursos históricos (`estado = 'HISTORICO'`) para preservar integridad referencial | 2 duplicados, 6 tipos, 10 recursos huérfanos en generación | 0 duplicados, catálogo normalizado y 0 recursos huérfanos (2,501 plantas únicas) |

### 2.3 Fuente 3: IDEAM – Datos Hidrometeorológicos (`datos.gov.co`)

| # | Tabla destino | Problema | Regla aplicada | Antes | Después |
|---:|---|---|---|---|---|
| R18 | `ideam_precipitacion` | Fechas con sufijo de hora (`2025-01-01T00:00:00.000`), métricas en texto (`str`) y nombres de municipio sin código DANE (`SAN VICENTE` vs. `SAN VICENTE FERRER`) | Convertir `fecha` a `datetime64[ns]`, `precipitacion_mm`/`latitud`/`longitud` a `float64`, `n_obs` a `int64` y cruzar cada estación con `dane_divipola` (`cod_mpio`) | 29,804 filas con tipos `str` y 50 municipios sin `cod_mpio` | 29,797 filas tipadas y 100% vinculadas a `cod_mpio` de Antioquia |
| R19 | `ideam_precipitacion` | Valores extremos físicamente imposibles de precipitación diaria (`> 500 mm/día`, hasta `3,081.8 mm` por volcado acumulado de observaciones atrasadas) | Aislar en `data/silver/ideam_cuarentena.parquet` los registros con `precipitacion_mm > 500 mm` y validar rango `[0, 500]` con Pandera | 7 registros con precipitación diaria > 500 mm | 0 registros fuera de `[0, 500]` mm en `ideam_precipitacion` (7 en cuarentena) |
| R20 | `ideam_temperatura` | Temperaturas (`temp_media_c`, `temp_min_c`, `temp_max_c`) como texto con hasta 16 decimales de precisión flotante y estaciones sin `cod_mpio` | Convertir `fecha` a `datetime64[ns]`, redondear temperaturas a 2 decimales (`float64`), validar rangos térmicos y asignar `cod_mpio` oficial DIVIPOLA | 17,349 filas en texto (`str`) sin código de municipio DANE | 17,349 filas tipadas (`float64`) con `cod_mpio` validado en 37 municipios |

### 2.4 Fuente 4: NOAA – Índice Oceánico El Niño (`ONI`)

| # | Tabla destino | Problema | Regla aplicada | Antes | Después |
|---:|---|---|---|---|---|
| R21 | `noaa_oni` | Serie en trimestres móviles (`DJF`, `JFM`, …, `JAS`) y valores de temperatura/anomalía (`TOTAL`, `ANOM`) como texto (`str`) | Asignar cada trimestre móvil a su mes central (`DJF` → `1`, …, `NDJ` → `12`), construir `periodo` (`AAAA-MM`) y `fecha` (`YYYY-MM-01`) y convertir `total_c` y `oni` a `float` | 920 trimestres móviles en texto sin fecha calendario | 920 meses únicos con `periodo` (`AAAA-MM`), `fecha` y `oni` numérico |
| R22 | `noaa_oni` | Ausencia de clasificación categórica de la fase del fenómeno ENSO | Agregar `fase_enso`: `'El Niño'` si `oni >= 0.5`, `'La Niña'` si `oni <= -0.5` y `'Neutral'` en los demás casos | 0 filas con fase ENSO clasificada | 920 meses clasificados (El Niño: 234, La Niña: 238, Neutral: 448) |

### 2.5 Fuente 5 (Propia): DANE – Catálogo Oficial `DIVIPOLA`

| # | Tabla destino | Problema | Regla aplicada | Antes | Después |
|---:|---|---|---|---|---|
| R23 | `dane_divipola` | Coordenadas geográficas (`latitud` y `longitud`) almacenadas como texto con coma decimal (`,`) en lugar de punto (`.`) | Reemplazar `,` por `.` y convertir `latitud` y `longitud` a `float`, validando rangos de Colombia (`latitud` en [-5, 14], `longitud` en [-82, -66]) | 1,122 lat / 1,122 lon con coma decimal (`str`) | 0 con coma decimal (`float` válido en las 1,122 filas) |
| R24 | `dane_divipola` | Estandarización de códigos DANE (`cod_dpto`, `cod_mpio`), nombres oficiales y verificación de unicidad de `cod_mpio` | Formatear `cod_dpto` a 2 dígitos y `cod_mpio` a 5 dígitos, normalizar nombres en mayúsculas y garantizar llave única `cod_mpio` | 1,122 filas (0 duplicados) | 1,122 municipios únicos validados con Pandera |

---

## 3. Análisis Detallado de Filas en Cuarentena

Siguiendo la regla de oro de la Capa Plata vista en clase (**no inventar datos ni borrar filas malas sin dejar rastro**), los registros que no se pueden corregir con certeza se manejan así:
- **Segmento vacío (`28` filas):** se marca explícitamente como `'No informado'` (Regla 5 de la clase), conservando la energía y facturación en la tabla limpia.
- **Valor facturado vacío (`28` filas):** se deja vacío (`NaN`, permitido por `nullable=True` en `ESQUEMA_VENTAS`) y se documenta en el reporte (Regla 9 de la clase).
- **Energía vacía o negativa (`43` filas en EnerAndes) y lecturas extremas (`7` filas en IDEAM):** se apartan en archivos Parquet de cuarentena.

### 3.1 Cuarentena de EnerAndes (`data/silver/enerandes_cuarentena.parquet` — **43 filas**)

De las **4,184 filas brutas** en las 4 hojas del Excel (`2023` a `2026`):
1. Se quitaron **6 filas de títulos, notas y renglones en blanco** al inicio de las hojas `2025` y `2026`, más **4 filas de encabezado** y **4 filas `TOTAL`**, quedando **4,170 filas de ventas**.
2. Se eliminaron **120 filas duplicadas exactas**, quedando **4,050 filas únicas**.
3. Se apartaron en `data/silver/enerandes_cuarentena.parquet` las **43 filas** con energía vacía o negativa, dejando **4,007 filas limpias** en `data/silver/enerandes_ventas.parquet`.

| Motivo en `enerandes_cuarentena.parquet` | Filas | ¿Por qué van a cuarentena? |
|---|---:|---|
| `Energia vacia (NaN)` | 25 | No existe forma de adivinar cuántos kWh se consumieron en esa venta; poner `0` distorsionaría los promedios. |
| `Energia negativa (< 0)` | 18 | No existe consumo eléctrico negativo (error de digitación o ajuste sin soporte); cambiar el signo inventaría un dato. |
| **Total cuarentena EnerAndes** | **43** | **Conservadas intactas para revisión con la Gerencia Comercial** |

### 3.2 Cuarentena del IDEAM (`data/silver/ideam_cuarentena.parquet` — **7 filas**)

- En `ideam_precipitacion_diaria.parquet` se detectaron **7 registros** donde la lluvia acumulada de un día supera los `500 mm/día` (hasta `3,081.8 mm` por volcado acumulado de observaciones atrasadas del sensor).
- Esas **7 filas** quedaron apartadas en `data/silver/ideam_cuarentena.parquet`, de modo que `data/silver/ideam_precipitacion.parquet` (**29,797 filas**) cumple el rango físico `[0, 500] mm/día` exigido por `ESQUEMA_IDEAM_PRECIPITACION`.

---

## 4. Esquemas de Validación Pandera (`src/quality/esquemas.py`)

| Esquema Pandera | Tabla validada en `data/silver/` | Llave única (`unique`) | Condiciones principales (`Check`) |
|---|---|---|---|
| `ESQUEMA_VENTAS` | `enerandes_ventas.parquet` | `['periodo', 'divipola', 'segmento', 'tipo_compra']` | `periodo` `^\d{4}-(0[1-9]\|1[0-2])$`, `divipola` `^\d{5}$`, `segmento` en 4 valores, `tipo_compra` en `['Bolsa', 'Contrato']`, `energia_kwh >= 0`, `valor_cop >= 0` (`nullable=True`), `clientes >= 0` |
| `ESQUEMA_XM_PRECIO_BOLSA` | `xm_precio_bolsa.parquet` | `['fecha', 'hora']` | `hora` en `[1, 24]`, `precio_bolsa_cop_kwh` en `[0, 20000]` |
| `ESQUEMA_XM_DEMANDA` | `xm_demanda.parquet` | `['fecha', 'hora']` | `hora` en `[1, 24]`, `demanda_real_kwh > 0` |
| `ESQUEMA_XM_GENERACION_RECURSO` | `xm_generacion_recurso.parquet` | `['fecha', 'hora', 'codigo_recurso']` | `hora` en `[1, 24]`, `codigo_recurso` no vacío, `generacion_kwh > 0` |
| `ESQUEMA_XM_EMBALSES` | `xm_embalses.parquet` | `['fecha']` | `volumen_util_pct` en `[0.0, 100.0]` |
| `ESQUEMA_XM_APORTES` | `xm_aportes.parquet` | `['fecha']` | `aportes_energia_kwh > 0` |
| `ESQUEMA_XM_LISTADO_RECURSOS` | `xm_listado_recursos.parquet` | `['codigo_recurso']` | `codigo_recurso` único, `tipo_generacion`, `tipo_despacho` y `estado` en listas permitidas |
| `ESQUEMA_IDEAM_PRECIPITACION` | `ideam_precipitacion.parquet` | `['codigo_estacion', 'fecha']` | `cod_mpio` `^05\d{3}$`, `precipitacion_mm` en `[0.0, 500.0]`, `n_obs > 0` |
| `ESQUEMA_IDEAM_TEMPERATURA` | `ideam_temperatura.parquet` | `['codigo_estacion', 'fecha']` | `cod_mpio` `^05\d{3}$`, `temp_media_c` en `[-5, 45]`, `temp_min_c` en `[-10, 45]`, `temp_max_c` en `[-5, 50]` |
| `ESQUEMA_NOAA_ONI` | `noaa_oni.parquet` | `['fecha']` | `periodo` `AAAA-MM`, `mes` en `[1, 12]`, `oni` en `[-4, 4]`, `fase_enso` en `['El Niño', 'La Niña', 'Neutral']` |
| `ESQUEMA_DANE_DIVIPOLA` | `dane_divipola.parquet` | `['cod_mpio']` | `cod_dpto` `^\d{2}$`, `cod_mpio` `^\d{5}$`, `latitud` en `[-5, 14]`, `longitud` en `[-82, -66]` |

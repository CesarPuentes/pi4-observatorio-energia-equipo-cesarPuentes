# Bitácora de Entendimiento – Estado Inicial y Arquitectura (Punto 1)

## 1. Contexto del Problema y Modelo de Negocio

- **Matriz energética colombiana:** ~**70 % hidroeléctrica**. Durante el **fenómeno de El Niño** (anomalía térmica en el Pacífico > `+0.5 °C`; `+2.16 °C` en el trimestre `JAS` de 2026), caen las lluvias y el nivel de los embalses, obligando a despachar **plantas térmicas** (gas, carbón, líquidos) de alto costo.
- **Impacto en bolsa:** El precio de bolsa en 2026 subió de **212 COP/kWh** (enero) a **942 COP/kWh** (agosto).
- **Cliente (simulado):** **EnerAndes S.A.S. E.S.P.** (comercializadora en Antioquia). Compra energía mayorista mediante **Contratos bilaterales** (precio fijo a largo plazo) o **Bolsa** (precio spot horario) para venderla a clientes industriales y comerciales.
- **Objetivo del software:** Pipeline CLI en Python de **Ingeniería de Datos / BI** que centraliza fuentes heterogéneas para medir la exposición financiera de EnerAndes ante picos de bolsa y déficit hídrico.

---

## 2. Proveedores de Datos y Cadena Causal

Las fuentes forman una cadena causal directa con desfase temporal:

1. **NOAA (*National Oceanic and Atmospheric Administration* – EE. UU.):**
   - **Rol:** Monitorea océanos y atmósfera; publica el **Índice ONI** (*Oceanic Niño Index*) por trimestres móviles (`DJF`, `JFM`, ..., `JAS`) desde 1950 (`ANOM >= +0.5 °C` = El Niño; `<= -0.5 °C` = La Niña).
   - **Extracción:** `GET` de archivo plano ASCII separado por espacios (`oni.data`, 920 filas).
   - **URL de la API / Fuente:** `https://psl.noaa.gov/data/correlation/oni.data`
   - **Resumen y conclusión (en simple):** Fuente global que avisa meses antes si viene sequía o lluvia; nos da el contexto macro del clima descargando un archivo de texto plano.
2. **IDEAM (*Instituto de Hidrología, Meteorología y Estudios Ambientales* – Colombia):**
   - **Rol:** Mide precipitación (`mm`) y temperatura (`°C`) en estaciones meteorológicas. El calentamiento del Pacífico reduce la lluvia y eleva la temperatura en Antioquia (sede de embalses clave como Guatapé, Peñol e Hidroituango).
   - **Extracción:** API **Socrata** en `datos.gov.co` (`GET`). Como la base cruda tiene millones de registros subhorarios desde 2005, se filtra y agrega en el servidor mediante **SoQL** (`$select`, `$where`, `$group`, `$limit=50000`, `$offset`) en ventanas de **7 días** para evitar *Timeouts*.
   - **URLs de las APIs usadas:**
     - Precipitación: `https://www.datos.gov.co/resource/s54a-sgyg.json`
     - Temperatura: `https://www.datos.gov.co/resource/sbwg-7ju4.json`
   - **Resumen y conclusión (en simple):** Datos meteorológicos locales de Antioquia; le pedimos al servidor estatal que nos devuelva el agua caída y el calor diario ya sumados y promediados para no saturar la red.
3. **XM S.A. E.S.P. (Filial de ISA, Medellín):**
   - **Rol:** Operador del **SIN** (*Sistema Interconectado Nacional*) y administrador del **MEM** (*Mercado de Energía Mayorista*). Menos lluvia reduce los **aportes hídricos** (`AporEner`) y el **volumen útil de embalses** (`PorcVoluUtilDiar`), sustituyendo generación hidráulica por térmica (`Gene` por `Recurso`) y elevando el **precio de bolsa** (`PrecBolsNaci`) frente a la **demanda** (`DemaReal`), con picos entre las 18:00 y 21:00 horas.
   - **Extracción:** API REST **Sinergox** (`POST` con payload JSON). Restringe consultas con fechas a máximo **30 días** por petición.
   - **URLs de las APIs usadas:**
     - Base API: `https://servapibi.xm.com.co`
     - Métricas horarias: `https://servapibi.xm.com.co/hourly`
     - Métricas diarias: `https://servapibi.xm.com.co/daily`
     - Catálogos maestros: `https://servapibi.xm.com.co/lists`
   - **Resumen y conclusión (en simple):** Es el corazón del mercado eléctrico; nos dice cuánta agua tienen los embalses, qué plantas generaron energía y cuánto costó cada kilovatio hora hora a hora en bolsa.
4. **EnerAndes S.A.S. E.S.P. (Fuente interna):**
   - **Rol:** Registra ventas mensuales por municipio, segmento y modalidad de compra (Contrato vs. Bolsa).
   - **Extracción:** Archivo local `ventas_enerandes_2023_2026.xlsx` (4 hojas anuales, 4,184 filas brutas) leído con `openpyxl` (`header=None`, `dtype=str`).
   - **Ruta del archivo local:** `data/raw/ventas_enerandes_2023_2026.xlsx`
   - **Resumen y conclusión (en simple):** Datos comerciales de la empresa cliente; contiene las ventas reales pero viene con filas basura, fechas desordenadas y nombres de municipios mal escritos que tocará limpiar en la Capa Plata.

---

## 3. Arquitectura de Datos e Ingeniería (Versión Base)

### Estado de la Arquitectura Medallion y enfoque ELT
En la versión inicial (y toda la **EA1**) **solo existe la Capa Bronce (`data/bronze/`)**:
- **Enfoque ELT (*Extract, Load, Transform*):** A diferencia del ETL clásico, el dato se extrae y se carga **crudo sin transformar** en disco local. Si falla una regla de limpieza futura, se reprocesa desde el archivo local sin re-consultar las APIs.
- **🥉 Capa Bronce (`data/bronze/`) — [Implementada]:** Almacena los datos originales como texto (`str`/`object`) más **3 columnas de linaje**: `_fuente`, `_origen` y `_extraido_en` (timestamp UTC ISO-8601).
- **🥈 Capa Plata (`data/silver/`) y 🥇 Capa Oro (`data/gold/`) — [Pendientes para EA2 y EA3]:** Solo figuran en `.gitignore`. En Plata se tiparán datos y eliminarán registros basura; en Oro se construirá el **modelo estrella** (hechos y dimensiones) para el dashboard BI.

### Stack Técnico y Decisiones de Diseño
- **Parquet (`pyarrow`) vs. CSV:** Almacenamiento columnar comprimido con metadatos de tipos; ocupa **5 a 10 veces menos espacio** que CSV y permite lectura selectiva de columnas.
- **DuckDB vs. RDBMS tradicional (PostgreSQL/SQL Server):** Motor SQL OLAP embebido en proceso (`duckdb.connect()`) que ejecuta consultas analíticas directamente sobre `read_parquet('data/bronze/*.parquet')` sin servidor externo.
- **Formato Ancho vs. Largo (`UNPIVOT`):** XM entrega datos horarios en **formato ancho** (`Hour01`..`Hour24`, 24 columnas por fila-día). En `consultas/*.sql` se usa `UNPIVOT` para pasarlo a **formato largo** (1 fila por fecha-hora) y `TRY_CAST(... AS DOUBLE)` para convertir texto a número sin fallar ante vacíos.

### Estructura de la App en Blanco (`02_Clase_19_oct_Extraccion/observatorio-energia`)
- [`src/config.py`](observatorio-energia/src/config.py): Centraliza rutas, URLs y fechas (en la base: solo `2026-01-01` a `2026-09-30` para XM y desde `2026-06-01` para IDEAM).
- [`src/utils.py`](observatorio-energia/src/utils.py): Implementa **reintentos con espera exponencial** (`_con_reintentos`: 2, 4, 8 s ante fallos HTTP), partición de fechas (`ventanas()`), **idempotencia** (`ya_existe()`: omite archivos ya descargados salvo `--forzar`) y escritura con linaje (`guardar_bronce()`).
- [`src/pipeline.py`](observatorio-energia/src/pipeline.py): Orquestador único (`python -m src.pipeline`) que ejecuta los extractores en secuencia.
- [`src/consultar.py`](observatorio-energia/src/consultar.py): Ejecuta `01_precio_vs_embalses.sql` y `02_precio_por_hora.sql` con DuckDB.

---

## 4. Desafíos de Calidad y Cruce entre Fuentes (Por qué no se pueden unir aún en Bronce)

1. **Asimetría de granularidad temporal y formatos:**
   - **XM:** Horaria en formato ancho (`24,096 horas` en 1,004 días) y diaria en formato largo.
   - **IDEAM:** Diaria por estación (`YYYY-MM-DD`).
   - **NOAA:** Trimestral móvil (`YR` + `SEAS`).
   - **EnerAndes:** Mensual con **4 formatos de fecha incompatibles** entre hojas (`2023-04` en 2023; mezcla de `jun-24`, `09/2024` y `2024-07` en 2024; `06/2025` en 2025; `01/03/2026` en 2026) y distinto número de columnas (11 en 2024 vs. 10 en el resto).
2. **Ruido estructural y anomalías en EnerAndes:**
   - Contiene **14 filas no transaccionales** (títulos superiores en hojas 2025/2026, encabezados intercalados, filas vacías y filas `TOTAL`), **120 registros duplicados**, **19 consumos negativos**, **39 celdas nulas** de energía y mezcla de unidades en 2024 (`kWh` vs. `MWh`, factor `1,000x`).
3. **Ruptura de integridad referencial geográfica:**
   - EnerAndes presenta **38 cadenas distintas** para referirse a solo **20 municipios reales** de Antioquia (ej. `Medellín`, `Medellin`, `MEDELLÍN`, `Medellín `). Esto justifica incorporar la 5.ª fuente (**DIVIPOLA – DANE**, `gdxc-w37w`, 1,122 municipios, 125 en Antioquia) para estandarizar mediante `cod_mpio` (`05001`), teniendo en cuenta que DIVIPOLA usa **coma decimal** (`6,246631`) en sus coordenadas frente al punto decimal del IDEAM.
4. **Rezago de publicación (*Data Lag*):**
   - Mientras XM cubre hasta el `2026-09-30`, el IDEAM en datos abiertos presenta un rezago de ~2.5 meses (último dato disponible: **`2026-07-24`**; las semanas posteriores devuelven `0 filas`, lo cual representa ausencia de reporte y no `0 mm` de lluvia).

---

## 5. Desglose de la Actividad 1: ¿Por qué?, ¿Cómo? y ¿Para qué?

### Punto 2 · Ampliar la extracción de XM (API REST)
- **¿Por qué?**
  1. Con solo 9 meses de 2026 (`273 días`) no se podía contrastar el Niño 2026 frente al Niño 2023–2024.
  2. Precio, demanda y embalses no bastan para ver la sustitución hidro-térmica ni el caudal entrante a los ríos.
  3. El script base solo soportaba endpoints temporales (`hourly` y `daily`) y fallaba ante catálogos maestros.
- **¿Cómo?**
  1. En [`src/config.py`](observatorio-energia/src/config.py): se amplió `FECHA_INICIO = date(2024, 1, 1)` (`1,004 días`, 34 ventanas de 30 días) y se agregaron 3 tuplas a `XM_METRICAS`: `("Gene", "Recurso", "hourly", "xm_generacion_recurso")`, `("AporEner", "Sistema", "daily", "xm_aportes")` y `("ListadoRecursos", "Sistema", "lists", "xm_listado_recursos")`.
  2. En [`src/extract/xm.py`](observatorio-energia/src/extract/xm.py): se añadió la rama `periodo == "lists"` que envía un `POST` único sin fechas (`{"MetricId": "ListadoRecursos", "Entity": "Sistema"}`) al endpoint `/lists` (corrigiendo el error `/list` del manual de XM) y desempaca `item["ListEntities"][i]["Values"]`. Las métricas con fechas se paralelizaron con `ThreadPoolExecutor(max_workers=6)`.
- **¿Para qué?**
  - Obtener `xm_generacion_recurso.parquet` (`350,345 filas`) y cruzarlo mediante el código de planta (`Code`, ej. `2QBW` = Guatapé) con `xm_listado_recursos.parquet` (`2,494 filas`) para distinguir qué fracción de la generación provino de fuentes `HIDRAULICA` vs. `TERMICA`, y relacionar `xm_aportes.parquet` (`1,004 días` de energía hídrica entrante) con la caída de los embalses.
- **Resumen y conclusión (en simple):**
  - *Qué se hizo:* Pasamos de descargar 3 a 6 tablas de XM y ampliamos la historia de 9 meses a casi 3 años (2024–2026), agregando soporte para catálogos sin fecha (`/lists`).
  - *Por qué y para qué:* Porque necesitábamos saber cuánta agua entra a los ríos y qué plantas (agua vs. gas/carbón) están generando la energía en cada sequía, para entender exactamente qué dispara el precio en bolsa que paga EnerAndes.
- **URLs de las APIs usadas:**
  - Base API XM Sinergox (`POST`): `https://servapibi.xm.com.co`
  - Métricas horarias (`PrecBolsNaci`, `DemaReal`, `Gene`): `https://servapibi.xm.com.co/hourly`
  - Métricas diarias (`PorcVoluUtilDiar`, `AporEner`): `https://servapibi.xm.com.co/daily`
  - Catálogos maestros (`ListadoRecursos`): `https://servapibi.xm.com.co/lists`

---

### Punto 3 · Ampliar la extracción del IDEAM (Datos Abiertos / SoQL)
- **¿Por qué?**
  1. Cuatro meses de lluvia (`jun–sep 2026`, truncados además el `2026-07-24` por rezago del IDEAM) no permiten medir la estacionalidad ni el déficit acumulado.
  2. El Niño combina déficit de precipitación con ondas de calor que incrementan la evaporación y la demanda eléctrica por refrigeración.
  3. Descargar millones de lecturas crudas cada 5–10 minutos colapsaría la red y la memoria local.
- **¿Cómo?**
  1. En [`src/config.py`](observatorio-energia/src/config.py): se fijó `IDEAM_FECHA_INICIO = date(2025, 1, 1)` y se añadió `IDEAM_TEMPERATURA_URL` (`sbwg-7ju4.json`).
  2. En [`src/extract/ideam.py`](observatorio-energia/src/extract/ideam.py): se extendió `consulta_soql()` para delegar el cálculo al servidor Socrata: `sum(valorobservado) AS precipitacion_mm` en lluvia y `avg(valorobservado) AS temp_media_c, min(valorobservado) AS temp_min_c, max(valorobservado) AS temp_max_c` en temperatura, agrupando por estación y día (`$group`) en Antioquia.
- **¿Para qué?**
  - Generar `ideam_precipitacion_diaria.parquet` (`29,804 filas`) e `ideam_temperatura_diaria.parquet` (`17,349 filas`) listos a nivel diario por estación, reduciendo el tráfico de red en >99 % frente a la descarga cruda.
- **Resumen y conclusión (en simple):**
  - *Qué se hizo:* Ampliamos las lluvias de Antioquia desde enero de 2025 y sumamos un segundo dataset con la temperatura diaria (media, mínima y máxima), pidiéndole al servidor que nos entregue los datos ya resumidos por día.
  - *Por qué y para qué:* Porque bajar millones de datos minuto a minuto es inviable, y necesitamos tanto la falta de lluvia como el calor extremo desde 2025 para medir cómo el clima local seca los embalses y sube el consumo eléctrico en Antioquia.
- **URLs de las APIs usadas:**
  - Precipitación IDEAM (Socrata `SoQL` `GET`): `https://www.datos.gov.co/resource/s54a-sgyg.json`
  - Temperatura IDEAM (Socrata `SoQL` `GET`): `https://www.datos.gov.co/resource/sbwg-7ju4.json`

---

### Punto 4 · Mantener las fuentes de NOAA y EnerAndes
- **¿Por qué?**
  - Cumplen la **Regla 1 de la Capa Bronce**: preservar la evidencia original intacta (`noaa_oni.parquet` con `920 trimestres` como texto y `enerandes_ventas_2023..2026.parquet` con sus `4,184 filas` brutas, incluyendo títulos, huecos y filas `TOTAL`).
- **¿Cómo?**
  - `noaa.py` usa `pd.read_csv(..., sep=r"\s+", dtype=str)` y `enerandes.py` usa `pd.read_excel(..., sheet_name=None, header=None, dtype=str)`.
- **¿Para qué?**
  - Asegurar que cualquier error en las reglas de limpieza de la **Capa Plata (EA2)** pueda revertirse y recalcularse desde el dato crudo local sin depender de fuentes externas ni alterar el archivo original de auditoría.
- **Resumen y conclusión (en simple):**
  - *Qué se hizo:* Se conservaron sin cambios los extractores del índice climático de la NOAA y del Excel interno de ventas de EnerAndes, guardando todo como texto tal cual viene.
  - *Por qué y para qué:* Porque en la capa Bronce nunca se altera ni se borra nada; así protegemos una copia fiel del original por si mañana necesitamos auditar o corregir la limpieza sin perder datos.
- **URLs / Rutas de las fuentes usadas:**
  - Índice ONI – NOAA (`GET` texto plano): `https://psl.noaa.gov/data/correlation/oni.data`
  - Excel interno EnerAndes (local): `data/raw/ventas_enerandes_2023_2026.xlsx`

---

### Punto 5 · Agregar una fuente propia (DIVIPOLA – DANE)
- **¿Por qué?**
  - En las 4 hojas de EnerAndes los 20 municipios donde opera la empresa están escritos de **38 formas distintas** (`Medellin`, `MEDELLÍN`, `Medellín `, `Apartado`, `APARTADÓ`), mientras que el IDEAM reporta en mayúsculas sin tilde. Un `JOIN` por texto directo pierde registros o duplica municipios.
- **¿Cómo?**
  - Se creó [`src/extract/divipola.py`](observatorio-energia/src/extract/divipola.py) que consume por `GET` paginado (`$limit=5000`, `$order=cod_mpio`) el dataset `gdxc-w37w.json` en `datos.gov.co`, guardando `dane_divipola.parquet` (`1,122 municipios` de Colombia, `125` de Antioquia) e integrándolo en `src/pipeline.py`.
- **¿Para qué?**
  - Responder la pregunta de negocio propia del equipo (*exposición financiera en bolsa de EnerAndes por municipio vs. anomalías locales de lluvia y temperatura máxima*) usando el código oficial `cod_mpio` (ej. `05001` = Medellín) como llave primaria de la futura dimensión conformada `dim_municipio`.
- **Resumen y conclusión (en simple):**
  - *Qué se hizo:* Conectamos una 5.ª fuente oficial (el catálogo DIVIPOLA del DANE) que trae los códigos únicos y coordenadas de todos los municipios de Colombia.
  - *Por qué y para qué:* Porque en el Excel de EnerAndes escribieron los municipios con errores, tildes y espacios distintos (38 variantes para 20 municipios); con el código numérico del DANE podremos cruzar sin errores las ventas de cada municipio con sus estaciones de clima del IDEAM.
- **URLs de las APIs usadas:**
  - DIVIPOLA DANE (Socrata `GET`): `https://www.datos.gov.co/resource/gdxc-w37w.json`

---

### Punto 6 · Reproducibilidad y muestras en `data/sample/`
- **¿Por qué?**
  - Los 14 archivos `.parquet` de `data/bronze/` pesan ~**44 MB** (`xm_generacion_recurso.parquet` solo pesa `43.1 MB`). Subir binarios pesados a Git es una mala práctica; pero si no se sube nada, quien revise el repositorio en GitHub no puede inspeccionar la estructura real de los datos sin esperar varios minutos a que corra el pipeline.
- **¿Cómo?**
  - `data/bronze/` se mantiene excluido en `.gitignore`, y se programó `exportar_muestras()` en [`src/pipeline.py`](observatorio-energia/src/pipeline.py) para exportar automáticamente `df.head(200).to_csv(...)` de cada uno de los 14 archivos Parquet en `data/sample/*.csv` (~`552 KB` en total).
- **¿Para qué?**
  - Permitir que cualquier evaluador o desarrollador clone el repositorio, inspeccione de inmediato 200 filas reales de cada tabla en GitHub y reproduzca toda la capa bronce desde cero con un solo comando (`uv run python -m src.pipeline`).
- **Resumen y conclusión (en simple):**
  - *Qué se hizo:* Configuramos el pipeline para que, además de guardar los 14 archivos completos en Parquet (que no se suben a Git por pesados), guarde automáticamente una muestra liviana de 200 filas en CSV (`data/sample/`) que sí va a GitHub.
  - *Por qué y para qué:* Para no inflar el repositorio con archivos pesados de 44 MB y, al mismo tiempo, permitir que cualquiera vea en GitHub una vista previa real de las 14 tablas sin tener que descargar todo primero.

---

### Punto 7 · Perfilamiento de los datos (`docs/perfilamiento.md`)
- **¿Por qué?**
  - Como en Bronce no se limpia nada, no se puede diseñar la **Capa Plata (EA2)** a ciegas: hay que cuantificar exactamente qué anomalías de estructura, completitud, unicidad, validez y oportunidad trae cada tabla.
- **¿Cómo?**
  - Se construyó [`src/perfilar.py`](observatorio-energia/src/perfilar.py), que inspecciona programáticamente los 14 `.parquet` y genera [`docs/perfilamiento.md`](observatorio-energia/docs/perfilamiento.md) con conteo de filas, columnas, tipos (`dtype`), `%` de nulos, duplicados sobre columnas de negocio y rangos temporales, más **8 hallazgos respaldados con evidencia numérica**.
- **¿Para qué?**
  - Definir la hoja de ruta exacta de transformación para la Entrega 2:
    1. Eliminar las `14 filas` parásitas/TOTAL de EnerAndes.
    2. Unificar los `4 formatos` de fecha de EnerAndes a `YYYY-MM-01`.
    3. Estandarizar las `38 variantes` de municipios contra `dane_divipola`.
    4. Convertir los registros en `MWh` de 2024 a `kWh` (`* 1000`), deduplicar las `120 filas` repetidas y tratar los `19 negativos` y `39 nulos`.
    5. Reemplazar la coma decimal (`',' -> '.'`) en las `1,122 coordenadas` de DIVIPOLA.
    6. Deduplicar los `2 códigos` repetidos (`2ZP9`, `3DJY`) en `xm_listado_recursos`.
- **Resumen y conclusión (en simple):**
  - *Qué se hizo:* Creamos un script (`perfilar.py`) que radiografía los 14 archivos descargados y documenta en una tabla cuántas filas, nulos, duplicados y errores de formato tiene cada fuente.
  - *Por qué y para qué:* Porque antes de limpiar en la siguiente entrega (Capa Plata), necesitamos saber con números exactos dónde están las trampas en los datos (fechas revueltas, consumos negativos, kWh mezclados con MWh y rezago de fechas en el IDEAM).

---

### Puntos 8 y 9 · Pruebas automáticas (`pytest`), Trabajo Colaborativo y Tag `ea1`
- **¿Por qué?**
  - Un pipeline de datos sin pruebas unitarias puede corromper silenciosamente los archivos al modificar una función (ej. dejar días por fuera en `ventanas()` o perder columnas al aplanar el JSON de `lists`). Además, la trazabilidad de ingeniería exige control de versiones auditable.
- **¿Cómo?**
  - **Pruebas ([`tests/test_pipeline.py`](observatorio-energia/tests/test_pipeline.py)):** 8 tests con `pytest` y `monkeypatch`/`tmp_path` que validan en <1 segundo y sin tocar internet: partición exacta de fechas (`ventanas`), aplanado de XM (`hourly`, `daily`, `lists`), generación de parámetros `SoQL` (`precipitacion` y `temperatura`), idempotencia (`ya_existe`) e inyección de linaje (`guardar_bronce`).
  - **Git / GitHub:** Flujo en rama `developer` con commits incrementales por Issue, revisión por Pull Request hacia `main`, bitácora individual en [`docs/bitacoras/puentes_cesar.md`](observatorio-energia/docs/bitacoras/puentes_cesar.md) y etiqueta inmutable `git tag ea1`.
- **¿Para qué?**
  - Garantizar que el código sea mantenible y verificable (preparado para automatizarse con **GitHub Actions** en las siguientes entregas) y dejar congelada con el tag `ea1` la foto exacta de la Evidencia 1.
- **Resumen y conclusión (en simple):**
  - *Qué se hizo:* Programamos 8 pruebas automáticas (`pytest`) que verifican que el código funcione sin tener que conectarse a internet, documentamos la bitácora individual y organizamos la entrega en GitHub con ramas (`developer` -> `main`), Pull Requests y la etiqueta `ea1`.
  - *Por qué y para qué:* Para detectar de inmediato si un cambio futuro rompe alguna función del pipeline y dejar un registro ordenado y auditable del trabajo de ingeniería de esta primera entrega.
- **URLs de referencia (Repositorio):**
  - Repositorio GitHub: `https://github.com/CesarPuentes/pi4-observatorio-energia-equipo-cesarPuentes`
  - Pull Request #5 (`developer` -> `main`): `https://github.com/CesarPuentes/pi4-observatorio-energia-equipo-cesarPuentes/pull/5`

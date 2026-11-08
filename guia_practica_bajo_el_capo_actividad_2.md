# Guía Práctica "Bajo el Capó" – Actividad 2 (EA2)

Esta guía acompaña a [`bitacora__entendimiento_actividad_2.md`](bitacora__entendimiento_actividad_2.md) (sección **4. Desglose de la Actividad 2: ¿Por qué?, ¿Cómo? y ¿Para qué?**). Aquí encontrarás comandos listos para copiar y pegar que te permiten **ver con tus propios ojos**:
1. **El problema en crudo (Capa Bronce).**
2. **Qué hace nuestro código bajo el capó.**
3. **El resultado limpio y validado (Capa Plata, Cuarentena y Capa Oro en DuckDB).**

> **Preparación única:** Abre una terminal y ubícate en la carpeta del proyecto antes de ejecutar cualquiera de los comandos de esta guía:
> ```bash
> cd /home/flan/Desktop/Tareas/ProyectoIV/entrega/observatorio-energia
> ```

---

## Punto 1 · Limpiar el Excel de EnerAndes completo (Capa Plata)

### 1.1 Ver el problema estructural en las 4 hojas crudas (Bronce)
En la clase solo se limpió la hoja `2023` (donde el encabezado estaba en la fila `0`), pero las hojas `2024`, `2025` y `2026` vienen con otra estructura. Ejecuta:

```bash
.venv/bin/python -c "
import pandas as pd
for a in [2023, 2024, 2025, 2026]:
    df = pd.read_parquet(f'data/bronze/enerandes_ventas_{a}.parquet')
    print(f'=== HOJA {a} ({len(df)} filas) ===')
    print(df.iloc[:4, :6].to_string())
    print(df.iloc[-2:, :6].to_string())
    print()
"
```

**Qué observar:**
- En **`2023` y `2024`** el encabezado está en la fila `0`, pero en **`2024`** hay una columna extra (`col_5 = UNIDAD`) con valores `kWh` y `MWh`.
- En **`2025` y `2026`** las filas `0`, `1` y `2` son **títulos decorativos y filas en blanco**, y el encabezado real recién aparece en la **fila `3`** (`mes`, `Fecha corte`, `Ciudad`, etc.).
- En **las 4 hojas**, la última fila es un `TOTAL` que duplicaría las ventas si se suma (`14` filas parásitas en total).

### 1.2 Ver los problemas de contenido (fechas, MWh vs kWh y nombres de municipios)
```bash
.venv/bin/python -c "
import pandas as pd
h24 = pd.read_parquet('data/bronze/enerandes_ventas_2024.parquet').iloc[1:-1]
h26 = pd.read_parquet('data/bronze/enerandes_ventas_2026.parquet').iloc[4:-1]

print('1) 4 formatos de fecha mezclados (ejemplos en 2024 y 2026):')
print('   Hoja 2024:', h24['col_0'].sample(6, random_state=1).tolist())
print('   Hoja 2026:', h26['col_0'].unique()[:5].tolist(), '-> DD/MM/YYYY (01/03/2026 es marzo, no enero)')

print('\n2) Mezcla de unidades en Hoja 2024 (col_5 = UNIDAD):')
print(h24['col_5'].value_counts().to_string())

print('\n3) Ejemplos de cómo vienen escritos los municipios en 2024:')
print('  ', sorted(h24['col_1'].dropna().unique())[:12])
"
```

**Qué observar:**
- **4 formatos de fecha:** `YYYY-MM`, `MM/YYYY`, `Mon-YY` en español e inglés (`mar-24`, `apr-24`) y `DD/MM/YYYY` en 2026 (`01/03/2026` = marzo de 2026).
- **Unidades mezcladas:** En `2024` hay **347 filas en `MWh`** que deben multiplicarse por `1,000` para pasarlas a `kWh`.
- **Municipios mal escritos:** `32` variantes (`Apartado`, `Apartadó`, `medellin`, `Santafé de Antioquia`, `Sta Fe de Antioquia`) para los `20` municipios reales.

### 1.3 Ejecutar el limpiador y ver el resultado en Plata y Cuarentena
Ejecuta el módulo [`src/silver/enerandes.py`](observatorio-energia/src/silver/enerandes.py) y revisa cómo quedaron las tablas:

```bash
.venv/bin/python -m src.silver.enerandes
```

```bash
.venv/bin/python -c "
import pandas as pd
limpio = pd.read_parquet('data/silver/enerandes_ventas.parquet')
cuarentena = pd.read_parquet('data/silver/enerandes_cuarentena.parquet')

print(f'=== TABLA LIMPIA: {len(limpio)} filas ===')
print(limpio.head(5).to_string())
print('\nConteo por segmento (incluyendo los 28 vacíos marcados como No informado):')
print(limpio['segmento'].value_counts().to_string())
print('\nFilas con valor_cop nulo conservadas (nullable=True):', limpio['valor_cop'].isna().sum())

print(f'\n=== TABLA CUARENTENA: {len(cuarentena)} filas ===')
print(cuarentena['motivo'].value_counts().to_string())
print('\nMuestra de filas en cuarentena:')
print(cuarentena[['periodo', 'municipio', 'segmento', 'energia_kwh', 'motivo']].head(6).to_string())
"
```

---

## Punto 2 · Limpiar las demás fuentes: XM, IDEAM, NOAA y Fuente Propia (Capa Plata)

### 2.1 XM Sinergox: De 24 columnas horarias (`Hour01..Hour24`) a formato largo y catálogo sin huérfanos
En Bronce, XM viene en formato "ancho" (`Hour01` a `Hour24` como texto), los embalses vienen en fracción `0..1` y `ListadoRecursos` tiene 2 códigos duplicados (`5J8H`, `5PUN`) y le faltan 10 plantas históricas que sí generaron energía en 2024–2025. Compruébalo con este comando:

```bash
.venv/bin/python -c "
import pandas as pd
pb_b = pd.read_parquet('data/bronze/xm_precio_bolsa.parquet')
pb_s = pd.read_parquet('data/silver/xm_precio_bolsa.parquet')
print('--- XM Precio Bolsa ANTES (Bronce, formato ancho) ---')
print('Columnas:', pb_b.columns[:7].tolist(), '... total cols:', len(pb_b.columns), '| filas:', len(pb_b))
print(pb_b[['Date', 'Hour01', 'Hour02', 'Hour20']].head(2).to_string())

print('\n--- XM Precio Bolsa DESPUÉS (Plata, formato largo por fecha y hora 1..24) ---')
print('Columnas:', pb_s.columns.tolist(), '| filas:', len(pb_s), '(1,004 días x 24 horas)')
print(pb_s.head(4).to_string())

gen_b = pd.read_parquet('data/bronze/xm_generacion_recurso.parquet')
gen_s = pd.read_parquet('data/silver/xm_generacion_recurso.parquet')
rec_b = pd.read_parquet('data/bronze/xm_listado_recursos.parquet')
rec_s = pd.read_parquet('data/silver/xm_listado_recursos.parquet')
print(f'\n--- XM Generación y Catálogo de Recursos ---')
print(f'Generación Bronce: {len(gen_b):,} filas anchas -> Plata: {len(gen_s):,} filas horarias válidas (se filtraron 2,472,918 horas vacías)')
print(f'Catálogo Recursos Bronce: {len(rec_b)} filas ({rec_b[\"Code\"].nunique()} únicos) -> Plata: {len(rec_s)} únicos (incluye 10 históricos para integridad referencial)')
"
```

### 2.2 IDEAM: Cruce con DIVIPOLA y aislamiento de las 7 lluvias físicamente imposibles (`> 500 mm/día`)
En Bronce, el IDEAM trae `7` registros donde el pluviómetro volcó el acumulado de semanas en un solo día (hasta **`3,081.8 mm/día`** en San Carlos, cuando el máximo físico diario es `500 mm`). Ejecuta:

```bash
.venv/bin/python -c "
import pandas as pd
id_s = pd.read_parquet('data/silver/ideam_precipitacion.parquet')
id_q = pd.read_parquet('data/silver/ideam_cuarentena.parquet')

print(f'=== IDEAM Precipitación Limpia: {len(id_s):,} filas (rango: {id_s[\"precipitacion_mm\"].min()} a {id_s[\"precipitacion_mm\"].max()} mm) ===')
print(id_s[['fecha', 'codigo_estacion', 'cod_mpio', 'municipio', 'precipitacion_mm']].head(4).to_string())

print(f'\n=== IDEAM Cuarentena: {len(id_q)} lecturas extremas (> 500 mm/día) ===')
print(id_q[['fecha', 'codigo_estacion', 'cod_mpio', 'municipio', 'precipitacion_mm', 'motivo_cuarentena']].to_string())
"
```

### 2.3 NOAA y DANE DIVIPOLA: Trimestres móviles a meses (`fase_enso`) y coordenadas con coma decimal
En Bronce, la NOAA viene por trimestres móviles (`DJF`, `JFM`, ..., `JAS`) sin fecha mensual ni etiqueta del fenómeno ENSO, y el DANE trae las coordenadas con coma decimal (`6,246631`) como texto. Ejecuta:

```bash
.venv/bin/python -c "
import pandas as pd
no_b = pd.read_parquet('data/bronze/noaa_oni.parquet')
no_s = pd.read_parquet('data/silver/noaa_oni.parquet')
print('--- NOAA ANTES (Bronce) ---')
print(no_b[['SEAS', 'YR', 'TOTAL', 'ANOM']].tail(4).to_string())
print('\n--- NOAA DESPUÉS (Plata: mes central + fase_enso) ---')
print(no_s[['fecha', 'periodo', 'trimestre_movil', 'oni', 'fase_enso']].tail(4).to_string())
print('\nConteo histórico por fase ENSO:', no_s['fase_enso'].value_counts().to_dict())

dv_b = pd.read_parquet('data/bronze/dane_divipola.parquet')
dv_s = pd.read_parquet('data/silver/dane_divipola.parquet')
print('\n--- DANE DIVIPOLA ANTES (coma decimal en str) vs DESPUÉS (float64) ---')
print('Bronce:', dv_b[['cod_mpio', 'nom_mpio', 'latitud', 'longitud']].head(2).to_dict('records'))
print('Plata :', dv_s[['cod_mpio', 'municipio', 'latitud', 'longitud']].head(2).to_dict('records'))
"
```

---

## Punto 3 · Validar la calidad con Pandera y probar las reglas con `pytest`

### 3.1 Ver cómo Pandera bloquea un dato corrupto en vivo
En [`src/quality/esquemas.py`](observatorio-energia/src/quality/esquemas.py) definimos los contratos `DataFrameSchema` de cada tabla. Ejecuta este comando para simular qué pasa si alguien intenta colar una venta con **energía negativa** o un **código DIVIPOLA inválido**:

```bash
.venv/bin/python -c "
import pandas as pd, pandera.pandas as pa
from src.quality.esquemas import ESQUEMA_VENTAS

df_malo = pd.DataFrame({
    'periodo': ['2024-03'],
    'divipola': ['9999999'],      # Inválido: debe tener 5 dígitos
    'municipio': ['Medellín'],
    'segmento': ['Residencial'],
    'tipo_compra': ['Bolsa'],
    'energia_kwh': [-150.0],      # Inválido: debe ser > 0
    'valor_cop': [120000.0],
    'clientes': [10],
})

try:
    ESQUEMA_VENTAS.validate(df_malo, lazy=True)
except pa.errors.SchemaErrors as err:
    print('¡Pandera bloqueó la tabla corrupta! Errores detectados:')
    print(err.failure_cases[['column', 'check', 'failure_case']].to_string())
"
```

### 3.2 Ejecutar las 25 pruebas automáticas con `pytest`
Para correr las **17 pruebas de limpieza y calidad** ([`tests/test_limpieza.py`](observatorio-energia/tests/test_limpieza.py): las 7 de la clase + las 10 nuevas del equipo) junto con las **8 pruebas de extracción** ([`tests/test_pipeline.py`](observatorio-energia/tests/test_pipeline.py)):

```bash
.venv/bin/python -m pytest -v
```

---

## Punto 4 · Escribir el reporte de calidad (`docs/reporte_calidad.md`)

El módulo [`src/quality/reporte.py`](observatorio-energia/src/quality/reporte.py) toma las métricas antes y después de cada limpiador y genera automáticamente [`docs/reporte_calidad.md`](observatorio-energia/docs/reporte_calidad.md) con **23 reglas medidas**. Puedes ver la tabla resumen directamente en terminal con:

```bash
.venv/bin/python -c "
from pathlib import Path
lineas = Path('docs/reporte_calidad.md').read_text().splitlines()
for l in lineas[:42]:
    print(l)
"
```

---

## Punto 5 · Construir el esquema estrella con `dbt` y DuckDB (Capa Oro)

### 5.1 Ver cómo `dbt` construye las 11 vistas (`staging`) y las 12 tablas (`marts`) y corre las 82 pruebas
Ejecuta `dbt build` directamente para ver cómo materializa las vistas y tablas en `data/observatorio.duckdb` y verifica que las **82 pruebas declarativas** (`unique`, `not_null`, `relationships` en [`dbt/models/marts/schema.yml`](observatorio-energia/dbt/models/marts/schema.yml)) pasen al 100 % (`PASS=105`):

```bash
.venv/bin/dbt build --project-dir dbt --profiles-dir dbt
```

### 5.2 Inspeccionar por dentro la base de datos `data/observatorio.duckdb`
Ejecuta este comando para listar todas las vistas `stg_*`, dimensiones `dim_*` y tablas de hechos `fact_*` creadas dentro de DuckDB con su conteo de filas:

```bash
.venv/bin/python -c "
import duckdb
con = duckdb.connect('data/observatorio.duckdb', read_only=True)
tablas = con.execute('''
    SELECT table_name, table_type
    FROM information_schema.tables
    WHERE table_schema = 'main'
    ORDER BY table_type, table_name
''').fetchall()

print(f'{\"NOMBRE EN DUCKDB\":<30} | {\"TIPO\":<12} | {\"FILAS\":>12}')
print('-' * 60)
for nombre, tipo in tablas:
    n = con.execute(f'SELECT COUNT(*) FROM {nombre}').fetchone()[0]
    print(f'{nombre:<30} | {tipo:<12} | {n:>12,}')
"
```

---

## Punto 6 · Documentar el modelo y responder preguntas de negocio en Capa Oro

### 6.1 Ejecutar la consulta rápida con `dbt show` (igual que en la clase)
```bash
.venv/bin/dbt show --project-dir dbt --profiles-dir dbt --inline "
select s.segmento, round(sum(f.energia_kwh) / 1000000, 1) as gwh
from {{ ref('fact_ventas_mensual') }} f
join {{ ref('dim_segmento') }} s using (segmento_id)
group by s.segmento order by gwh desc
"
```

### 6.2 Ejecutar las 5 consultas analíticas de negocio sobre el Esquema Estrella (`consultas/oro/*.sql`)
Este comando ejecuta las 5 consultas SQL ([`consultas/oro/`](observatorio-energia/consultas/oro/)) que cruzan **ENSO (NOAA) → Embalses y Aportes (XM) → Matriz Hidro/Térmica (XM) → Precio y Demanda Horaria (XM) → Exposición a Bolsa y Clima por Municipio en Antioquia (EnerAndes + IDEAM + DIVIPOLA)**:

```bash
.venv/bin/python -m src.consultar --solo-oro
```

---

## Puntos 7 y 8 · Reproducibilidad con un solo comando e Higiene de Git

### 7.1 Ejecutar todo el pipeline Plata + Reporte + Oro (`dbt build`) con un solo comando
El orquestador [`src/transformar.py`](observatorio-energia/src/transformar.py) limpia las 5 fuentes hacia `data/silver/`, regenera `docs/reporte_calidad.md` y ejecuta `dbt build` sobre `data/observatorio.duckdb`:

```bash
.venv/bin/python -m src.transformar
```

### 7.2 Verificar que `.gitignore` protege el repositorio de archivos pesados
Ejecuta este comando para comprobar que `data/bronze/`, `data/silver/`, `data/observatorio.duckdb`, `dbt/target/` y `dbt/logs/` están correctamente ignorados por Git:

```bash
git status --ignored -s
```

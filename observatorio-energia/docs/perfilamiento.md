# Perfilamiento de Datos – Capa Bronce (`data/bronze/`)

> **Proyecto Integrado IV – Observatorio Energía y Clima Colombia (2026-2)**
> Documento generado automáticamente a partir de los **14 archivos Parquet** de la capa bronce.

---

## 1. Resumen general de la capa bronce

| Archivo en `data/bronze/` | Fuente | Filas | Columnas | Filas duplicadas (datos) | Rango de fechas / cobertura | Tamaño (KB) |
|---|---|---:|---:|---:|---|---:|
| `dane_divipola.parquet` | DANE-DIVIPOLA | 1,122 | 10 | 0 | Catalogo maestro vigente (sin serie temporal) | 45 |
| `enerandes_ventas_2023.parquet` | EnerAndes | 1,114 | 10 | 32 | Anio 2023 (ej. '2023-04' ... '2023-10') | 32 |
| `enerandes_ventas_2024.parquet` | EnerAndes | 1,114 | 11 | 32 | Anio 2024 (ej. 'jun-24' ... 'jul-24') | 34 |
| `enerandes_ventas_2025.parquet` | EnerAndes | 1,117 | 10 | 32 | Anio 2025 (ej. '06/2025' ... '07/2025') | 33 |
| `enerandes_ventas_2026.parquet` | EnerAndes | 839 | 10 | 24 | Anio 2026 (ej. '01/03/2026' ... '01/03/2026') | 26 |
| `ideam_precipitacion_diaria.parquet` | IDEAM | 29,804 | 11 | 0 | 2025-01-01 a 2026-07-24 | 102 |
| `ideam_temperatura_diaria.parquet` | IDEAM | 17,349 | 13 | 0 | 2025-01-01 a 2026-07-24 | 164 |
| `noaa_oni.parquet` | NOAA | 920 | 7 | 0 | 1950-DJF a 2026-JAS (trimestres moviles) | 9 |
| `xm_aportes.parquet` | XM | 1,004 | 6 | 0 | 2024-01-01 a 2026-09-30 | 20 |
| `xm_demanda.parquet` | XM | 1,004 | 30 | 0 | 2024-01-01 a 2026-09-30 | 282 |
| `xm_embalses.parquet` | XM | 1,004 | 6 | 0 | 2024-01-01 a 2026-09-30 | 15 |
| `xm_generacion_recurso.parquet` | XM | 350,345 | 30 | 0 | 2024-01-01 a 2026-09-30 | 43,125 |
| `xm_listado_recursos.parquet` | XM | 2,494 | 14 | 2 | Corte catalogo: 2026-10-22 | 74 |
| `xm_precio_bolsa.parquet` | XM | 1,004 | 30 | 0 | 2024-01-01 a 2026-09-30 | 260 |

---

## 2. Perfilamiento detallado por archivo de bronce

### 2.1 `dane_divipola.parquet`

- **Fuente:** `DANE-DIVIPOLA` (`https://www.datos.gov.co/resource/gdxc-w37w.json`)
- **Filas:** 1,122 | **Columnas:** 10
- **Filas duplicadas:** 0 (exactas incluyendo linaje) / 0 (sobre columnas de negocio)
- **Rango de fechas:** Catalogo maestro vigente (sin serie temporal)

| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |
|---|---|---:|---:|---:|---|
| `cod_dpto` | `str` | 0 | 0.00% | 33 | `05`, `08` |
| `dpto` | `str` | 0 | 0.00% | 33 | `ANTIOQUIA`, `ATLÁNTICO` |
| `cod_mpio` | `str` | 0 | 0.00% | 1,122 | `05001`, `05002` |
| `nom_mpio` | `str` | 0 | 0.00% | 1,037 | `MEDELLÍN`, `ABEJORRAL` |
| `tipo_municipio` | `str` | 0 | 0.00% | 3 | `Municipio`, `Isla` |
| `longitud` | `str` | 0 | 0.00% | 1,121 | `-75,581775`, `-75,428739` |
| `latitud` | `str` | 0 | 0.00% | 1,122 | `6,246631`, `5,789315` |
| `_fuente` | `str` | 0 | 0.00% | 1 | `DANE-DIVIPOLA` |
| `_origen` | `str` | 0 | 0.00% | 1 | `https://www.datos.gov.co/resource/g` |
| `_extraido_en` | `str` | 0 | 0.00% | 1 | `2026-10-23T01:45:06+00:00` |

### 2.2 `enerandes_ventas_2023.parquet`

- **Fuente:** `EnerAndes` (`ventas_enerandes_2023_2026.xlsx#Ventas 2023`)
- **Filas:** 1,114 | **Columnas:** 10
- **Filas duplicadas:** 32 (exactas incluyendo linaje) / 32 (sobre columnas de negocio)
- **Rango de fechas:** Anio 2023 (ej. '2023-04' ... '2023-10')

| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |
|---|---|---:|---:|---:|---|
| `col_0` | `str` | 0 | 0.00% | 14 | `Fecha`, `2023-04` |
| `col_1` | `str` | 1 | 0.09% | 32 | `Municipio`, `Copacabana` |
| `col_2` | `str` | 16 | 1.44% | 7 | `Segmento`, `Industrial` |
| `col_3` | `str` | 1 | 0.09% | 5 | `Tipo_Compra`, `Bolsa` |
| `col_4` | `str` | 10 | 0.90% | 1,070 | `Energia_kWh`, `98240` |
| `col_5` | `str` | 8 | 0.72% | 1,074 | `Valor_COP`, `78251589` |
| `col_6` | `str` | 1 | 0.09% | 587 | `Clientes`, `2` |
| `_fuente` | `str` | 0 | 0.00% | 1 | `EnerAndes` |
| `_origen` | `str` | 0 | 0.00% | 1 | `ventas_enerandes_2023_2026.xlsx#Ven` |
| `_extraido_en` | `str` | 0 | 0.00% | 1 | `2026-10-23T01:45:05+00:00` |

### 2.3 `enerandes_ventas_2024.parquet`

- **Fuente:** `EnerAndes` (`ventas_enerandes_2023_2026.xlsx#Ventas 2024`)
- **Filas:** 1,114 | **Columnas:** 11
- **Filas duplicadas:** 32 (exactas incluyendo linaje) / 32 (sobre columnas de negocio)
- **Rango de fechas:** Anio 2024 (ej. 'jun-24' ... 'jul-24')

| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |
|---|---|---:|---:|---:|---|
| `col_0` | `str` | 0 | 0.00% | 38 | `PERIODO`, `jun-24` |
| `col_1` | `str` | 1 | 0.09% | 33 | `MUNICIPIO`, `Bello` |
| `col_2` | `str` | 4 | 0.36% | 7 | `SEGMENTO CLIENTE`, `Comercial` |
| `col_3` | `str` | 1 | 0.09% | 5 | `MODALIDAD`, `Bolsa` |
| `col_4` | `str` | 8 | 0.72% | 1,075 | `ENERGIA`, `384574` |
| `col_5` | `str` | 1 | 0.09% | 3 | `UNIDAD`, `kWh` |
| `col_6` | `str` | 12 | 1.08% | 1,070 | `VALOR ($)`, `413631897` |
| `col_7` | `str` | 1 | 0.09% | 583 | `NUM CLIENTES`, `275` |
| `_fuente` | `str` | 0 | 0.00% | 1 | `EnerAndes` |
| `_origen` | `str` | 0 | 0.00% | 1 | `ventas_enerandes_2023_2026.xlsx#Ven` |
| `_extraido_en` | `str` | 0 | 0.00% | 1 | `2026-10-23T01:45:05+00:00` |

### 2.4 `enerandes_ventas_2025.parquet`

- **Fuente:** `EnerAndes` (`ventas_enerandes_2023_2026.xlsx#Ventas 2025`)
- **Filas:** 1,117 | **Columnas:** 10
- **Filas duplicadas:** 32 (exactas incluyendo linaje) / 32 (sobre columnas de negocio)
- **Rango de fechas:** Anio 2025 (ej. '06/2025' ... '07/2025')

| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |
|---|---|---:|---:|---:|---|
| `col_0` | `str` | 1 | 0.09% | 16 | `EnerAndes S.A.S. E.S.P. - Reporte d`, `Fuente: sistema comercial. Uso inte` |
| `col_1` | `str` | 4 | 0.36% | 31 | `municipio`, `Apartadó` |
| `col_2` | `str` | 10 | 0.90% | 7 | `segmento`, `Comercial` |
| `col_3` | `str` | 4 | 0.36% | 5 | `tipo compra`, `Bolsa` |
| `col_4` | `str` | 10 | 0.90% | 1,076 | `consumo (kWh)`, `121318` |
| `col_5` | `str` | 8 | 0.72% | 1,077 | `facturado`, `143967156` |
| `col_6` | `str` | 4 | 0.36% | 602 | `usuarios`, `87` |
| `_fuente` | `str` | 0 | 0.00% | 1 | `EnerAndes` |
| `_origen` | `str` | 0 | 0.00% | 1 | `ventas_enerandes_2023_2026.xlsx#Ven` |
| `_extraido_en` | `str` | 0 | 0.00% | 1 | `2026-10-23T01:45:05+00:00` |

### 2.5 `enerandes_ventas_2026.parquet`

- **Fuente:** `EnerAndes` (`ventas_enerandes_2023_2026.xlsx#Ventas 2026`)
- **Filas:** 839 | **Columnas:** 10
- **Filas duplicadas:** 24 (exactas incluyendo linaje) / 24 (sobre columnas de negocio)
- **Rango de fechas:** Anio 2026 (ej. '01/03/2026' ... '01/03/2026')

| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |
|---|---|---:|---:|---:|---|
| `col_0` | `str` | 1 | 0.12% | 13 | `EnerAndes S.A.S. E.S.P. - Reporte d`, `Fuente: sistema comercial. Uso inte` |
| `col_1` | `str` | 4 | 0.48% | 30 | `Ciudad`, `Apartadó` |
| `col_2` | `str` | 9 | 1.07% | 7 | `Tipo cliente`, `Industrial` |
| `col_3` | `str` | 4 | 0.48% | 5 | `Compra`, `Bolsa` |
| `col_4` | `str` | 9 | 1.07% | 806 | `kWh`, `171572` |
| `col_5` | `str` | 11 | 1.31% | 805 | `Total facturado COP`, `177022706` |
| `col_6` | `str` | 4 | 0.48% | 473 | `Clientes activos`, `4` |
| `_fuente` | `str` | 0 | 0.00% | 1 | `EnerAndes` |
| `_origen` | `str` | 0 | 0.00% | 1 | `ventas_enerandes_2023_2026.xlsx#Ven` |
| `_extraido_en` | `str` | 0 | 0.00% | 1 | `2026-10-23T01:45:05+00:00` |

### 2.6 `ideam_precipitacion_diaria.parquet`

- **Fuente:** `IDEAM` (`https://www.datos.gov.co/resource/s54a-sgyg.json`)
- **Filas:** 29,804 | **Columnas:** 11
- **Filas duplicadas:** 0 (exactas incluyendo linaje) / 0 (sobre columnas de negocio)
- **Rango de fechas:** 2025-01-01 a 2026-07-24

| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |
|---|---|---:|---:|---:|---|
| `codigoestacion` | `str` | 0 | 0.00% | 72 | `0011057020`, `0011115040` |
| `nombreestacion` | `str` | 0 | 0.00% | 72 | `SAN ANTONIO PADUA`, `MUSINGA` |
| `municipio` | `str` | 0 | 0.00% | 50 | `VIGIA DEL FUERTE`, `FRONTINO` |
| `latitud` | `str` | 0 | 0.00% | 72 | `6.286666667`, `6.777972222` |
| `longitud` | `str` | 0 | 0.00% | 72 | `-76.76180556`, `-76.20333333` |
| `fecha` | `str` | 0 | 0.00% | 537 | `2025-01-01T00:00:00.000`, `2025-01-02T00:00:00.000` |
| `precipitacion_mm` | `str` | 0 | 0.00% | 1,125 | `0`, `1.4` |
| `n_obs` | `str` | 0 | 0.00% | 322 | `266`, `278` |
| `_fuente` | `str` | 0 | 0.00% | 1 | `IDEAM` |
| `_origen` | `str` | 0 | 0.00% | 1 | `https://www.datos.gov.co/resource/s` |
| `_extraido_en` | `str` | 0 | 0.00% | 1 | `2026-10-23T01:44:16+00:00` |

### 2.7 `ideam_temperatura_diaria.parquet`

- **Fuente:** `IDEAM` (`https://www.datos.gov.co/resource/sbwg-7ju4.json`)
- **Filas:** 17,349 | **Columnas:** 13
- **Filas duplicadas:** 0 (exactas incluyendo linaje) / 0 (sobre columnas de negocio)
- **Rango de fechas:** 2025-01-01 a 2026-07-24

| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |
|---|---|---:|---:|---:|---|
| `codigoestacion` | `str` | 0 | 0.00% | 44 | `0011115040`, `0023085080` |
| `nombreestacion` | `str` | 0 | 0.00% | 44 | `MUSINGA`, `GRANJA EXPERIMENTAL EL NUS` |
| `municipio` | `str` | 0 | 0.00% | 37 | `FRONTINO`, `SAN ROQUE` |
| `latitud` | `str` | 0 | 0.00% | 44 | `6.777972222`, `6.483583333` |
| `longitud` | `str` | 0 | 0.00% | 44 | `-76.20333333`, `-74.83669444` |
| `fecha` | `str` | 0 | 0.00% | 528 | `2025-01-01T00:00:00.000`, `2025-01-02T00:00:00.000` |
| `temp_media_c` | `str` | 0 | 0.00% | 7,608 | `19.6739130434782609`, `22.8526315789473684` |
| `temp_min_c` | `str` | 0 | 0.00% | 293 | `17.1`, `19.4` |
| `temp_max_c` | `str` | 0 | 0.00% | 291 | `23.7`, `27.6` |
| `n_obs` | `str` | 0 | 0.00% | 205 | `46`, `38` |
| `_fuente` | `str` | 0 | 0.00% | 1 | `IDEAM` |
| `_origen` | `str` | 0 | 0.00% | 1 | `https://www.datos.gov.co/resource/s` |
| `_extraido_en` | `str` | 0 | 0.00% | 1 | `2026-10-23T01:45:04+00:00` |

### 2.8 `noaa_oni.parquet`

- **Fuente:** `NOAA` (`https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt`)
- **Filas:** 920 | **Columnas:** 7
- **Filas duplicadas:** 0 (exactas incluyendo linaje) / 0 (sobre columnas de negocio)
- **Rango de fechas:** 1950-DJF a 2026-JAS (trimestres moviles)

| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |
|---|---|---:|---:|---:|---|
| `SEAS` | `str` | 0 | 0.00% | 12 | `DJF`, `JFM` |
| `YR` | `str` | 0 | 0.00% | 77 | `1950`, `1951` |
| `TOTAL` | `str` | 0 | 0.00% | 339 | `25.01`, `25.36` |
| `ANOM` | `str` | 0 | 0.00% | 308 | `-1.32`, `-1.20` |
| `_fuente` | `str` | 0 | 0.00% | 1 | `NOAA` |
| `_origen` | `str` | 0 | 0.00% | 1 | `https://www.cpc.ncep.noaa.gov/data/` |
| `_extraido_en` | `str` | 0 | 0.00% | 1 | `2026-10-23T01:45:05+00:00` |

### 2.9 `xm_aportes.parquet`

- **Fuente:** `XM` (`https://servapibi.xm.com.co/daily MetricId=AporEner`)
- **Filas:** 1,004 | **Columnas:** 6
- **Filas duplicadas:** 0 (exactas incluyendo linaje) / 0 (sobre columnas de negocio)
- **Rango de fechas:** 2024-01-01 a 2026-09-30

| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |
|---|---|---:|---:|---:|---|
| `Date` | `str` | 0 | 0.00% | 1,004 | `2024-01-01`, `2024-01-02` |
| `Id` | `str` | 0 | 0.00% | 1 | `Sistema` |
| `Value` | `str` | 0 | 0.00% | 1,004 | `113920600.00000`, `107403100.00000` |
| `_fuente` | `str` | 0 | 0.00% | 1 | `XM` |
| `_origen` | `str` | 0 | 0.00% | 1 | `https://servapibi.xm.com.co/daily M` |
| `_extraido_en` | `str` | 0 | 0.00% | 1 | `2026-10-23T01:35:45+00:00` |

### 2.10 `xm_demanda.parquet`

- **Fuente:** `XM` (`https://servapibi.xm.com.co/hourly MetricId=DemaReal`)
- **Filas:** 1,004 | **Columnas:** 30
- **Filas duplicadas:** 0 (exactas incluyendo linaje) / 0 (sobre columnas de negocio)
- **Rango de fechas:** 2024-01-01 a 2026-09-30

| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |
|---|---|---:|---:|---:|---|
| `Date` | `str` | 0 | 0.00% | 1,004 | `2024-01-01`, `2024-01-02` |
| `Id` | `str` | 0 | 0.00% | 1 | `Sistema` |
| `code` | `str` | 0 | 0.00% | 1 | `Sistema` |
| `Hour01` | `str` | 0 | 0.00% | 1,004 | `7236893.31000`, `7235609.90000` |
| `Hour02` | `str` | 0 | 0.00% | 1,004 | `7104164.61000`, `7008752.02000` |
| `Hour03` | `str` | 0 | 0.00% | 1,004 | `7012446.40000`, `6849053.28000` |
| `Hour04` | `str` | 0 | 0.00% | 1,004 | `6870115.23000`, `6778829.26000` |
| `Hour05` | `str` | 0 | 0.00% | 1,004 | `6759771.97000`, `6832928.86000` |
| `Hour06` | `str` | 0 | 0.00% | 1,004 | `6671795.60000`, `7000995.55000` |
| `Hour07` | `str` | 0 | 0.00% | 1,004 | `6287595.26000`, `7119165.29000` |
| `Hour08` | `str` | 0 | 0.00% | 1,004 | `6319646.62000`, `7575100.32000` |
| `Hour09` | `str` | 0 | 0.00% | 1,004 | `6520217.34000`, `8114467.79000` |
| `Hour10` | `str` | 0 | 0.00% | 1,004 | `6695340.87000`, `8495141.21000` |
| `Hour11` | `str` | 0 | 0.00% | 1,004 | `6888638.47000`, `8924817.19000` |
| `Hour12` | `str` | 0 | 0.00% | 1,004 | `7190683.86000`, `9212097.61000` |
| `Hour13` | `str` | 0 | 0.00% | 1,004 | `7340773.88000`, `9334384.70000` |
| `Hour14` | `str` | 0 | 0.00% | 1,004 | `7382892.56000`, `9418814.27000` |
| `Hour15` | `str` | 0 | 0.00% | 1,004 | `7324239.94000`, `9577984.47000` |
| `Hour16` | `str` | 0 | 0.00% | 1,004 | `7335829.33000`, `9559801.66000` |
| `Hour17` | `str` | 0 | 0.00% | 1,004 | `7316670.59000`, `9384656.76000` |
| `Hour18` | `str` | 0 | 0.00% | 1,004 | `7381571.21000`, `9181488.18000` |
| `Hour19` | `str` | 0 | 0.00% | 1,004 | `8108189.21000`, `9714483.87000` |
| `Hour20` | `str` | 0 | 0.00% | 1,004 | `8336059.98000`, `9846198.13000` |
| `Hour21` | `str` | 0 | 0.00% | 1,004 | `8268100.14000`, `9792471.23000` |
| `Hour22` | `str` | 0 | 0.00% | 1,004 | `8106656.06000`, `9425189.28000` |
| `Hour23` | `str` | 0 | 0.00% | 1,004 | `7833804.62000`, `8960022.36000` |
| `Hour24` | `str` | 0 | 0.00% | 1,004 | `7518276.26000`, `8415379.52000` |
| `_fuente` | `str` | 0 | 0.00% | 1 | `XM` |
| `_origen` | `str` | 0 | 0.00% | 1 | `https://servapibi.xm.com.co/hourly ` |
| `_extraido_en` | `str` | 0 | 0.00% | 1 | `2026-10-23T01:35:02+00:00` |

### 2.11 `xm_embalses.parquet`

- **Fuente:** `XM` (`https://servapibi.xm.com.co/daily MetricId=PorcVoluUtilDiar`)
- **Filas:** 1,004 | **Columnas:** 6
- **Filas duplicadas:** 0 (exactas incluyendo linaje) / 0 (sobre columnas de negocio)
- **Rango de fechas:** 2024-01-01 a 2026-09-30

| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |
|---|---|---:|---:|---:|---|
| `Date` | `str` | 0 | 0.00% | 1,004 | `2024-01-01`, `2024-01-02` |
| `Id` | `str` | 0 | 0.00% | 1 | `Sistema` |
| `Value` | `str` | 0 | 0.00% | 989 | `0.70058`, `0.69708` |
| `_fuente` | `str` | 0 | 0.00% | 1 | `XM` |
| `_origen` | `str` | 0 | 0.00% | 1 | `https://servapibi.xm.com.co/daily M` |
| `_extraido_en` | `str` | 0 | 0.00% | 1 | `2026-10-23T01:35:06+00:00` |

### 2.12 `xm_generacion_recurso.parquet`

- **Fuente:** `XM` (`https://servapibi.xm.com.co/hourly MetricId=Gene`)
- **Filas:** 350,345 | **Columnas:** 30
- **Filas duplicadas:** 0 (exactas incluyendo linaje) / 0 (sobre columnas de negocio)
- **Rango de fechas:** 2024-01-01 a 2026-09-30

| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |
|---|---|---:|---:|---:|---|
| `Date` | `str` | 0 | 0.00% | 1,004 | `2024-01-01`, `2024-01-02` |
| `Id` | `str` | 0 | 0.00% | 1 | `Recurso` |
| `code` | `str` | 0 | 0.00% | 632 | `2QBW`, `2QRL` |
| `Hour01` | `str` | 182,004 | 51.95% | 128,392 | `10584.24`, `646.2` |
| `Hour02` | `str` | 184,002 | 52.52% | 126,571 | `10583.15`, `646.17` |
| `Hour03` | `str` | 184,611 | 52.69% | 125,990 | `10585.63`, `645.93` |
| `Hour04` | `str` | 184,797 | 52.75% | 125,463 | `10585.1`, `645.87` |
| `Hour05` | `str` | 183,623 | 52.41% | 126,485 | `10585.61`, `645.75` |
| `Hour06` | `str` | 156,043 | 44.54% | 133,139 | `10586.25`, `645.81` |
| `Hour07` | `str` | 52,254 | 14.92% | 176,596 | `10588.94`, `645.78` |
| `Hour08` | `str` | 37,157 | 10.61% | 197,402 | `10588.27`, `645.78` |
| `Hour09` | `str` | 30,425 | 8.68% | 207,867 | `10586.76`, `645.48` |
| `Hour10` | `str` | 26,801 | 7.65% | 212,014 | `10587.84`, `645.45` |
| `Hour11` | `str` | 24,798 | 7.08% | 213,562 | `10585.94`, `645.93` |
| `Hour12` | `str` | 24,115 | 6.88% | 214,133 | `10585.79`, `645.72` |
| `Hour13` | `str` | 24,045 | 6.86% | 214,267 | `10585.5`, `645.33` |
| `Hour14` | `str` | 23,720 | 6.77% | 214,551 | `10582.82`, `645.45` |
| `Hour15` | `str` | 24,071 | 6.87% | 214,121 | `10580.24`, `645.81` |
| `Hour16` | `str` | 26,503 | 7.56% | 209,987 | `10576.65`, `645.6` |
| `Hour17` | `str` | 31,431 | 8.97% | 200,265 | `10573.16`, `645.63` |
| `Hour18` | `str` | 40,134 | 11.46% | 180,083 | `10574.85`, `645.66` |
| `Hour19` | `str` | 141,429 | 40.37% | 139,647 | `10573.67`, `645.63` |
| `Hour20` | `str` | 175,946 | 50.22% | 133,311 | `10574.26`, `645.6` |
| `Hour21` | `str` | 177,075 | 50.54% | 132,929 | `10895.48`, `645.57` |
| `Hour22` | `str` | 177,886 | 50.77% | 132,269 | `13496.85`, `645.45` |
| `Hour23` | `str` | 179,788 | 51.32% | 130,246 | `17401.35`, `645.21` |
| `Hour24` | `str` | 180,260 | 51.45% | 130,335 | `19974.2`, `644.67` |
| `_fuente` | `str` | 0 | 0.00% | 1 | `XM` |
| `_origen` | `str` | 0 | 0.00% | 1 | `https://servapibi.xm.com.co/hourly ` |
| `_extraido_en` | `str` | 0 | 0.00% | 1 | `2026-10-23T01:35:41+00:00` |

### 2.13 `xm_listado_recursos.parquet`

- **Fuente:** `XM` (`https://servapibi.xm.com.co/lists MetricId=ListadoRecursos`)
- **Filas:** 2,494 | **Columnas:** 14
- **Filas duplicadas:** 2 (exactas incluyendo linaje) / 2 (sobre columnas de negocio)
- **Rango de fechas:** Corte catalogo: 2026-10-22

| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |
|---|---|---:|---:|---:|---|
| `Date` | `str` | 0 | 0.00% | 1 | `2026-10-22` |
| `Id` | `str` | 0 | 0.00% | 1 | `Sistema` |
| `Code` | `str` | 0 | 0.00% | 2,492 | `2QBW`, `2QEK` |
| `Name` | `str` | 0 | 0.00% | 2,492 | `EL POPAL`, `SALTO II` |
| `Type` | `str` | 0 | 0.00% | 6 | `HIDRAULICA`, `TERMICA` |
| `Disp` | `str` | 0 | 0.00% | 2 | `NO DESPACHADO CENTRALMENTE`, `DESPACHADO CENTRALMENTE` |
| `RecType` | `str` | 0 | 0.00% | 9 | `NORMAL`, `FILO DE AGUA` |
| `CompanyCode` | `str` | 0 | 0.00% | 149 | `ISGG`, `ENDG` |
| `EnerSource` | `str` | 0 | 0.00% | 12 | `AGUA`, `BIOGAS` |
| `OperStartdate` | `str` | 0 | 0.00% | 732 | `2014-03-31`, `2014-06-25` |
| `State` | `str` | 0 | 0.00% | 3 | `OPERACION`, `PRUEBAS` |
| `_fuente` | `str` | 0 | 0.00% | 1 | `XM` |
| `_origen` | `str` | 0 | 0.00% | 1 | `https://servapibi.xm.com.co/lists M` |
| `_extraido_en` | `str` | 0 | 0.00% | 1 | `2026-10-23T01:35:45+00:00` |

### 2.14 `xm_precio_bolsa.parquet`

- **Fuente:** `XM` (`https://servapibi.xm.com.co/hourly MetricId=PrecBolsNaci`)
- **Filas:** 1,004 | **Columnas:** 30
- **Filas duplicadas:** 0 (exactas incluyendo linaje) / 0 (sobre columnas de negocio)
- **Rango de fechas:** 2024-01-01 a 2026-09-30

| Columna | Tipo de dato | Nulos | % Nulos | Valores únicos | Ejemplo de valores crudos |
|---|---|---:|---:|---:|---|
| `Date` | `str` | 0 | 0.00% | 1,004 | `2024-01-01`, `2024-01-02` |
| `Id` | `str` | 0 | 0.00% | 1 | `Sistema` |
| `code` | `str` | 0 | 0.00% | 1 | `Sistema` |
| `Hour01` | `str` | 0 | 0.00% | 1,000 | `251.91161`, `360.22127` |
| `Hour02` | `str` | 0 | 0.00% | 1,001 | `251.91161`, `360.22127` |
| `Hour03` | `str` | 0 | 0.00% | 1,000 | `251.91161`, `309.82127` |
| `Hour04` | `str` | 0 | 0.00% | 1,001 | `281.91161`, `284.32127` |
| `Hour05` | `str` | 0 | 0.00% | 1,001 | `281.91161`, `309.82127` |
| `Hour06` | `str` | 0 | 0.00% | 1,002 | `251.91161`, `317.32127` |
| `Hour07` | `str` | 0 | 0.00% | 1,002 | `152.91161`, `317.32127` |
| `Hour08` | `str` | 0 | 0.00% | 1,001 | `95.85161`, `360.22127` |
| `Hour09` | `str` | 0 | 0.00% | 1,002 | `95.85161`, `379.32127` |
| `Hour10` | `str` | 0 | 0.00% | 1,002 | `95.85161`, `317.32127` |
| `Hour11` | `str` | 0 | 0.00% | 1,002 | `95.85161`, `360.22127` |
| `Hour12` | `str` | 0 | 0.00% | 1,002 | `152.91161`, `379.32127` |
| `Hour13` | `str` | 0 | 0.00% | 1,002 | `152.91161`, `419.32127` |
| `Hour14` | `str` | 0 | 0.00% | 1,001 | `152.91161`, `419.32127` |
| `Hour15` | `str` | 0 | 0.00% | 1,000 | `152.91161`, `419.32127` |
| `Hour16` | `str` | 0 | 0.00% | 1,001 | `251.91161`, `419.32127` |
| `Hour17` | `str` | 0 | 0.00% | 1,001 | `281.91161`, `419.32127` |
| `Hour18` | `str` | 0 | 0.00% | 998 | `281.91161`, `419.32127` |
| `Hour19` | `str` | 0 | 0.00% | 999 | `301.23261`, `449.32127` |
| `Hour20` | `str` | 0 | 0.00% | 999 | `301.23261`, `449.32127` |
| `Hour21` | `str` | 0 | 0.00% | 1,000 | `301.23261`, `449.32127` |
| `Hour22` | `str` | 0 | 0.00% | 1,000 | `301.23261`, `449.32127` |
| `Hour23` | `str` | 0 | 0.00% | 1,000 | `301.23261`, `419.32127` |
| `Hour24` | `str` | 0 | 0.00% | 999 | `290.91161`, `419.32127` |
| `_fuente` | `str` | 0 | 0.00% | 1 | `XM` |
| `_origen` | `str` | 0 | 0.00% | 1 | `https://servapibi.xm.com.co/hourly ` |
| `_extraido_en` | `str` | 0 | 0.00% | 1 | `2026-10-23T01:34:59+00:00` |

---

## 3. Hallazgos de calidad de datos (con evidencia numérica)

A continuación se documentan **8 hallazgos de calidad** identificados sobre los archivos crudos de la capa bronce, junto con su dimensión DAMA afectada y su evidencia numérica exacta:

### Hallazgo 1 · Filas parásitas (títulos, notas, filas vacías y totales) en el Excel de EnerAndes (*Validez / Estructura*)
- **Descripción:** Al extraer el archivo interno `ventas_enerandes_2023_2026.xlsx` sin modificar (`header=None`), las hojas no empiezan directamente con datos tabulares. En `enerandes_ventas_2023` (1,114 filas) y `enerandes_ventas_2024` (1,114 filas) la fila `0` es el encabezado y la última fila (`1113`) es una fila de resumen `TOTAL` con celdas vacías (`NaN`). En `enerandes_ventas_2025` (1,117 filas) y `enerandes_ventas_2026` (839 filas) existen además **3 filas previas al encabezado** (fila `0` con el título del reporte, fila `1` con la nota `'Fuente: sistema comercial. Uso interno.'` y fila `2` completamente vacía).
- **Evidencia numérica:** En total hay **14 filas no transaccionales** entre las 4 hojas (4 filas de encabezados incrustados, 4 filas `TOTAL`, 4 filas de títulos/notas y 2 filas en blanco), lo que explica que en `enerandes_ventas_2025` las columnas `col_1` a `col_6` presenten al menos **4 filas nulas adicionales** (0.36% a 0.90% de nulos por columna).

### Hallazgo 2 · Esquemas y formatos de fecha heterogéneos entre las hojas 2023–2026 de EnerAndes (*Consistencia / Validez*)
- **Descripción:** Cada hoja anual del Excel de EnerAndes tiene nombres de columna distintos y formatos de fecha incompatibles entre sí, además de que la hoja 2024 tiene **11 columnas** (`col_0` a `col_7` + 3 de linaje) mientras que 2023, 2025 y 2026 tienen **10 columnas** (`col_0` a `col_6` + 3 de linaje).
- **Evidencia numérica:**
  - `enerandes_ventas_2023`: encabezado `Fecha` con formato `AAAA-MM` (ej. `2023-04`) en las 1,112 filas de datos.
  - `enerandes_ventas_2024`: encabezado `PERIODO` con **3 formatos mezclados** en la misma columna (`jun-24`, `09/2024`, `2024-07`).
  - `enerandes_ventas_2025`: encabezado `mes` en la fila índice 3 con formato `MM/AAAA` (ej. `06/2025`).
  - `enerandes_ventas_2026`: encabezado `Fecha corte` en la fila índice 3 con formato `DD/MM/AAAA` (ej. `01/03/2026`).

### Hallazgo 3 · Falta de estandarización en nombres de municipios y tipos de compra en EnerAndes (*Consistencia / Integridad referencial*)
- **Descripción:** Los nombres de municipios y los tipos de contrato en EnerAndes presentan variaciones de mayúsculas/minúsculas, tildes omitidas y espacios al final, lo que impide cruzarlos directamente con `ideam_precipitacion_diaria` o `dane_divipola` sin normalización.
- **Evidencia numérica:** En las 4 hojas de EnerAndes aparecen **32 cadenas distintas** en la columna de municipio (`col_1`), pero al normalizar mayúsculas, espacios y tildes se reducen a solo **20 municipios reales** de Antioquia (de los 125 municipios oficiales de Antioquia en `dane_divipola`). Por ejemplo, para Medellín coexisten las variantes `{'Medellín': 248, 'Medellín D.E.': 8, 'Medellín ': 7, 'Medellin': 5, 'medellin': 4, 'MEDELLÍN': 2}`. De igual forma, en la columna de modalidad de compra (`col_3`) coexisten **4 variantes** para solo 2 conceptos de negocio: `{'Bolsa': 1975, 'Contrato': 1974, 'CONTRATOS': 117, 'bolsa': 104}`.

### Hallazgo 4 · Unidades mezcladas (`kWh` vs `MWh`), valores negativos imposibles y filas duplicadas en EnerAndes (*Validez / Unicidad / Completitud*)
- **Descripción:** La hoja 2024 mezcla mediciones en kilovatios-hora (`kWh`) y megavatios-hora (`MWh`, 1 MWh = 1,000 kWh), y todas las hojas contienen registros duplicados, celdas de energía vacías y consumos negativos físicamente imposibles.
- **Evidencia numérica:**
  - **Unidades mezcladas (2024):** distribución en `col_5` (`UNIDAD`): `{'kWh': 765, 'MWh': 347}`.
  - **Registros duplicados:** **120 filas duplicadas** en total sobre las columnas de negocio (`2023`: 32, `2024`: 32, `2025`: 32, `2026`: 24).
  - **Valores negativos en energía (`col_4`):** **18 registros con consumo negativo** (`2023`: 7, `2024`: 3, `2025`: 4, `2026`: 4).
  - **Valores nulos en energía (`col_4`):** **27 registros de ventas sin dato de energía**.

### Hallazgo 5 · Rezago de publicación en datos abiertos del IDEAM frente a XM (*Oportunidad*)
- **Descripción:** Mientras que la API de XM entrega series completas hasta el último día consultado (`2026-09-30`), los datasets abiertos del IDEAM en `datos.gov.co` presentan un rezago de publicación de aproximadamente 2.5 meses.
- **Evidencia numérica:** En `ideam_precipitacion_diaria.parquet` (29,804 filas) la última fecha con datos reportados es **`2026-07-24`**, y en `ideam_temperatura_diaria.parquet` (17,349 filas) la última fecha disponible es **`2026-07-24`**, frente a **`2026-09-30`** en `xm_precio_bolsa.parquet` (1,004 días completos entre `2024-01-01` y `2026-09-30`). Las ventanas semanales posteriores a esa fecha devuelven `0 filas`.

### Hallazgo 6 · Números almacenados como texto y separador decimal con coma en `dane_divipola` (*Validez / Tipos de datos*)
- **Descripción:** Siguiendo la regla de la capa bronce, todas las fuentes conservan los valores como texto (`object`/`str`) o tipos crudos de origen. En particular, el catálogo oficial `dane_divipola.parquet` entrega las coordenadas geográficas (`latitud` y `longitud`) usando **coma (`,`) como separador decimal**, mientras que el IDEAM usa **punto (`.`)**.
- **Evidencia numérica:** De las **1,122 filas** de `dane_divipola.parquet`, **1,122 registros** (100.00%) contienen coma decimal en `latitud` (ej. `'6,246631'` para Medellín), lo que produciría `NULL` al hacer `CAST(latitud AS DOUBLE)` en SQL si no se reemplaza primero `','` por `'.'` en la capa plata.

### Hallazgo 7 · Registros duplicados en el catálogo `xm_listado_recursos` y cadenas vacías en `xm_generacion_recurso` (*Unicidad / Completitud*)
- **Descripción:** El catálogo de plantas `xm_listado_recursos.parquet` contiene registros duplicados para ciertos códigos de recurso (`Code`), y en `xm_generacion_recurso.parquet` las horas sin generación vienen representadas como cadenas vacías (`''`) o `'0'` en lugar de `NULL`.
- **Evidencia numérica:** En `xm_listado_recursos.parquet` hay **2,494 filas** pero solo **2,492 códigos únicos**, existiendo **2 filas duplicadas exactas** (códigos repetidos: `['5J8H', '5PUN']`). Además, de los 2,492 recursos del catálogo, solo **632 recursos** aparecen generando en `xm_generacion_recurso.parquet`, donde sobre **8,408,280 celdas horarias** (`Hour01`..`Hour24`) hay **2,472,918 celdas vacías/nulas** y **0 celdas en `'0'`**.

### Hallazgo 8 · Desalineación de granularidad temporal y formato ancho vs. largo entre las 5 fuentes (*Consistencia / Modelado*)
- **Descripción:** Las cinco fuentes operan en escalas temporales y estructuras distintas que impiden unirlas sin transformación previa en la capa plata/oro:
- **Evidencia numérica:**
  - **Horaria en formato ancho (24 columnas `Hour01`..`Hour24`):** `xm_precio_bolsa` (1,004 filas = 24,096 horas), `xm_demanda` (1,004 filas) y `xm_generacion_recurso` (350,345 filas planta-día).
  - **Diaria en formato largo (1 valor por fila):** `xm_embalses` (1,004 días), `xm_aportes` (1,004 días), `ideam_precipitacion_diaria` (29,804 estación-día) e `ideam_temperatura_diaria` (17,349 estación-día).
  - **Trimestral móvil:** `noaa_oni` (920 trimestres móviles desde `1950-DJF` hasta `2026-JAS`).
  - **Mensual por municipio y segmento:** EnerAndes (4,184 filas brutas entre 2023 y 2026).

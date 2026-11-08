-- Tabla de HECHOS: clima diario por estacion meteorologica del IDEAM en Antioquia.
-- Grano: una fecha (dia) y una estacion meteorologica (codigo_estacion).

with precip as (
    select
        cast(fecha as date)                 as fecha,
        cast(codigo_estacion as varchar)    as codigo_estacion,
        cast(cod_mpio as varchar)           as cod_mpio,
        cast(precipitacion_mm as double)    as precipitacion_mm,
        cast(n_obs as integer)              as n_obs_precip
    from {{ ref('stg_ideam_precipitacion') }}
),
temp as (
    select
        cast(fecha as date)                 as fecha,
        cast(codigo_estacion as varchar)    as codigo_estacion,
        cast(cod_mpio as varchar)           as cod_mpio,
        cast(temp_media_c as double)        as temp_media_c,
        cast(temp_min_c as double)          as temp_min_c,
        cast(temp_max_c as double)          as temp_max_c,
        cast(n_obs as integer)              as n_obs_temp
    from {{ ref('stg_ideam_temperatura') }}
)
select
    strftime(coalesce(p.fecha, t.fecha), '%Y-%m-%d') || '|' || coalesce(p.codigo_estacion, t.codigo_estacion) as clima_diario_id,
    coalesce(p.fecha, t.fecha)                      as fecha,
    coalesce(p.codigo_estacion, t.codigo_estacion)  as codigo_estacion,
    coalesce(p.cod_mpio, t.cod_mpio)                as municipio_id,
    coalesce(p.cod_mpio, t.cod_mpio)                as cod_mpio,
    p.precipitacion_mm,
    t.temp_media_c,
    t.temp_min_c,
    t.temp_max_c
from precip as p
full outer join temp as t
    on p.fecha = t.fecha
   and p.codigo_estacion = t.codigo_estacion
order by fecha, codigo_estacion

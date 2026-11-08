-- Dimension ESTACION: una fila por estacion meteorologica del IDEAM en Antioquia, vinculada a su municipio DIVIPOLA.
-- Grano: una estacion meteorologica (codigo_estacion).

with estaciones_unidas as (
    select
        cast(codigo_estacion as varchar) as codigo_estacion,
        cast(nombre_estacion as varchar) as nombre_estacion,
        cast(cod_mpio as varchar)        as cod_mpio,
        cast(municipio as varchar)       as municipio,
        cast(latitud as double)          as latitud,
        cast(longitud as double)         as longitud,
        1                                as mide_precipitacion,
        0                                as mide_temperatura
    from {{ ref('stg_ideam_precipitacion') }}
    union all
    select
        cast(codigo_estacion as varchar) as codigo_estacion,
        cast(nombre_estacion as varchar) as nombre_estacion,
        cast(cod_mpio as varchar)        as cod_mpio,
        cast(municipio as varchar)       as municipio,
        cast(latitud as double)          as latitud,
        cast(longitud as double)         as longitud,
        0                                as mide_precipitacion,
        1                                as mide_temperatura
    from {{ ref('stg_ideam_temperatura') }}
)
select
    codigo_estacion,
    max(nombre_estacion)                 as nombre_estacion,
    max(cod_mpio)                        as municipio_id,
    max(cod_mpio)                        as cod_mpio,
    max(municipio)                       as municipio,
    round(avg(latitud), 6)               as latitud,
    round(avg(longitud), 6)              as longitud,
    max(mide_precipitacion) = 1          as mide_precipitacion,
    max(mide_temperatura) = 1            as mide_temperatura
from estaciones_unidas
group by codigo_estacion
order by codigo_estacion

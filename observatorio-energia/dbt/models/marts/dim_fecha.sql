-- Dimension FECHA: una fila por dia calendario (2023-01-01 a 2026-12-31), con mes,
-- trimestre, dia de la semana y fase ENSO de la NOAA.
-- Grano: un dia (fecha).

with serie_dias as (
    select cast(unnest(generate_series(date '2023-01-01', date '2026-12-31', interval '1 day')) as date) as fecha
),
noaa as (
    select
        cast(anio as integer)       as anio,
        cast(mes as integer)        as mes,
        trimestre_movil,
        cast(oni as double)         as oni,
        fase_enso
    from {{ ref('stg_noaa_oni') }}
)
select
    d.fecha                                                                 as fecha,
    cast(strftime(d.fecha, '%Y%m%d') as integer)                            as fecha_id,
    cast(strftime(d.fecha, '%Y%m') as integer)                              as mes_id,
    strftime(d.fecha, '%Y-%m')                                              as periodo,
    cast(extract(year from d.fecha) as integer)                             as anio,
    cast(extract(quarter from d.fecha) as integer)                          as trimestre,
    cast(extract(month from d.fecha) as integer)                            as mes,
    case extract(month from d.fecha)
        when 1 then 'Enero'
        when 2 then 'Febrero'
        when 3 then 'Marzo'
        when 4 then 'Abril'
        when 5 then 'Mayo'
        when 6 then 'Junio'
        when 7 then 'Julio'
        when 8 then 'Agosto'
        when 9 then 'Septiembre'
        when 10 then 'Octubre'
        when 11 then 'Noviembre'
        when 12 then 'Diciembre'
    end                                                                     as nombre_mes,
    cast(extract(day from d.fecha) as integer)                              as dia_mes,
    cast(extract(isodow from d.fecha) as integer)                           as dia_semana_iso,
    case extract(isodow from d.fecha)
        when 1 then 'Lunes'
        when 2 then 'Martes'
        when 3 then 'Miércoles'
        when 4 then 'Jueves'
        when 5 then 'Viernes'
        when 6 then 'Sábado'
        when 7 then 'Domingo'
    end                                                                     as nombre_dia_semana,
    extract(isodow from d.fecha) in (6, 7)                                  as es_fin_de_semana,
    coalesce(n.trimestre_movil, 'N/A')                                      as trimestre_movil_oni,
    round(coalesce(n.oni, 0.0), 2)                                          as oni,
    coalesce(n.fase_enso, 'Neutral')                                        as fase_enso
from serie_dias as d
left join noaa as n
    on extract(year from d.fecha) = n.anio
   and extract(month from d.fecha) = n.mes
order by d.fecha

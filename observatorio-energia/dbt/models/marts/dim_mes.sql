-- Dimension MES: una fila por cada mes del estudio (2023 a 2026), enriquecida con el ONI y la fase ENSO.
-- Grano: un mes (mes_id = AAAAMM).

with meses_ventas as (
    select distinct
        cast(replace(periodo, '-', '') as integer)      as mes_id,
        periodo,
        cast(left(periodo, 4) as integer)               as anio,
        cast(right(periodo, 2) as integer)              as mes,
        (cast(right(periodo, 2) as integer) + 2) // 3   as trimestre
    from {{ ref('stg_ventas') }}
)
select
    m.mes_id,
    m.periodo,
    m.anio,
    m.mes,
    m.trimestre,
    round(coalesce(n.oni, 0.0), 2)                      as oni,
    coalesce(n.fase_enso, 'Neutral')                    as fase_enso
from meses_ventas as m
left join {{ ref('stg_noaa_oni') }} as n
    on m.periodo = n.periodo
order by m.mes_id

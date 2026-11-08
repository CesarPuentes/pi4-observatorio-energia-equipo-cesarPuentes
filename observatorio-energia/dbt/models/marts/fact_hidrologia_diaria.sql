-- Tabla de HECHOS: hidrologia diaria del SIN (embalses y aportes hidricos de XM).
-- Grano: una fecha (dia).

select
    cast(e.fecha as date)                   as fecha,
    cast(e.volumen_util_pct as double)      as volumen_util_pct,
    cast(a.aportes_energia_kwh as double)   as aportes_energia_kwh,
    round(cast(a.aportes_energia_kwh as double) / 1000000.0, 4) as aportes_energia_gwh
from {{ ref('stg_xm_embalses') }} as e
inner join {{ ref('stg_xm_aportes') }} as a
    on cast(e.fecha as date) = cast(a.fecha as date)
order by fecha

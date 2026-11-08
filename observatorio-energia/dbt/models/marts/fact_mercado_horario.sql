-- Tabla de HECHOS: precio de bolsa y demanda nacional por hora (XM).
-- Grano: una fecha (dia) y una hora del dia (1 a 24).

select
    strftime(cast(p.fecha as date), '%Y-%m-%d') || '|' || lpad(cast(p.hora as varchar), 2, '0') as mercado_horario_id,
    cast(p.fecha as date)                   as fecha,
    cast(p.hora as integer)                 as hora,
    cast(p.precio_bolsa_cop_kwh as double)  as precio_bolsa_cop_kwh,
    cast(d.demanda_real_kwh as double)      as demanda_real_kwh,
    round(cast(d.demanda_real_kwh as double) / 1000.0, 4) as demanda_real_mwh,
    round(cast(p.precio_bolsa_cop_kwh as double) * cast(d.demanda_real_kwh as double), 2) as costo_horario_bolsa_cop
from {{ ref('stg_xm_precio_bolsa') }} as p
inner join {{ ref('stg_xm_demanda') }} as d
    on cast(p.fecha as date) = cast(d.fecha as date)
   and cast(p.hora as integer) = cast(d.hora as integer)
order by fecha, hora

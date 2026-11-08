-- Tabla de HECHOS: las ventas de energia de EnerAndes (2023 a 2026).
-- Grano: un mes, un municipio, un segmento y un tipo de compra.
-- Conserva las columnas del modelo de la clase (mes_id, municipio_id, segmento_id, tipo_compra,
-- energia_kwh, valor_cop, clientes) y agrega fecha (primer dia del mes) para cruzar con dim_fecha.

select
    v.periodo || '|' || v.divipola || '|' || cast(s.segmento_id as varchar) || '|' || v.tipo_compra as venta_id,
    cast(replace(v.periodo, '-', '') as integer)    as mes_id,
    cast(v.periodo || '-01' as date)                as fecha,
    v.divipola                                      as municipio_id,
    v.divipola                                      as cod_mpio,
    s.segmento_id,
    v.tipo_compra,
    cast(v.energia_kwh as double)                   as energia_kwh,
    cast(v.valor_cop as double)                     as valor_cop,
    cast(v.clientes as integer)                     as clientes,
    round(cast(v.valor_cop as double) / nullif(cast(v.energia_kwh as double), 0), 2) as precio_unitario_cop_kwh
from {{ ref('stg_ventas') }} as v
join {{ ref('dim_segmento') }} as s
    on v.segmento = s.segmento

-- Tabla de HECHOS: generacion electrica horaria por planta/recurso del SIN (XM).
-- Grano: una fecha (dia), una hora del dia (1 a 24) y una planta (codigo_recurso).

select
    cast(fecha as date)             as fecha,
    cast(hora as integer)           as hora,
    cast(codigo_recurso as varchar) as codigo_recurso,
    cast(generacion_kwh as double)  as generacion_kwh
from {{ ref('stg_xm_generacion_recurso') }}

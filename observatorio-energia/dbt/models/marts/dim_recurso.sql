-- Dimension RECURSO: una fila por planta o unidad de generacion del SIN (a partir de ListadoRecursos).
-- Grano: un recurso de generacion (codigo_recurso).

select
    cast(codigo_recurso as varchar)         as codigo_recurso,
    cast(nombre_recurso as varchar)         as nombre_recurso,
    cast(tipo_generacion as varchar)        as tipo_generacion,
    cast(fuente_energia as varchar)         as fuente_energia,
    cast(tipo_despacho as varchar)          as tipo_despacho,
    cast(tipo_recurso as varchar)           as tipo_recurso,
    cast(codigo_agente as varchar)          as codigo_agente,
    cast(fecha_operacion as date)           as fecha_operacion,
    cast(estado as varchar)                 as estado,
    tipo_generacion in ('HIDRAULICA', 'SOLAR', 'EOLICA') as es_renovable
from {{ ref('stg_xm_listado_recursos') }}
order by codigo_recurso

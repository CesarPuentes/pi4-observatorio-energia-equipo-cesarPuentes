-- Dimension MUNICIPIO: una fila por municipio de Colombia con su codigo oficial DIVIPOLA (DANE).
-- Conserva municipio_id (nombre de llave de la clase) y cod_mpio para cruces con ventas y clima.
-- Grano: un municipio (municipio_id / cod_mpio).

select
    cast(cod_mpio as varchar)       as municipio_id,
    cast(cod_mpio as varchar)       as cod_mpio,
    cast(municipio as varchar)      as municipio,
    cast(cod_dpto as varchar)       as cod_dpto,
    cast(departamento as varchar)   as departamento,
    cast(tipo_municipio as varchar) as tipo_municipio,
    round(cast(latitud as double), 6)  as latitud,
    round(cast(longitud as double), 6) as longitud
from {{ ref('stg_divipola') }}
order by municipio_id

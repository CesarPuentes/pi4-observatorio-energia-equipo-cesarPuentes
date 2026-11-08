-- Staging: lee el precio de bolsa horario limpio desde la capa plata.
select *
from {{ source('plata', 'xm_precio_bolsa') }}

-- Staging: lee el volumen util diario de embalses desde la capa plata.
select *
from {{ source('plata', 'xm_embalses') }}

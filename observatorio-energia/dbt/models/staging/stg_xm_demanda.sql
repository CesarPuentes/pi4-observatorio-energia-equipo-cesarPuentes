-- Staging: lee la demanda real horaria limpia desde la capa plata.
select *
from {{ source('plata', 'xm_demanda') }}

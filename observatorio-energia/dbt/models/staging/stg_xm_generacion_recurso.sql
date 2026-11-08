-- Staging: lee la generacion horaria por planta desde la capa plata.
select *
from {{ source('plata', 'xm_generacion_recurso') }}

-- Staging: lee la precipitacion diaria limpia del IDEAM desde la capa plata.
select *
from {{ source('plata', 'ideam_precipitacion') }}

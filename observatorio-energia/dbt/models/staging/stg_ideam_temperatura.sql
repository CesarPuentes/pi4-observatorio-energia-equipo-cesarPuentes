-- Staging: lee la temperatura diaria limpia del IDEAM desde la capa plata.
select *
from {{ source('plata', 'ideam_temperatura') }}

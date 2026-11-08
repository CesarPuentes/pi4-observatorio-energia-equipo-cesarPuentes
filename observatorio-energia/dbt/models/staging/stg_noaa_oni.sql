-- Staging: lee el indice ONI mensual y la fase ENSO desde la capa plata.
select *
from {{ source('plata', 'noaa_oni') }}

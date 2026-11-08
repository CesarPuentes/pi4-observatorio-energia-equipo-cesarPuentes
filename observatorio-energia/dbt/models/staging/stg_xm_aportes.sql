-- Staging: lee los aportes hidricos diarios desde la capa plata.
select *
from {{ source('plata', 'xm_aportes') }}

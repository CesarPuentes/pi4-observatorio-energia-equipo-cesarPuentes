-- Staging: lee el catalogo limpio de plantas (ListadoRecursos) desde la capa plata.
select *
from {{ source('plata', 'xm_listado_recursos') }}

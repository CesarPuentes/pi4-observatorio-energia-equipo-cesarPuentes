-- Staging: lee el catalogo oficial DANE DIVIPOLA limpio desde la capa plata.
select *
from {{ source('plata', 'dane_divipola') }}

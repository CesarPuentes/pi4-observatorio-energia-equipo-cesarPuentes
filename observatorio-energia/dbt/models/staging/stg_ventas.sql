-- Staging: lee la tabla de ventas de la capa plata, sin cambiarla.
-- dbt reemplaza source('plata', 'enerandes_ventas') por la ruta
-- data/silver/enerandes_ventas.parquet (la dice sources.yml).
-- Se crea como VISTA (dbt_project.yml): los demas modelos leen de aqui.

select *
from {{ source('plata', 'enerandes_ventas') }}

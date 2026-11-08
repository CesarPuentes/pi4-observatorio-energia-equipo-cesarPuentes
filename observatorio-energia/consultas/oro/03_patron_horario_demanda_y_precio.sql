-- Pregunta de Negocio 4: Patrones de Demanda y Precio por Hora Pico / Valle
-- ¿Cuales son las horas pico de demanda y mayor precio de bolsa en el sistema electrico colombiano?

SELECT
    h.hora,
    h.franja_horaria,
    h.periodo_dia,
    h.tipo_franja_demanda,
    ROUND(AVG(m.demanda_real_kwh) / 1e3, 1)     AS demanda_media_mwh,
    ROUND(MAX(m.demanda_real_kwh) / 1e3, 1)     AS demanda_max_mwh,
    ROUND(AVG(m.precio_bolsa_cop_kwh), 1)       AS precio_bolsa_medio_cop_kwh,
    ROUND(MAX(m.precio_bolsa_cop_kwh), 1)       AS precio_bolsa_max_cop_kwh
FROM fact_mercado_horario m
INNER JOIN dim_hora h
    ON m.hora = h.hora
GROUP BY h.hora, h.franja_horaria, h.periodo_dia, h.tipo_franja_demanda
ORDER BY demanda_media_mwh DESC
LIMIT 10;

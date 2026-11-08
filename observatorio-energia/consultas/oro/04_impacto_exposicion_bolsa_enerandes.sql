-- Pregunta de Negocio 5: Impacto en el Negocio de EnerAndes (Exposicion a Bolsa por Municipio y Segmento)
-- ¿Que municipios y segmentos de clientes de EnerAndes concentran el mayor volumen y tarifa en compras de Bolsa?

SELECT
    m.cod_mpio,
    m.municipio,
    ROUND(SUM(v.energia_kwh) / 1e6, 2)                                                  AS energia_total_gwh,
    ROUND(SUM(CASE WHEN v.tipo_compra = 'Bolsa' THEN v.energia_kwh ELSE 0 END) / 1e6, 2) AS energia_bolsa_gwh,
    ROUND(
        100.0 * SUM(CASE WHEN v.tipo_compra = 'Bolsa' THEN v.energia_kwh ELSE 0 END)
        / SUM(v.energia_kwh),
        1
    )                                                                                    AS pct_exposicion_bolsa,
    ROUND(
        SUM(CASE WHEN v.tipo_compra = 'Bolsa' THEN v.valor_cop ELSE 0 END)
        / NULLIF(SUM(CASE WHEN v.tipo_compra = 'Bolsa' THEN v.energia_kwh ELSE 0 END), 0),
        1
    )                                                                                    AS tarifa_media_bolsa_cop_kwh,
    ROUND(
        SUM(CASE WHEN v.tipo_compra = 'Contrato' THEN v.valor_cop ELSE 0 END)
        / NULLIF(SUM(CASE WHEN v.tipo_compra = 'Contrato' THEN v.energia_kwh ELSE 0 END), 0),
        1
    )                                                                                    AS tarifa_media_contrato_cop_kwh
FROM fact_ventas_mensual v
INNER JOIN dim_municipio m
    ON v.cod_mpio = m.cod_mpio
GROUP BY m.cod_mpio, m.municipio
ORDER BY energia_bolsa_gwh DESC
LIMIT 10;

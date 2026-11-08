-- Pregunta de Negocio 6 (Propia): Cruce Clima Local (IDEAM) + Municipio (DIVIPOLA) + Ventas EnerAndes
-- ¿Como se relacionan la precipitacion y la temperatura local en los municipios de Antioquia con las ventas de EnerAndes?

WITH clima_mensual_mpio AS (
    SELECT
        DATE_TRUNC('month', c.fecha)    AS fecha_mes,
        c.cod_mpio,
        SUM(c.precipitacion_mm)         AS lluvia_mensual_mm,
        AVG(c.temp_media_c)             AS temp_media_mensual_c
    FROM fact_clima_diario c
    GROUP BY 1, 2
),
ventas_mensual_mpio AS (
    SELECT
        v.fecha                         AS fecha_mes,
        v.cod_mpio,
        SUM(v.energia_kwh) / 1e6        AS ventas_gwh,
        SUM(v.valor_cop) / 1e6          AS facturado_millones_cop
    FROM fact_ventas_mensual v
    GROUP BY 1, 2
)
SELECT
    m.cod_mpio,
    m.municipio,
    COUNT(DISTINCT v.fecha_mes)                     AS meses_con_cruce,
    ROUND(AVG(cm.lluvia_mensual_mm), 1)             AS lluvia_promedio_mes_mm,
    ROUND(AVG(cm.temp_media_mensual_c), 2)          AS temp_media_c,
    ROUND(SUM(v.ventas_gwh), 2)                     AS energia_vendida_gwh,
    ROUND(SUM(v.facturado_millones_cop), 1)         AS facturacion_total_mm_cop
FROM ventas_mensual_mpio v
INNER JOIN clima_mensual_mpio cm
    ON v.fecha_mes = cm.fecha_mes
   AND v.cod_mpio = cm.cod_mpio
INNER JOIN dim_municipio m
    ON v.cod_mpio = m.cod_mpio
GROUP BY m.cod_mpio, m.municipio
ORDER BY energia_vendida_gwh DESC;

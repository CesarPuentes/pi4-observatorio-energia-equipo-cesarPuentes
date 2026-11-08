-- Pregunta de Negocio 3: Matriz de Generacion por Tecnologia y Fase ENSO
-- ¿Que proporcion de la energia viene de fuente hidraulica, termica, solar y cogeneracion, y como cambia en El Niño?

WITH gen_fase AS (
    SELECT
        f.fase_enso,
        r.tipo_generacion,
        SUM(g.generacion_kwh) / 1e6 AS generacion_gwh
    FROM fact_generacion_recurso g
    INNER JOIN dim_fecha f
        ON g.fecha = f.fecha
    INNER JOIN dim_recurso r
        ON g.codigo_recurso = r.codigo_recurso
    WHERE r.tipo_generacion <> 'NO ESPECIFICADO'
    GROUP BY f.fase_enso, r.tipo_generacion
)
SELECT
    fase_enso,
    tipo_generacion,
    ROUND(generacion_gwh, 1) AS generacion_gwh,
    ROUND(
        100.0 * generacion_gwh / SUM(generacion_gwh) OVER (PARTITION BY fase_enso),
        2
    ) AS participacion_pct
FROM gen_fase
ORDER BY
    CASE fase_enso WHEN 'El Niño' THEN 1 WHEN 'Neutral' THEN 2 ELSE 3 END,
    generacion_gwh DESC;

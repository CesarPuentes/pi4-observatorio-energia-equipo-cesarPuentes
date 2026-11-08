-- Pregunta de Negocio 1 y 2: Riesgo hidrico y Clima (ENSO) -> Precio de Bolsa
-- ¿Como cambian el volumen util de los embalses, los aportes hidricos y el precio de bolsa segun la fase ENSO?

WITH mercado_diario AS (
    SELECT
        fecha,
        AVG(precio_bolsa_cop_kwh)       AS precio_bolsa_dia_cop_kwh,
        SUM(demanda_real_kwh) / 1e6     AS demanda_dia_gwh
    FROM fact_mercado_horario
    GROUP BY fecha
)
SELECT
    f.fase_enso                                         AS fase_enso,
    COUNT(DISTINCT m.fecha)                             AS dias_operacion,
    ROUND(AVG(f.oni), 2)                                AS oni_promedio_c,
    ROUND(AVG(h.volumen_util_pct), 2)                   AS embalses_volumen_util_pct,
    ROUND(AVG(h.aportes_energia_gwh), 2)                AS aportes_hidricos_gwh_dia,
    ROUND(AVG(m.precio_bolsa_dia_cop_kwh), 1)           AS precio_bolsa_promedio_cop_kwh,
    ROUND(MAX(m.precio_bolsa_dia_cop_kwh), 1)           AS precio_bolsa_max_dia_cop_kwh,
    ROUND(AVG(m.demanda_dia_gwh), 2)                    AS demanda_promedio_gwh_dia
FROM mercado_diario m
INNER JOIN dim_fecha f
    ON m.fecha = f.fecha
INNER JOIN fact_hidrologia_diaria h
    ON m.fecha = h.fecha
GROUP BY f.fase_enso
ORDER BY precio_bolsa_promedio_cop_kwh DESC;

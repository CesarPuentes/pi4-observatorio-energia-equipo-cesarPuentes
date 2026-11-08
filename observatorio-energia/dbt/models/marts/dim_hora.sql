-- Dimension HORA: una fila por hora del dia (1 a 24, correspondiente a Hour01..Hour24 de XM).
-- Grano: una hora del dia (hora = 1..24).

with horas as (
    select cast(unnest(generate_series(1, 24)) as integer) as hora
)
select
    h.hora                                                                              as hora,
    lpad(cast(h.hora - 1 as varchar), 2, '0') || ':00 - ' || lpad(cast(h.hora as varchar), 2, '0') || ':00' as franja_horaria,
    case
        when h.hora between 1 and 6 then 'Madrugada'
        when h.hora between 7 and 12 then 'Mañana'
        when h.hora between 13 and 18 then 'Tarde'
        else 'Noche'
    end                                                                                 as periodo_dia,
    case
        when h.hora between 19 and 22 then 'Pico'
        when h.hora between 1 and 5 then 'Valle'
        else 'Intermedia'
    end                                                                                 as tipo_franja_demanda,
    h.hora between 7 and 18                                                             as es_horario_solar
from horas as h
order by h.hora

# Mapa del Proyecto y Reporte de Avance

## ¿Por qué se desarrolló la Actividad 1?

El código provisto en clase correspondía a una demostración reducida a la que le faltaban piezas críticas de negocio e ingeniería:

1. **Rango histórico insuficiente:** Los datos iniciales cubrían únicamente el año 2026 (y precipitaciones desde junio), lo que impedía comparar la coyuntura actual frente al fenómeno de El Niño 2023–2024. Por ello, se amplió la ventana histórica de XM desde enero de 2024 y la del IDEAM desde enero de 2025.
2. **Falta de variables explicativas del precio:** Aunque se contaba con el precio de bolsa y el nivel de embalses, no se disponía de la generación por planta (`Gene` por `Recurso` para distinguir generación hidráulica frente a térmica), los aportes hídricos (`AporEner`) ni el comportamiento de la temperatura del aire del IDEAM.
3. **Limitación técnica del extractor de XM:** El script base solo admitía consultas particionadas por fechas (`hourly` y `daily`), por lo que no podía consultar el catálogo maestro de plantas (`ListadoRecursos`) en el endpoint `lists`, el cual no recibe fechas y devuelve la estructura `ListEntities`.
4. **Calidad y gobernabilidad previas a la Capa Plata:** Antes de transformar los datos en la siguiente entrega, fue necesario auditar la calidad de los datos crudos (`docs/perfilamiento.md`), publicar muestras livianas en el repositorio (`data/sample/`) e implementar pruebas unitarias automatizadas con `pytest`.

---

## Primer Commit – Ampliación de la extracción de XM (`#1`)

1. **Actualización de `src/config.py`:**
   - Se modificó `FECHA_INICIO = date(2024, 1, 1)` para cubrir más de dos años de historia (`2024-01-01` a `2026-09-30`).
   - Se añadieron las 3 métricas faltantes a `XM_METRICAS` (`Gene`, `AporEner` y `ListadoRecursos`), completando los 6 datasets requeridos.

2. **Extensión de `src/extract/xm.py`:**
   - En `aplanar()`: se incorporó la condición `elif periodo == "lists":` para iterar sobre `item.get("ListEntities", [])` y desempacar `Date`, `Id` y los atributos de `Values`.
   - En `extraer_metrica()`: se agregó el bloque `if periodo == "lists":` para realizar una única petición `POST` sin parámetros de fecha, manteniendo en el bloque `else:` la descarga por ventanas de 30 días.

3. **Ejecución de la descarga completa de XM:**
   - Dado que en la prueba inicial solo se habían descargado datos de 2026, se ejecutó el extractor con la bandera `--forzar` para regenerar los archivos existentes con el rango `2024–2026` y descargar las 3 métricas nuevas:
     ```bash
     uv run python -m src.extract.xm --forzar
     ```
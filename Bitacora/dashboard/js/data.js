/**
 * Diccionario Completo de Información Técnica (Scripts y Archivos) para los 7 Puntos.
 * Observatorio de Energía & Clima Colombia - EA2 Kimball
 */
const DETALLES_PUNTOS = {
      1: {
        num: "1",
        titulo: "Punto 1 · Limpieza de EnerAndes (Hojas 2023 a 2026)",
        subtitulo: "De 4 hojas heterogéneas con títulos y MWh a 1 tabla limpia en Plata + Cuarentena",
        scripts: [
          {
            path: "src/silver/enerandes.py",
            rol: "Limpieza Principal",
            color: "emerald",
            desc: "Implementa <code>limpiar_enerandes()</code>: busca cabeceras dinámicas en hojas 2023-2026, convierte MWh a kWh (x1,000), estandariza fechas a <code>YYYY-MM</code>, asigna <em>'No informado'</em> a segmentos vacíos y desvía 43 filas sin energía a cuarentena."
          },
          {
            path: "src/quality/esquemas.py",
            rol: "Contrato Pandera",
            color: "cyan",
            desc: "Define <code>ESQUEMA_VENTAS</code>: valida tipos de datos, formato de periodo (<code>^\\d{4}-\\d{2}$</code>), código DIVIPOLA de 5 dígitos, dominios válidos y no-negatividad de energía."
          },
          {
            path: "tests/test_limpieza.py",
            rol: "Pruebas Unitarias",
            color: "purple",
            desc: "Pruebas pytest que validan la limpieza de EnerAndes: descarte de duplicados, factor MWh, consistencia de las 4,007 filas limpias y 43 en cuarentena."
          },
          {
            path: "src/transformar.py",
            rol: "Orquestador",
            color: "amber",
            desc: "Función <code>ejecutar_transformacion()</code> que coordina la carga desde Bronce, la limpieza a Plata, la auditoría y el guardado en Parquet."
          }
        ],
        archivosAntes: [
          "data/bronze/enerandes_ventas_2023.parquet (1,114 filas brutas)",
          "data/bronze/enerandes_ventas_2024.parquet (1,114 filas, MWh y texto)",
          "data/bronze/enerandes_ventas_2025.parquet (1,117 filas, títulos)",
          "data/bronze/enerandes_ventas_2026.parquet (839 filas, notas internas)"
        ],
        archivosDespues: [
          { path: "data/silver/enerandes_ventas.parquet", note: "(4,007 filas limpias)", icon: "✅" },
          { path: "data/silver/enerandes_cuarentena.parquet", note: "(43 filas aisladas con motivo)", icon: "⚠️" }
        ],
        comando: ".venv/bin/python -c \"import pandas as pd; print(pd.read_parquet('data/silver/enerandes_ventas.parquet').head(3))\"",
        comandoLabel: "Inspeccionar muestra limpia de ventas en terminal:"
      },
      2: {
        num: "2",
        titulo: "Punto 2 · Limpieza de XM, IDEAM, NOAA y DANE DIVIPOLA",
        subtitulo: "Despivotar horas, tipar números, cruzar estaciones con municipios y etiquetar ENSO",
        scripts: [
          {
            path: "src/silver/xm.py",
            rol: "XM Mercado",
            color: "cyan",
            desc: "Despivota las 24 columnas horarias (<code>Hour01..Hour24</code>) de precio de bolsa y demanda a filas relacionales, castea valores numéricos a float y normaliza embalses y aportes."
          },
          {
            path: "src/silver/ideam.py",
            rol: "IDEAM Clima",
            color: "amber",
            desc: "Agrega mediciones meteorológicas por día y estación en Antioquia, filtrando y aislando en <code>ideam_cuarentena.parquet</code> las 7 lecturas absurdas &gt; 500 mm."
          },
          {
            path: "src/silver/noaa.py",
            rol: "NOAA Índice ONI",
            color: "blue",
            desc: "Mapea los trimestres móviles (DJF, JFM...) a su mes central calendario e incorpora la columna categórica <code>fase_enso</code> (El Niño, La Niña, Neutro)."
          },
          {
            path: "src/silver/divipola.py",
            rol: "DANE DIVIPOLA",
            color: "emerald",
            desc: "Estandariza los códigos de municipio a cadenas de 5 dígitos y corrige la coma decimal por punto en latitud/longitud convirtiéndolas a <code>float64</code>."
          },
          {
            path: "src/quality/esquemas.py & tests/test_limpieza.py",
            rol: "Contratos & Pruebas",
            color: "purple",
            desc: "Contratos Pandera (<code>ESQUEMA_XM_*</code>, <code>ESQUEMA_IDEAM_*</code>, <code>ESQUEMA_NOAA_ONI</code>, <code>ESQUEMA_DANE_DIVIPOLA</code>) y pruebas unitarias que verifican los rangos y despivotes."
          }
        ],
        archivosAntes: [
          "data/bronze/xm_precio_bolsa.parquet (24 cols texto)",
          "data/bronze/xm_demanda.parquet & xm_generacion_recurso.parquet",
          "data/bronze/xm_embalses.parquet & xm_aportes.parquet",
          "data/bronze/xm_listado_recursos.parquet (2 duplicados)",
          "data/bronze/ideam_precipitacion_diaria.parquet (7 extremos)",
          "data/bronze/ideam_temperatura_diaria.parquet",
          "data/bronze/noaa_oni.parquet (trimestres móviles)",
          "data/bronze/dane_divipola.parquet (coordenadas con coma)"
        ],
        archivosDespues: [
          { path: "data/silver/xm_precio_bolsa.parquet", note: "(24,096 filas horarias)", icon: "✅" },
          { path: "data/silver/xm_demanda.parquet & xm_generacion_recurso.parquet", note: "", icon: "✅" },
          { path: "data/silver/xm_embalses.parquet & xm_aportes.parquet", note: "", icon: "✅" },
          { path: "data/silver/xm_listado_recursos.parquet", note: "(2,501 recursos únicos)", icon: "✅" },
          { path: "data/silver/ideam_precipitacion.parquet", note: "(29,797 filas)", icon: "✅" },
          { path: "data/silver/ideam_cuarentena.parquet", note: "(7 lecturas > 500 mm)", icon: "⚠️" },
          { path: "data/silver/noaa_oni.parquet", note: "(920 meses con fase_enso)", icon: "✅" },
          { path: "data/silver/dane_divipola.parquet", note: "(1,122 municipios float64)", icon: "✅" }
        ],
        comando: ".venv/bin/python -c \"import pandas as pd; print(pd.read_parquet('data/silver/xm_precio_bolsa.parquet').head(4))\"",
        comandoLabel: "Inspeccionar muestra horaria de XM en terminal:"
      },
      3: {
        num: "3",
        titulo: "Punto 3 · Contratos con Pandera y Pruebas Unitarias con Pytest",
        subtitulo: "Inspector automático de datos en la puerta de salida + 25 pruebas que se ejecutan en 1.2s",
        scripts: [
          {
            path: "src/quality/esquemas.py",
            rol: "Contratos Pandera",
            color: "cyan",
            desc: "Centraliza los 12 contratos <code>pa.DataFrameSchema</code> con validaciones estrictas: rangos físicos, tipos de datos, no-nulos, checks lógicos y expresiones regulares."
          },
          {
            path: "tests/test_limpieza.py",
            rol: "17 Tests Unitarios",
            color: "emerald",
            desc: "Pruebas de limpieza y contratos: verifica cómo reacciona el código ante anomalías (duplicados, negativos, unidades, cuarentena y bloqueos con <code>pytest.raises(pa.errors.SchemaError)</code>)."
          },
          {
            path: "tests/test_pipeline.py",
            rol: "8 Tests Extracción",
            color: "purple",
            desc: "Pruebas heredadas de EA1 que verifican no-vacuidad de capas, fechas de partición, consultas SoQL de IDEAM y ventanas horarias de XM."
          },
          {
            path: "pyproject.toml",
            rol: "Configuración Pytest",
            color: "amber",
            desc: "Define la configuración de ejecución de pytest (rutas de prueba, flags de verbosidad, warnings y dependencias del entorno virtual)."
          }
        ],
        archivosAntes: [
          "src/quality/esquemas.py (Definición de 12 esquemas Pandera)",
          "src/quality/reporte.py (Generador de la auditoría numérica)"
        ],
        archivosDespues: [
          { path: "tests/test_limpieza.py", note: "(17 pruebas unitarias de limpieza y contratos)", icon: "🧪" },
          { path: "tests/test_pipeline.py", note: "(8 pruebas de integración y extracción EA1)", icon: "🧪" }
        ],
        comando: ".venv/bin/python -m pytest tests/test_limpieza.py -v",
        comandoLabel: "Ejecutar suite de 17 pruebas de limpieza:"
      },
      4: {
        num: "4",
        titulo: "Punto 4 · Reporte de Calidad Automático (`docs/reporte_calidad.md`)",
        subtitulo: "Auditoría numérica transparente: 24 reglas medidas antes y después en las 5 fuentes",
        scripts: [
          {
            path: "src/quality/reporte.py",
            rol: "Generador de Auditoría",
            color: "purple",
            desc: "Implementa <code>generar_reporte_calidad()</code>: recopila los diccionarios de métricas de cada fuente, computa el balance numérico antes vs después y redacta el informe en Markdown."
          },
          {
            path: "src/silver/*.py",
            rol: "Instrumentación",
            color: "cyan",
            desc: "Cada módulo de limpieza registra explícitamente sus contadores (nulos detectados, duplicados eliminados, registros en cuarentena y conversiones de unidades)."
          },
          {
            path: "docs/reporte_calidad.md",
            rol: "Reporte Generado",
            color: "emerald",
            desc: "Archivo Markdown resultante de salida con las 24 reglas dimensionales documentadas con cifras exactas antes y después de la limpieza."
          },
          {
            path: "src/transformar.py",
            rol: "Invocación Automática",
            color: "amber",
            desc: "Llama automáticamente a <code>generar_reporte_calidad()</code> justo al terminar la Capa Plata antes de ejecutar los modelos dbt."
          }
        ],
        archivosAntes: [
          "src/silver/enerandes.py (Instrumentación de métricas de ventas y cuarentena)",
          "src/silver/xm.py, ideam.py, noaa.py, divipola.py (Instrumentación multi-fuente)"
        ],
        archivosDespues: [
          { path: "docs/reporte_calidad.md", note: "(24 reglas auditadas con cifras exactas)", icon: "📊" },
          { path: "src/quality/reporte.py", note: "(Script generador automático)", icon: "⚙️" }
        ],
        comando: "head -n 35 docs/reporte_calidad.md",
        comandoLabel: "Leer el encabezado del reporte de calidad en terminal:"
      },
      5: {
        num: "5",
        titulo: "Punto 5 · Esquema Estrella en DuckDB con dbt (Capa Oro)",
        subtitulo: "11 Vistas Staging + 7 Dimensiones Conformes + 5 Tablas de Hechos · 82 Pruebas dbt",
        scripts: [
          {
            path: "dbt/models/staging/ (11 Vistas)",
            rol: "Staging SQL",
            color: "blue",
            desc: "<code>sources.yml</code>, <code>stg_ventas.sql</code>, <code>stg_xm_*.sql</code>, <code>stg_ideam_*.sql</code>, <code>stg_noaa_oni.sql</code>, <code>stg_divipola.sql</code>: leen Parquets de Plata y crean vistas preparatorias con nombres limpios y casting homogéneo."
          },
          {
            path: "dbt/models/marts/ (12 Tablas)",
            rol: "Marts Kimball",
            color: "purple",
            desc: "<strong>7 Dimensiones:</strong> <code>dim_fecha.sql</code>, <code>dim_mes.sql</code>, <code>dim_hora.sql</code>, <code>dim_municipio.sql</code>, <code>dim_segmento.sql</code>, <code>dim_recurso.sql</code>, <code>dim_estacion.sql</code>.<br><strong>5 Hechos:</strong> <code>fact_ventas_mensual.sql</code>, <code>fact_mercado_horario.sql</code>, <code>fact_generacion_recurso.sql</code>, <code>fact_hidrologia_diaria.sql</code>, <code>fact_clima_diario.sql</code>."
          },
          {
            path: "dbt/models/marts/schema.yml",
            rol: "82 Tests dbt",
            color: "cyan",
            desc: "Define las pruebas de integridad referencial (<code>unique</code>, <code>not_null</code>, <code>relationships</code>) que garantizan que ninguna clave foránea quede huérfana."
          },
          {
            path: "dbt_project.yml & profiles.yml",
            rol: "Configuración",
            color: "amber",
            desc: "Configuran el conector <code>dbt-duckdb</code> apuntando directamente al archivo local <code>data/observatorio.duckdb</code>."
          }
        ],
        archivosAntes: [
          "dbt/profiles.yml & dbt/dbt_project.yml (Configuración del conector)",
          "dbt/models/staging/ (11 vistas SQL stg_*.sql)"
        ],
        archivosDespues: [
          { path: "data/observatorio.duckdb", note: "(Base de datos analítica OLAP local)", icon: "🦆" },
          { path: "dbt/models/marts/", note: "(7 dimensiones + 5 hechos + 82 tests)", icon: "🏛️" },
          { path: "docs/modelo_dimensional.md & docs/diccionario_datos.md", note: "(Catálogo y diagramas)", icon: "📚" }
        ],
        comando: ".venv/bin/python -c \"import duckdb; print(duckdb.connect('data/observatorio.duckdb').execute('SHOW TABLES').df())\"",
        comandoLabel: "Listar todas las tablas y vistas en DuckDB:"
      },
      6: {
        num: "6",
        titulo: "Punto 6 · Consultas SQL de Negocio sobre el Esquema Estrella",
        subtitulo: "Demostración de impacto del fenómeno El Niño en hidrología, térmicas y precios",
        scripts: [
          {
            path: "consultas/oro/*.sql (5 Scripts SQL)",
            rol: "Consultas Analíticas",
            color: "amber",
            desc: "<code>01_enso_hidrologia_y_precio.sql</code>, <code>02_matriz_generacion_por_fase_enso.sql</code>, <code>03_patron_horario_demanda_y_precio.sql</code>, <code>04_impacto_exposicion_bolsa_enerandes.sql</code>, <code>05_clima_antioquia_vs_ventas_municipios.sql</code>."
          },
          {
            path: "src/consultar.py",
            rol: "Runner CLI",
            color: "cyan",
            desc: "Script ejecutor en Python: conecta a DuckDB, ejecuta las consultas del directorio <code>consultas/oro/</code> y formatea las tablas directamente en la terminal (soporta flag <code>--solo-oro</code>)."
          },
          {
            path: "docs/modelo_dimensional.md",
            rol: "Documentación Técnica",
            color: "purple",
            desc: "Diagrama conceptual, justificación de granos y claves foráneas que guían la sintaxis de los <code>JOIN</code> en las 5 consultas."
          },
          {
            path: "docs/diccionario_datos.md",
            rol: "Catálogo de Atributos",
            color: "emerald",
            desc: "Diccionario completo de cada métrica y dimensión utilizada en los filtros y agregaciones de las consultas de negocio."
          }
        ],
        archivosAntes: [
          "consultas/oro/01_enso_hidrologia_y_precio.sql",
          "consultas/oro/02_matriz_generacion_por_fase_enso.sql",
          "consultas/oro/03_patron_horario_demanda_y_precio.sql",
          "consultas/oro/04_impacto_exposicion_bolsa_enerandes.sql",
          "consultas/oro/05_clima_antioquia_vs_ventas_municipios.sql"
        ],
        archivosDespues: [
          { path: "src/consultar.py", note: "(Script runner ejecutor de consultas SQL)", icon: "🐍" },
          { path: "docs/modelo_dimensional.md", note: "(Explicación de granos y relaciones)", icon: "📖" }
        ],
        comando: ".venv/bin/python -m src.consultar --solo-oro",
        comandoLabel: "Ejecutar las 5 consultas en consola con python:"
      },
      7: {
        num: "7",
        titulo: "Puntos 7 y 8 · Reproducibilidad en 1 Comando & Higiene de Git",
        subtitulo: "Pipeline integral en 22 segundos manteniendo el repositorio Git 100% liviano",
        scripts: [
          {
            path: "src/transformar.py",
            rol: "Pipeline Principal",
            color: "emerald",
            desc: "El orquestador maestro que con un solo comando (<code>python -m src.transformar</code>) ejecuta las transformaciones de las 5 fuentes, genera el reporte de calidad y corre <code>dbt build</code> en DuckDB."
          },
          {
            path: "src/config.py",
            rol: "Configuración Global",
            color: "cyan",
            desc: "Define de manera centralizada las rutas de directorios (<code>DATA_BRONZE_DIR</code>, <code>DATA_SILVER_DIR</code>, <code>DUCKDB_PATH</code>) y parámetros compartidos sin rutas relativas 'hardcodeadas'."
          },
          {
            path: "src/utils.py",
            rol: "Utilidades & Logging",
            color: "amber",
            desc: "Configura el logger estructurado del proyecto, manejadores de tiempo y utilidades de archivo para garantizar trazabilidad durante la ejecución."
          },
          {
            path: "src/explorar.py / explorar_actividad_2.py",
            rol: "Explorador CLI",
            color: "purple",
            desc: "Menú interactivo en consola para navegar paso a paso por cada punto de la actividad e inspeccionar en vivo tablas antes y después."
          },
          {
            path: ".gitignore",
            rol: "Control de Versiones",
            color: "slate",
            desc: "Reglas estrictas que excluyen archivos pesados (<code>data/bronze/</code>, <code>data/silver/</code>, <code>*.duckdb</code>, <code>dbt/target/</code>, <code>.venv/</code>) para mantener el repositorio Git liviano y 100 % reproducible desde código."
          }
        ],
        archivosAntes: [
          "src/transformar.py (Orquestador maestro)",
          "src/config.py (Rutas centralizadas de Bronze, Silver, Oro)",
          ".gitignore (Reglas de exclusión de binarios)"
        ],
        archivosDespues: [
          { path: "docs/bitacoras/puentes_cesar.md", note: "(Bitácora de decisiones del equipo)", icon: "📖" },
          { path: "../bitacora__entendimiento_actividad_2.md", note: "(Bitácora de entendimiento detallada)", icon: "📖" },
          { path: "../guia_actividad_2.html", note: "(Esta guía visual interactiva)", icon: "🌐" }
        ],
        comando: "python -m src.transformar",
        comandoLabel: "Reconstruir todo el proyecto desde cero (~22 segundos):"
      }
    };

"""
Fuente 2 - IDEAM en datos.gov.co (plataforma Socrata, lenguaje de consulta SoQL).
  - El dataset tiene MILLONES de observaciones (una cada pocos minutos desde 2005)
  - Por eso FILTRAMOS ($where) y AGREGAMOS ($select + $group) EN EL SERVIDOR:
    viaja un resumen diario por estacion, no millones de filas
  - Ademas paginamos con $limit / $offset por si una ventana trae muchas filas
Documentacion SoQL: https://dev.socrata.com/docs/queries/
"""
# ---------------------------------------------------------------------------
# IMPORTS (traer codigo que ya existe)
# ---------------------------------------------------------------------------
from concurrent.futures import ThreadPoolExecutor
import pandas as pd     # pandas: libreria de tablas. "as pd" le pone el nombre corto pd.
                        # Aqui se usa para convertir la lista de filas en tabla (DataFrame).

from src import config  # config.py de este proyecto: URL del IDEAM, departamento, fechas, ventana.
from src.utils import guardar_bronce, http_json, log, ventanas, ya_existe
# Funciones de utils.py de este proyecto:
#   guardar_bronce: guarda la tabla en Parquet con 3 columnas de linaje
#   http_json:      le envia un pedido a una API y devuelve la respuesta; reintenta si falla
#   log:            escribe un mensaje en pantalla con la hora
#   ventanas:       parte un rango de fechas en bloques (aqui, de 7 dias)
#   ya_existe:      dice si el archivo ya esta en bronce (para no descargarlo otra vez)

# ---------------------------------------------------------------------------
# CONSTANTES: valores fijos de este extractor (en MAYUSCULAS por convencion)
# ---------------------------------------------------------------------------
NOMBRE = "ideam_precipitacion_diaria"          # nombre del archivo de precipitacion en bronce
NOMBRE_TEMP = "ideam_temperatura_diaria"       # nombre del archivo de temperatura en bronce
CAMPOS = "codigoestacion, nombreestacion, municipio, latitud, longitud"   # columnas que se piden
PAGINA = 50000                                 # filas maximas por pedido ($limit)

# ---------------------------------------------------------------------------
# NOTA sobre "offset: int" o "-> dict" en las funciones:
# son ANOTACIONES DE TIPO. Dicen que tipo de dato se espera (int = numero entero,
# bool = verdadero/falso, dict = diccionario) y que devuelve la funcion.
# Python no las obliga: sirven para que el codigo se entienda mejor.
# ---------------------------------------------------------------------------


def consulta_soql(inicio, fin, offset: int, variable: str = "precipitacion") -> dict:
    """Arma los parametros SoQL: filtrar Antioquia y fechas, y agregar por dia y estacion en el servidor."""
    # En precipitacion sumamos la lluvia del dia; en temperatura calculamos media, minima y maxima.
    if variable == "temperatura":
        agregacion = (
            "avg(valorobservado) AS temp_media_c, "
            "min(valorobservado) AS temp_min_c, "
            "max(valorobservado) AS temp_max_c, "
            "count(*) AS n_obs"
        )
    else:
        agregacion = "sum(valorobservado) AS precipitacion_mm, count(*) AS n_obs"

    return {
        "$select": f"{CAMPOS}, date_trunc_ymd(fechaobservacion) AS fecha, {agregacion}",
        "$where": f"departamento = '{config.IDEAM_DEPARTAMENTO}' AND "           # solo Antioquia
                  f"fechaobservacion BETWEEN '{inicio}T00:00:00' AND '{fin}T23:59:59'",   # esa semana
        "$group": f"{CAMPOS}, fecha",             # un grupo por estacion y dia
        "$order": "fecha, codigoestacion",        # ordenado por fecha y estacion
        "$limit": PAGINA,                         # filas por pagina
        "$offset": offset,                        # filas que se saltan (para pedir la pagina siguiente)
    }


def extraer_dataset(nombre: str, url: str, variable: str, forzar: bool = False) -> None:
    """Descarga un dataset del IDEAM (precipitacion o temperatura) semana por semana con SoQL."""
    if ya_existe(nombre, forzar):                 # si el archivo ya esta en bronce...
        return                                    # ...termina aqui, sin descargar
    filas = []                                    # aqui se juntan las filas de todas las semanas
    bloques = list(ventanas(config.IDEAM_FECHA_INICIO, config.FECHA_FIN, config.IDEAM_DIAS_VENTANA))

    def descargar_semana(rango):
        inicio, fin = rango
        offset = 0                                # empezar por la primera pagina
        filas_semana = []
        while True:                               # paginacion: repetir hasta la ultima pagina
            # GET con los parametros SoQL; requests los pone en la URL despues de ?
            # La respuesta es una lista de filas (cada fila es un diccionario).
            lote = http_json("GET", url, params=consulta_soql(inicio, fin, offset, variable))
            filas_semana.extend(lote)             # agrega las filas de esta pagina
            if len(lote) < PAGINA:                # llegaron menos filas que el limite: era la ultima
                break                             # break: sale del while
            offset += PAGINA                      # pedir la siguiente pagina
        log(f"   [{variable}] semana {inicio} a {fin}: {len(filas_semana)} filas")
        return filas_semana

    with ThreadPoolExecutor(max_workers=6) as pool:
        for filas_semana in pool.map(descargar_semana, bloques):
            filas.extend(filas_semana)
    # pd.DataFrame(filas) convierte la lista de filas en una tabla de pandas,
    # y guardar_bronce() la guarda en data/bronze/<nombre>.parquet
    guardar_bronce(pd.DataFrame(filas), nombre, fuente="IDEAM", origen=url)


def extraer(forzar: bool = False) -> None:
    """Descarga precipitacion y temperatura diaria por estacion del IDEAM y las guarda en bronce."""
    log("IDEAM - datos abiertos (SoQL: precipitacion y temperatura)")
    extraer_dataset(NOMBRE, config.IDEAM_URL, "precipitacion", forzar)
    extraer_dataset(NOMBRE_TEMP, config.IDEAM_TEMPERATURA_URL, "temperatura", forzar)


# ---------------------------------------------------------------------------
# Este bloque solo se ejecuta cuando se corre ESTE archivo directamente:
#     python -m src.extract.ideam
# Cuando otro archivo lo importa (como pipeline.py), este bloque NO se ejecuta.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys      # sys.argv: lista con lo que se escribio en el comando
    extraer(forzar="--forzar" in sys.argv)   # True si el comando trae --forzar

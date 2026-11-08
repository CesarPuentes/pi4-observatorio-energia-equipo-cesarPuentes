# Dashboard Interactivo · Arquitectura Modular "Bajo el Capó" (EA2)

Este directorio contiene la versión modular del dashboard interactivo de sustentación para la **Actividad 2 (EA2) del Observatorio de Energía y Clima**.

---

## 🎯 ¿Por qué esta arquitectura modular?

1. **Ahorro masivo de tokens (>90% de reducción):**
   - En lugar de cargar o editar un archivo monolítico de 1,712 líneas (~25,000 tokens), cada sección vive en su propio componente de solo 80 a 180 líneas (~1,000 a 2,000 tokens).
   - Cualquier modificación futura (por ejemplo, ajustar la explicación del Punto 3 o cambiar una consulta en el Punto 6) solo lee y modifica ese archivo específico.

2. **Facilidad de auditoría y mantenimiento:**
   - La lógica de datos (scripts involucrados y rutas de disco) está desacoplada en `js/data.js`.
   - La lógica de interactividad del modal está en `js/modal.js`.
   - El simulador de contratos Pandera en vivo está en `js/simulador.js`.
   - Los estilos y scrollbars personalizados están en `css/styles.css`.

3. **Ejecución 100% nativa y offline:**
   - No requiere servidor Node.js, Webpack, Vite ni configuraciones complejas.
   - `index.html` puede abrirse con **doble clic directo** desde el explorador de archivos en cualquier navegador web (`file:///.../index.html`).

---

## 📁 Estructura del Directorio

```text
dashboard/
├── index.html                    # Archivo principal ensamblado (listo para abrir en el navegador)
├── build.py                      # Script de ensamble ultra-rápido (0.02s)
├── README.md                     # Esta guía de uso y arquitectura
│
├── css/
│   └── styles.css                # Estilos visuales, scrollbars y utilidades
│
├── js/
│   ├── data.js                   # Diccionario DETALLES_PUNTOS con scripts, rutas y comandos
│   ├── modal.js                  # Controlador del modal "Bajo el Capó", pestañas y atajos
│   ├── simulador.js              # Simulador en vivo de Pandera y utilidades de copiado
│   └── glosario.js               # Controlador interactivo de búsqueda y filtros por capa
│
└── components/                   # Secciones HTML independientes para edición atómica
    ├── header.html               # Barra superior con métricas clave (4,007 ventas, 25 tests, etc.)
    ├── sidebar.html              # Índice flotante de navegación rápida
    ├── seccion0_panorama.html    # Sección 0: Vista Panorámica (Negocio & Data Engineering)
    ├── seccion0b_glosario.html   # Sección 0B: Glosario de 32 Conceptos (Bronce · Plata · Oro)
    ├── punto1_enerandes.html     # Punto 1: Limpieza EnerAndes (4 hojas, fechas, MWh, cuarentena)
    ├── punto2_fuentes_externas.html # Punto 2: XM, IDEAM, NOAA y DIVIPOLA
    ├── punto3_pandera_pytest.html# Punto 3: Contratos Pandera y 25 pruebas Pytest
    ├── punto4_reporte_calidad.html# Punto 4: Reporte de Calidad (24 reglas medidas)
    ├── punto5_esquema_estrella.html# Punto 5: Esquema Kimball en dbt + DuckDB
    ├── punto6_consultas_oro.html # Punto 6: 5 Consultas Analíticas de Negocio
    ├── punto7_reproducibilidad.html# Punto 7: Pipeline en 1 comando y Git colaborativo
    └── modal.html                # Estructura del diálogo modal interactivo
```

---

## 🛠️ Cómo Realizar Cambios

### Caso 1: Modificar texto o tablas de un punto (ej. Punto 5)
1. Edita directamente el archivo del componente: `components/punto5_esquema_estrella.html`.
2. En la terminal ejecuta:
   ```bash
   python build.py
   ```
3. ¡Listo! `index.html` se actualiza de inmediato.

### Caso 2: Modificar scripts, descripciones o rutas del modal
1. Edita directamente `js/data.js`.
2. **No hace falta reconstruir**: como `index.html` carga `js/data.js` dinámicamente mediante `<script src="js/data.js">`, los cambios se reflejan al recargar el navegador (`F5`).

### Caso 3: Modificar estilos visuales
1. Edita directamente `css/styles.css`.
2. Se reflejan al recargar el navegador (`F5`).

---

## 🚀 Cómo Visualizar el Dashboard

Puedes abrirlo de dos formas:

1. **Doble clic directo (Recomendado):**
   Abre el archivo `index.html` con tu navegador favorito:
   ```bash
   xdg-open index.html
   ```

2. **O mediante un servidor HTTP local:**
   ```bash
   python3 -m http.server 8000
   ```
   Luego visita `http://localhost:8000` en tu navegador.

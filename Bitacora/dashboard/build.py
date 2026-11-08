#!/usr/bin/env python3
"""
Script de construcción para el Dashboard Interactivo "Bajo el Capó" (EA2).
Observatorio de Energía & Clima Colombia.

Ensambla los componentes modulares de HTML ubicados en components/
hacia un archivo unificado 'index.html', vinculando los estilos en css/
y la lógica interactiva en js/.

Uso:
    python build.py
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
COMPONENTS_DIR = BASE_DIR / "components"
INDEX_PATH = BASE_DIR / "index.html"

TEMPLATE = """<!DOCTYPE html>
<html lang="es" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Observatorio Energía y Clima – Guía Interactiva "Bajo el Capó" (EA2)</title>
  <!-- Tailwind CSS Engine -->
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <!-- Estilos Personalizados Modulares -->
  <link rel="stylesheet" href="css/styles.css">
</head>
<body class="bg-[var(--background,#0f172a)] text-[var(--foreground,#f8fafc)] antialiased">

  <!-- Header Superior con Métricas Clave -->
{header}

  <!-- Layout Principal con Índice Flotante -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-8 flex gap-8">
    
    <!-- ÍNDICE FLOTANTE / SIDEBAR STICKY -->
{sidebar}

    <!-- CONTENIDO CENTRAL: VISTA PANORÁMICA, GLOSARIO Y SECCIONES 1 A 7 -->
    <main class="flex-1 space-y-12 min-w-0">
{panorama}

{glosario}

{punto1}

{punto2}

{punto3}

{punto4}

{punto5}

{punto6}

{punto7}
    </main>
  </div>

  <!-- MODAL INTERACTIVO DE INSPECCIÓN TÉCNICA (SCRIPTS Y ARCHIVOS) -->
{modal}

  <!-- Scripts JavaScript Modulares -->
  <script src="js/data.js"></script>
  <script src="js/simulador.js"></script>
  <script src="js/modal.js"></script>
  <script src="js/glosario.js"></script>
</body>
</html>
"""

COMPONENT_FILES = {
    "header": "header.html",
    "sidebar": "sidebar.html",
    "panorama": "seccion0_panorama.html",
    "glosario": "seccion0b_glosario.html",
    "punto1": "punto1_enerandes.html",
    "punto2": "punto2_fuentes_externas.html",
    "punto3": "punto3_pandera_pytest.html",
    "punto4": "punto4_reporte_calidad.html",
    "punto5": "punto5_esquema_estrella.html",
    "punto6": "punto6_consultas_oro.html",
    "punto7": "punto7_reproducibilidad.html",
    "modal": "modal.html",
}

def indent_block(text: str, spaces: int = 6) -> str:
    """Añade indentación uniforme a cada línea de un bloque HTML."""
    indent = " " * spaces
    lines = text.strip().splitlines()
    return "\n".join(indent + line if line.strip() else line for line in lines)

def build():
    context = {}
    for key, filename in COMPONENT_FILES.items():
        comp_path = COMPONENTS_DIR / filename
        if not comp_path.exists():
            print(f"❌ Error: Falta el componente {comp_path}", file=sys.stderr)
            sys.exit(1)
        raw_text = comp_path.read_text(encoding="utf-8")
        
        # Indentación adecuada según el rol
        if key in ("header", "modal"):
            context[key] = indent_block(raw_text, spaces=2)
        elif key == "sidebar":
            context[key] = indent_block(raw_text, spaces=4)
        else:
            context[key] = indent_block(raw_text, spaces=6)

    output_html = TEMPLATE.format(**context)
    INDEX_PATH.write_text(output_html, encoding="utf-8")
    
    line_count = len(output_html.splitlines())
    size_kb = len(output_html.encode("utf-8")) / 1024
    print(f"✔ [OK] Dashboard ensamblado exitosamente en:")
    print(f"       -> {INDEX_PATH} ({line_count} líneas, {size_kb:.1f} KB)")
    print(f"       -> Archivos JS vinculados: js/data.js, js/simulador.js, js/modal.js")
    print(f"       -> Archivo CSS vinculado: css/styles.css")

if __name__ == "__main__":
    build()

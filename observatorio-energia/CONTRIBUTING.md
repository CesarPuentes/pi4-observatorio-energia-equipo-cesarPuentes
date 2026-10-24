# Guía de Contribución del Equipo (`CONTRIBUTING.md`)

## 1. Flujo de trabajo en Git y GitHub (GitHub Flow)

1. **Rama principal protegida (`main`):**
   - Está prohibido hacer `push` directo a `main`.
   - Todo cambio debe entrar mediante un **Pull Request (PR)** revisado y aprobado por al menos otro integrante del equipo.
2. **Convención de nombres de ramas:**
   - `feature/<descripcion-corta>`: nuevas funcionalidades o extractores (ej. `feature/xm-ampliado`, `feature/ideam-temperatura`, `feature/fuente-divipola`).
   - `fix/<descripcion-corta>`: corrección de errores.
   - `docs/<descripcion-corta>`: documentación, perfilamiento y bitácoras (ej. `docs/perfilamiento-bronce`).
   - `test/<descripcion-corta>`: pruebas unitarias con `pytest`.
3. **Convención de mensajes de commit (Conventional Commits en español):**
   - `feat:` nueva característica o extractor.
   - `fix:` corrección de un bug.
   - `docs:` cambios en `README.md`, `docs/perfilamiento.md` o bitácoras.
   - `test:` adición o ajuste de pruebas en `tests/`.
   - `chore:` configuración de entorno, dependencias o mantenimiento.

## 2. Reglas de calidad antes de abrir un Pull Request

- Ejecutar `python -m src.pipeline` y verificar que la capa bronce y las muestras en `data/sample/` se generen sin errores.
- Ejecutar `python -m pytest` y asegurarse de que todas las pruebas pasen en verde.
- Verificar con `git status` que **no** se suban archivos de `data/bronze/`, `.venv/` ni credenciales (`.env`).

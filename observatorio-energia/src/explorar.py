"""
Punto de entrada dentro de `src/` para ejecutar el explorador interactivo de la Actividad 2.

Uso desde `observatorio-energia/`:
    .venv/bin/python -m src.explorar
"""
import importlib.util
from pathlib import Path


def main() -> None:
    ruta_script = Path(__file__).resolve().parent.parent.parent / "explorar_actividad_2.py"
    spec = importlib.util.spec_from_file_location("explorar_actividad_2", ruta_script)
    modulo = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(modulo)
    modulo.main()


if __name__ == "__main__":
    main()

# AGENTS.md

- `references/` es un entorno aislado para estudiar, reproducir y adaptar algoritmos de terceros; no forma parte del paquete `redistricting_lab` ni del pipeline productivo.
- **`references/repos/` (Solo lectura):** Mantiene el checkout original sin cambios. Nunca modifiques archivos directamente en `repos/` para preservar la referencia pura de upstream.
- **`references/adaptations/<referencia>/` (Laboratorio de adaptación):** Toda copia modificada, refactorización, depuración o prueba para comprender y hacer reproducible el algoritmo original DEBE realizarse dentro de este directorio, con la finalidad de lograr su reproducibilidad mas legitimas pero contros solver, o para lograr la compresión de los metodos que implementa desde la propuesta algoritmica del articulo.
- **Fase de datos mexicanos:** Las pruebas de compatibilidad y adaptadores para la estructura de datos electorales/geográficos de México también se desarrollan (y se consolidan en `final_adaptations/`).
- **Integración:** Ningún script en `references/` se importa directamente desde `src/`. La integración oficial requiere reimplementar el algoritmo adaptado usando los contratos de `src/redistricting_lab/solvers/`.
- **Aislamiento de dependencias:** Gestiona las dependencias de ejecución en el `.venv` propio de la referencia; no agregues librerías a `pyproject.toml` solo para correr o probar una referencia.
- **Licencias:** Conserva URL, commit, licencia y requisitos en `registry/`. Asegúrate de revisar obligaciones de licencia (e.g. GPL) antes de reimplementar código en `src/`.

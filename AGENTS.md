# AGENTS.md

- Repo de distritacion/redistritacion en Mexico; el paquete Python real es `redistricting_lab` y vive en `src/redistricting_lab/`.
- La raiz del repo es un scaffold inicial; no asumas que ya existen algoritmos, datasets finales o pipelines completos.
- Usa `uv sync --extra dev` para preparar el entorno de desarrollo; en este repo `--dev` no fue suficiente para instalar las dependencias de pruebas.
- Comandos de verificacion: `uv run ruff check .` y `uv run pytest`.
- Punto de entrada ejecutable: `uv run python -m redistricting_lab` o `uv run redistricting-lab`.
- Mantiene `uv.lock` versionado; si cambian dependencias, actualiza el lock junto con `pyproject.toml`.
- No modifiques el entorno global ni reutilices el viejo proyecto de investigacion como workspace de trabajo.
- `data/raw/` si se versiona; `data/interim/` y `data/processed/` no deben commitearse.
- `src/redistricting_lab/solvers/` es para envoltorios de algoritmos; `evaluation/` para metricas; `visualization/` para mapas y salidas graficas.
- Mantén la separacion entre logica de solver, preparacion de datos y reportes. No mezcles mapas o metricas dentro del solver.

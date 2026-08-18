# mex-redistricting-and-districting-lab-algorithm

Laboratorio para distritacion y redistritacion en Mexico, con foco principal en distritacion. La meta es comparar enfoques exactos, heuristicos, metaheuristicos y de machine learning sin acoplar la evaluacion ni la visualizacion a cada solver.

## Estructura

- `src/redistricting_lab/data/`: carga, limpieza y preparacion de insumos.
- `src/redistricting_lab/domain/`: entidades base, contratos e interfaces comunes.
- `src/redistricting_lab/solvers/`: adaptadores de algoritmos.
- `src/redistricting_lab/evaluation/`: metricas, comparativas y ranking de resultados.
- `src/redistricting_lab/visualization/`: mapas, graficas y salidas geoespaciales.
- `src/redistricting_lab/experiments/`: ejecucion de corridas y trazabilidad.
- `data/raw/`: datos originales versionables.
- `data/interim/`: datos intermedios no versionados.
- `data/processed/`: datasets listos para modelado.
- `configs/`: configuraciones de experimentos y algoritmos.
- `reports/`: mapas, tablas y artefactos generados.
- `docs/`: notas de arquitectura y metodologia.

## Arranque

```bash
uv sync --extra dev
uv run redistricting-lab
```

## Verificacion

```bash
uv run ruff check .
uv run pytest
```

## Notas de desarrollo

- El paquete importable es `redistricting_lab`, no el nombre del repositorio.
- `PuLP` sera el primer solver y debe quedar encapsulado dentro de `src/redistricting_lab/solvers/`.
- Los mapas y metricas deben vivir fuera del solver para mantener comparabilidad entre enfoques.
- `uv.lock` debe mantenerse actualizado junto con `pyproject.toml`.

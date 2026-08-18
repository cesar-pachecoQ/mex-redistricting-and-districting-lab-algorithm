# Init

Este proyecto nace para comparar enfoques de distritacion y redistritacion en Mexico con una arquitectura preparada para crecer sin refactorizaciones grandes.

## Idea central

- Unificar varios solvers bajo una interfaz comun.
- Separar preparacion de datos, resolucion, evaluacion y visualizacion.
- Automatizar reportes y mapas para comparar algoritmos con el menor trabajo manual posible.

## Estructura prevista

```text
data/
  raw/        insumos originales
  interim/    transformaciones intermedias
  processed/  datos listos para modelado
src/redistricting_lab/
  data/           carga y preparacion
  domain/         modelos e interfaces base
  solvers/        wrappers de algoritmos
    exact/
    heuristic/
    metaheuristic/
    machine_learning/
  evaluation/     metricas y comparaciones
  visualization/  mapas y graficos
  experiments/    ejecucion y trazabilidad
configs/          parametros de corridas
reports/          salidas generadas
docs/             notas tecnicas
```

## Primeras decisiones

- `uv` para entornos y dependencias.
- `PuLP` como primer solver exacto.
- `geopandas`, `shapely` y `pyarrow` para la capa espacial y tabular.
- `pytest` y `ruff` como controles basicos.

## Flujo esperado

1. Ingesta y limpieza de datos.
2. Construccion de instancia.
3. Ejecucion de solver.
4. Calculo de metricas.
5. Generacion de mapas y reporte.

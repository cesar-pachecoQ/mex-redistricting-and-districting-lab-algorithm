# Referencias externas

Este directorio permite estudiar, ejecutar y reproducir proyectos de terceros sin incorporarlos al codigo productivo de `redistricting_lab`.

## Limites de aislamiento

- Los checkouts originales viven en `repos/` y estan ignorados por Git.
- Cada checkout tiene su propio `.venv`; no modifica `pyproject.toml`, `uv.lock` ni `.venv` del proyecto principal.
- Las salidas externas van a `runs/`, tambien ignorado por Git.
- El codigo externo no se importa desde `src/` ni alimenta mapas, reportes o metricas oficiales.
- Una idea se integra solo despues de documentarla en `adaptations/` y reimplementarla con las interfaces propias del proyecto.

## Directorios versionados

- `registry/`: origen, commit fijado, licencia, dependencias y alcance de cada referencia.
- `setup_references.sh`: clonacion y preparacion reproducible de los checkouts definidos.
- `adaptations/`: notas metodologicas y adaptaciones propias; no copias del codigo externo.

## Preparar referencias

Desde la raiz del repositorio:

```bash
bash references/setup_references.sh
```

El script clona cada referencia en `references/repos/`, fija el commit registrado y crea su entorno aislado. No ejecuta notebooks ni solvers, porque pueden requerir licencias, datos o recursos adicionales.

Por defecto instala dependencias abiertas (`geopandas`, `networkx` y `jupyterlab`). El algoritmo de la primera referencia requiere Gurobi, que es opcional por su licencia:

```bash
INSTALL_GUROBI=1 bash references/setup_references.sh
```

## Flujo de integracion

1. Reproducir el proyecto externo en su checkout aislado.
2. Registrar hallazgos y compatibilidad en `adaptations/<referencia>/`.
3. Diseñar un adaptador para los datos y contratos de `redistricting_lab`.
4. Reimplementar el algoritmo en `src/redistricting_lab/solvers/`.
5. Solo entonces habilitar sus resultados para evaluacion, mapas y reportes oficiales.

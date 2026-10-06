# Adaptación de *Refuting a Widespread Belief About County Splits*

Esta es una reimplementación aislada y modificada del código que acompaña al
paper [*A widespread belief about county splits in political districting plans
is wrong*](https://github.com/AustinLBuchanan/refuting_a_widespread_belief_about_county_splits),
de Austin Buchanan, Soraya Ezazipour y Maral Shahmizad.

Resúmenes operativos:

- [Migración de Gurobi a PuLP](docs/01-migracion-gurobi-a-pulp.md).
- [Adaptación a datos de Tabasco](docs/02-adaptacion-tabasco.md).

## Del paper al código

El código original enumera distritos candidatos con un modelo entero, usa flujo
de Shirabe para la contigüidad del distrito enraizado y separadores mínimos para
descartar complementos desconectados. Esta adaptación conserva esa estructura,
pero sustituye Gurobi y sus callbacks por PuLP: `optimization.py` resuelve,
NetworkX verifica el complemento y el programa agrega cortes externamente hasta
obtener `t` resultados. `data.py` acepta el formato JSON de
`networkx.readwrite.json_graph.adjacency_graph` y normaliza `TOTPOP`.

La implementación es experimental y sólo sirve para estudiar el método. PuLP
ofrece una interfaz lineal: el inverso de Polsby-Popper es una métrica de
evaluación, pero no se impone como función no lineal; al solicitarlo se
optimiza el proxy lineal de perímetro y se reporta la métrica real después.
La formulación de dos partes no sustituye una validación geográfica completa,
ni resuelve por sí sola restricciones electorales o legales.

No se ejecutan los datos estatales del repositorio upstream. Los tests y el
ejemplo son grafos sintéticos pequeños; adicionalmente existe una corrida
explícita para los 17 municipios de Tabasco. Los scripts de `scripts/` son
reproducibles y configurables, pero no se ejecutan automáticamente.

## Uso local

```bash
python -m pip install -r requirements.txt
PYTHONPATH=. python -m pytest
PYTHONPATH=. python scripts/reproduce.py --input examples/synthetic.json --districts 2 --top-t 2 --lower 2 --upper 2
```

Para reproducir un cluster que representa varios distritos, use
`--cluster-size`; por ejemplo, `--cluster-size 2` impone población entre
`2 * lower` y `2 * upper` para el cluster y deja `k - 2` distritos en el
complemento. El carving de planes completos siempre usa tamaño 1.

El archivo de entrada debe ser un JSON de adjacency graph; cada nodo requiere
`TOTPOP` (también se aceptan `population` o `total_population`).

## Licencia y modificación

El upstream está bajo GNU GPL v3. Esta adaptación se distribuye bajo la misma
licencia. Véanse `LICENSE` y `NOTICE`: el código fue reescrito/adaptado para
PuLP, con modificaciones identificadas, y no es una copia literal. La licencia
GPL exige conservar los avisos y marcar las versiones modificadas.

Para Tabasco existe una corrida específica:

```bash
python scripts/run_tabasco.py --top-t 10
```

Usa `municipios_datos.csv` y `municipios.csv`, fija `k=3`, `L=U=800866`,
enraíza en `CENTRO` (ID 4), y escribe el resultado en
`references/runs/tabasco_k3.json`. Ese directorio está excluido del control de
versiones porque contiene salidas de experimentos.

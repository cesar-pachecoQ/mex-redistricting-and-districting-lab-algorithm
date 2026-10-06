# Resumen operativo: adaptacion a datos de Tabasco

## Alcance

La adaptacion mexicana usa los 17 municipios de Tabasco contenidos en:

- `data/raw/municipios_datos.csv`.
- `data/raw/municipios.csv`.

La equivalencia es:

| Articulo | Tabasco |
|---|---|
| State | Estado de Tabasco |
| County | Municipio |
| County-level graph | Grafo de 17 municipios |
| Population | `poblacion` |
| Adjacency | `vecinos` |
| District | Distrito buscado |
| County cluster | Cluster de municipios |
| Whole county | Municipio completo |
| County split | Municipio repartido entre distritos |

El experimento actual trabaja a nivel municipal. Todavia no trabaja con
secciones electorales, AGEB ni manzanas.

## Datos disponibles

### `municipios_datos.csv`

Contiene:

- `id`: identificador local.
- `nombre`: nombre del municipio.
- `poblacion`: poblacion municipal.
- `vecinos`: IDs separados por `;`.

### `municipios.csv`

Contiene:

- `id` y `nombre`.
- `x`, `y`: coordenadas puntuales, aparentemente centroides.
- `poblacion`.
- `frontera`.
- `indigenas`.

El adaptador comprueba que los IDs y las poblaciones coincidan entre los dos
archivos.

## Grafo construido

El lector especifico esta en:

`refuting_county_splits/data.py::load_municipios_csv`

El resultado tiene:

```text
nodo = id municipal
nodo["TOTPOP"] = poblacion
arista = vecindad municipio-municipio
```

Tambien conserva nombre, coordenadas y campos descriptivos disponibles en el
segundo CSV.

La validacion actual confirma:

- 17 nodos.
- 31 aristas no dirigidas.
- vecindades simetricas.
- grafo conexo.
- poblacion total `2,402,598`.

La regla geometrica que produjo `vecinos` no esta documentada. No se sabe si
representa contiguedad tipo `rook` (frontera con longitud positiva) o `queen`
(contacto tambien por vertice). Esa decision debe documentarse antes de usar
los resultados como evidencia geografica.

## Algoritmos que si se pudieron adaptar

### 1. Enumeracion top-t de clusters

Se puede ejecutar con:

- poblacion municipal;
- vecinos;
- raiz municipal;
- `k`;
- `k'` o `cluster_size`;
- limites `L,U`.

El objetivo disponible actualmente es `cut_edges`. El resultado significa:

> clusters contiguos de municipios que cumplen las cotas poblacionales y que
> minimizan el numero de adyacencias cruzadas.

No significa compacidad geografica real.

### 2. Heuristica de tallado

Tambien se puede aplicar con municipios completos. Cada distrito tallado es un
subconjunto de municipios y el remanente se vuelve a resolver.

El resultado es una familia de planes candidatos, no una enumeracion exhaustiva
ni un certificado de optimalidad.

### 3. Balance poblacional

El modelo puede imponer cualquier intervalo `L,U` entero o real. Para una
desviacion maxima de una persona se calculan los limites a partir de la
poblacion total y `k`.

## Experimento ejecutado: tres distritos

Se ejecuto:

```text
k = 3
L = U = 800866
raiz = CENTRO, ID 4
objetivo = cut_edges
cluster_size = 1
top_t = 10
```

La poblacion total es divisible entre tres:

```text
2,402,598 / 3 = 800,866
```

El resultado se guardo en:

`references/runs/tabasco_k3.json`

Resultado:

```json
{
  "top_clusters": 0,
  "whole_municipality_plans": 0
}
```

Ademas, se revisaron exhaustivamente las combinaciones de los 17 municipios.
No existe ningun subconjunto con poblacion exacta `800866`, ni siquiera
ignorando la conectividad. Por tanto, el resultado vacio es una imposibilidad
combinatoria de los municipios actuales, no un fallo de la validacion de
conectividad.

Como prueba diagnostica, con cotas relajadas `700000 <= poblacion <= 900000`,
el modelo encontro 3 clusters candidatos y la heuristica encontro 9 planes.
El primer plan diagnostico tuvo poblaciones:

```text
739035, 878330, 785233
```

y `cut_edges=12`.

Esta corrida relajada valida el funcionamiento del pipeline, pero no sustituye
la condicion de desviacion de una persona.

## Limitacion conceptual de municipios completos

Si el modelo asigna municipios completos, todos los resultados tienen cero
municipios divididos por construccion. Esto no prueba que una redistritacion
electoral real pueda evitar divisiones municipales.

Para estudiar divisiones reales se necesitan unidades inferiores al municipio,
por ejemplo:

- secciones electorales;
- AGEB;
- manzanas censales.

Cada unidad inferior debe tener:

- identificador estable;
- municipio de pertenencia;
- poblacion;
- geometria o vecindades;
- relacion de adyacencia con otras unidades.

Entonces la metrica equivalente seria:

```text
municipality_splits =
sum_m (numero de distritos que intersectan al municipio m - 1)
```

La implementacion actual todavia no contiene esa metrica ni ese modelo de
asignacion.

## Objetivos que no se pudieron usar validamente

### Perimetro

El modelo requiere:

- `shared_perim` para cada par de municipios vecinos;
- `boundary_node`;
- `boundary_perim` para el borde exterior.

Los CSV no contienen longitudes de frontera compartida. El campo `frontera` no
esta documentado y no permite saber que parte del borde corresponde al limite
exterior del estado. Por eso no debe mapearse automaticamente a
`boundary_perim`.

### Polsby-Popper

Tambien se requiere:

- geometria poligonal valida;
- area municipal;
- CRS proyectado con unidades metricas;
- perimetros externos y compartidos.

Las coordenadas `x,y` no sustituyen poligonos ni areas. Actualmente
`inverse_polsby_popper` solo puede evaluarse como infinito si no hay area y no
debe usarse para comparar municipios.

### Representacion indigena

`indigenas` parece ser un porcentaje municipal, pero no documenta:

- poblacion base;
- si es poblacion total o poblacion en edad de votar;
- distribucion espacial dentro del municipio;
- fuente y fecha;
- unidad electoral asignable.

No es suficiente para reproducir el caso de Alabama sobre mayoria de VAP
indigena.

### Justicia partidista

No existen votos, resultados electorales, preferencias partidistas ni planes de
referencia. Por tanto no se pueden reproducir los analisis tipo North Carolina.

## Datos faltantes prioritarios

1. Claves oficiales de INEGI, preferentemente `CVEGEO`/`AGEM`, para no depender
   de IDs locales ni nombres.
2. Poligonos municipales oficiales o reconciliados con una fuente y fecha
   documentadas.
3. Regla de contiguidad documentada: `rook` o `queen`.
4. Longitud de frontera compartida por cada arista.
5. Area y frontera exterior de cada municipio.
6. Secciones electorales, AGEB o manzanas para permitir divisiones reales.
7. Poblacion de cada unidad inferior.
8. Datos electorales y de representacion indigena si se agregan criterios
   politicos o de derechos electorales.

El informe existente sobre fuentes recomienda usar el Catalogo Unico de INEGI
para claves, Banco de Indicadores para poblacion y geometria municipal para
derivar colindancias, areas y perimetros.

## Interpretacion final

Con los datos actuales se puede usar el nucleo matematico del articulo para
estudiar factibilidad, conectividad y clusters de municipios. Para Tabasco, el
experimento estricto de tres distritos municipales con desviacion maxima de una
persona no tiene solucion porque ninguna suma de municipios alcanza `800866`.

La siguiente etapa no debe ser forzar el algoritmo sobre los mismos CSV, sino
decidir primero la unidad territorial de distritacion. Si se mantiene el nivel
municipal, deben reportarse resultados como exploracion de particiones
municipales. Si se quiere una redistritacion electoral real, se necesitan las
unidades submunicipales y sus datos poblacionales.

---
---

Revisar la converción de datos.

Revisar conexidad.

ID seccion, Zona Correspondiente.

15%, 10% y 7% de población.

user: @
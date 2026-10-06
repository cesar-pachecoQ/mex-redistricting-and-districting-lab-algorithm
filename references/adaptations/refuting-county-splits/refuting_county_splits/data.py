"""Entrada mínima y normalización de grafos de unidades geográficas."""

import csv
import json
from math import isfinite
from pathlib import Path
from typing import Any

import networkx as nx
from networkx.readwrite import json_graph


def normalize_population(graph: nx.Graph, field: str = "TOTPOP") -> nx.Graph:
    """Return a copy whose node populations are finite non-negative numbers."""
    result = graph.copy()
    aliases = (field, "TOTPOP", "P0010001", "total_population", "population")
    for node, attrs in result.nodes(data=True):
        value = next((attrs[key] for key in aliases if key in attrs), None)
        if value is None:
            raise ValueError(f"El nodo {node!r} no tiene población ({field})")
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Población inválida en {node!r}") from exc
        if value < 0 or not isfinite(value):
            raise ValueError(f"Población inválida en {node!r}")
        result.nodes[node][field] = value
        # The optimization layer follows the upstream contract regardless of
        # the source field name used by a dataset.
        result.nodes[node]["TOTPOP"] = value
    return result


def load_adjacency_graph(path: str | Path, population_field: str = "TOTPOP") -> nx.Graph:
    """Load NetworkX adjacency-graph JSON and normalize ``population_field``."""
    with Path(path).open(encoding="utf-8") as stream:
        payload: dict[str, Any] = json.load(stream)
    return normalize_population(json_graph.adjacency_graph(payload), population_field)


def load_municipios_csv(
    data_path: str | Path,
    attributes_path: str | Path | None = None,
) -> nx.Graph:
    """Build a Tabasco municipality graph from the two project CSV files.

    ``data_path`` supplies the population and semicolon-separated neighbors.
    ``attributes_path`` optionally supplies names, coordinates and descriptive
    fields from ``municipios.csv``. The resulting graph follows the adaptation
    contract: node IDs are integers and population is stored as ``TOTPOP``.
    """
    data_path = Path(data_path)
    graph = nx.Graph()
    with data_path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"No hay municipios en {data_path}")

    declared_neighbors: dict[int, set[int]] = {}
    for row in rows:
        node = int(row["id"])
        if node in graph:
            raise ValueError(f"ID municipal duplicado: {node}")
        population = float(row["poblacion"])
        if population < 0 or not population.is_integer():
            raise ValueError(f"Población municipal inválida para {node}")
        graph.add_node(
            node,
            NAME=row["nombre"],
            TOTPOP=int(population),
            vecinos=row.get("vecinos", ""),
        )
        declared_neighbors[node] = {
            int(value) for value in row.get("vecinos", "").strip().split(";") if value
        }

    for row in rows:
        node = int(row["id"])
        for neighbor in declared_neighbors[node]:
            if neighbor not in graph:
                raise ValueError(f"Vecino inexistente {neighbor} para municipio {node}")
            if neighbor != node:
                graph.add_edge(node, neighbor)

    missing_reverse = [
        (node, neighbor)
        for node, neighbors in declared_neighbors.items()
        for neighbor in neighbors
        if node not in declared_neighbors[neighbor]
    ]
    if missing_reverse:
        raise ValueError(f"Vecindad no simétrica: {missing_reverse[:3]}")
    if not nx.is_connected(graph):
        raise ValueError("El grafo municipal no es conexo")

    if attributes_path is not None:
        attributes_path = Path(attributes_path)
        with attributes_path.open(newline="", encoding="utf-8-sig") as stream:
            attribute_rows = {int(row["id"]): row for row in csv.DictReader(stream)}
        if set(attribute_rows) != set(graph):
            raise ValueError("Los IDs de ambos CSV no coinciden")
        for node, row in attribute_rows.items():
            if int(float(row["poblacion"])) != graph.nodes[node]["TOTPOP"]:
                raise ValueError(f"Poblaciones discrepantes para municipio {node}")
            graph.nodes[node].update(
                {
                    key: value
                    for key, value in row.items()
                    if key not in {"id", "nombre", "poblacion"}
                }
            )

    graph.graph.update(source=str(data_path), municipality_count=graph.number_of_nodes())
    return graph

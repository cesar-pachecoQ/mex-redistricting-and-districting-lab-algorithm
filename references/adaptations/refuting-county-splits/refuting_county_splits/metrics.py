"""Métricas de evaluación, separadas del modelo de optimización."""

import math
from collections.abc import Iterable

import networkx as nx


def cut_edges(graph: nx.Graph, district: Iterable) -> float:
    members = set(district)
    return float(sum(1 for u, v in graph.edges if (u in members) != (v in members)))


def perimeter(graph: nx.Graph, district: Iterable) -> float:
    members = set(district)
    total = 0.0
    for u, v, attrs in graph.edges(data=True):
        if (u in members) != (v in members):
            total += float(attrs.get("shared_perim", 1.0))
    for node in members:
        if graph.nodes[node].get("boundary_node", False):
            total += float(graph.nodes[node].get("boundary_perim", 0.0))
    return total


def inverse_polsby_popper(graph: nx.Graph, district: Iterable) -> float:
    members = set(district)
    area = sum(float(graph.nodes[n].get("area", 0.0)) for n in members)
    if area <= 0:
        return math.inf
    return perimeter(graph, members) ** 2 / (4.0 * math.pi * area)


def district_metrics(graph: nx.Graph, district: Iterable) -> dict[str, float]:
    return {
        "cut_edges": cut_edges(graph, district),
        "perimeter": perimeter(graph, district),
        "inverse_polsby_popper": inverse_polsby_popper(graph, district),
    }


def plan_objective(graph: nx.Graph, plan: list[Iterable], objective: str) -> float:
    """Evaluate a complete plan using the same metric as the reference."""
    if objective == "cut_edges":
        labels = {
            node: district_id
            for district_id, district in enumerate(plan)
            for node in district
        }
        return float(sum(labels[u] != labels[v] for u, v in graph.edges))
    if objective == "perimeter":
        return float(sum(perimeter(graph, district) for district in plan))
    if objective == "inverse_polsby_popper":
        values = [inverse_polsby_popper(graph, district) for district in plan]
        return float(sum(values) / len(values))
    raise ValueError(f"Objetivo no soportado: {objective}")

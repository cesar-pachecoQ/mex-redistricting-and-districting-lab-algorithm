"""Reimplementación aislada para estudiar el algoritmo del paper."""

from .data import load_adjacency_graph, load_municipios_csv, normalize_population
from .metrics import district_metrics
from .optimization import districting_heuristic, enumerate_top_districts

__all__ = [
    "district_metrics",
    "districting_heuristic",
    "enumerate_top_districts",
    "load_adjacency_graph",
    "load_municipios_csv",
    "normalize_population",
]

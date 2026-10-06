import json

import networkx as nx
from networkx.readwrite import json_graph
from refuting_county_splits.data import load_adjacency_graph
from refuting_county_splits.metrics import district_metrics
from refuting_county_splits.optimization import (
    districting_heuristic,
    enumerate_top_districts,
    find_minimal_separator,
)


def graph_fixture():
    graph = nx.path_graph(4)
    nx.set_node_attributes(graph, 1, "TOTPOP")
    nx.set_edge_attributes(graph, 2.0, "shared_perim")
    graph.nodes[0].update(boundary_node=True, boundary_perim=3.0, area=1.0)
    graph.nodes[3].update(boundary_node=True, boundary_perim=3.0, area=1.0)
    nx.set_node_attributes(graph, 1.0, "area")
    return graph


def test_load_adjacency_graph_normalizes_alias(tmp_path):
    graph = graph_fixture()
    for node in graph:
        graph.nodes[node]["population"] = graph.nodes[node].pop("TOTPOP")
    path = tmp_path / "graph.json"
    path.write_text(json.dumps(json_graph.adjacency_data(graph)), encoding="utf-8")
    loaded = load_adjacency_graph(path)
    assert all(loaded.nodes[node]["TOTPOP"] == 1 for node in loaded)


def test_load_adjacency_graph_accepts_census_population_field(tmp_path):
    graph = graph_fixture()
    for node in graph:
        graph.nodes[node]["P0010001"] = graph.nodes[node].pop("TOTPOP")
    path = tmp_path / "census_graph.json"
    path.write_text(json.dumps(json_graph.adjacency_data(graph)), encoding="utf-8")
    loaded = load_adjacency_graph(path)
    assert all(loaded.nodes[node]["TOTPOP"] == 1 for node in loaded)


def test_metrics_are_evaluation_only_and_consistent():
    metrics = district_metrics(graph_fixture(), {0, 1})
    assert metrics["cut_edges"] == 1
    assert metrics["perimeter"] == 5
    assert metrics["inverse_polsby_popper"] > 0


def test_separator_and_small_pulp_model_are_feasible():
    graph = graph_fixture()
    assert find_minimal_separator(graph, {0}, 3) == {1}
    results = enumerate_top_districts(graph, districts=2, lower=2, upper=2, enumeration_limit=2)
    assert results
    for result in results:
        district = set(result["district"])
        assert nx.is_connected(graph.subgraph(district))
        assert nx.is_connected(graph.subgraph(set(graph) - district))


def test_cluster_size_supports_article_case_study_shape():
    graph = graph_fixture()
    results = enumerate_top_districts(
        graph, districts=2, cluster_size=1, lower=2, upper=2, enumeration_limit=1
    )
    assert len(results[0]["district"]) == 2


def test_sequential_heuristic_recalculates_and_completes():
    plans = districting_heuristic(graph_fixture(), districts=2, lower=2, upper=2, enumeration_limit=1)
    assert plans
    assert set(plans[0][0]) | set(plans[0][1]) == set(range(4))

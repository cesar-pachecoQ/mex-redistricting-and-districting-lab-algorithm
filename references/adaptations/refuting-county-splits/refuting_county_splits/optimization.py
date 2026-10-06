"""Modelo PuLP y separación externa para enumerar distritos candidatos."""

from collections.abc import Iterable
from typing import Any

import networkx as nx
import pulp

from .metrics import district_metrics


def find_minimal_separator(graph: nx.Graph, component: Iterable, target: Any) -> set:
    """Find a minimal node boundary separating ``component`` from ``target``.

    This is the boundary-search step used by the separator cuts of Fischetti et
    al.; it is deliberately independent of PuLP so it can be unit-tested.
    """
    component = set(component)
    boundary = set(nx.node_boundary(graph, component))
    visited = {target}
    frontier = [target]
    while frontier:
        current = frontier.pop()
        if current in boundary:
            continue
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.append(neighbor)
    return boundary & visited


def _configuration(graph, districts, lower, upper, root, cluster_size):
    k = districts or graph.graph.get("k")
    if not k or k < 2:
        raise ValueError("districts/k debe ser al menos 2")
    lower = graph.graph.get("L", lower)
    upper = graph.graph.get("U", upper)
    if lower is None or upper is None:
        total = sum(graph.nodes[n]["TOTPOP"] for n in graph)
        ideal = total / k
        lower, upper = ideal, ideal
    if root is None:
        root = max(graph, key=lambda node: graph.nodes[node]["TOTPOP"])
    size = cluster_size if cluster_size is not None else graph.graph.get("size", 1)
    if not 1 <= size < k:
        raise ValueError("cluster_size debe estar entre 1 y k - 1")
    return int(k), float(lower), float(upper), root, int(size)


def _add_articulation_constraints(model, graph, x, lower, upper, k, size, root):
    """Prevent an articulation from isolating an impossible population side."""
    for articulation in nx.articulation_points(graph):
        for component in nx.connected_components(nx.subgraph(graph, set(graph) - {articulation})):
            population = sum(graph.nodes[node]["TOTPOP"] for node in component)
            if root in component:
                # Match the reference strengthening: a component that is too
                # small cannot form the rooted side without its articulation.
                impossible = population < lower * size
            else:
                impossible = population < lower * (k - size)
            if impossible:
                for node in component:
                    model += x[articulation] == x[node], f"articulation_{articulation}_{node}"


def _build_model(graph, objective, lower, upper, k, size, root):
    model = pulp.LpProblem("top_districts", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("district", list(graph), cat=pulp.LpBinary)
    total = sum(graph.nodes[n]["TOTPOP"] for n in graph)
    model += pulp.lpSum(graph.nodes[n]["TOTPOP"] * x[n] for n in graph) >= lower * size
    model += pulp.lpSum(graph.nodes[n]["TOTPOP"] * x[n] for n in graph) <= upper * size
    complement_population = total - pulp.lpSum(graph.nodes[n]["TOTPOP"] * x[n] for n in graph)
    model += complement_population >= (k - size) * lower
    model += complement_population <= (k - size) * upper
    model += x[root] == 1

    # Shirabe single-commodity flow makes the root district connected.
    arcs = [(u, v) for u, v in graph.edges for u, v in ((u, v), (v, u))]
    flow = pulp.LpVariable.dicts("flow", arcs, lowBound=0)
    big_m = max(1, graph.number_of_nodes() - 1)
    for node in graph:
        if node != root:
            model += (
                pulp.lpSum(flow[a] for a in arcs if a[1] == node)
                - pulp.lpSum(flow[a] for a in arcs if a[0] == node)
                == x[node]
            )
        for arc in arcs:
            if arc[0] == node:
                model += flow[arc] <= big_m * x[node]

    cuts = pulp.LpVariable.dicts("cut", list(graph.edges), cat=pulp.LpBinary)
    for u, v in graph.edges:
        model += x[u] - x[v] <= cuts[(u, v)]
        model += x[v] - x[u] <= cuts[(u, v)]
    edge_cost = pulp.lpSum(
        graph.edges[u, v].get("shared_perim", 1.0) * cuts[(u, v)] for u, v in graph.edges
    )
    boundary_cost = pulp.lpSum(
        graph.nodes[n].get("boundary_perim", 0.0) * x[n]
        for n in graph
        if graph.nodes[n].get("boundary_node", False)
    )
    if objective == "cut_edges":
        model += pulp.lpSum(cuts.values())
    else:
        # Perimeter is linear. inverse_polsby_popper is evaluated after solving.
        model += edge_cost + boundary_cost
    _add_articulation_constraints(model, graph, x, lower, upper, k, size, root)
    return model, x


def _add_separator_cuts(model, graph, x, district):
    complement = set(graph) - set(district)
    components = list(nx.connected_components(graph.subgraph(complement)))
    if len(components) <= 1:
        return False
    largest = max(components, key=lambda c: sum(graph.nodes[n]["TOTPOP"] for n in c))
    target = max(largest, key=lambda n: graph.nodes[n]["TOTPOP"])
    changed = False
    for component in components:
        if component is largest:
            continue
        source = max(component, key=lambda n: graph.nodes[n]["TOTPOP"])
        separator = find_minimal_separator(graph, component, target)
        # The upstream inequality is expressed with complement-assignment
        # variables. Here ``x`` means membership in the rooted district.
        complement_source = 1 - x[source]
        complement_target = 1 - x[target]
        complement_separator = pulp.lpSum(1 - x[n] for n in separator)
        model += (
            complement_source + complement_target
            <= 1 + complement_separator
        )
        changed = True
    return changed


def enumerate_top_districts(graph: nx.Graph, objective="cut_edges", enumeration_limit=10,
                            districts=None, lower=None, upper=None, root=None,
                            cluster_size=None,
                            solver=None) -> list[dict[str, Any]]:
    """Enumerate up to ``enumeration_limit`` feasible connected districts."""
    if objective not in {"cut_edges", "perimeter", "inverse_polsby_popper"}:
        raise ValueError("objective no soportado")
    k, lower, upper, root, size = _configuration(
        graph, districts, lower, upper, root, cluster_size
    )
    model, x = _build_model(graph, objective, lower, upper, k, size, root)
    solver = solver or pulp.PULP_CBC_CMD(msg=False)
    results = []
    seen = set()
    while len(results) < enumeration_limit:
        if model.solve(solver) != pulp.LpStatusOptimal:
            break
        district = frozenset(node for node in graph if pulp.value(x[node]) > 0.5)
        if not district or district in seen:
            break
        if _add_separator_cuts(model, graph, x, district):
            continue
        seen.add(district)
        metrics = district_metrics(graph, district)
        results.append({"district": sorted(district, key=str), "metrics": metrics})
        # Exclude this exact assignment and permit the next optimum.
        complement = set(graph) - set(district)
        model += pulp.lpSum(x[n] for n in district) + pulp.lpSum(1 - x[n] for n in complement) <= graph.number_of_nodes() - 1
    return results


def _recalculate_boundary(graph: nx.Graph, remaining: set, used: set) -> nx.Graph:
    subgraph = graph.subgraph(remaining).copy()
    for node in subgraph:
        original = graph.nodes[node]
        boundary = bool(original.get("boundary_node", False))
        boundary_perim = float(original.get("boundary_perim", 0.0)) if boundary else 0.0
        for neighbor in graph.neighbors(node):
            if neighbor in used:
                boundary = True
                boundary_perim += float(graph.edges[node, neighbor].get("shared_perim", 1.0))
        subgraph.nodes[node]["boundary_node"] = boundary
        subgraph.nodes[node]["boundary_perim"] = boundary_perim
    return subgraph


def districting_heuristic(graph: nx.Graph, objective="cut_edges", enumeration_limit=10,
                           districts=None, lower=None, upper=None, root=None) -> list[list[list]]:
    """Build complete plans sequentially, recalculating the frontier each step."""
    k, lower, upper, root, _ = _configuration(graph, districts, lower, upper, root, 1)
    pending = [[item["district"]] for item in enumerate_top_districts(
        graph, objective, enumeration_limit, k, lower, upper, root, 1
    )]
    plans = []
    while pending:
        plan = pending.pop()
        used = {node for district in plan for node in district}
        if len(plan) == k - 1:
            if used != set(graph):
                plans.append(plan + [sorted(set(graph) - used, key=str)])
            continue
        remaining = set(graph) - used
        subgraph = _recalculate_boundary(graph, remaining, used)
        count = k - len(plan)
        subgraph.graph.update(k=count, L=lower, U=upper)
        for item in enumerate_top_districts(
            subgraph, objective, enumeration_limit, count, lower, upper, cluster_size=1
        ):
            pending.append(plan + [item["district"]])
    return plans

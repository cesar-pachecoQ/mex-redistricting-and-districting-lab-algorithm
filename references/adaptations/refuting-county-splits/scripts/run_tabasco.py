"""Ejecuta la réplica municipal de Tabasco para tres distritos.

La corrida usa sólo municipios completos y ``cut_edges``. No interpreta
``frontera`` como perímetro geométrico.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from refuting_county_splits.data import load_municipios_csv
from refuting_county_splits.metrics import plan_objective
from refuting_county_splits.optimization import districting_heuristic, enumerate_top_districts
from refuting_county_splits.serialization import save_results

TOTAL_POPULATION = 2_402_598
DISTRICTS = 3
LOWER = 800_866
UPPER = 800_866


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/raw/municipios_datos.csv"))
    parser.add_argument("--attributes", type=Path, default=Path("data/raw/municipios.csv"))
    parser.add_argument("--output", type=Path, default=Path("references/runs/tabasco_k3.json"))
    parser.add_argument("--top-t", type=int, default=10)
    args = parser.parse_args()

    graph = load_municipios_csv(args.data, args.attributes)
    actual_total = sum(graph.nodes[node]["TOTPOP"] for node in graph)
    if actual_total != TOTAL_POPULATION:
        raise ValueError(f"Población total inesperada: {actual_total}")

    clusters = enumerate_top_districts(
        graph,
        objective="cut_edges",
        enumeration_limit=args.top_t,
        districts=DISTRICTS,
        cluster_size=1,
        lower=LOWER,
        upper=UPPER,
        root=4,
    )
    plans = districting_heuristic(
        graph,
        objective="cut_edges",
        enumeration_limit=args.top_t,
        districts=DISTRICTS,
        lower=LOWER,
        upper=UPPER,
        root=4,
    )
    serialized_plans = [
        {
            "districts": plan,
            "objective": plan_objective(graph, plan, "cut_edges"),
            "populations": [
                sum(graph.nodes[node]["TOTPOP"] for node in district)
                for district in plan
            ],
        }
        for plan in plans
    ]
    save_results(
        args.output,
        {"top_clusters": clusters, "whole_municipality_plans": serialized_plans},
        source_data=str(args.data),
        source_attributes=str(args.attributes),
        districts=DISTRICTS,
        lower=LOWER,
        upper=UPPER,
        root=4,
        objective="cut_edges",
        top_t=args.top_t,
        total_population=actual_total,
        note="Municipios completos; no representa perímetro geométrico ni municipality splits submunicipales.",
    )
    print(json.dumps({"top_clusters": len(clusters), "plans": len(plans)}, indent=2))


if __name__ == "__main__":
    main()

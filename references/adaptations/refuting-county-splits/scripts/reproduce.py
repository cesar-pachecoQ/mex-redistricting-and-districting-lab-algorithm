"""Reproducción manual: no se invoca al importar ni durante la instalación."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from refuting_county_splits.data import load_adjacency_graph
from refuting_county_splits.optimization import enumerate_top_districts
from refuting_county_splits.serialization import save_results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    parser.add_argument("--districts", type=int, default=2)
    parser.add_argument("--top-t", type=int, default=3)
    parser.add_argument("--cluster-size", type=int, default=1)
    parser.add_argument("--lower", type=float, required=True)
    parser.add_argument("--upper", type=float, required=True)
    args = parser.parse_args()
    graph = load_adjacency_graph(args.input)
    results = enumerate_top_districts(graph, districts=args.districts, lower=args.lower,
                                      upper=args.upper, cluster_size=args.cluster_size,
                                      enumeration_limit=args.top_t)
    save_results(args.output, results, input=str(args.input), districts=args.districts)
    print(json.dumps(results, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()

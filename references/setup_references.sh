#!/usr/bin/env bash

# Reproduce checkouts externos definidos en references/registry/.
# Cada referencia se fija a un commit; no se ejecutan notebooks ni solvers aqui.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(git -C "$SCRIPT_DIR/.." rev-parse --show-toplevel)"
REPOS_DIR="$ROOT_DIR/references/repos"

REFERENCE_NAME="refuting_a_widespread_belief_about_county_splits"
REFERENCE_URL="https://github.com/AustinLBuchanan/refuting_a_widespread_belief_about_county_splits.git"
REFERENCE_COMMIT="c179753d1223c9fd4beb85dbaa5b7ea5ed33afc6"
REFERENCE_DIR="$REPOS_DIR/$REFERENCE_NAME"
PYTHON_VERSION="3.12"
INSTALL_GUROBI="${INSTALL_GUROBI:-0}"

mkdir -p "$REPOS_DIR"

if [[ -d "$REFERENCE_DIR/.git" ]]; then
  git -C "$REFERENCE_DIR" fetch --tags --prune origin
else
  git clone "$REFERENCE_URL" "$REFERENCE_DIR"
fi

git -C "$REFERENCE_DIR" checkout --detach "$REFERENCE_COMMIT"

if [[ "$(git -C "$REFERENCE_DIR" rev-parse HEAD)" != "$REFERENCE_COMMIT" ]]; then
  printf '%s\n' "La referencia no quedo en el commit esperado: $REFERENCE_COMMIT" >&2
  exit 1
fi

if [[ ! -x "$REFERENCE_DIR/.venv/bin/python" ]]; then
  uv venv --python "$PYTHON_VERSION" "$REFERENCE_DIR/.venv"
fi

uv pip install --python "$REFERENCE_DIR/.venv/bin/python" \
  "geopandas>=1" \
  "jupyterlab>=4" \
  "networkx>=3"

if [[ "$INSTALL_GUROBI" == "1" ]]; then
  uv pip install --python "$REFERENCE_DIR/.venv/bin/python" "gurobipy>=12"
else
  printf '%s\n' "Gurobi omitido. Para instalarlo: INSTALL_GUROBI=1 ./references/setup_references.sh"
fi

printf '%s\n' "Referencia preparada en: $REFERENCE_DIR"
printf '%s\n' "Commit fijado: $REFERENCE_COMMIT"
printf '%s\n' "Se requiere una licencia valida de Gurobi para ejecutar el algoritmo original."

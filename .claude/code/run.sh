#!/usr/bin/env bash
# Contrato de verificación (política de QA). exit 0 = verde; verbo no implementado sale 0.
set -e
cd "$(dirname "$0")/../.."
case "${1:-test}" in
  test|rapido) uv run pytest -q ;;
  humo) uv run python -c "import publi.lexico, publi.mascara, publi.pu" ;;
  *) exit 0 ;;
esac

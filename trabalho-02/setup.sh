#!/usr/bin/env bash
# =============================================================================
# setup.sh — Trabalho 02 FAED/PPGIA/PUC-PR
# Configura o ambiente, gera o banco e executa os experimentos.
# Requer: Python 3.10+
# Uso:  bash setup.sh
# =============================================================================

set -euo pipefail
export PYTHONIOENCODING=utf-8

GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}   $*"; }
err()   { echo -e "${RED}[ERRO]${NC} $*"; exit 1; }

echo
echo " ============================================================"
echo "  Trabalho 02 — FAED / PPGIA / PUC-PR"
echo "  Análise de Algoritmos de Busca em Grafos"
echo " ============================================================"
echo

# Verifica Python 3.10+
PYTHON=$(command -v python3 || command -v python || true)
[[ -z "$PYTHON" ]] && err "Python não encontrado. Instale Python 3.10+."

PY_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
[[ "$PY_MAJOR" -lt 3 || ( "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 10 ) ]] && \
    err "Python $PY_VERSION encontrado, mas 3.10+ é necessário."
ok "Python $PY_VERSION encontrado"

# Cria e ativa venv
if [[ ! -d ".venv" ]]; then
    info "Criando ambiente virtual..."
    "$PYTHON" -m venv .venv
fi

info "Ativando ambiente virtual..."
# shellcheck disable=SC1091
source .venv/bin/activate

# Instala dependências
info "Instalando dependências..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
ok "Dependências instaladas"

# Gera banco SQLite
info "Gerando banco de dados sintético..."
python -m db.seed
ok "Banco gerado em db/backhaul_sim.db"

# Executa experimentos
info "Executando experimentos..."
python -m src.runner

echo
echo " ============================================================"
echo "  Concluído com sucesso!"
echo "  Resultados: results/metrics/sumario.csv"
echo "  Grafos:     results/graphs/*.html"
echo " ============================================================"
echo

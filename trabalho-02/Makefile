# =============================================================================
# Makefile — Trabalho 02 FAED/PPGIA/PUC-PR
# Requer: make, Python 3.10+, pip
# =============================================================================

PYTHON  := python
PIP     := $(PYTHON) -m pip
DB_PATH := db/backhaul_sim.db
ZIP     := ../trabalho-02.zip

.PHONY: all install seed run viz clean zip help

all: install seed run        ## Fluxo completo: instalar → seed → experimentos

help:                        ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install:                     ## Instala dependências Python
	$(PIP) install -q -r requirements.txt

seed:                        ## Gera o banco SQLite sintético
	$(PYTHON) -m db.seed --db $(DB_PATH)

run:                         ## Executa experimentos e exporta CSVs
	$(PYTHON) -m src.runner

viz:                         ## Gera apenas as visualizações Pyvis (sem runner completo)
	$(PYTHON) -c "from src.graph_data import carregar_grafo; \
	              from src.visualization import renderizar_base; \
	              renderizar_base(carregar_grafo())"

clean:                       ## Remove resultados gerados (mantém banco)
	$(RM) results/metrics/*.csv results/graphs/*.html

zip: run                     ## Gera .zip para entrega (código + banco + relatório)
	$(PYTHON) -m zipfile -c $(ZIP) \
	    db/backhaul_sim.db db/schema.sql db/seed.py \
	    src/ results/ report/artigo.md report/references.bib \
	    requirements.txt README.md
	@echo "Entrega gerada: $(ZIP)"

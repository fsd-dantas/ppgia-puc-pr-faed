"""
setup_baseline.py
-----------------
Gera o baseline de dados compartilhado entre todas as implementações.

Usa data_generator.py (fsd-dantas, seed=42) como fonte canônica e
exporta os dados nos formatos esperados por cada contribuidor:

  fsd-dantas/dados/
    registros_<N>.csv          colunas: matricula, nome, salario, cod_setor

  rafaCS2002/genDataSequence/
    data_<N>_1.csv ... data_<N>_5.csv   colunas: Mat, Name, Sal, CodSec
    (5 cópias idênticas — mesmo dado, mesma seed, runs "diferentes" do Rafael)

Uso:
    python setup_baseline.py
    python setup_baseline.py --volumes 10000 50000 100000
    python setup_baseline.py --dry-run   # mostra o que seria gerado
"""

import argparse
import csv
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos relativos ao diretório deste script
# ---------------------------------------------------------------------------
BASE        = Path(__file__).parent
FSD_DADOS   = BASE / "fsd-dantas" / "dados"
RAFA_SEQ    = BASE / "rafaCS2002" / "genDataSequence"
DATA_GEN    = BASE / "fsd-dantas"

sys.path.insert(0, str(DATA_GEN))
from data_generator import gerar_registros, salvar_csv  # noqa: E402

VOLUMES_DEFAULT = [10_000, 50_000, 100_000]


# ---------------------------------------------------------------------------
# Exportadores
# ---------------------------------------------------------------------------

def exportar_fsd(registros: list[dict], n: int, dry_run: bool) -> Path:
    """Salva no formato fsd-dantas: matricula, nome, salario, cod_setor."""
    dest = FSD_DADOS / f"registros_{n}.csv"
    if dry_run:
        print(f"  [dry-run] {dest}")
        return dest
    FSD_DADOS.mkdir(parents=True, exist_ok=True)
    salvar_csv(registros, dest)
    return dest


def exportar_rafa(registros: list[dict], n: int, dry_run: bool) -> list[Path]:
    """
    Salva 5 cópias no formato rafaCS2002: Mat, Name, Sal, CodSec.
    Cópias idênticas — garante mesma baseline para as 5 rodadas dele.
    """
    dests = []
    for k in range(1, 6):
        dest = RAFA_SEQ / f"data_{n}_{k}.csv"
        dests.append(dest)
        if dry_run:
            print(f"  [dry-run] {dest}")
            continue
        RAFA_SEQ.mkdir(parents=True, exist_ok=True)
        with dest.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Mat", "Name", "Sal", "CodSec"])
            for r in registros:
                writer.writerow([
                    r["matricula"],
                    r["nome"],
                    r["salario"],
                    r["cod_setor"],
                ])
    return dests


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def main(volumes: list[int], dry_run: bool) -> None:
    t0 = time.perf_counter()
    print(f"\n{'='*60}")
    print(f"  setup_baseline.py")
    print(f"  Inicio  : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Volumes : {volumes}")
    print(f"  Dry-run : {dry_run}")
    print(f"{'='*60}")

    for n in volumes:
        print(f"\n  Gerando N = {n:,} (seed=42)...")
        registros = gerar_registros(n, seed=42)

        print(f"  -> fsd-dantas/dados/")
        exportar_fsd(registros, n, dry_run)

        print(f"  -> rafaCS2002/genDataSequence/ (5 copias)")
        exportar_rafa(registros, n, dry_run)

        print(f"  N = {n:,} concluido.")

    print(f"\n{'='*60}")
    print(f"  Fim     : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Duracao : {time.perf_counter() - t0:.2f}s")
    print(f"{'='*60}")
    if not dry_run:
        print(f"\n  Proximos passos:")
        print(f"    fsd-dantas  : python fsd-dantas/benchmark.py")
        print(f"    rafaCS2002  : cd rafaCS2002 && python linearArray.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gera baseline de dados compartilhado entre implementacoes"
    )
    parser.add_argument(
        "--volumes", nargs="+", type=int, default=VOLUMES_DEFAULT,
        help=f"Volumes N (default: {VOLUMES_DEFAULT})"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Mostra o que seria gerado sem criar arquivos"
    )
    args = parser.parse_args()
    main(volumes=args.volumes, dry_run=args.dry_run)

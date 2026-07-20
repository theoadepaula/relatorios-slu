"""Extrai texto por pagina e todas as tabelas detectadas dos relatorios anuais do SLU."""
import fitz, pdfplumber, glob, os, csv, re, json

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRUTOS = os.path.join(RAIZ, "dados_brutos")
TEXTO = os.path.join(BRUTOS, "texto")
TAB = os.path.join(RAIZ, "dados", "tabelas_brutas")
os.makedirs(TEXTO, exist_ok=True)
os.makedirs(TAB, exist_ok=True)

def limpa(c):
    if c is None:
        return ""
    return re.sub(r"\s+", " ", str(c)).strip()

indice = []
for pdf in sorted(glob.glob(os.path.join(BRUTOS, "*.pdf"))):
    ano = re.search(r"(\d{4})", os.path.basename(pdf)).group(1)

    # texto por pagina
    doc = fitz.open(pdf)
    with open(os.path.join(TEXTO, f"slu_{ano}.txt"), "w", encoding="utf-8") as fh:
        for i, pg in enumerate(doc, 1):
            fh.write(f"\n===== [pagina {i}] =====\n")
            fh.write(pg.get_text())
    npag = len(doc)
    doc.close()

    # tabelas
    ntab = 0
    with pdfplumber.open(pdf) as pl:
        for i, pg in enumerate(pl.pages, 1):
            try:
                tabelas = pg.extract_tables()
            except Exception:
                continue
            for j, t in enumerate(tabelas, 1):
                linhas = [[limpa(c) for c in row] for row in t]
                linhas = [r for r in linhas if any(r)]
                if len(linhas) < 2:
                    continue
                nome = f"slu_{ano}_p{i:03d}_t{j}.csv"
                with open(os.path.join(TAB, nome), "w", encoding="utf-8-sig", newline="") as fh:
                    csv.writer(fh, delimiter=";").writerows(linhas)
                ntab += 1
                indice.append({"ano": int(ano), "pagina": i, "tabela": j,
                               "arquivo": nome, "n_linhas": len(linhas),
                               "n_colunas": max(len(r) for r in linhas),
                               "primeira_linha": " | ".join(linhas[0])[:200]})
    print(f"{ano}: {npag} paginas, {ntab} tabelas", flush=True)

with open(os.path.join(RAIZ, "dados", "indice_tabelas.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(indice[0].keys()), delimiter=";")
    w.writeheader(); w.writerows(indice)
print(f"TOTAL: {len(indice)} tabelas")

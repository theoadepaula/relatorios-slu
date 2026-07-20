"""Extrai as series financeiras (LOA x Despesa e Taxa de Limpeza Publica)."""
import re, os
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXTO = os.path.join(RAIZ, "dados_brutos", "texto")
DADOS = os.path.join(RAIZ, "dados")
REL = 2025  # o relatorio mais recente ja traz a serie completa

txt = open(os.path.join(TEXTO, f"slu_{REL}.txt"), encoding="utf-8").read()

def num(s):
    s = s.strip()
    if not re.fullmatch(r"-?\d{1,3}(\.\d{3})*(,\d+)?", s):
        return None
    return float(s.replace(".", "").replace(",", "."))

# --- LOA x Despesa: blocos de 7 campos (ano, loa, var%, abs, despesa, var%, abs)
i = [m.end() for m in re.finditer(r"LOA x DESPESA|LOA X DESPESA", txt)][-1]
linhas = [l.strip() for l in txt[i:i + 4000].split("\n") if l.strip()]
regs, k = [], 0
while k < len(linhas) - 6:
    a = linhas[k]
    if re.fullmatch(r"20[0-2][0-9]", a):
        loa, desp = num(linhas[k + 1]), num(linhas[k + 4])
        if loa is not None and desp is not None:
            regs.append({"ano": int(a), "loa_receita_rs": loa, "despesa_rs": desp})
            k += 7; continue
    k += 1
orc = pd.DataFrame(regs).drop_duplicates("ano").sort_values("ano")
orc["relatorio_fonte"] = REL

# --- Taxa de Limpeza Publica: pares (ano, valor)
j = [m.end() for m in re.finditer(r"EVOLU[CÇ][AÃ]O DA RECEITA DA TAXA DE LIMPEZA", txt, re.I)][-1]
linhas = [l.strip() for l in txt[j:j + 2500].split("\n") if l.strip()]
regs, k = [], 0
while k < len(linhas) - 1:
    if re.fullmatch(r"20[0-2][0-9]", linhas[k]) and num(linhas[k + 1]) is not None:
        regs.append({"ano": int(linhas[k]), "tlp_receita_rs": num(linhas[k + 1])})
        k += 2; continue
    k += 1
tlp = pd.DataFrame(regs).drop_duplicates("ano").sort_values("ano")
tlp["relatorio_fonte"] = REL

for nome, d in [("slu_orcamento", orc), ("slu_taxa_limpeza_publica", tlp)]:
    d.to_csv(os.path.join(DADOS, f"{nome}.csv"), sep=";", index=False, encoding="utf-8-sig")
    d.to_parquet(os.path.join(DADOS, f"{nome}.parquet"), index=False)
    print(f"{nome}: {len(d)} anos ({d.ano.min()}-{d.ano.max()})")
print(orc.to_string(index=False))
print(tlp.to_string(index=False))


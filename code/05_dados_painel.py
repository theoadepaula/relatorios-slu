"""Monta o JSON compacto que alimenta o painel HTML."""
import json, os
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados")

pa = pd.read_csv(os.path.join(DADOS, "slu_painel.csv"), sep=";", encoding="utf-8-sig")
orc = pd.read_csv(os.path.join(DADOS, "slu_orcamento.csv"), sep=";", encoding="utf-8-sig")
tlp = pd.read_csv(os.path.join(DADOS, "slu_taxa_limpeza_publica.csv"), sep=";", encoding="utf-8-sig")

def serie(aid, unidade=None):
    d = pa[pa.atividade_id == aid]
    if unidade:
        d = d[d.unidade == unidade]
    d = d.sort_values("ano")
    return [{"ano": int(r.ano), "valor": float(r.valor)} for r in d.itertuples()]

payload = {
    "series": {k: serie(k) for k in [
        "coleta_seletiva", "coleta_domiciliar_comercial", "aterrado_asb",
        "processado_usinas", "varricao_manual", "varricao_mecanizada",
        "coleta_corretiva", "entulho_ure"]},
    "orcamento": [{"ano": int(r.ano), "loa": float(r.loa_receita_rs), "despesa": float(r.despesa_rs)}
                  for r in orc.itertuples()],
    "tlp": [{"ano": int(r.ano), "valor": float(r.tlp_receita_rs)} for r in tlp.itertuples()],
}
with open(os.path.join(DADOS, "painel_dados.json"), "w", encoding="utf-8") as fh:
    json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))

for k, v in payload["series"].items():
    print(f"{k:30s} {len(v):2d} pts  {v[0]['ano']}-{v[-1]['ano']}")
print("orcamento", len(payload["orcamento"]), "| tlp", len(payload["tlp"]))
print("bytes:", os.path.getsize(os.path.join(DADOS, "painel_dados.json")))

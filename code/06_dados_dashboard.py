"""Gera o payload do dashboard interativo.

Diferente do 05_dados_painel.py, que produz um recorte curado para a pagina
narrativa, aqui vai a serie INTEIRA: o usuario escolhe o que ver, entao o
dashboard precisa de tudo.

Saida: dados/dashboard_dados.json  (embutido no painel/index.html na geracao)
"""

import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados"

LER = dict(sep=";", encoding="utf-8-sig")


def num(x):
    """JSON nao aceita NaN; e 'nao reportado' e diferente de zero."""
    return None if pd.isna(x) else float(x)


painel = pd.read_csv(DADOS / "slu_painel.csv", **LER)
orc = pd.read_csv(DADOS / "slu_orcamento.csv", **LER)
tlp = pd.read_csv(DADOS / "slu_taxa_limpeza_publica.csv", **LER)

anos = sorted(painel["ano"].unique().tolist())

# Uma serie por (atividade, unidade): a mesma atividade muda de unidade ao longo
# do tempo (ex.: animais mortos vai de 'unidade' para 't'), e somar as duas
# leituras seria um erro. Ficam como series distintas, explicitamente.
series = []
for (aid, rot, uni), g in painel.groupby(
    ["atividade_id", "atividade_rotulo", "unidade"], sort=False
):
    g = g.sort_values("ano")
    por_ano = dict(zip(g["ano"], g["valor"]))
    valores = [num(por_ano.get(a)) for a in anos]
    presentes = [a for a in anos if a in por_ano]
    series.append(
        {
            "id": f"{aid}__{uni}",
            "rotulo": rot,
            "unidade": uni,
            "valores": valores,
            "ini": int(min(presentes)),
            "fim": int(max(presentes)),
            "n_anos": len(presentes),
            # divergencia maxima entre relatorios que declararam o mesmo ponto:
            # e a medida de confianca da validacao cruzada
            "divergencia_max": num(g["divergencia_pct"].max()),
            "n_fontes_max": int(g["n_fontes"].max()),
        }
    )

# --- defeito conhecido: mesma medida, dois rotulos de unidade -------------
# Ha atividade cujo MESMO valor aparece sob duas unidades em anos coincidentes
# (rejeitos das IRRs: 3.517 e 'viagem' em 2020-2023 e 't' em 2024-2025, sem que
# o numero mude). Uma das duas etiquetas esta errada, e sem a fonte primaria nao
# da para saber qual. Plotadas juntas, as series sairiam como linhas identicas,
# entao vao marcadas.
dup_unid = set()
for (ano, aid), g in painel.groupby(["ano", "atividade_id"]):
    if g["unidade"].nunique() > 1 and g["valor"].nunique() == 1:
        dup_unid.add(aid)

for s in series:
    aid = s["id"].rsplit("__", 1)[0]
    s["alerta"] = (
        "mesmo valor declarado sob mais de uma unidade — uma das etiquetas está errada"
        if aid in dup_unid
        else None
    )

# ordena por cobertura: as series longas primeiro, que e o que o usuario quer ver
series.sort(key=lambda s: (-s["n_anos"], s["rotulo"]))

unidades = {
    "t": "toneladas",
    "km": "quilômetros",
    "unidade": "unidades",
    "equipe": "equipes",
    "ha": "hectares",
    "viagem": "viagens",
    "m3": "metros cúbicos",
    "t_x_km": "tonelada × km",
}

anos_orc = sorted(set(orc["ano"]) | set(tlp["ano"]))
orc_m = dict(zip(orc["ano"], orc["loa_receita_rs"]))
desp_m = dict(zip(orc["ano"], orc["despesa_rs"]))
tlp_m = dict(zip(tlp["ano"], tlp["tlp_receita_rs"]))

# A despesa de 2025 e execucao PARCIAL no momento da publicacao do relatorio.
# Plotada junto, produz uma queda falsa de 67%. Vai como null, nao como valor.
ANO_DESPESA_PARCIAL = 2025

payload = {
    "anos": anos,
    "series": series,
    "unidades": unidades,
    "financeiro": {
        "anos": anos_orc,
        "loa": [num(orc_m.get(a)) for a in anos_orc],
        "despesa": [
            None if a == ANO_DESPESA_PARCIAL else num(desp_m.get(a)) for a in anos_orc
        ],
        "tlp": [num(tlp_m.get(a)) for a in anos_orc],
    },
    "meta": {
        "n_series": len(series),
        "n_atividades": int(painel["atividade_id"].nunique()),
        "ano_ini": int(min(anos)),
        "ano_fim": int(max(anos)),
        "despesa_parcial": ANO_DESPESA_PARCIAL,
        "n_pontos": int(len(painel)),
        # Serie que acaba cedo nem sempre e atividade que sumiu: quatro
        # atividades apenas TROCARAM de unidade (animais mortos vai de
        # 'unidade' para 't'). So conta como descontinuada a atividade cuja
        # ultima medicao, em qualquer unidade, e anterior ao ultimo ano.
        "n_descontinuadas": int(
            (painel.groupby("atividade_id")["ano"].max() < max(anos)).sum()
        ),
        "n_divergentes": int((painel["divergencia_pct"] > 1).sum()),
    },
}

saida = DADOS / "dashboard_dados.json"
texto = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
saida.write_text(texto, encoding="utf-8")

print(f"{saida.name}: {len(series)} series, {len(anos)} anos, {saida.stat().st_size/1024:.1f} KB")

# Injeta no template. Mesma convencao do painel narrativo: placeholder
# __PAYLOAD__ substituido na geracao, HTML final autocontido e sem rede.
PAINEL = RAIZ / "painel"
tpl = (PAINEL / "_template.html").read_text(encoding="utf-8")
if "__PAYLOAD__" not in tpl:
    raise SystemExit("_template.html nao tem o placeholder __PAYLOAD__")

html = tpl.replace("__PAYLOAD__", texto)
destino = PAINEL / "index.html"
destino.write_text(html, encoding="utf-8")

print(f"{destino.relative_to(RAIZ)}: {destino.stat().st_size/1024:.1f} KB, autocontido")

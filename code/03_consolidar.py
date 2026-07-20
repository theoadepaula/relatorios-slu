"""Padroniza nomes de atividades e consolida o painel (CSV + Parquet)."""
import csv, os, re, unicodedata
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados")

# palavra-chave -> (id canonico, rotulo). A ULTIMA palavra-chave encontrada no texto
# vence: quando sobra texto da linha anterior no nome, a atividade real e a do fim.
MAPA = [
    ("domiciliares e comerciais",        "coleta_domiciliar_comercial", "Coleta domiciliar e comercial"),
    ("servicos de saude",                "coleta_rss",                  "Coleta de resíduos de serviços de saúde"),
    ("coleta corretiva",                 "coleta_corretiva",            "Coleta de remoção (corretiva)"),
    ("varricao manual",                  "varricao_manual",             "Varrição manual"),
    ("varricao mecanizada",              "varricao_mecanizada",         "Varrição mecanizada"),
    ("varricao mecanica",                "varricao_mecanizada",         "Varrição mecanizada"),
    ("pintura de meios-fios",            "pintura_meios_fios",          "Pintura de meios-fios"),
    ("pintura manual e mecanizada",      "pintura_meios_fios",          "Pintura de meios-fios"),
    ("lavagem de vias",                  "lavagem_vias",                "Lavagem de vias"),
    ("lavagem de abrigos",               "lavagem_abrigos",             "Lavagem de abrigos de passageiros"),
    ("catacao de papel",                 "catacao_papel",               "Catação de papel em áreas verdes"),
    ("catacao de residuos",              "catacao_residuos",            "Catação de resíduos"),
    ("limpeza de equipamentos",          "limpeza_equip_bens",          "Limpeza de equipamentos e bens públicos"),
    ("caixa de gordura",                 "caixa_gordura",               "Resíduos de caixa de gordura / pós-eventos"),
    ("processados em usinas",            "processado_usinas",           "Resíduos processados em usinas"),
    ("aterrados no asb",                 "aterrado_asb",                "Resíduos aterrados no Aterro Sanitário de Brasília"),
    ("domiciliares aterrados",           "domiciliar_aterrado",         "Resíduos domiciliares aterrados"),
    ("animais mortos",                   "animais_mortos",              "Coleta de animais mortos"),
    ("coleta seletiva",                  "coleta_seletiva",             "Coleta seletiva"),
    ("transferencia de residuos",        "transferencia",               "Transferência de resíduos"),
    ("aterrados na ure",                 "entulho_ure",                 "Entulho aterrado na URE"),
    ("transporte de chorume",            "transporte_chorume",          "Transporte de chorume"),
    ("tratamento de chorume",            "tratamento_chorume",          "Tratamento de chorume"),
    ("rejeitos das irrs",                "rejeito_irr",                 "Retirada de rejeitos das IRRs"),
    ("entulhos dos pevs",                "entulho_pev",                 "Retirada de entulho dos PEVs"),
    ("servicos diversos",                "servicos_diversos",           "Serviços diversos"),
]

def sem_acento(s):
    return unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()

def canoniza(nome):
    t = sem_acento(nome)
    melhor = None
    for chave, cid, rotulo in MAPA:
        pos = t.rfind(chave)
        if pos >= 0 and (melhor is None or pos > melhor[0]):
            melhor = (pos, cid, rotulo)
    return (melhor[1], melhor[2]) if melhor else (None, None)

UNID = {"u": "unidade", "unid.": "unidade", "unid": "unidade",
        "t x km": "t_x_km", "km x t": "t_x_km", "m3": "m3"}

df = pd.read_csv(os.path.join(DADOS, "slu_serie_historica.csv"), sep=";", encoding="utf-8-sig")
df[["atividade_id", "atividade_rotulo"]] = df["atividade"].apply(lambda s: pd.Series(canoniza(s)))
n_sem = df["atividade_id"].isna().sum()
df = df.dropna(subset=["atividade_id"])
df["unidade"] = df["unidade"].map(lambda u: UNID.get(u, u))
print(f"registros: {len(df)} (descartados sem mapeamento: {n_sem})")
print(f"atividades canonicas: {df['atividade_id'].nunique()}")

df = df[["ano", "atividade_id", "atividade_rotulo", "unidade", "valor", "relatorio_fonte"]]
df = df.sort_values(["atividade_id", "ano", "relatorio_fonte"])
df.to_csv(os.path.join(DADOS, "slu_serie_historica.csv"), sep=";", index=False, encoding="utf-8-sig")

# painel consolidado: vale o relatorio mais recente que publicou aquele ano
g = df.groupby(["ano", "atividade_id", "atividade_rotulo", "unidade"], as_index=False)
painel = g.apply(lambda d: pd.Series({
    "valor": d.loc[d["relatorio_fonte"].idxmax(), "valor"],
    "relatorio_fonte": int(d["relatorio_fonte"].max()),
    "n_fontes": int(d["relatorio_fonte"].nunique()),
    "divergencia_pct": round(float((d["valor"].max() - d["valor"].min()) / d["valor"].max() * 100), 2)
                      if d["valor"].max() else 0.0,
}), include_groups=False).reset_index(drop=False) if hasattr(g, "apply") else None

painel = painel.drop(columns=[c for c in painel.columns if c.startswith("level_")], errors="ignore")
painel = painel.sort_values(["atividade_id", "ano"])
painel.to_csv(os.path.join(DADOS, "slu_painel.csv"), sep=";", index=False, encoding="utf-8-sig")
painel.to_parquet(os.path.join(DADOS, "slu_painel.parquet"), index=False)
print(f"painel: {len(painel)} linhas, anos {painel['ano'].min()}-{painel['ano'].max()}")
print(painel.groupby("atividade_id")["ano"].agg(["min","max","count"]).to_string())

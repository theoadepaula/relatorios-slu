# Confere os numeros AFIRMADOS NA PROSA dos artigos contra os dados.
#
# Por que existe: os blocos R geram tabela e grafico a partir do parquet, entao
# eles nunca mentem. O texto em volta, sim -- ele foi escrito a mao e envelhece
# calado quando o pipeline muda. Foi exatamente o que aconteceu: os artigos
# afirmavam "267 pontos" e "15 divergencias" enquanto os dados diziam 164 e 9.
#
# Rode depois de qualquer mudanca em 02_serie_historica.py ou 03_consolidar.py,
# e antes de publicar:
#     python code/06_conferir_prosa.py
#
# Sai com codigo 1 se alguma afirmacao quebrar.

import sys, pathlib
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parent.parent
serie = pd.read_csv(RAIZ / "dados" / "slu_serie_historica.csv", sep=";")
painel = pd.read_parquet(RAIZ / "dados" / "slu_painel.parquet")

falhas = []


def confere(condicao, afirmacao):
    if condicao:
        print(f"  OK     {afirmacao}")
    else:
        print(f"  FALHA  {afirmacao}")
        falhas.append(afirmacao)


ultimo_ano = painel.groupby("atividade_id").ano.max()
por_relatorio = serie.groupby("relatorio_fonte").atividade_id.nunique()
aterro = (painel[painel.atividade_id.isin(["domiciliar_aterrado", "aterrado_asb"])]
          .pivot_table(index="ano", columns="atividade_id", values="valor"))
diverg = painel[painel.divergencia_pct > 0]
trocam_unidade = sum(len(v) > 1 for v in serie.groupby("atividade_id").unidade.unique())

print("artigo 01 — o que pararam de contar")
confere((ultimo_ano < 2025).sum() == 12, "doze atividades terminam antes de 2025")
confere((ultimo_ano == 2023).sum() == 6, "seis delas param em 2023 (a poda de 2024)")
confere(por_relatorio[2023] == 20 and por_relatorio[2024] == 13
        and por_relatorio[2025] == 12, "a tabela encolhe de 20 para 13 e depois 12")
confere(len(set(serie[serie.relatorio_fonte == 2023].atividade_id)
            - set(serie[serie.relatorio_fonte == 2024].atividade_id)) == 7,
        "sete linhas saem de 2023 para 2024")
confere(aterro.loc[2017, "domiciliar_aterrado"] == 809085
        and aterro.loc[2017, "aterrado_asb"] == 252703,
        "em 2017: 809.085 t contra 252.703 t")
confere(aterro.loc[2019, "domiciliar_aterrado"] == aterro.loc[2019, "aterrado_asb"] == 800872,
        "em 2019 as duas series marcam 800.872 t")
confere(abs(aterro.loc[2020, "domiciliar_aterrado"] - aterro.loc[2020, "aterrado_asb"]) == 1,
        "em 2020 diferem em 1 t")
confere(abs(aterro.loc[2021, "domiciliar_aterrado"] - aterro.loc[2021, "aterrado_asb"]) == 18,
        "em 2021 diferem em 18 t")

print("\nartigo 02 — como validei doze PDFs")
confere((painel.n_fontes > 1).sum() == 164, "164 pontos com mais de uma fonte")
confere(painel.n_fontes.max() == 9, "o ponto mais republicado aparece em nove relatorios")
confere(len(diverg) == 9, "nove divergencias restantes")
confere((diverg.divergencia_pct > 5).sum() == 2, "duas sao revisao de exercicio incompleto")
confere((diverg.divergencia_pct <= 5).sum() == 7
        and diverg[diverg.divergencia_pct <= 5].divergencia_pct.max() == 1.72,
        "sete sao revisao miuda, teto de 1,72%")
confere(trocam_unidade == 4, "quatro atividades trocam de unidade")

irr = serie[(serie.atividade_id == "rejeito_irr") & (serie.ano == 2020)]
confere(set(irr[irr.valor == 3517].relatorio_fonte) == {2021, 2022, 2023, 2024, 2025},
        "rejeitos das IRRs 2020: cinco relatorios posteriores dizem 3.517")
lav = serie[(serie.atividade_id == "lavagem_vias") & (serie.ano == 2019)]
confere(set(lav[lav.valor == 78.7].relatorio_fonte) == {2020, 2021, 2022, 2023},
        "lavagem de vias 2019: quatro relatorios posteriores dizem 78,7")

print("\nartigo 03 — a seletiva triplicou")
sel = painel[painel.atividade_id == "coleta_seletiva"].set_index("ano").valor
# a prosa cita valores arredondados; o dado tem centavos de tonelada (18.311,03)
confere(round(sel[2020]) == 18311 and round(sel[2025]) == 54549,
        "de 18.311 t (2020) para 54.549 t (2025)")
confere(round(100 * (sel[2025] / sel[2020] - 1)) == 198, "crescimento de 198% desde 2020")
confere(round(100 * (sel[2025] / sel[2017] - 1)) == 82, "crescimento de 82% desde 2017")
confere(all(sel[a] > sel[a - 1] for a in range(2021, 2026)),
        "cinco altas consecutivas de 2021 a 2025")
confere(sel[2014] == 48586 and sel[2015] == 57496, "2014 e 2015 acima de 2020 (outra metodologia)")

print()
if falhas:
    print(f"{len(falhas)} afirmacao(oes) da prosa nao batem mais com os dados:")
    for f in falhas:
        print("  -", f)
    sys.exit(1)
print("Todas as afirmacoes da prosa conferem com os dados.")

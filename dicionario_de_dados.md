# Dicionário de dados — Relatórios Anuais do SLU/DF

Fonte: relatórios anuais de atividades do Serviço de Limpeza Urbana do Distrito Federal,
2014 a 2025 (<https://www.slu.df.gov.br/relatorios>). PDFs originais em `dados_brutos/`.

Todos os CSV usam separador `;` e codificação UTF-8 com BOM (abrem direto no Excel).
Os mesmos dados estão em `.parquet` para uso analítico.

---

## `dados/slu_painel.csv` / `.parquet` — painel consolidado

Uma linha por ano × atividade × unidade. É a tabela recomendada para o painel do site.

| coluna | tipo | descrição |
|---|---|---|
| `ano` | inteiro | ano de referência do dado |
| `atividade_id` | texto | identificador estável da atividade (ex.: `coleta_seletiva`) |
| `atividade_rotulo` | texto | rótulo legível para exibição |
| `unidade` | texto | `t`, `km`, `m3`, `unidade`, `equipe`, `viagem`, `t_x_km` |
| `valor` | decimal | quantitativo executado |
| `relatorio_fonte` | inteiro | ano do relatório de onde veio o valor adotado |
| `n_fontes` | inteiro | em quantos relatórios diferentes esse ano aparece |
| `divergencia_pct` | decimal | diferença percentual entre o maior e o menor valor publicado para o mesmo ponto |

Quando um mesmo ano aparece em vários relatórios, **adota-se o do relatório mais recente**
(revisões posteriores costumam corrigir o número). `divergencia_pct` preserva o rastro:
valores acima de ~2% merecem conferência no PDF antes de virar manchete.

## `dados/slu_serie_historica.csv` — base longa, sem consolidação

Mesma estrutura, porém **um registro por relatório de origem** (746 linhas). Serve para
auditar divergências e reproduzir o que cada relatório afirmou na época.

## `dados/slu_orcamento.csv` / `.parquet`

| coluna | descrição |
|---|---|
| `ano` | exercício (2011–2025) |
| `loa_receita_rs` | receita prevista na Lei Orçamentária Anual, em R$ correntes |
| `despesa_rs` | despesa executada, em R$ correntes |

## `dados/slu_taxa_limpeza_publica.csv` / `.parquet`

Receita da Taxa de Limpeza Pública (TLP), 2005–2025, em R$ correntes (`tlp_receita_rs`).

## `dados/tabelas_brutas/` e `dados/indice_tabelas.csv`

Toda tabela detectada em todos os PDFs, uma por CSV, nomeada
`slu_<ano>_p<pagina>_t<n>.csv`. O índice traz ano, página, dimensões e a primeira linha
de cada uma — use-o para localizar tabelas ainda não tratadas (gravimetria, catadores,
recursos humanos, unidades por região administrativa etc.).

## `dados_brutos/texto/`

Texto integral de cada relatório, com marcadores `===== [pagina N] =====`, para busca e
conferência rápida de qualquer número contra a página de origem.

---

## Ressalvas metodológicas (importantes antes de publicar)

1. **Quebra na coleta seletiva em 2017.** A série cai de 48.673 t (2016) para 29.968 t
   (2017). Não é colapso do serviço: muda o que é contabilizado — os relatórios recentes
   rotulam a linha como "coleta seletiva das empresas". Não trate 2014–2016 e 2017–2025
   como série contínua sem nota de rodapé.

2. **Mudanças de unidade.** Algumas atividades trocam de unidade e viram outra medida:
   pintura de meios-fios passa de `km` para `equipe`; coleta de animais mortos, de
   `unidade` para `t`; retirada de rejeitos das IRRs, de `viagem` para `t`. Por isso a
   unidade faz parte da chave — séries com unidades diferentes não devem ser somadas
   nem plotadas na mesma linha.

3. **Aterro: mudança de destino, não só de número.** "Resíduos domiciliares aterrados"
   (até 2021) e "Resíduos aterrados no ASB" convivem no período de transição do Aterro
   Controlado do Jóquei para o Aterro Sanitário de Brasília. O salto de 252.703 t (2017)
   para 749.608 t (2018) no ASB reflete essa transição, não crescimento de geração.

4. **2025 é ano corrente.** A despesa de 2025 (R$ 202,4 mi contra R$ 620,8 mi em 2024)
   é execução parcial no momento de publicação do relatório. Não use como ano fechado.

5. **Valores nominais.** Orçamento e TLP estão em reais correntes, sem deflacionamento.
   Para comparação real ao longo de 20 anos, deflacione (IPCA) antes de interpretar.

6. **RSS interrompido.** A coleta de resíduos de serviços de saúde tem série até 2021: a
   partir de março/2021 a mudança de contratação (Ata SRP) passou a computar apenas o
   RSS coletado nas instalações do SLU, e a linha sai dos relatórios recentes.

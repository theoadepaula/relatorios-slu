# Contexto do projeto — Relatórios Anuais do SLU/DF

> Ponto de entrada do projeto. O [`README.md`](README.md) é o manual técnico
> (como reproduzir, o que cada script faz); **este arquivo é o porquê** — as
> decisões, o que foi descartado e o que está pendente.

---

## 1. O que é e para que serve

Extração estruturada dos doze relatórios anuais de atividades do Serviço de
Limpeza Urbana do DF, 2014–2025 (1.704 páginas de PDF), virando série histórica
tratada para alimentar **três artigos** e **um painel** no site.

Fonte: <https://www.slu.df.gov.br/relatorios>.

⚠️ **Cuidado de contexto:** Théo é servidor do SLU-DF. Este projeto analisa o
próprio órgão. Todo o material usa apenas dado público já publicado pelo SLU, e
o tom é de crítica metodológica à série histórica — não a pessoas, gestões ou
decisões administrativas. Manter assim.

---

## 2. Decisões tomadas

### Sobre a extração

- **Validação cruzada por sobreposição editorial.** Cada relatório republica de
  3 a 9 anos anteriores. Isso não é redundância: é a única forma de conferir o
  parser contra algo. Cada ponto foi checado contra até 9 publicações
  independentes. **Pegou três bugs que nenhum teste de sanidade pegaria**, porque
  todos produziam números *plausíveis* na coluna *errada*.
- **A unidade faz parte da chave** — `(ano, atividade, unidade)`. Quatro
  atividades trocam de unidade no meio da série; sem isso na chave, elas
  apareceriam como os maiores erros do projeto.
- **Preferir sempre o relatório mais recente** para cada ponto. O relatório do
  próprio ano publica com o exercício ainda aberto e destoa; os seguintes
  corrigem.
- **`04_orcamento.py` lê só o relatório de 2025**, de propósito: ele já traz LOA
  × despesa (2011–2025) e TLP (2005–2025) completas numa tabela só.

### Sobre os artigos

- Três artigos, todos em `.qmd` com R (regra fixa do site).
- **Tabelas em `gt`**, gráficos em **`plot_ly()` nativo**. Estilo compartilhado em
  [`code/tema_visual.R`](code/tema_visual.R) — um arquivo, não três cópias.
- ✅ **Decidido em 2026-07-19:** o SLU fica em `plot_ly()` nativo mesmo com o
  Cargos em `ggiraph`. O que o Cargos reprovou foi o conversor `ggplotly()`, que
  não é o que se usa aqui. Custo assumido: dois idiomas de hover no site.
  Quadro completo em `docs/CONTEXTO-SITE.md`, seção 9.2.
- **Paleta reaproveitada do painel**, validada para daltonismo nos modos claro e
  escuro. Não trocar cor no olho.
- ✅ **Decidido em 2026-08-15:** os artigos passam a pedir ao `theoviz` o **modo
  escuro** — `paleta(modo = "escuro")`, `tinta(..., modo = "escuro")` e
  `tabela()` com `modo = "escuro"`. Eles sempre foram publicados em página
  escura e pediam as cores do modo claro; sem `modo`, o `gt` crava
  `background-color: #FFFFFF` **inline**, que nenhuma folha de estilo derruba, e
  toda tabela de todo artigo ia ao ar como retângulo branco.
  - Saiu junto o `TINTA_2 <- "#8a8a85"` que este projeto cravava. O comentário
    que o defendia — *"não é o `tinta('fraca')` do theoviz: aquele foi calibrado
    só para fundo claro"* — era **verdade quando foi escrito** e deixou de ser:
    o `theoviz` 0.3.0 tem um piso próprio para o escuro (`#7d858e`), medido
    contra o fundo e contra a chapa. Cinza inventado no projeto é exatamente a
    divergência que o pacote existe para eliminar.
  - `GRADE` passa de `grade_rgba(0.22)` para o filete sólido. O `rgba` é o
    recurso de **chão desconhecido**; aqui o chão é conhecido.
  - Exige `theoviz` ≥ 0.3.0. Depois de mexer no tema, re-renderizar **tudo** no
    repo do site: apagar `quarto/_freeze/` e rodar `npm run build:quarto`
    (`quarto render --no-freeze` **não existe** no Quarto 1.9 — falha o render
    inteiro).
- No artigo 03, os dois trechos da série entram como **traces separados**: ligá-los
  com linha contínua afirmaria visualmente a continuidade que o texto nega.

### Sobre o painel

- HTML autocontido, sem dependência externa. Payload embutido (`__PAYLOAD__`).
- **Catálogo de séries num dropdown com busca**, não em rol plano: são 29 séries
  para no máximo 4 no gráfico, e listar tudo empurrava o gráfico para fora da
  tela. Opções agrupadas por unidade.
- **Nenhum KPI é variação percentual.** Toda variação depende do ano-base, e esta
  série tem um vale profundo em 2020 — ancorar manchete nele diria "triplicou"
  sobre o que, em doze anos, cresceu 12%.
- **Despesa cortada em 2024**: 2025 é execução parcial e produziria queda falsa
  de 67%.
- Sem eixo duplo. Unidades diferentes → Índice 100.

---

## 3. Os achados, em uma linha cada

1. **Doze linhas somem da série** ao longo dos doze relatórios: seis uma a uma
   (2018–2021) e **sete cortadas de uma vez na edição de 2024** — a tabela cai de
   20 para 13 atividades, sem nota.
2. **A coleta seletiva das empresas cresceu 82% desde 2017**, com cinco altas
   consecutivas de 2021 a 2025 — mas 2014–2016 medem outra coisa e não se somam.
3. **As duas séries de aterro convergem em 2019** (800.872 t nas duas) e uma é
   descartada em 2022 — quando o Jóquei fecha, viram a mesma medida.
4. **O DF gera menos lixo domiciliar que em 2014** (844 mil t → 724 mil t) com
   população maior. Pauta de reserva: quanto é geração e quanto é pesagem.
5. **Uma linha morta foi republicada por quatro anos**: transporte de chorume,
   com o mesmo dado de 2019, até sumir em 2024.

---

## 4. Armadilhas do dado

Detalhe em [`dicionario_de_dados.md`](dicionario_de_dados.md). Em resumo: quebra
metodológica da seletiva em 2017, quatro trocas de unidade, transição
Jóquei→ASB, 2025 é exercício parcial, valores nominais (deflacione antes de
comparar), RSS descontinuado por mudança de contrato.

---

## 5. Estado do trabalho

### Pronto
- [x] 12 PDFs baixados e conferidos, 2.010 tabelas extraídas
- [x] Série histórica validada por sobreposição — 9 divergências, todas explicadas
- [x] Três artigos em `.qmd`, com `gt` e plotly, **renderizados em `_site/`**
- [x] Painel autocontido com dropdown de séries, matriz de descontinuidade e
      Índice 100
- [x] `code/06_conferir_prosa.py` — afirma contra o dado os 21 números que os
      artigos citam em texto corrido

### Aguardando
- [ ] **Revisão do Théo** nos três artigos e no painel. Depois disso, agendar.

### Pendências abertas
- [ ] O `_quarto.yml` aponta para um `index.qmd` que **não existe** — renderizar
      o projeto inteiro falha até criá-lo. Artigo a artigo funciona.
- [ ] Decidir se a poda de 2024 vira parágrafo (como está) ou artigo próprio.
- [ ] Pautas 2 a 5 do README seguem sem dono.

---

## 6. O que NÃO dá para extrair

Registrado em detalhe no README, seção "becos já percorridos". O essencial:
**busca por palavra-chave no `indice_tabelas.csv` superestima muito** — a coluna
`primeira_linha` casa com prosa e nome de cooperativa. Gravimetria: zero tabelas
extraíveis. Catadores: 4 tabelas reais, não 125. Não há base para painel
territorial nem para taxa de recuperação de recicláveis; para isso a fonte teria
que ser SNIS ou pedido via LAI.

---

## 7. Onde está cada coisa

| O que | Onde |
|---|---|
| Manual técnico, reprodução, becos | [`README.md`](README.md) |
| Colunas e ressalvas | [`dicionario_de_dados.md`](dicionario_de_dados.md) |
| Scripts, na ordem | `code/01…06` |
| Tema visual dos artigos | `code/tema_visual.R` |
| Artigos | `artigos/*.qmd` |
| HTML para revisão | `_site/artigos/` |
| Painel | `painel/index.html` |

---

## 8. ⚠️ Onde o site realmente vive

Esta pasta do OneDrive **não é o site**. O site é um projeto Astro em
`C:\Users\theoa\dev\theoalbuquerque-site`, deliberadamente fora do OneDrive.

### Como este projeto entra no site

**Nada é transferido antes da aprovação do Théo.** O projeto fica inteiro aqui
até os três artigos e o painel serem aprovados. Só então:

```
artigos/<slug>.qmd      →  <repo>\quarto\posts\<slug>\index.qmd
painel/index.html       →  <repo>\public\apps\slu-serie\
                           + <repo>\src\content\paineis\<slug>.md
```

Render local (o Cloudflare não roda R). **R não está no PATH desta máquina** —
veja a receita em `README.md`, seção "Como renderizar".

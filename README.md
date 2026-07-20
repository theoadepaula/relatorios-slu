# Relatórios Anuais do SLU/DF — dados abertos

Extração estruturada dos relatórios anuais de atividades do Serviço de Limpeza Urbana do
Distrito Federal, 2014–2025, para alimentar painel e artigos.

Fonte: <https://www.slu.df.gov.br/relatorios> (12 PDFs, 1.704 páginas).

## Estrutura

```
dados_brutos/          12 PDFs originais, como baixados
dados_brutos/texto/    texto integral por página, para conferência
dados/                 saídas tratadas (CSV + Parquet)
code/                  scripts de extração, na ordem de execução
artigos/               pautas
```

## Como reproduzir

```bash
python code/01_extrair_bruto.py     # texto + todas as tabelas (~40 min)
python code/02_serie_historica.py   # série histórica dos quantitativos
python code/03_consolidar.py        # padroniza nomes e consolida o painel
python code/04_orcamento.py         # orçamento e Taxa de Limpeza Pública
python code/05_dados_painel.py      # JSON que alimenta o painel HTML
python code/06_conferir_prosa.py    # confere os numeros AFIRMADOS nos artigos
```

O `06_conferir_prosa.py` não gera nada: ele afirma, contra o parquet, os 21
números que os artigos citam **em texto corrido**. Existe porque os blocos R
nunca mentem — eles leem o dado na hora — mas a prosa em volta foi escrita à mão
e envelhece calada. Foi o que aconteceu: os artigos afirmaram "267 pontos" e "15
divergências" por um tempo, enquanto os dados diziam 164 e 9. Rode depois de
qualquer mudança em `02_serie_historica.py` ou `03_consolidar.py`, e antes de
publicar. Sai com código 1 se alguma afirmação quebrar.

O `04_orcamento.py` lê **apenas o relatório de 2025**, de propósito: ele já traz a série
completa de LOA × despesa (2011–2025) e da TLP (2005–2025) numa tabela só. Não há ganho
em costurar os doze.

Dependências: `pymupdf`, `pdfplumber`, `pandas`, `pyarrow`.

## O que saiu

| arquivo | conteúdo |
|---|---|
| `dados/slu_painel.csv` / `.parquet` | 214 linhas, 24 atividades, 2014–2025 — **base do painel** |
| `dados/slu_serie_historica.csv` | 746 registros, um por relatório de origem (auditoria) |
| `dados/slu_orcamento.csv` / `.parquet` | LOA e despesa executada, 2011–2025 |
| `dados/slu_taxa_limpeza_publica.csv` / `.parquet` | receita da TLP, 2005–2025 |
| `dados/tabelas_brutas/` | toda tabela detectada nos PDFs, uma por CSV |
| `dados/indice_tabelas.csv` | índice navegável das tabelas brutas |

Colunas e ressalvas em [`dicionario_de_dados.md`](dicionario_de_dados.md). **Leia as
ressalvas antes de publicar qualquer número** — há quebras de metodologia que, ignoradas,
produzem manchetes erradas.

## Validação feita

A série histórica é publicada de forma sobreposta: cada relatório repete de 3 a 9 anos
anteriores. Isso permitiu conferir cada ponto contra até 9 publicações independentes.

- Pontos com mais de uma fonte: **164** (chave `ano + atividade + unidade`).
- Divergências que sobraram: **9**. Todas explicadas, em dois grupos:
  - **7 revisões miúdas** do próprio SLU, teto de 1,72%;
  - **2 revisões de exercício incompleto** — rejeitos das IRRs em 2020 (63,6%) e
    lavagem de vias em 2019 (15,9%). Nos dois casos é o relatório *do próprio
    ano* que destoa, e as edições seguintes convergem. Daí a regra da
    consolidação: para qualquer ano, prefira o relatório seguinte.
- **Mudança de unidade não aparece como divergência**, de propósito: a unidade
  faz parte da chave, então as 4 atividades que trocam de unidade viram séries
  distintas em vez de conflito (`animais_mortos`, `lavagem_abrigos`,
  `pintura_meios_fios`, `rejeito_irr`).

> ⚠️ **A frase "sempre ≤ 1,1%" está errada** (conferido em 2026-07-19). Há cinco
> pontos acima de 1% em `divergencia_pct`, e dois deles são grandes:
>
> | ano | atividade | fontes | divergência |
> |---|---|---|---|
> | 2020 | Retirada de rejeitos das IRRs | 4 | **63,55%** |
> | 2019 | Lavagem de vias | 5 | **15,88%** |
> | 2017 | Pintura de meios-fios | 2 | 1,72% |
> | 2018 | Coleta seletiva | 8 | 1,37% |
> | 2017 | Resíduos processados em usinas | 9 | 1,15% |
>
> **Verificado em 2026-07-19: não são mudança de unidade — são revisões.** Em
> `slu_serie_historica.csv`, os dois casos aparecem na **mesma unidade** nos
> relatórios que discordam:
>
> - *Rejeitos das IRRs, 2020*: o relatório de 2020 declara **9.649,78 viagens**;
>   os de 2021, 2022 e 2023 declaram **3.517**, mesma unidade.
> - *Lavagem de vias, 2019*: o relatório de 2019 declara **66,2 equipes**;
>   os de 2020 a 2023 declaram **78,7**, mesma unidade.
>
> Ou seja, a classificação "8 por mudança de unidade, 5 por revisão" e o limite de
> 1,1% precisam ser refeitos. Reescrever esta seção antes de citá-la.
- Nenhum erro de alinhamento remanescente — três bugs de parsing foram encontrados
  exatamente por essa checagem cruzada (ano deslocado no relatório 2017, tabela truncada
  na quebra de página em 2019/2020, e células `0` descartadas como número de página).
- Chaves duplicadas: 0.

## O primeiro relatório a publicar um ano é o que erra

Achado de 2026-07-19, ao montar o dashboard. Dos 214 pontos da série, **164 foram
publicados por mais de um relatório** e portanto são conferíveis. Desses, **10
divergem** — taxa de revisão de **6,1%**.

O padrão é o que interessa: **em 10 de 10, o relatório discordante é o mais antigo**,
isto é, aquele que publicou o ano pela primeira vez. Todos os posteriores convergem
para um valor único.

| ano | atividade | 1º relatório | consenso posterior |
|---|---|---|---|
| 2017 | Coleta domiciliar e comercial | 829.229 | 828.765 |
| 2017 | Resíduos processados em usinas | 233.595 | 230.916 |
| 2018 | Coleta seletiva | 28.945 | 28.549 |
| 2019 | Lavagem de vias | 66,2 | 78,7 |
| 2020 | Retirada de rejeitos das IRRs | 9.649,78 | 3.517 |

Consequências práticas:

1. **Ao citar um número, prefira o relatório mais recente que o republica**, nunca o
   do próprio ano. O `slu_painel.csv` já faz isso.
2. **O dado do ano corrente é o menos confiável de toda a série** — e é justamente o
   que costuma virar notícia.
3. É uma pauta pronta, e da mesma família da tese do AMB: *quanto o passado oficial se
   move depois de publicado*. Aqui a resposta é medida, não estimada.

### Defeito separado: mesmo número, duas unidades

`Retirada de rejeitos das IRRs` aparece com **valor idêntico sob rótulos diferentes**
— 3.517 como `viagem` (relatórios 2021–2023) e como `t` (2024–2025); o mesmo em 2021,
2022 e 2023. Uma das duas etiquetas está errada e a fonte aberta não diz qual. O
dashboard marca essas séries com `!`, e o campo `alerta` no payload carrega o motivo.

## O que NÃO dá para extrair (becos já percorridos)

Esta seção existe para você — ou eu, numa sessão futura — não repetir garimpo já feito.
Uma busca por palavra-chave em `indice_tabelas.csv` **superestima muito** o que existe,
porque a coluna `primeira_linha` casa com prosa, nome de cooperativa e item de obra.
Números abaixo já descontam os falsos positivos, conferidos abrindo as tabelas.

| Tema | O que a busca sugere | O que existe de fato | Veredito |
|---|---|---|---|
| Gravimetria (composição do lixo) | "gravimetr" aparece em 7 anos | **zero** tabelas extraíveis — está em texto corrido e imagem | Inviável sem OCR/leitura manual |
| Composição por material | 7 tabelas | 1–2 reais; o resto é nome de associação com "PAPEL" e descrição de acidente | Insuficiente para série |
| Dados mensais | 12 tabelas | 12 reais, mas em 5 anos **não consecutivos** (2015, 2018, 2020, 2021, 2025) | Esparso demais para série |
| Tonelagem por região administrativa | 82 tabelas | maioria é cadastro de imóveis, endereço e área construída | Não sustenta painel territorial |
| Nº de catadores por ano | 125 tabelas com "cooperativa" | **4** tabelas com a coluna, cobrindo 2014, 2017, 2018 (a de 2024 é lixo) | 3 recortes transversais, não série |

A única exceção genuína encontrada: `slu_2018_p142_t1.csv` traz tonelagem por localidade
dos papa-entulhos (entulho, volumosos, podas, recicláveis, óleo). É um ano só.

**Consequência prática:** não há base para um segundo painel territorial nem para calcular
taxa de recuperação de recicláveis. Se isso for necessário, a fonte tem que ser outra
(SNIS, ou pedido via LAI ao SLU), não estes PDFs.

## Artigos escritos (rascunhos, aguardando revisão)

| arquivo | tese |
|---|---|
| [`artigos/01-o-que-pararam-de-contar.qmd`](artigos/01-o-que-pararam-de-contar.qmd) | Doze linhas somem da série: seis uma a uma, mais sete cortadas de uma vez na edição de 2024 |
| [`artigos/02-como-validei-doze-pdfs.qmd`](artigos/02-como-validei-doze-pdfs.qmd) | Método de validação cruzada; os três bugs que ele pegou |
| [`artigos/03-a-seletiva-triplicou.qmd`](artigos/03-a-seletiva-triplicou.qmd) | Crescimento de 198% desde 2020 — e a armadilha de 2017 |

> ⚠️ **Revisar o artigo 03 antes de publicar** (apontado em 2026-07-19, ao montar o
> dashboard). O "+198%" é medido a partir de **2020, o menor ponto de toda a série**
> (18,3 mil t). A série completa não sustenta "triplicou":
>
> | ano | coleta seletiva (t) |
> |---|---|
> | 2014 | 48.586 |
> | 2019 | 28.522 |
> | **2020** | **18.311** ← base do "+198%" |
> | 2025 | 54.549 |
>
> De 2014 a 2025 o crescimento é de **12,3%**, não 198%. O que houve foi uma queda
> longa até 2020 e uma recuperação que apenas voltou ao patamar de 2014. "Triplicou"
> é verdade aritmética sobre um vale, e é exatamente o tipo de leitura por ano-base
> que os outros artigos deste projeto criticam. Reenquadrar como *recuperação* — ou
> declarar a escolha de base no texto.

### Como renderizar

O R **não está no PATH** desta máquina (está em `C:\Program Files\R\R-4.5.2`), então
`quarto render` sozinho falha e cai no motor Python. Antes de renderizar:

```powershell
$env:PATH = 'C:\Program Files\R\R-4.5.2\bin;' + $env:PATH
quarto render artigos\01-o-que-pararam-de-contar.qmd --to html
```

Saída em `_site/artigos/`. Pacotes necessários já instalados: `arrow`, `dplyr`,
`ggplot2`, `readr`, `here`, `knitr`.

Dois detalhes que custam tempo se esquecidos:

- O arquivo vazio `.here` na raiz é a âncora do pacote `here` — sem ele,
  `here::here("dados", ...)` resolve para outro diretório e o setup quebra.
- O `_quarto.yml` aponta para um `index.qmd` que **não existe**. Renderizar
  artigo a artigo funciona (só emite `WARN: Unable to resolve link target`),
  mas `quarto render` do projeto inteiro vai falhar até esse arquivo ser criado.

### Tabelas e gráficos

Tabelas em **`gt`**, gráficos em **`plotly`**. O estilo dos dois mora num arquivo
só, [`code/tema_visual.R`](code/tema_visual.R), que cada artigo carrega no bloco
`setup`. Mexa lá, não em cada `.qmd`.

- `tabela()` — o estilo `gt` do projeto: sem linhas verticais, régua fina, cabeçalho
  discreto, alinhado à esquerda.
- `grafico()` — layout `plotly` com `hovermode = "x unified"`, que é o que entrega
  crosshair mais tooltip num gráfico de linha.
- `rotulo_final()` — rótulo direto na ponta da série.

Três decisões que parecem detalhe e não são:

- **Fundo transparente** nos gráficos (`paper_bgcolor`/`plot_bgcolor` em `rgba(0,0,0,0)`),
  para o widget herdar a cor da página em vez de cravar um branco no meio de um
  tema escuro. Por isso o texto de eixo usa `#8a8a85`, um cinza que passa em
  contraste tanto sobre `#fcfcfb` quanto sobre `#1a1a19`.
- **A paleta é a mesma do painel** e passou no validador de daltonismo nos dois
  modos. O par azul-verde (`#2a78d6`/`#008300`) passa em todos os seis testes,
  inclusive contraste. Não troque cor no olho.
- **Nome de série curto.** A legenda do `plotly` trunca sem avisar e o tooltip
  unificado alarga junto. "Coleta seletiva das empresas (2017–)" virou
  "Só empresas (2017–2025)" por isso.

No gráfico do artigo 03, os dois trechos da série entram como **traces separados**
de propósito: ligá-los com uma linha contínua afirmaria visualmente a continuidade
que o texto nega.

## Painel

São **dois** arquivos, com propósitos diferentes:

| arquivo | o que é |
|---|---|
| [`painel/index.html`](painel/index.html) | **dashboard interativo** — o usuário escolhe séries, período e escala |
| [`painel/narrativa.html`](painel/narrativa.html) | a página narrativa anterior, preservada — quatro seções fixas, sem controles |

O dashboard é gerado por `python code/06_dados_dashboard.py`, que injeta o payload
em `painel/_template.html` (placeholder `__PAYLOAD__`) e escreve o `index.html`.
**Editar o template, nunca o `index.html`** — ele é sobrescrito a cada geração.

Controles: recorte de anos, filtro por unidade, alternância valor ↔ índice 100,
tabela-gêmea sob demanda, e uma matriz de cobertura (29 séries × 12 anos) em que
clicar numa linha a leva ao gráfico.

### Decisões de desenho que não são óbvias no código

- **Unidades diferentes não dividem eixo.** As 24 atividades vêm em 8 unidades
  (t, km, equipe, ha, m³, viagem, t×km, unidade). Selecionar séries de unidades
  distintas **bloqueia** o gráfico em valor absoluto e exige o modo índice. Eixo
  duplo seria a saída fácil e errada.
- **Buraco na linha é buraco, não zero.** Ano não publicado interrompe o traço.
  Ligar os pontos por cima da lacuna inventaria dado.
- **Nenhum KPI é variação percentual.** Toda variação depende do ano-base, e esta
  série tem um vale profundo em 2020: ancorado nele, o número vira "+198%"; em doze
  anos, a mesma série cresce 12%. Quem quiser a variação escolhe o período no
  explorador, vendo a base. Ver a ressalva sobre o artigo 03, abaixo.
- **Rótulo direto no último ponto**, além da legenda: no tema claro, duas cores da
  paleta ficam abaixo de 3:1 de contraste. Identidade nunca depende só da cor.
- **`<meta charset="utf-8">` agora está no arquivo.** A narrativa antiga não tinha,
  de propósito, para herdar o charset do documento pai ao ser embutida. O dashboard
  tende a ser servido avulso ou em iframe, onde a ausência quebra os acentos — o que
  se reproduz em dois minutos com `python -m http.server`.
- Paleta reaproveitada da narrativa e **revalidada** nos dois modos com o validador
  de daltonismo: claro e escuro passam em todos os testes.

O JSON que o alimenta é gerado por `code/05_dados_painel.py` e fica **embutido** no HTML
(placeholder `__PAYLOAD__` substituído na geração). Ao regerar os dados, reinjete.

### O seletor de séries

São **29 séries** no payload para no máximo **4** no gráfico (`MAX = 4`, limite da
paleta categórica). Listar as 29 como chips na página empurrava o gráfico para
baixo da dobra — o seletor ocupava mais espaço que o próprio dado.

Agora o catálogo mora num **dropdown com busca** (`#dd-btn` / `#dd-pop`) e a
página mostra só a seleção corrente. O seletor caiu de vários blocos de chips
para uma linha de 36 px.

- Opções **agrupadas por unidade**, porque séries de unidades diferentes não são
  comparáveis num eixo só — ver isso na hora de escolher evita a comparação errada.
- Cada opção traz o intervalo de anos (`2014–2025`): a maioria das séries não
  cobre a série inteira, e isso decide a escolha.
- Ao atingir 4, as demais ficam `aria-disabled` com a razão escrita no rodapé.
  Não é silencioso.
- Fecha por `Escape` e por clique fora — sem isso o popover fica por cima do
  gráfico, que é justamente o que se quer enxergar.
- `montaPicker()` continua sendo o ponto de entrada único (chamado pelo filtro de
  unidade, pela matriz e na inicialização); ele agora delega para `montaChips()`
  e `montaLista()`.

> Armadilha de CSS que já custou uma rodada: em `.opt`, o `all:unset` precisa vir
> **antes** de `display:flex`. Ele zera tudo que vem antes, e um `.opt` sem flex
> quebra a linha entre a caixa de seleção e o rótulo.

### Decisões que não são óbvias no código

- **A linha de despesa termina em 2024.** O valor de 2025 (R$ 202,4 mi) é execução parcial
  no momento da publicação do relatório; plotado junto, produz uma queda falsa de 67%.
- **Nada de eixo duplo.** LOA, despesa e TLP dividem um eixo só porque estão todos em R$.
- **Rótulo direto no último ponto de cada série** não é enfeite: três cores da paleta
  clara ficam abaixo de 3:1 de contraste, o que obriga rótulo visível ou tabela. Tem os dois.
- Paleta conferida com o validador de daltonismo nos dois modos antes de escrever
  o gráfico — não no olho.

### Pegadinha ao servir o arquivo

O HTML é UTF-8 **sem `<meta charset>`** (a página é feita para ser embutida e herdar o
charset do documento pai). Servido solto por um servidor que não manda
`Content-Type: text/html; charset=utf-8`, os acentos saem embaralhados (`relatÃ³rios`).
No WordPress e no artefato publicado renderiza correto. Se for hospedar avulso,
garanta o header — ou acrescente a meta tag.

## Pautas de reserva

1. ~~A coleta seletiva desde 2020~~ — **virou o artigo 03**. (De 18,3 mil t em 2020 para
   54,5 mil t em 2025: +198%, ou seja, triplicou — não "dobrou", como constava aqui antes.)
2. **O DF gera menos lixo domiciliar do que gerava em 2014** — 844 mil t (2014) para
   724 mil t (2025), com população maior. Vale investigar quanto é mudança real de
   geração e quanto é mudança de pesagem/contabilização.
3. **A despesa cresce mais rápido que a TLP** — a taxa financia parcela decrescente do
   custo. Série de 20 anos disponível, mas deflacione antes.
4. **Varrição mecanizada quintuplicou** (41 mil km em 2017 para 213 mil km em 2025)
   enquanto a manual ficou estável — substituição tecnológica visível no dado.
5. **O que os relatórios pararam de contar** — RSS some após 2021, catação e transporte
   de chorume desaparecem. Artigo sobre descontinuidade de série histórica em dado
   público: o tipo de pauta que só quem trabalha com o dado enxerga.

---

## Como reproduzir

### 1. Dependências

```r
pak::pak("theoadepaula/theoviz")   # paleta, tabelas gt, formatação pt-BR
```

Artigos em R (`arrow`, `dplyr`, `plotly`, `gt`); pipeline de extração em Python
(`pdfplumber`, `pandas`). R 4.5.2, Quarto 1.9.

> **Por que o pipeline é Python e os artigos são R.** Exceção consciente à regra
> do projeto: a extração de tabela de PDF é sensivelmente melhor em Python. O
> pipeline roda offline e só produz `.parquet`/`.csv`; tudo que vai ao ar é R.

### 2. Dados brutos — não versionados

Os 12 relatórios anuais (2014–2025, 1.704 páginas) somam **160 MB** e ficam fora
do repositório. São públicos em <https://www.slu.df.gov.br/relatorios>.

Depois de baixá-los para `dados_brutos/`, confirme que são os mesmos que geraram
esta análise:

```bash
sha256sum -c MANIFEST-dados-brutos.sha256
```

**`dados/tabelas_brutas/` está versionado de propósito** (2.010 CSVs, 5,1 MB):
é a saída da extração. Sem ele, auditar a extração exigiria baixar os 160 MB de
PDFs — e auditar a extração é justamente o assunto do artigo 02.

### 3. Rodar

```bash
python code/01_extrair_bruto.py
python code/02_serie_historica.py
python code/03_consolidar.py
python code/04_orcamento.py
python code/05_dados_painel.py
python code/06_conferir_prosa.py    # tem que sair 0 antes de publicar
quarto render
```

### 4. O conferidor de prosa

`code/06_conferir_prosa.py` afirma **contra o dado** todo número citado em texto
corrido, e sai com código 1 se algum quebrar. Não é zelo abstrato: os artigos
afirmaram "267 pontos" e "15 divergências" por um tempo, enquanto os dados
diziam 164 e 9. Foi este script que pegou.

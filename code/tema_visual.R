# Tema visual compartilhado pelos artigos (gt + plotly).
#
# Existe para os tres .qmd nao carregarem cada um a sua copia do estilo. Cada
# artigo faz: source(here::here("code", "tema_visual.R")).
#
# A paleta e a MESMA do painel (painel/index.html), e passou no validador de
# daltonismo nos modos claro e escuro. Nao troque cor no olho: rode
#   node scripts/validate_palette.js "#2a78d6,#008300" --mode light --surface "#fcfcfb"
# do skill dataviz antes de mexer.

suppressPackageStartupMessages({
  library(gt)
  library(plotly)
  library(theoviz)
})

# O estilo das tabelas nao mora mais aqui: vem do pacote theoviz, comum aos tres
# projetos. Editar la, nao neste arquivo. (Antes era um source() do _comum, que
# subia um nivel na arvore do OneDrive e quebraria ao migrar para o site.)

# --- paleta -----------------------------------------------------------------
# s1 azul, s2 verde, s3 rosa, s4 ambar. Ordem fixa: serie 1 sempre s1, etc.
# Nunca cicle -- uma 5a serie vira facetas ou "outros", nao uma cor nova.
# As cores vem do theoviz; o nome local CORES e preservado para os .qmd.
CORES <- paleta()

# Cinza medio proposital: os graficos usam fundo TRANSPARENTE para herdar a cor
# da pagina, entao o texto de eixo precisa passar em contraste tanto sobre
# claro (#fcfcfb) quanto sobre escuro (#1a1a19). Este tom passa nos dois.
# Nao e o `tinta("fraca")` do theoviz: aquele foi calibrado so para fundo claro.
TINTA_2 <- "#8a8a85"
GRADE   <- grade_rgba(0.22)

# --- gt ---------------------------------------------------------------------
# `tabela()` e so o nome local do tema canonico -- mantido para nao mexer nos
# .qmd. A tabela e o "par acessivel" do grafico: quando a cor falha, ela responde.
tabela <- tabela_gt

# --- plotly -----------------------------------------------------------------
# Fundo transparente de proposito (ver TINTA_2). hovermode "x unified" e o que
# entrega o crosshair + tooltip que um grafico de linha deve ter.
grafico <- function(p, y_titulo = NULL, sufixo = "") {
  p |>
    layout(
      paper_bgcolor = "rgba(0,0,0,0)",
      plot_bgcolor  = "rgba(0,0,0,0)",
      font   = list(family = "IBM Plex Sans, system-ui, sans-serif",
                    size = 13, color = TINTA_2),
      hovermode = "x unified",
      hoverlabel = list(font = list(size = 13), align = "left"),
      margin = list(l = 60, r = 90, t = 20, b = 40),
      xaxis  = list(title = "", showgrid = FALSE, zeroline = FALSE,
                    tickmode = "linear", dtick = 1,
                    linecolor = GRADE, ticks = "outside", tickcolor = GRADE),
      yaxis  = list(title = y_titulo, gridcolor = GRADE, zeroline = FALSE,
                    showline = FALSE, ticksuffix = sufixo,
                    separatethousands = TRUE),
      legend = list(orientation = "h", x = 0, y = 1.12,
                    bgcolor = "rgba(0,0,0,0)"),
      showlegend = TRUE
    ) |>
    config(displayModeBar = FALSE, locale = "pt-br", responsive = TRUE)
}

# Rotulo direto no ultimo ponto da serie. Nao e enfeite: garante que a
# identidade da serie nunca dependa so da cor.
rotulo_final <- function(p, x, y, texto, cor) {
  add_annotations(p, x = x, y = y, text = paste0(" ", texto),
                  xanchor = "left", yanchor = "middle", showarrow = FALSE,
                  font = list(color = cor, size = 12.5))
}

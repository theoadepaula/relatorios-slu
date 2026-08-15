# Tema visual compartilhado pelos artigos (gt + plotly).
#
# Existe para os tres .qmd nao carregarem cada um a sua copia do estilo. Cada
# artigo faz: source(here::here("code", "tema_visual.R")).
#
# A paleta e a MESMA do painel (painel/index.html), e passou no validador de
# daltonismo nos modos claro e escuro. Nao troque cor no olho: rode
#   node scripts/validate_palette.js "#3987e5,#008300" --mode dark --surface "#0d1014"
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
#
# MODO ESCURO (2026-08-15) ----------------------------------------------------
# Os artigos deste projeto sao publicados em pagina escura -- sempre foram -- e
# ate aqui pediam ao theoviz as cores do modo CLARO. Passam a pedir o escuro.
# Contra o chao do site (#0d1014) os quatro slots medem 5,24 / 3,86 / 4,83 e
# 6,21 -- todos acima do piso de 3:1.
CORES <- paleta(modo = "escuro")

# Este arquivo cravava um `TINTA_2 <- "#8a8a85"` proprio, com o comentario "nao
# e o tinta('fraca') do theoviz: aquele foi calibrado so para fundo claro". Era
# verdade, e deixou de ser: desde a 0.3.0 o theoviz tem um piso proprio para o
# escuro (#7d858e, o `rotulo` do sistema visual do site), medido contra o fundo
# E contra a chapa. Um cinza inventado aqui era exatamente a divergencia que o
# pacote existe para eliminar.
TINTA_2 <- tinta("fraca", modo = "escuro")

# Grade solida, nao rgba. O `grade_rgba()` e o recurso de CHAO DESCONHECIDO:
# serve quando a figura nao sabe sobre o que vai pousar. Aqui sabe -- a pagina
# do artigo e escura --, e o filete do site e o traco certo.
GRADE   <- tinta("grade", modo = "escuro")

# --- gt ---------------------------------------------------------------------
# `tabela()` e so o nome local do tema canonico -- mantido para nao mexer nos
# .qmd. A tabela e o "par acessivel" do grafico: quando a cor falha, ela responde.
#
# O `modo = "escuro"` nao e detalhe: sem ele o gt crava `background-color:
# #FFFFFF` inline, e nenhuma folha de estilo derruba estilo inline. Toda tabela
# destes artigos ia ao ar como um retangulo branco no meio da pagina escura. No
# escuro a tabela e transparente e pousa na pagina -- a mesma escolha que o
# `grafico()` abaixo ja fazia com `paper_bgcolor`.
tabela <- function(...) tabela_gt(..., modo = "escuro")

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

"""Extrai a tabela 'Serie Historica dos Quantitativos' de cada relatorio -> painel longo."""
import re, os, glob, csv

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXTO = os.path.join(RAIZ, "dados_brutos", "texto")
SAIDA = os.path.join(RAIZ, "dados")

UNIDADES = {"t","km","u","ha","equipe","m3","m³","viagem","txkm","kmxton","unid","und"}

def norm_unidade(s):
    s = s.strip().lower().replace(" ", "")
    return {"txkm": "t x km", "kmxton": "km x t", "m3": "m3", "m³": "m3"}.get(s, s)

def eh_unidade(l):
    return l.strip().lower().replace(" ", "").rstrip(".") in UNIDADES

def num(s):
    s = s.strip().replace("+", "").replace("−", "-")
    if not re.fullmatch(r"-?\d{1,3}(\.\d{3})*(,\d+)?|-?\d+([.,]\d+)?", s):
        return None
    return float(s.replace(".", "").replace(",", "."))

def parse(txt, relatorio):
    hits = [m.end() for m in re.finditer(r"S[EÉ]RIE HIST[OÓ]RICA DOS QUANTITATIVOS", txt, re.I)]
    if not hits:
        return []
    inicio = hits[-1]
    # o titulo pode terminar com o ano do relatorio ("... dos Servicos - 2017"), que
    # nao e coluna: descarta o resto da linha do titulo antes de ler o cabecalho.
    inicio = txt.find("\n", inicio) + 1
    bloco = txt[inicio: inicio + 12000]
    # a tabela costuma atravessar paginas: remove marcadores e ruido de cabecalho/rodape
    # em vez de truncar no primeiro salto de pagina.
    # A tabela atravessa paginas. Marcadores de pagina, numeros de pagina soltos e o
    # cabecalho corrido da secao (que reaparece no topo de cada pagina) sao ruido,
    # nao fim de tabela -- por isso sao descartados em vez de encerrarem o bloco.
    CABECALHO = re.compile(r"\d+(\.\d+)*\.?\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ \-/,()]{5,}")
    linhas = []
    desde_marcador = 99
    for l in bloco.split("\n"):
        l = l.strip()
        if l.startswith("===== [pagina"):
            desde_marcador = 0
            continue
        desde_marcador += 1
        if CABECALHO.fullmatch(l):
            continue
        # numero de pagina solto: so descarta junto ao marcador, senao engoliria
        # celulas de valor legitimas (varios relatorios usam "0" para ausencia).
        if desde_marcador <= 3 and re.fullmatch(r"\d{1,3}", l):
            continue
        linhas.append(l)

    # anos do cabecalho: primeiros 4-digitos plausiveis antes da 1a unidade
    anos = []
    for l in linhas[:40]:
        for a in re.findall(r"\b(20[01][0-9]|202[0-9])\b", l):
            if int(a) not in anos:
                anos.append(int(a))
        if eh_unidade(l) and anos:
            break
    if not anos:
        return []
    anos.sort()  # as colunas sao sempre cronologicas da esquerda para a direita

    regs, nome = [], []
    i, desde_unidade = 0, 0
    while i < len(linhas):
        l = linhas[i]
        # sem unidade por muitas linhas seguidas = ja saimos da tabela
        desde_unidade += 1
        if desde_unidade > 60:
            break
        if eh_unidade(l) and nome:
            desde_unidade = 0
            unid = norm_unidade(l)
            vals, j = [], i + 1
            while j < len(linhas) and len(vals) < len(anos):
                v = num(linhas[j])
                if v is None:
                    if linhas[j] in ("", "-", "–"):
                        vals.append(None); j += 1; continue
                    break
                vals.append(v); j += 1
            atividade = re.sub(r"^\d+\s*", "", " ".join(nome)).strip()
            atividade = re.sub(r"\s+", " ", atividade)
            # remove cabecalho de coluna que as vezes gruda na 1a atividade
            atividade = re.sub(r"^ATIVIDADE\s+UNIDADE\s*", "", atividade, flags=re.I).strip()
            if atividade and len(atividade) > 5:
                for a, v in zip(anos, vals):
                    if v is not None:
                        regs.append({"ano": a, "atividade": atividade, "unidade": unid,
                                     "valor": v, "relatorio_fonte": relatorio})
            nome = []; i = j; continue
        if l and not re.fullmatch(r"[\d\.,\s%+\-/()]*", l) and "Ano" not in l[:4]:
            nome.append(l)
            if len(nome) > 4:
                nome = nome[-4:]
        i += 1
    return regs

todos = []
for f in sorted(glob.glob(os.path.join(TEXTO, "*.txt"))):
    rel = int(os.path.basename(f)[4:8])
    r = parse(open(f, encoding="utf-8").read(), rel)
    print(f"relatorio {rel}: {len(r)} registros, {len(set(x['atividade'] for x in r))} atividades")
    todos += r

os.makedirs(SAIDA, exist_ok=True)
with open(os.path.join(SAIDA, "slu_serie_historica.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["ano","atividade","unidade","valor","relatorio_fonte"], delimiter=";")
    w.writeheader(); w.writerows(todos)
print("TOTAL:", len(todos))

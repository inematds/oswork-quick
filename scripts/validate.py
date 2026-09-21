#!/usr/bin/env python3
"""Portão mecânico do formato-curso-v5 para o OSWork v5.

Confere o conteúdo real — nunca a autodeclaração (CHECKLIST-V5 §3, nota de escopo).
Uso:  python3 scripts/validate.py [arquivo.html ...]
Sem argumento, valida curso.html.
"""
import html
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROFISSOES = ("gestora", "gestor", "professor", "professora")

SENTINELA = [
    r"JSON", r"terminal", r"\bGit\b", r"reposit[óo]rio", r"commit", r"\bbranch\b",
    r"pipeline", r"arquivo de configura", r"instalar", r"\bscript\b", r"servidor",
    r"\bAPI\b", r"deploy", r"\bCLI\b", r"diret[óo]rio", r"plugin", r"encoding",
]

QUADROS = ("qerr", "qbefore-after", "qapply", "qsteps", "qanchor")

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF←-⇿⬀-⯿]"
)
# setas tipográficas usadas como chrome pelo próprio template (↓ ← → ✓ ✕) não contam
CHROME_OK = set("←→↓↑✓✕—…·")

erros = []
avisos = []


def falha(msg):
    erros.append(msg)


def aviso(msg):
    avisos.append(msg)


def texto_visivel(frag):
    """Só o que o aluno lê: sem tags, sem comentários, sem script/style."""
    t = re.sub(r"<!--.*?-->", " ", frag, flags=re.S)
    t = re.sub(r"<script\b.*?</script>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<style\b.*?</style>", " ", t, flags=re.S | re.I)
    # atributos que o aluno lê mesmo assim
    legendas = " ".join(re.findall(r'data-(?:cap|def)="([^"]*)"', t))
    t = re.sub(r"<[^>]+>", " ", t)
    return html.unescape(t + " " + legendas)


def palavras(s):
    return len(re.findall(r"[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9'-]*", s))


def normaliza(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s)).lower()
    s = re.sub(r"[^a-zà-ÿ0-9 ]+", " ", s)
    return re.findall(r"\S+", s)


def checa_aula(num, view, tipo_esperado=None):
    p = f"aula {num}"
    steps = re.findall(r'<section class="step"[^>]*>(.*?)</section>', view, re.S)
    k = len(steps)
    if not 3 <= k <= 7:
        falha(f"{p}: {k} steps — fora de 3..7")

    # --- espinha ---
    for cls, n in (("promise", 1), ("why", 1), ("practice", 1), ("psafe", 1),
                   ("pgoal", 1), ("recap-autor", 1), ("next-action", 1)):
        got = len(re.findall(r'class="[^"]*\b%s\b' % re.escape(cls), view))
        if got != n:
            falha(f"{p}: .{cls} aparece {got}x, esperado {n}")

    m = re.search(r'data-tempo="(\d+)min"', view)
    if not m:
        falha(f"{p}: data-tempo ausente ou malformado")
        declarado = 0
    else:
        declarado = int(m.group(1))

    # --- prática ---
    mode = re.search(r'class="practice"[^>]*data-mode="([^"]+)"', view)
    if not mode:
        falha(f"{p}: .practice sem data-mode")
    elif mode.group(1) == "codigo":
        falha(f"{p}: data-mode=codigo é proibido para público sem base técnica")
    pgoal = re.search(r'class="pgoal"[^>]*>(.*?)</p>', view, re.S)
    pmin = 0
    if pgoal:
        mt = re.search(r"(\d+)\s*min", pgoal.group(1))
        if not mt:
            falha(f"{p}: .pgoal sem tempo declarado")
        else:
            pmin = int(mt.group(1))
            if not 5 <= pmin <= 15:
                falha(f"{p}: prática de {pmin}min — fora de 5..15")
    if not re.search(r'data-ptask="', view):
        falha(f"{p}: prática sem passos verificáveis (input[data-ptask])")

    # --- exemplo por profissão e apoio visual em 100% dos steps ---
    for i, s in enumerate(steps, 1):
        if not re.search(r'<p data-ex="', s):
            falha(f"{p} step {i}: sem exemplo-profissão marcado (<p data-ex=...>)")
        else:
            for ex in re.findall(r'data-ex="([^"]*)"', s):
                if ex.lower() not in PROFISSOES:
                    falha(f"{p} step {i}: data-ex=\"{ex}\" não é profissão da descoberta")
    # QUICK: a figura carrega o ensino — cada step leva TAMBEM uma figura inline
    for i, sec in enumerate(steps, 1):
        if not re.search(r'<figure class="colfig"', sec):
            falha(f"{p} step {i}: sem figura inline .colfig (o Quick exige 2 visuais por step)")
        elif not re.search(r'<figcaption>', sec):
            falha(f"{p} step {i}: .colfig sem <figcaption> que ensina")
    figs = set(re.findall(r'class="fig[^"]*"[^>]*data-fig="(\d+)"', view))
    stepfigs = set(re.findall(r'<section class="step"[^>]*data-fig="(\d+)"', view))
    if stepfigs != figs or len(figs) != k:
        falha(f"{p}: apoio visual não cobre 100% dos steps "
              f"(steps={sorted(stepfigs)} figs={sorted(figs)} k={k})")
    for f in re.findall(r'<div class="fig(?: on)?"[^>]*>', view):
        if "data-cap=" not in f:
            falha(f"{p}: figura sem legenda-que-ensina (data-cap)")

    # --- dosagem e densidade ---
    usados = [q for q in QUADROS if re.search(r'class="%s"' % q, view)]
    tem_quiz = bool(re.search(r'class="quiz"', view))
    tem_cards = bool(re.search(r'id="cards-%s"' % num, view))
    tipos = len(usados) + (1 if tem_quiz else 0) + (1 if tem_cards else 0)
    if tipos > 5:
        falha(f"{p}: pool de fixação com {tipos} tipos — teto é 5 ({usados})")
    if tipo_esperado == "FUNDAMENTO" and not tem_quiz:
        falha(f"{p}: aula FUNDAMENTO sem teste-se (quiz data-fb)")
    for q in re.findall(r'<div class="quiz"[^>]*data-answer="([^"]+)"(.*?)</div>', view, re.S):
        if f'data-k="{q[0]}"' not in q[1] or "data-fb=" not in q[1]:
            falha(f"{p}: quiz sem data-fb na opção certa")
    if len(re.findall(r'class="qanchor"', view)) > 1:
        falha(f"{p}: mais de uma .qanchor")
    # densidade: nenhum par de steps adjacentes com quadro funcional
    pos = []
    for i, s in enumerate(steps, 1):
        if any(re.search(r'class="%s"' % q, s) for q in QUADROS):
            pos.append(i)
    for a, b in zip(pos, pos[1:]):
        if b - a < 2:
            falha(f"{p}: quadros funcionais em steps adjacentes ({a} e {b}) — densidade")

    # --- qapply precisa de ≥2 profissões ---
    for bloco in re.findall(r'<div class="qapply">(.*?)</div>', view, re.S):
        nomes = {x for x in PROFISSOES if re.search(r"\b%s" % x, bloco, re.I)}
        base = {n.rstrip("a") for n in nomes}
        if len(base) < 2:
            falha(f"{p}: .qapply com menos de 2 profissões distintas")

    # --- cartões: forma + anti-duplicação ---
    recap = re.search(r'<div class="recap-autor">(.*?)</div>', view, re.S)
    recap_tokens = normaliza(recap.group(1)) if recap else []
    cards_raw = re.search(r'id="cards-%s"[^>]*>(.*?)</script>' % num, view, re.S)
    ncards = 0
    if not cards_raw:
        falha(f"{p}: <script id=cards-{num}> ausente")
    else:
        fronts = re.findall(r'"front"\s*:\s*"((?:[^"\\]|\\.)*)"', cards_raw.group(1))
        ncards = len(fronts)
        if ncards < 3:
            falha(f"{p}: só {ncards} cartões (mínimo 3)")
        seis = {tuple(recap_tokens[i:i + 6]) for i in range(max(0, len(recap_tokens) - 5))}
        versos = re.findall(r'"back"\s*:\s*"((?:[^"\\]|\\.)*)"', cards_raw.group(1))
        for b in versos:
            bt = normaliza(b)
            for i in range(max(0, len(bt) - 5)):
                if tuple(bt[i:i + 6]) in seis:
                    falha(f"{p}: verso de cartão repete ≥6 palavras do recap: "
                          f"{' '.join(bt[i:i + 6])}")
                    break
        for f in fronts:
            if "?" not in f:
                falha(f"{p}: cartão-afirmação (frente sem pergunta): {f[:60]}")
            ft = normaliza(f)
            for i in range(max(0, len(ft) - 5)):
                if tuple(ft[i:i + 6]) in seis:
                    falha(f"{p}: cartão repete ≥6 palavras do recap: "
                          f"{' '.join(ft[i:i + 6])}")
                    break

    # --- recap não pergunta ---
    if recap and "?" in re.sub(r"<[^>]+>", "", recap.group(1)):
        falha(f"{p}: .recap-autor contém pergunta (é síntese, nunca recall)")

    # --- manifesto ---
    man = re.search(r"<!--\s*COMPLETUDE aula-%s\s*\|\s*tipo=(\w+)\s*\|\s*steps=(\d+)(.*?)-->"
                    % num, view, re.S)
    if not man:
        falha(f"{p}: manifesto de completude ausente")
    else:
        tipo, ksaid, corpo = man.group(1), int(man.group(2)), man.group(3)
        if ksaid != k:
            falha(f"{p}: manifesto diz steps={ksaid}, o real é {k}")
        if tipo_esperado and tipo != tipo_esperado:
            falha(f"{p}: manifesto diz tipo={tipo}, currículo diz {tipo_esperado}")
        # o manifesto nao pode mentir: o tempo citado nele tem de ser o real
        mt = re.search(r'data-tempo="(\d+)min"', corpo)
        if mt and declarado and int(mt.group(1)) != declarado:
            falha(f"{p}: manifesto cita data-tempo={mt.group(1)}min, o real é {declarado}min")
        if "[AUSENTE]" in corpo:
            falha(f"{p}: manifesto tem [AUSENTE]")
        itens = ["promise", "why", "tempo", "exemplo-profissao", "apoio-visual",
                 "practice", "psafe", "pgoal-tempo", "recap-autor", "next-action",
                 "cards", "anti-duplicacao", "teste-se-FUND"]
        for it in itens:
            if not re.search(r"\[(OK|N/A|AUSENTE)\]\s+%s\b" % re.escape(it), corpo):
                falha(f"{p}: manifesto sem a linha '{it}'")
        mk = re.search(r"\[(OK|N/A|AUSENTE)\]\s+teste-se-FUND", corpo)
        if mk:
            if tipo == "FUNDAMENTO" and mk.group(1) != "OK":
                falha(f"{p}: teste-se-FUND deve ser [OK] em FUNDAMENTO")
            if tipo != "FUNDAMENTO" and mk.group(1) != "N/A":
                falha(f"{p}: teste-se-FUND deve ser [N/A] fora de FUNDAMENTO "
                      f"(marcador reflete a obrigação, não a presença)")

    # --- tempo calculado vs declarado ---
    nq = len(re.findall(r'class="quiz"', view))
    w = palavras(texto_visivel(view))
    calc = math.ceil(w / 200 + pmin + nq * 0.5)
    # teto por STEP, nao por aula: uma aula de 5 steps carrega mais conteudo por
    # estrutura, nao por prolixidade. 205 palavras/step (a edicao longa gasta ~370).
    teto = 205 * k
    if w > teto:
        falha(f"{p}: {w} palavras para {k} steps — teto é {teto} "
              f"(205/step; o visual ensina, o texto amarra)")
    if declarado and declarado < calc:
        falha(f"{p}: data-tempo={declarado}min < custo calculado {calc}min "
              f"({w} palavras + {pmin}min prática + {nq} perguntas) — arredonde para cima")
    elif declarado and declarado > calc + 6:
        aviso(f"{p}: data-tempo={declarado}min bem acima do calculado {calc}min")

    return dict(k=k, cards=ncards, tempo=declarado, calc=calc, tipos=tipos)


def main():
    alvos = sys.argv[1:] or [os.path.join(ROOT, "curso.html")]
    for alvo in alvos:
        if not os.path.exists(alvo):
            falha(f"arquivo não encontrado: {alvo}")
            continue
        doc = open(alvo, encoding="utf-8").read()
        views = re.findall(r'<section class="view" id="v-aula-(\d+)"(.*?)\n</section>',
                           doc, re.S)
        if not views:
            falha(f"{alvo}: nenhuma view de aula encontrada")
            continue

        tipos_curr = {"1": "FUNDAMENTO", "2": "FUNDAMENTO", "3": "FERRAMENTA",
                      "4": "FERRAMENTA", "5": "FERRAMENTA", "6": "FUNDAMENTO",
                      "7": "PRATICA"}
        resumo = []
        for num, view in views:
            resumo.append((num, checa_aula(num, view, tipos_curr.get(num))))

        # --- globais ---
        vis = texto_visivel(doc)
        for pat in SENTINELA:
            for m in re.finditer(pat, vis, re.I):
                ctx = vis[max(0, m.start() - 70):m.end() + 70].replace("\n", " ")
                falha(f"jargão-sentinela '{m.group(0)}' no texto do aluno: …{ctx.strip()}…")
        if len(re.findall(r'class="gterm"', doc)) < 1:
            falha("zero .gterm no curso inteiro — glossário de domínio esquecido")
        for ch in set(EMOJI.findall(vis)) - CHROME_OK:
            falha(f"emoji/símbolo decorativo no texto: {ch!r}")
        if "!!" in vis:
            falha("exclamação dupla no texto (regra de clímax)")
        if re.search(r"imagine uma empresa|empresa X|profissional qualquer", vis, re.I):
            falha("placeholder genérico no texto")
        sem_com = re.sub(r"<!--.*?-->", " ", doc, flags=re.S)
        if "termdemo" in sem_com:
            falha(".termdemo presente — currículo não tem comando real (decisão registrada)")

        print(f"\n== {os.path.basename(alvo)} — {len(views)} aulas ==")
        for num, r in resumo:
            print(f"  aula {num}: {r['k']} steps · {r['cards']} cartões · "
                  f"{r['tempo']}min (calc {r['calc']}) · {r['tipos']} tipos de fixação")
        tot = sum(r["tempo"] for _, r in resumo)
        print(f"  total: {tot}min")

    print()
    for a in avisos:
        print(f"AVISO  {a}")
    for e in erros:
        print(f"FALHA  {e}")
    print(f"\n{len(erros)} falha(s), {len(avisos)} aviso(s).")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())

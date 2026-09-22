#!/usr/bin/env python3
"""Portão das edições EN e ES do OSWork Quick.

O portão em português não serve aqui: a lista de jargão-sentinela é em português e
os marcadores mudam de idioma. O que este confere é PARIDADE ESTRUTURAL com o PT —
a tradução não pode perder aula, step, figura, prática, cartão nem manifesto — mais
as regras que continuam valendo em qualquer idioma.

Uso:  python3 scripts/validate-locales.py
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDIOMAS = ("en", "es")

# a lista-sentinela traduzida: o curso promete não usar jargão de plataforma
SENTINELA = {
    "en": [r"\bterminal\b", r"\binstall\b", r"\bscript\b", r"\bserver\b", r"\brepositor",
           r"\bcommit\b", r"\bbranch\b", r"\bGit\b", r"\bJSON\b", r"\bpipeline\b",
           r"config file", r"\bAPI\b", r"\bdeploy\b", r"\bCLI\b", r"\bdirectory\b",
           r"\bplugin\b", r"\bencoding\b"],
    "es": [r"\bterminal\b", r"\binstalar\b", r"\bscript\b", r"\bservidor\b", r"\brepositorio\b",
           r"\bcommit\b", r"\brama\b", r"\bGit\b", r"\bJSON\b", r"\bpipeline\b",
           r"archivo de configuraci", r"\bAPI\b", r"\bdeploy\b", r"\bCLI\b", r"\bdirectorio\b",
           r"\bplugin\b", r"\bencoding\b"],
}

# literais legitimos: extensao de arquivo no botao de exportar, tipo MIME no markup,
# e a propria lista do que o curso NAO exige ("Installing programs. Nothing needs...").
PERMITIDO = (
    ".json", "application/json",
    "Installing programs", "Instalación de programas", "Instalar programas",
)

erros = []


def falha(m):
    erros.append(m)


def visivel(frag):
    t = re.sub(r"<!--.*?-->", " ", frag, flags=re.S)
    t = re.sub(r"<script\b.*?</script>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<style\b.*?</style>", " ", t, flags=re.S | re.I)
    legendas = " ".join(re.findall(r'data-(?:cap|def)="([^"]*)"', t))
    return html.unescape(re.sub(r"<[^>]+>", " ", t) + " " + legendas)


def conta(doc, pat):
    return len(re.findall(pat, doc))


def sem_comentarios(doc):
    """O manifesto de completude cita '<script id="cards-1">' como texto —
    contar cartões sem remover comentários faz o portão ler o manifesto."""
    return re.sub(r"<!--.*?-->", " ", doc, flags=re.S)


def main():
    pt = open(os.path.join(ROOT, "curso.html"), encoding="utf-8").read()
    base = {
        "aulas": conta(pt, r'<section[^>]*id="v-aula-\d+"'),
        "steps": conta(pt, r'<section[^>]*class="step"'),
        "figs trilho": conta(pt, r'<div[^>]*class="fig(?: on)?"[^>]*data-fig='),
        "figs inline": conta(pt, r'<figure[^>]*class="colfig"'),
        "práticas": conta(pt, r'class="practice"'),
        "psafe": conta(pt, r'class="psafe"'),
        "quizzes": conta(pt, r'class="quiz"'),
        "recaps": conta(pt, r'class="recap-autor"'),
        "next-action": conta(pt, r'class="next-action"'),
        "manifestos": conta(pt, r"COMPLETUDE aula-"),
        "exemplos profissão": conta(pt, r'<p[^>]*data-ex="'),
        "gterm": conta(pt, r'class="gterm"'),
    }
    cards_pt = sum(len(json.loads(m)) for m in
                   re.findall(r'<script[^>]*id="cards-\d+"[^>]*>(.*?)</script>',
                              sem_comentarios(pt), re.S))

    print(f"PT (referência): " + " · ".join(f"{k} {v}" for k, v in base.items()) +
          f" · cartões {cards_pt}")

    for lang in IDIOMAS:
        p = os.path.join(ROOT, lang, "curso.html")
        if not os.path.exists(p):
            falha(f"{lang}: {lang}/curso.html ausente")
            continue
        doc = open(p, encoding="utf-8").read()

        # 1. paridade estrutural
        for nome, esperado in base.items():
            achado = conta(doc, {
                "aulas": r'<section[^>]*id="v-aula-\d+"',
                "steps": r'<section[^>]*class="step"', "figs trilho": r'<div[^>]*class="fig(?: on)?"[^>]*data-fig=',
                "figs inline": r'<figure[^>]*class="colfig"', "práticas": r'class="practice"',
                "psafe": r'class="psafe"', "quizzes": r'class="quiz"',
                "recaps": r'class="recap-autor"', "next-action": r'class="next-action"',
                "manifestos": r"COMPLETUDE aula-", "exemplos profissão": r'<p[^>]*data-ex="',
                "gterm": r'class="gterm"',
            }[nome])
            if achado != esperado:
                falha(f"{lang}: {nome} = {achado}, o PT tem {esperado}")

        cards = sum(len(json.loads(m)) for m in
                    re.findall(r'<script[^>]*id="cards-\d+"[^>]*>(.*?)</script>',
                               sem_comentarios(doc), re.S))
        if cards != cards_pt:
            falha(f"{lang}: {cards} cartões, o PT tem {cards_pt}")

        # 2. estado isolado por idioma
        mm_ = re.search(r'<meta[^>]*name="curso"[^>]*>', doc)
        estado = re.search(r'content="([^"]+)"', mm_.group(0)).group(1) if mm_ else None
        if not estado or not estado.endswith("-" + lang):
            falha(f"{lang}: <meta name=curso> deveria terminar em -{lang} "
                  f"(progresso e cartões ficariam misturados com o PT)")
        if not re.search(r'<html[^>]*lang="%s"' % lang, doc):
            falha(f"{lang}: <html lang> não é {lang}")

        # 3. tempos preservados (número é fato, não texto)
        t_pt = re.findall(r'data-tempo="(\d+min)"', pt)
        t_l = re.findall(r'data-tempo="(\d+min)"', doc)
        if t_pt != t_l:
            falha(f"{lang}: data-tempo divergente — PT {t_pt} vs {lang} {t_l}")

        # 4. nada de português sobrando nos textos longos
        vis = visivel(doc)
        sobra = re.findall(r"\b(você|não|então|também|aula|trabalho|pasta|pedido)\b", vis)
        if lang == "en" and len(sobra) > 3:
            falha(f"{lang}: {len(sobra)} palavras em português no texto visível "
                  f"(ex.: {sorted(set(sobra))[:5]})")

        # 5. jargão-sentinela no idioma de destino
        for pat in SENTINELA[lang]:
            for mm in re.finditer(pat, vis, re.I):
                ctx = vis[max(0, mm.start() - 60):mm.end() + 60].replace("\n", " ")
                if any(a.lower() in ctx.lower() for a in PERMITIDO):
                    continue
                falha(f"{lang}: jargão '{mm.group(0)}' — …{ctx.strip()}…")

        # 6. o seletor de idioma existe e aponta para os outros dois
        if 'class="langsel"' not in doc:
            falha(f"{lang}: sem seletor de idioma")
        for outro in ("pt",) + tuple(x for x in IDIOMAS if x != lang):
            if f'data-lang="{outro}"' not in doc:
                falha(f"{lang}: seletor não oferece {outro}")

        # 6b. rótulos gerados por CSS traduzidos (superfície invisível ao HTML)
        css = os.path.join(ROOT, lang, "assets", "i18n.css")
        if not os.path.exists(css):
            falha(f"{lang}: assets/i18n.css ausente — PROMESSA/seguro ficariam em português")
        else:
            c = open(css, encoding="utf-8").read()
            if "PROMESSA" in c:
                falha(f"{lang}: rótulo CSS .promise ainda em português")
            if 'href="assets/i18n.css"' not in doc:
                falha(f"{lang}: i18n.css existe mas não está ligado na página")
        # 6c. o motor traduzido é o local, nunca o compartilhado em português
        if 'src="../assets/curso.js"' in doc:
            falha(f"{lang}: página carrega o motor em português (../assets/curso.js)")

        # 7. os assets compartilhados sobem um nível
        if 'href="assets/aula.css"' in doc:
            falha(f"{lang}: caminho de asset não ajustado (deveria ser ../assets/)")

        # 8. zero emoji e zero exclamação dupla, como no PT
        CHROME = set("←→↓↑✓✕—…·")
        for ch in set(re.findall("[\U0001F300-\U0001FAFF\U00002600-\U000027BF]", vis)) - CHROME:
            falha(f"{lang}: emoji no texto: {ch!r}")
        if "!!" in vis:
            falha(f"{lang}: exclamação dupla")

        print(f"{lang}: {conta(doc, r'<section[^>]*id="v-aula-')} aulas · "
              f"{cards} cartões · estado '{estado or '?'}'")

    # 9. o PT também precisa do seletor: é a página que o portal linka, e sem ele
    # não existe caminho para EN/ES. Foi exatamente o que escapou em 21/09.
    import os.path as _op
    for f in ("curso.html", "landing.html"):
        p_pt = os.path.join(ROOT, f)
        if not os.path.exists(p_pt):
            continue
        d_pt = open(p_pt, encoding="utf-8").read()
        if 'class="langsel"' not in d_pt:
            falha(f"pt/{f}: sem seletor de idioma — quem chega pelo português "
                  f"não alcança EN/ES")
            continue
        for l in IDIOMAS:
            if f'data-lang="{l}"' not in d_pt:
                falha(f"pt/{f}: seletor não oferece {l}")
    # 10. todo destino do seletor, nos três idiomas, tem de existir em disco
    for pasta in ("", ) + IDIOMAS:
        for f in ("curso.html", "landing.html"):
            p_x = os.path.join(ROOT, pasta, f)
            if not os.path.exists(p_x):
                continue
            d_x = open(p_x, encoding="utf-8").read()
            for tag in re.findall(r"<a[^>]*data-lang=\"[^\"]+\"[^>]*>", d_x):
                hf = re.search(r'href="([^"]+)"', tag)
                if not hf:
                    falha(f"{pasta or 'pt'}/{f}: link de idioma sem href")
                    continue
                dest = _op.normpath(os.path.join(ROOT, pasta, hf.group(1)))
                if not os.path.exists(dest):
                    falha(f"{pasta or 'pt'}/{f}: seletor aponta para "
                          f"arquivo inexistente: {hf.group(1)}")

    print()
    for e in erros:
        print("FALHA ", e)
    print(f"\n{len(erros)} falha(s).")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())

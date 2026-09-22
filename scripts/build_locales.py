#!/usr/bin/env python3
"""Monta en/ e es/ a partir do PT e dos dicionários em i18n/. Build offline.

Não chama API. Uma unidade sem tradução INTERROMPE o build — página meio traduzida
é pior que página ausente, porque passa despercebida.

O que muda por idioma:
  - <html lang>, <title>, texto, atributos lidos pelo aluno e os cartões
  - <meta name="curso">: osworkq -> osworkq-en / osworkq-es, para o progresso ficar
    isolado por idioma (cartões do aluno guardam o texto; misturar idiomas sujaria
    a revisão espaçada)
  - assets/curso.js: os literais de interface, recortados por deslocamento
  - caminhos relativos: assets/ continua compartilhado via ../assets/
  - um seletor de idioma no topo, preservando a aula aberta (a âncora)

O que NÃO muda: a arte dos SVG, o CSS, a lógica do motor, os data-* estruturais.
"""
import html as html_mod
import json
import os
import re
import shutil
import sys

from bs4 import BeautifulSoup, Comment, NavigableString

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATTRS = ("data-cap", "data-def", "data-fb", "aria-label", "title", "alt", "placeholder")
PULAR_TAGS = {"script", "style"}
IDIOMAS = {"en": "en", "es": "es"}
ROTULO = {"pt": "Português", "en": "English", "es": "Español"}

# mesma convenção do extrator: os nomes de idioma não se traduzem
NAO_TRADUZ = {"Português", "English", "Español"}

faltando = set()


def tr(d, s):
    """Traduz ou registra a ausência. Nunca devolve português silenciosamente."""
    if s is None:
        return None
    chave = s.strip("\n")
    if not chave.strip():
        return s
    if chave in NAO_TRADUZ:
        return s
    if chave in d:
        return s.replace(chave, d[chave], 1)
    faltando.add(chave)
    return s


# o script preserva a aula aberta ao trocar de idioma: sem ele, quem está na aula 5
# volta para a trilha e perde o lugar.
ANCORA_JS = (
    '<script>(function(){document.querySelectorAll(".langsel a[data-lang]")'
    '.forEach(function(a){a.addEventListener("click",function(e){'
    'if(location.hash){e.preventDefault();location.href=a.getAttribute("href")+location.hash;}'
    '});});})();</script>'
)


def seletor(lang, pagina="curso.html"):
    """Um seletor por página, com os caminhos relativos certos para cada idioma.

    De 'pt' (raiz) para en/es desce uma pasta; de en/es para pt sobe uma; entre
    en e es sobe uma e desce na outra.
    """
    links = []
    for l in ["pt"] + list(IDIOMAS):
        if l == lang:
            links.append(f'<span class="lang-cur">{ROTULO[l]}</span>')
            continue
        if lang == "pt":
            destino = f"{l}/{pagina}"
        elif l == "pt":
            destino = f"../{pagina}"
        else:
            destino = f"../{l}/{pagina}"
        links.append(f'<a href="{destino}" data-lang="{l}">{ROTULO[l]}</a>')
    return '<div class="langsel">' + "".join(links) + "</div>"


# o CSS e a capa são compartilhados e sobem um nível; o MOTOR não, porque cada
# idioma tem a sua cópia traduzida em <lang>/assets/curso.js. Mandar curso.js para
# ../assets/ faz a página traduzida carregar o motor em português — a interface
# volta ao PT sem nenhum erro aparecer.
LOCAIS = ("assets/curso.js",)


def ajusta_caminhos(soup, subpasta):
    """De dentro de en/ ou es/, os assets compartilhados sobem um nível."""
    for el in soup.find_all(["link", "script", "img", "a"]):
        for attr in ("href", "src"):
            v = el.get(attr)
            if not v or v in LOCAIS:
                continue
            if v.startswith("assets/") or v.startswith("capa/"):
                el[attr] = "../" + v


def traduz_html(caminho, d, lang, saida):
    soup = BeautifulSoup(open(caminho, encoding="utf-8").read(), "html.parser")

    if soup.html:
        soup.html["lang"] = {"en": "en", "es": "es"}[lang]

    m = soup.find("meta", {"name": "curso"})
    if m:
        m["content"] = m.get("content", "osworkq") + "-" + lang

    for el in list(soup.find_all(string=True)):
        if isinstance(el, Comment):
            continue
        if (el.parent.name if el.parent else "") in PULAR_TAGS:
            continue
        if not el.strip():
            continue
        novo = tr(d, str(el))
        if novo != str(el):
            el.replace_with(NavigableString(novo))

    for el in soup.find_all(True):
        for a in ATTRS:
            v = el.get(a)
            if v and re.search(r"[A-Za-zÀ-ÿ]{2,}", re.sub(r"<[^>]+>", " ", v)):
                el[a] = tr(d, v)
        if el.name == "meta" and el.get("name") == "description":
            el["content"] = tr(d, el.get("content", ""))

    for el in soup.find_all("script", {"type": "application/json"}):
        try:
            cards = json.loads(el.string or "[]")
        except Exception:
            continue
        for c in cards:
            c["front"] = tr(d, c.get("front", ""))
            c["back"] = tr(d, c.get("back", ""))
        el.string = "\n" + json.dumps(cards, ensure_ascii=False, indent=2) + "\n"

    ajusta_caminhos(soup, lang)

    # o override de idioma entra DEPOIS do aula.css compartilhado
    base = soup.find("link", {"href": "../assets/aula.css"})
    if base and not soup.find("link", {"href": "assets/i18n.css"}):
        novo = soup.new_tag("link", rel="stylesheet", href="assets/i18n.css")
        base.insert_after(novo)

    # seletor de idioma, logo depois da marca, preservando a âncora ao trocar
    pagina = os.path.basename(saida)
    # o PT já traz um seletor, com caminhos relativos à RAIZ. De dentro de en/ ou es/
    # esses caminhos apontam para o lugar errado (en/en/curso.html), então o antigo sai
    # e entra o do idioma. Também remove o script da âncora, que é reinserido depois.
    for velho in soup.select(".langsel"):
        velho.decompose()
    for sc in soup.find_all("script"):
        if sc.string and "langsel a[data-lang]" in sc.string:
            sc.decompose()
    marca = (soup.select_one(".bar .bar-inner .brand")
             or soup.select_one("span.course")
             or soup.select_one("header .wrap span.course"))
    if marca:
        marca.insert_after(BeautifulSoup(seletor(lang, pagina), "html.parser"))
        if soup.body:
            soup.body.append(BeautifulSoup(ANCORA_JS, "html.parser"))
    else:
        print(f"  aviso: {os.path.basename(saida)} ({lang}) sem marca; sem seletor")

    out = str(soup)
    with open(saida, "w", encoding="utf-8") as fh:
        fh.write(out)


def traduz_js(d, lang, saida):
    src = open(os.path.join(ROOT, "assets", "curso.js"), encoding="utf-8").read()
    offs = json.load(open(os.path.join(ROOT, "i18n", "js-offsets.json"), encoding="utf-8"))
    for o in sorted(offs, key=lambda x: -x["inicio"]):
        v = o["valor"]
        if v not in d:
            faltando.add(v)
            continue
        novo = d[v].replace("\\", "\\\\").replace("'", "\\'")
        src = src[:o["inicio"]] + novo + src[o["fim"]:]
    with open(saida, "w", encoding="utf-8") as fh:
        fh.write(src)


CSS_LANDING = """
  .langsel{display:inline-flex;gap:8px;align-items:center;margin-left:14px}
  .langsel a,.langsel .lang-cur{font-family:var(--mono,ui-monospace,monospace);font-size:11px;
    letter-spacing:.04em;text-decoration:none;padding:5px 9px;border-radius:9px;
    border:1px solid rgba(236,230,217,.22)}
  .langsel a{color:#948DA6}
  .langsel a:hover{color:#ECE6D9;border-color:#7CE0C6}
  .langsel .lang-cur{color:#7CE0C6;border-color:#7CE0C6}
  @media(max-width:720px){.langsel{margin-left:0;margin-top:10px}}
"""

CSS_TEXTOS = {
    ".promise::before": "PROMESSA",
    ".psafe::before": "✓ seguro — ",
}

CSS_SELETOR = """
/* seletor de idioma (build_locales.py) */
.langsel{display:inline-flex;gap:8px;align-items:center;margin-left:14px}
.langsel a,.langsel .lang-cur{font-family:var(--mono);font-size:11px;letter-spacing:.04em;
  text-decoration:none;padding:5px 9px;border-radius:9px;border:1px solid var(--line2)}
.langsel a{color:var(--muted)}
.langsel a:hover{color:var(--ink);border-color:var(--accent)}
.langsel .lang-cur{color:var(--accent);border-color:var(--accent)}
@media(max-width:720px){.langsel{margin-left:6px}.langsel a,.langsel .lang-cur{padding:4px 7px}}
"""


def main():
    for lang in IDIOMAS:
        dic_path = os.path.join(ROOT, "i18n", f"{lang}.json")
        if not os.path.exists(dic_path):
            print(f"FALTA i18n/{lang}.json — rode scripts/i18n_translate.py {lang}")
            return 1
        d = json.load(open(dic_path, encoding="utf-8"))
        destino = os.path.join(ROOT, lang)
        os.makedirs(os.path.join(destino, "assets"), exist_ok=True)

        for f in ("curso.html", "landing.html"):
            p = os.path.join(ROOT, f)
            if os.path.exists(p):
                traduz_html(p, d, lang, os.path.join(destino, f))
        traduz_js(d, lang, os.path.join(destino, "assets", "curso.js"))

        # rótulos gerados por CSS: um override por idioma, carregado depois do
        # aula.css compartilhado
        linhas = []
        for sel, pt in CSS_TEXTOS.items():
            if pt not in d:
                faltando.add(pt)
                continue
            val = d[pt].replace("\\", "\\\\").replace('"', '\\"')
            linhas.append(f'{sel}{{content:"{val}"}}')
        with open(os.path.join(destino, "assets", "i18n.css"), "w", encoding="utf-8") as fh:
            fh.write("/* rótulos gerados por CSS, traduzidos (build_locales.py) */\n"
                     + "\n".join(linhas) + "\n")

        # index.html do idioma: redireciona para a landing daquele idioma
        with open(os.path.join(destino, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(f'<!doctype html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n'
                     f'<meta http-equiv="refresh" content="0; url=landing.html">\n'
                     f'<link rel="canonical" href="landing.html">\n'
                     f'<title>OSWork Quick</title>\n</head>\n<body>\n'
                     f'<p><a href="landing.html">OSWork Quick</a></p>\n</body>\n</html>\n')
        print(f"{lang}/: curso.html, landing.html, index.html, assets/curso.js")

    # o PT também precisa do seletor: sem ele, quem chega pela página em português
    # (a que o portal linka) não tem como alcançar os outros dois idiomas.
    # Roda DEPOIS de scripts/build.py, que reescreve curso.html inteiro.
    for f in ("curso.html", "landing.html"):
        p = os.path.join(ROOT, f)
        if not os.path.exists(p):
            continue
        bruto = open(p, encoding="utf-8").read()
        if 'class="langsel"' in bruto:
            continue
        # curso.html: a marca é <span class="brand">…<a class="course">…</a></span>
        # landing.html: é <span class="course">…</span>, e a página é auto-contida
        m_brand = re.search(r'<span class="brand">.*?</span>', bruto, re.S)
        m_course = re.search(r'<span class="course">.*?</span>', bruto, re.S)
        alvo = m_brand or m_course
        if not alvo:
            print(f"  aviso: {f} sem a marca; seletor do PT não inserido")
            continue
        j = alvo.end()
        novo = bruto[:j] + "\n  " + seletor("pt", f) + bruto[j:]
        novo = novo.replace("</body>", "  " + ANCORA_JS + "\n</body>", 1)
        if f == "landing.html" and ".langsel{" not in novo:
            novo = novo.replace("</style>", CSS_LANDING + "</style>", 1)
        open(p, "w", encoding="utf-8").write(novo)
        print(f"{f}: seletor de idioma inserido no PT")

    # o CSS do seletor entra uma vez no asset compartilhado
    css = os.path.join(ROOT, "assets", "aula.css")
    atual = open(css, encoding="utf-8").read()
    if ".langsel" not in atual:
        open(css, "a", encoding="utf-8").write(CSS_SELETOR)
        print("assets/aula.css: estilo do seletor de idioma acrescentado")

    if faltando:
        print(f"\nBUILD INTERROMPIDO: {len(faltando)} unidades sem tradução.")
        for s in list(sorted(faltando))[:8]:
            print("  •", repr(s)[:110])
        return 1
    print("\nbuild dos idiomas concluído, cobertura 100%")
    return 0


if __name__ == "__main__":
    sys.exit(main())

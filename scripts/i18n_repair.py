#!/usr/bin/env python3
"""Conserta defeitos mecanicos das traducoes, antes do build.

Tres classes de defeito observadas em 21/09/2026, todas invisiveis a olho nu num
dicionario de 884 unidades:

  1. Espaco de borda perdido. Varias unidades sao fragmentos concatenados em tempo
     de execucao (' lido', ' feito', ' esperando por voce'). Sem o espaco inicial a
     interface renderiza "12read". Restauramos o espaco exato da fonte.
  2. Markup inventado. Uma traducao devolveu uma <div> a mais. Se o numero de tags
     abre/fecha nao bate com a fonte, a unidade e rejeitada do cache para ser
     retraduzida, em vez de entrar quebrada.
  3. Entidades HTML perdidas ou trocadas.

Idempotente. Uso: python3 scripts/i18n_repair.py [en es]
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def bordas(fonte, trad):
    """Devolve a traducao com o mesmo espaco inicial/final da fonte."""
    ini = re.match(r"\s*", fonte).group(0)
    fim = re.search(r"\s*$", fonte).group(0)
    return ini + trad.strip() + fim

# so contam TAGS DE VERDADE: os blocos colaveis do curso usam <cole o material>,
# <ate 10 linhas> e afins, onde o < e literal e nao markup.
TAGS_HTML = {
    "a", "b", "i", "em", "strong", "span", "p", "div", "br", "ul", "ol", "li",
    "code", "pre", "small", "h1", "h2", "h3", "h4", "h5", "h6", "button",
    "figure", "figcaption", "svg", "details", "summary", "label", "input",
    "table", "tr", "td", "th", "section", "aside", "nav", "header", "footer",
    "textarea", "img", "meta", "link", "script", "style", "text", "mark",
}

def tags(s):
    return sorted(t.lower() for t in re.findall(r"</?([a-zA-Z][\w-]*)", s)
                  if t.lower() in TAGS_HTML)

def main():
    langs = sys.argv[1:] or ["en", "es"]
    fonte = json.load(open(os.path.join(ROOT, "i18n", "source.json"), encoding="utf-8"))
    for lang in langs:
        p = os.path.join(ROOT, "i18n", f"{lang}.json")
        if not os.path.exists(p):
            print(f"{lang}: sem dicionario"); continue
        d = json.load(open(p, encoding="utf-8"))
        espacos = rejeitadas = 0
        for k in list(d):
            if k not in fonte:
                continue
            novo = bordas(k, d[k])
            if novo != d[k]:
                d[k] = novo; espacos += 1
            if tags(k) != tags(d[k]):
                del d[k]; rejeitadas += 1
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=2); fh.write("\n")
        print(f"{lang}: {espacos} espacos de borda restaurados, "
              f"{rejeitadas} unidades rejeitadas por markup divergente "
              f"(rode i18n_translate.py {lang} para refazer), cache {len(d)}/{len(fonte)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())

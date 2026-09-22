#!/usr/bin/env python3
"""Extrai o texto traduzível do OSWork Quick para i18n/source.json.

Chaves = o próprio texto em português (igual às convenções do OSWork v2), o que dá
reaproveitamento de cache de graça entre execuções e entre cursos.

Cobre três superfícies:
  1. curso.html  — nós de texto, atributos que o aluno lê, e os cartões (JSON)
  2. landing.html — idem
  3. assets/curso.js — os literais de interface, por deslocamento (offset), para o
     build poder recortar com precisão em vez de fazer substituição cega.

Não traduz: identificadores, seletores, classes, nomes de arquivo, data-ex
(marcador de profissão), data-answer/data-k, e o nome do produto OSWork.
"""
import html
import json
import os
import re
import sys

from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# atributos cujo valor o aluno lê na tela
ATTRS = ("data-cap", "data-def", "data-fb", "aria-label", "title", "alt", "placeholder")
# nunca entram em tradução
PULAR_TAGS = {"script", "style"}

# literais de curso.js que NÃO são texto de interface (classe, seletor, CSS, flag)
JS_DENY = {
    "use strict", "side back", " done", "-45% 0px -45% 0px",
    "schema inválido",
}

# Rótulos de interface que são uma palavra minúscula só — o filtro genérico os
# confundiria com nome de classe ou de atributo. Cada âncora abaixo captura a
# ocorrência EXATA (grupo 1), o que resolve o caso de 'papel', que aparece duas
# vezes seguidas: a primeira é a chave do tema e não pode ser traduzida, a segunda
# é o rótulo que o aluno lê.
JS_ANCORAS = [
    r"\['dark',\s*'(escuro)'\]",
    r"\['papel',\s*'(papel)'\]",
    r"\['good',\s*'(bom)'\]",
    r"b\.textContent\s*=\s*'(copiar)'",
    r"st\.textContent\s*=\s*done\s*\?\s*'(feito)'",
    r"st\.textContent\s*=\s*done\s*\?\s*'feito'\s*:\s*'(pendente)'",
    r"rs\.textContent\s*=\s*'(resetar)'",
]


def texto_util(s):
    """Sobra alguma palavra depois de tirar tags e entidades?"""
    t = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return len(re.findall(r"[A-Za-zÀ-ÿ]{2,}", t)) > 0


def add(bag, kind, valor):
    valor = valor.strip("\n")
    if not valor.strip():
        return
    if valor in bag:
        return
    bag[valor] = {"kind": kind}


def do_html(caminho, bag):
    soup = BeautifulSoup(open(caminho, encoding="utf-8").read(), "html.parser")
    for el in soup.find_all(string=True):
        if isinstance(el, Comment):
            continue
        pai = el.parent.name if el.parent else ""
        if pai in PULAR_TAGS:
            continue
        if not el.strip():
            continue
        add(bag, "texto", str(el))
    for el in soup.find_all(True):
        for a in ATTRS:
            v = el.get(a)
            if v and texto_util(v):
                add(bag, "atributo", v)
        if el.name == "meta" and el.get("name") == "description":
            add(bag, "atributo", el.get("content", ""))
    # cartões: JSON dentro de <script type="application/json">
    for el in soup.find_all("script", {"type": "application/json"}):
        try:
            cards = json.loads(el.string or "[]")
        except Exception:
            continue
        for c in cards:
            add(bag, "cartao", c.get("front", ""))
            add(bag, "cartao", c.get("back", ""))
    return bag


def js_literais(src):
    """Cada literal de string do curso.js, com deslocamento, na ordem do arquivo."""
    pat = re.compile(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"")
    for m in pat.finditer(src):
        bruto = m.group(1) if m.group(1) is not None else m.group(2)
        yield m.start() + 1, m.end() - 1, bruto


def do_js(caminho, bag):
    src = open(caminho, encoding="utf-8").read()
    achados = []
    # posições que entram mesmo sendo palavra minúscula só
    forcar = set()
    for anc in JS_ANCORAS:
        m = re.search(anc, src)
        if not m:
            print(f"  aviso: âncora sem correspondência em curso.js: {anc}")
            continue
        forcar.add(m.start(1))
    for ini, fim, v in js_literais(src):
        if not v.strip() or v in JS_DENY:
            continue
        if ini not in forcar and re.match(r'^["\]\[.#]|^--|^[a-z-]+$', v):
            continue   # seletor, variável CSS, token — a menos que seja âncora
        if not texto_util(v):
            continue
        achados.append({"inicio": ini, "fim": fim, "valor": v})
        add(bag, "interface", v)
    return achados


# Rótulos que o CSS gera com content: — superfície invisível ao HTML e ao JS, mas
# que o aluno lê na tela. Sem isto, "PROMESSA" e "seguro" ficam em português em
# todos os idiomas, e nenhum portão de HTML acusa.
CSS_TEXTOS = {
    ".promise::before": "PROMESSA",
    ".psafe::before": "✓ seguro — ",
}


def main():
    bag = {}
    for v in CSS_TEXTOS.values():
        add(bag, "css", v)
    for f in ("curso.html", "landing.html"):
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            do_html(p, bag)
    js = do_js(os.path.join(ROOT, "assets", "curso.js"), bag)

    os.makedirs(os.path.join(ROOT, "i18n"), exist_ok=True)
    src = {k: v["kind"] for k, v in bag.items()}
    with open(os.path.join(ROOT, "i18n", "source.json"), "w", encoding="utf-8") as fh:
        json.dump(src, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(os.path.join(ROOT, "i18n", "js-offsets.json"), "w", encoding="utf-8") as fh:
        json.dump(js, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    por_tipo = {}
    for k in src.values():
        por_tipo[k] = por_tipo.get(k, 0) + 1
    palavras = sum(len(re.findall(r"[A-Za-zÀ-ÿ0-9]+", html.unescape(re.sub(r"<[^>]+>", " ", k))))
                   for k in src)
    print(f"i18n/source.json: {len(src)} unidades, ~{palavras} palavras")
    for k, v in sorted(por_tipo.items()):
        print(f"  {k}: {v}")
    print(f"i18n/js-offsets.json: {len(js)} literais de interface")
    return 0


if __name__ == "__main__":
    sys.exit(main())

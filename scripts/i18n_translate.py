#!/usr/bin/env python3
"""Traduz i18n/source.json para en/es, com cache. Nunca roda no acesso do aluno.

Rota: OpenRouter + gpt-5.4-nano (a Groq devolveu 403/1010 em 21/09; ver LIMITES.md).

A chave vem do ambiente em tempo de execução (~/projetos/openpcbotv2/.env ou
~/projetos/wifi/.env) e nunca é impressa. O cache em i18n/<lang>.json é a fonte do
build: uma unidade já traduzida nunca é reenviada.

Uso:  python3 scripts/i18n_translate.py en es
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOMES = {"en": "English (United States)", "es": "Spanish (Latin America)"}
MODELO = "openai/gpt-5.4-nano"  # escolhido no piloto trilingue do WiFi (19/09)
URL = "https://openrouter.ai/api/v1/chat/completions"

GLOSSARIO = {
    "en": {
        "pedido completo": "complete request", "critério de pronto": "definition of done",
        "régua de conferência": "checking ruler", "ficha de orientação": "orientation sheet",
        "molde": "template", "cópia datada": "dated copy", "gestora": "manager",
        "professor": "teacher", "trilha": "track", "aula": "lesson",
        "pratique agora": "practice now", "teste-se": "test yourself",
        "grifar": "highlight", "cartão": "card", "jornada": "journey",
    },
    "es": {
        "pedido completo": "pedido completo", "critério de pronto": "criterio de terminado",
        "régua de conferência": "regla de verificación", "ficha de orientação": "ficha de orientación",
        "molde": "plantilla", "cópia datada": "copia fechada", "gestora": "gestora",
        "professor": "profesor", "trilha": "ruta", "aula": "lección",
        "pratique agora": "practica ahora", "teste-se": "ponte a prueba",
        "grifar": "resaltar", "cartão": "tarjeta", "jornada": "trayecto",
    },
}


def chave():
    for p in ("~/projetos/openpcbotv2/.env", "~/projetos/wifi/.env"):
        f = os.path.expanduser(p)
        if not os.path.exists(f):
            continue
        for linha in open(f, encoding="utf-8"):
            m = re.match(r"\s*OPENROUTER_API_KEY\s*=\s*(.+)", linha)
            if m:
                return m.group(1).strip().strip("'\"")
    raise SystemExit("OPENROUTER_API_KEY não encontrada nos dois .env conhecidos.")


def limite(detalhe):
    p = os.path.expanduser("~/projetos/wifi/LIMITES.md")
    linha = (f"| 2026-09-21 | Traduzir OSWork Quick (EN/ES) via OpenRouter | {detalhe} "
             f"| Retentativa com espera; cache preservado | Respeitar limites da conta | aceito |\n")
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(linha)


SYS = """You are a careful professional educational translator. Translate ALL provided Brazilian Portuguese content into {nome}.

HARD RULES:
- Return a JSON object mapping each exact input ID to its translated string. No other keys.
- Never summarize, omit, add content, or change technical facts, numbers, times or dates.
- Preserve EVERY HTML tag, attribute, id, class name and HTML entity exactly as given. Translate only the human-readable text between tags and inside quoted UI labels. A string like '<p class="lbl">Tempo</p>' must come back as '<p class="lbl">Time</p>' — the markup is untouched.
- Preserve leading and trailing spaces exactly. Several strings are sentence fragments joined at runtime (e.g. ' seções · abrir →'); keeping the spaces is required or the interface breaks.
- Preserve the characters · — ✓ ↓ ← → ~ and any emoji-free typography exactly.
- OSWork is a product name: never translate it. INEMA.CLUB and INEMA.PRO are brand names: never translate them.
- Keep file names, folder names, paths, URLs and identifiers unchanged.
- This is a course for people over 40 who have never programmed. Use plain, warm, adult language. Never infantilize, never hype, never mention age as a limitation. Keep sentences short and in active voice, addressing the reader directly.
- The course deliberately avoids platform jargon. Do NOT introduce the words: terminal, install, script, server, repository, commit, branch, Git, JSON, pipeline, config file, API, deploy, CLI, directory, plugin, encoding. Use everyday words (say "folder", never "directory").

GLOSSARY (use these renderings consistently):
{glossario}
"""


def traduz(lang, chave_api):
    fonte = json.load(open(os.path.join(ROOT, "i18n", "source.json"), encoding="utf-8"))
    destino = os.path.join(ROOT, "i18n", f"{lang}.json")
    cache = json.load(open(destino, encoding="utf-8")) if os.path.exists(destino) else {}

    faltando = [k for k in fonte if k not in cache]
    if not faltando:
        print(f"{lang}: nada a traduzir, {len(cache)} em cache")
        return

    lotes, lote, tam = [], {}, 0
    for i, k in enumerate(faltando):
        lote[str(i)] = k
        tam += len(k)
        if tam > 2600:
            lotes.append(lote)
            lote, tam = {}, 0
    if lote:
        lotes.append(lote)

    gl = "\n".join(f"  {a} -> {b}" for a, b in GLOSSARIO[lang].items())
    sistema = SYS.format(nome=NOMES[lang], glossario=gl)
    total_in = total_out = 0

    for idx, lote in enumerate(lotes, 1):
        corpo = {
            "model": MODELO, "temperature": 0.15, "max_completion_tokens": 8000,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": sistema},
                         {"role": "user", "content": json.dumps(lote, ensure_ascii=False)}],
        }
        for tentativa in range(6):
            req = urllib.request.Request(
                URL, data=json.dumps(corpo).encode(),
                headers={"Authorization": f"Bearer {chave_api}",
                         "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    res = json.loads(r.read())
            except urllib.error.HTTPError as e:
                detalhe = f"HTTP {e.code} no lote {idx}/{len(lotes)} ({lang})"
                if e.code in (429, 500, 502, 503):
                    espera = 12 * (tentativa + 1)
                    print(f"  {detalhe}; esperando {espera}s", flush=True)
                    if tentativa == 5:
                        limite(detalhe)
                        raise SystemExit(f"{detalhe}: cache preservado com {len(cache)} unidades.")
                    time.sleep(espera)
                    continue
                limite(detalhe)
                raise
            saida = json.loads(res["choices"][0]["message"]["content"])
            traduzido = {lote[i]: v for i, v in saida.items() if i in lote and isinstance(v, str)}
            if len(traduzido) != len(lote):
                if tentativa == 5:
                    raise SystemExit(f"lote {idx} incompleto após 6 tentativas; cache preservado.")
                continue
            cache.update(traduzido)
            with open(destino, "w", encoding="utf-8") as fh:
                json.dump(cache, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            u = res.get("usage", {})
            total_in += u.get("prompt_tokens", 0)
            total_out += u.get("completion_tokens", 0)
            print(f"  {lang} lote {idx}/{len(lotes)} · cache {len(cache)}/{len(fonte)}", flush=True)
            break

    print(f"{lang}: pronto. tokens entrada {total_in}, saída {total_out}")


def main():
    langs = sys.argv[1:] or ["en", "es"]
    k = chave()
    for l in langs:
        traduz(l, k)
    return 0


if __name__ == "__main__":
    sys.exit(main())

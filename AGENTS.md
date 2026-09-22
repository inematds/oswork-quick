# OSWork Quick — edição direta e visual

Versão curta do OSWork para profissionais 40+. **Mesmos assuntos da edição longa, menos
texto.** Repositório independente: a edição longa vive em `../oswork-v5`, a edição técnica
em `../oswork`. Nenhum dos três compartilha código ou estado.

- **Conta e autoria:** `inematds <inematds@gmail.com>`, author e committer.
- **Base:** formato `formato-curso-v5` com **uma divergência declarada** (abaixo).
  Motor `assets/curso.js` + `assets/aula.css`, herdados sem alteração.
- **Desenhos:** SVG inline, feitos com Fable. Zero raster no corpo da aula.

## A divergência

O contrato `formato-curso-v5` exige **≥60% de prosa por seção**. O Quick rompe essa regra
de propósito: aqui a figura ensina e o texto amarra. Em troca, cada step carrega **duas**
peças visuais (diagrama no trilho + figura inline `.colfig` na coluna) e o texto tem teto
de **820 palavras por aula**. Todos os demais portões do v5 continuam valendo e são
conferidos mecanicamente por `scripts/validate.py`.

## Estrutura

- `curso.html` — **artefato montado**. Não edite as aulas aqui.
- `aulas/aula-N.html` — fragmento fonte de cada uma das 7 aulas. É onde se edita.
- `context/spec-quick.md` — o que o Quick é e como cortar sem perder tópico.
- `scripts/build.py` — remonta `curso.html` e **sincroniza o tempo do card da trilha com o
  `data-tempo` da própria aula** (fonte única). Idempotente.
- `scripts/validate.py` — o portão. Além das regras do v5, cobra o teto de 820 palavras e
  a figura inline `.colfig` com `<figcaption>` em 100% dos steps.
- `scripts/browser-test.cjs` — 16 grupos em `file://`, incluindo AAA nos 3 temas.

## Fluxo

```bash
python3 scripts/build.py
python3 scripts/validate.py
node scripts/browser-test.cjs
```

Editar uma aula = editar `aulas/aula-N.html`, remontar, revalidar. `build.py` sobrescreve
o que estiver montado em `curso.html`.

## Regras que o portão cobra

- Jargão-sentinela zero no texto do aluno: terminal, instalar, script, servidor,
  repositório, commit, branch, Git, JSON, pipeline, "arquivo de configuração", API,
  deploy, CLI, diretório, plugin, encoding. Use *pasta*, nunca *diretório*.
- `<p data-ex="gestora|professor">` em 100% dos steps — e só essas duas profissões.
- `.colfig` com `<figcaption>` que ensina em 100% dos steps; `.fig` do trilho com
  `data-cap`. `.herofig` é metáfora do mundo real; trilho e coluna são diagrama de
  mecanismo. Nunca trocados.
- Cartões nunca repetem ≥6 palavras seguidas do `.recap-autor` (frente e verso).
- Manifesto de completude por aula, 13 linhas, zero `[AUSENTE]`. `teste-se-FUND` reflete a
  **obrigação**: `[OK]` só em FUNDAMENTO, `[N/A]` nas demais.
- Zero emoji, zero exclamação dupla, zero gamificação.

## Publicação

Por git, GitHub Pages na raiz de `main`. Não usar Vercel.

## Idiomas (EN e ES)

PT na raiz, inglês em `en/`, espanhol em `es/`. Progresso e cartões são **isolados por
idioma** (`<meta name="curso">` vira `osworkq-en` / `osworkq-es`): os cartões guardam o
texto no estado do aluno, então compartilhar o progresso misturaria idiomas na revisão.

```bash
python3 scripts/i18n_extract.py      # PT -> i18n/source.json (+ js-offsets.json)
python3 scripts/i18n_translate.py    # traduz o que falta; cache em i18n/<lang>.json
python3 scripts/i18n_repair.py       # conserta espaço de borda e markup inventado
python3 scripts/build_locales.py     # monta en/ e es/. OFFLINE, não chama API
python3 scripts/validate-locales.py  # portão: paridade com o PT + jargão traduzido
node scripts/browser-locales.cjs     # navegador nos dois idiomas
```

Rota de tradução: **OpenRouter + `gpt-5.4-nano`** (a `GROQ_API_KEY` devolveu 403 em
21/09 — ver `~/projetos/wifi/LIMITES.md`). Chave lida em runtime dos `.env`, nunca
copiada para o repo. Unidade sem tradução **interrompe o build**.

### Quatro superfícies, não uma

Traduzir só o HTML deixa o curso meio em português, sem erro nenhum aparecer:

1. **HTML** — texto, atributos lidos pelo aluno, e os cartões em JSON.
2. **`assets/curso.js`** — os rótulos do motor, recortados por **deslocamento**. Cada
   idioma tem a sua cópia em `<lang>/assets/curso.js`; essa é a única que **não** sobe
   para `../assets/`, senão a página traduzida carrega o motor em português.
3. **CSS `content:`** — `PROMESSA` e `✓ seguro — ` são gerados pelo CSS. Vão para
   `<lang>/assets/i18n.css`, carregado depois do `aula.css` compartilhado.
4. **Texto dentro dos SVG** — os rótulos dos desenhos são nós de texto e entram no (1).

O que **não** se traduz: `data-ex` (marcador de profissão), `data-answer`/`data-k`,
`data-tempo`, nomes de classe, ids, e o nome OSWork.

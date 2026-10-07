# OSWork Quick — na prática (v2.0.0)

Atalho do OSWork, comando por comando: terminal do Windows (cmd) → pasta `projetos\meu-site`
→ ver a mesma pasta no Explorador → Claude Code ou Codex trabalhando nela → Git, gh e chave
SSH → repositório público/privado e GitHub Pages → a mesma navegação numa VPS → visão de
Vercel e Supabase. Quatro trilhas de um módulo cada, 25 passos.

- **Conta e autoria:** `inematds <inematds@gmail.com>`, author e committer.
- **Formato:** `formato-curso-v2` (camada de aprendizagem: progresso, dúvida, notas, jornada,
  temas, manifesto em toda página). Motor `assets/learn.*` + `assets/site.*` herdado do
  OSWork v2 (`../oswork`) sem alteração; desenhos SVG em `scripts/figures.py`, também herdados.
- **A edição anterior** (organização com IA sem terminal, formato v5, sete aulas e vídeos)
  está na tag `v1-sem-terminal`. Os vídeos dela continuam em `videos/` e na release v1.1.0.

## Fonte única

- `conteudo/pt.json` — conteúdo autoral: textos da interface, início, trilhas, módulos,
  tópicos (`cmd`, `see`, `what`, `why`, `keys`, `fix`), laboratório, figuras e fontes.
- `conteudo/en.json`, `conteudo/es.json` — traduções revisáveis do mesmo JSON. **Os campos
  `cmd` de EN/ES são gerados no build a partir do PT** (`localize_cmd` em `build.py`): só os
  nomes de exemplo mudam (`projetos`, `meu-site`, `SeuNome`, `SEU-USUARIO`, `IP-DA-VPS`…).
  Nunca edite um comando só num idioma.
- HTML em `index.html`, `curso/`, `materiais/` (e `en/`, `es/`) é **gerado**. Não edite à mão.

## Fluxo

```bash
python3 scripts/build.py      # gera PT, EN e ES (30 páginas) + cola .txt + FONTES.md
python3 scripts/validate.py   # portão: meta, manifesto, links, âncoras, SVG, comandos iguais entre idiomas, sem sobras de PT
python3 -m http.server 8080   # e em outro terminal:
BASE_URL=http://localhost:8080 node scripts/browser-test.cjs
```

Mudou texto em PT? Atualize o mesmo campo em `en.json` e `es.json` (tradução pelo Codex na
assinatura, por módulo, nunca o arquivo inteiro de uma vez; sem API paga) e rode os três
comandos. `assets-src/` guarda `learn.js`/`site.js` originais: o build gera `assets/*.js`
de cada idioma a partir deles, com os textos de `i18n-v2/` (offsets em `js-strings.json`).

## Regras de conteúdo

- Comando primeiro, depois "Você vê", "O que é", "Por que aprender", "Conceitos-chave" e
  "Deu erro?". Todo termo novo definido na primeira vez (cmd, winget, chave pública, repositório…).
- Comandos só de fonte oficial e com data: ver `FONTES.md`. Nenhum comando foi executado num
  Windows real por este repo; quem testar e achar diferença, corrija o `pt.json` e registre em `FALHAS.md`.
- `scripts/browser-locales.cjs` e `scripts/i18n_translate.py` são da edição anterior (tinham
  mudanças locais não commitadas em 07/10/2026); não fazem parte do build novo.

## Publicação

Por git, GitHub Pages na raiz de `main`. Não usar Vercel.

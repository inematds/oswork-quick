# OSWork Quick — na prática

Do terminal à sua página no ar, comando por comando. Quatro partes, 25 passos:

1. **Seu computador** — abrir o cmd, criar `projetos\meu-site`, ver a mesma pasta no
   Explorador (`explorer .`), navegar com 6 comandos, instalar Git/gh/Node pelo `winget` e
   pôr o Claude Code ou o Codex para trabalhar na pasta.
2. **GitHub** — `git config`, chave SSH (`ssh-keygen`), `gh auth login`, repositório público
   ou privado (`gh repo create`), GitHub Pages e a rotina `add` / `commit` / `push`.
3. **VPS** — entrar com `ssh`, a mesma navegação com outros nomes (`dir`→`ls`), `git clone`,
   agente no servidor e `git pull`.
4. **Visão** — Vercel (publica a cada push) e Supabase (banco e login), com as chaves fora do repositório.

- Português: https://inematds.github.io/oswork-quick/
- English: https://inematds.github.io/oswork-quick/en/
- Español: https://inematds.github.io/oswork-quick/es/
- Cola de comandos: `materiais/` (página e `.txt` por idioma).

Formato INEMA v2: marcar como lido, dúvidas, notas, "minha jornada" com exportação, temas e
ajustes de leitura. Funciona sem cadastro; o progresso fica no navegador.

Os comandos vêm das documentações oficiais conferidas em 07/10/2026 (ver `FONTES.md`).
Telas e versões mudam: se algo aparecer diferente, cada passo tem um "Deu erro?".

## Edição anterior

A primeira edição (organização com IA sem terminal, sete aulas, com vídeo do Nei) está na tag
[`v1-sem-terminal`](https://github.com/inematds/oswork-quick/tree/v1-sem-terminal). Vídeos:
https://inematds.github.io/oswork-quick/videos/

## Editar

Conteúdo em `conteudo/{pt,en,es}.json`; páginas geradas por `scripts/build.py`. Ver `AGENTS.md`.

## Mais no INEMA.CLUB

- Ficha do curso: https://www.inema.club/cursos/280-oswork-quick-do-terminal-a-sua-pagina-no-ar/
- Guia: como aprender inteligência artificial: https://www.inema.club/aprender-inteligencia-artificial/
- Todos os cursos: https://www.inema.club/cursos/

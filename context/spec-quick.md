# OSWork Quick — especificação

Versão direta e visual do OSWork v5. **Mesmos tópicos, menos texto.**
Repo independente. `<meta name="curso" content="osworkq">`.

## O que muda em relação ao v5 (`~/projetos/oswork-v5`)

| | v5 | Quick |
|---|---|---|
| aulas | 7 | 7 (as mesmas) |
| steps | 29 | 29 (os mesmos) |
| palavras/aula | ~1.400–1.650 | **≤820**, alvo ~640 |
| tempo/aula | 20–24 min | **9–12 min** |
| visual por step | 1 diagrama no trilho | **2**: diagrama no trilho + figura inline `.colfig` na coluna |
| prosa por seção | ≥60% | **relaxado de propósito** — a figura ensina, o texto amarra |

**Divergência declarada:** o contrato `formato-curso-v5` exige ≥60% de prosa por seção.
O Quick rompe essa regra deliberadamente, porque o pedido é "direto e visual, sem cortar
tópicos". Todos os demais portões do v5 continuam valendo e são conferidos por
`scripts/validate.py`: promessa verificável, tempo, exemplo por profissão em 100% dos
steps, prática com `.psafe` e tempo, `.recap-autor`, `.next-action`, cartões com
anti-duplicação, manifesto de completude de 13 linhas, densidade de quadros, jargão
-sentinela zero, AAA nos 3 temas.

## O que NÃO muda

- Público: profissionais 40+ iniciantes. Profissões: **gestora** e **professor**, só essas.
- As 7 promessas, os ganchos encadeados e as cenas de exemplo são as do v5 — não reinvente,
  condense. As cenas já passaram por auditoria anti-clone.
- Jargão proibido: terminal, instalar, script, servidor, repositório, commit, branch, Git,
  JSON, pipeline, "arquivo de configuração", API, deploy, CLI, diretório, plugin, encoding.
- Zero emoji, zero exclamação dupla, zero gamificação.
- Registros visuais: `.herofig` = metáfora do mundo real; `.fig` do trilho e `.colfig` da
  coluna = diagrama de mecanismo. Nunca trocados. Proibido robô humanoide, cérebro-circuito,
  chuva de código, aperto de mão com robô.

## Como cortar o texto sem perder tópico

1. Todo step mantém a ideia, o exemplo por profissão e o quadro funcional que tinha.
2. O que sai: a repetição, o parágrafo de reforço, a frase de transição, o adjetivo.
3. O que entra no lugar: a figura inline `.colfig`, com `<figcaption>` que ensina — diz o
   que olhar e o que aquilo significa, nunca um título decorativo.
4. O exemplo por profissão pode encolher para 1–2 frases, mas continua nomeado e concreto.

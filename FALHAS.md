# Falhas — OSWork Quick

Uma linha por falha real: data, o que quebrou, a menor correção, e se era PROMPT ou INFRA.
Mais recente no topo.

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 2026-09-21 | manifestos de completude citavam um `data-tempo` antigo depois que o tempo da aula mudou (aulas 3, 6 e 7) — o manifesto mentia e nada acusava | o portão passou a comparar o tempo citado no manifesto com o real | prompt |
| 2026-09-21 | copiei o `validate.py` do Quick por cima do v5; as regras exclusivas do Quick (teto de palavras, `.colfig`) reprovaram o v5 com 36 falhas | reverter pelo git e portar só a checagem nova | prompt |
| 2026-09-21 | teto de palavras fixo por aula reprovava a Aula 7 por ela ter 5 steps, não por ser prolixa | teto por step (205/step) em vez de por aula | prompt |
| 2026-09-21 | traços das figuras invisíveis nos temas papel e sépia: fundo da caixa é escuro nos 3 temas, mas `currentColor` seguia `--ink` (contraste medido 1,10 e 1,36) | token `--figink` claro em `.figstage`, `.colfig` e `.mobfig` | infra |
| 2026-09-21 | limite de uso do Fable estourou no meio da geração; 6 de 7 subagentes caíram com HTTP 429 | os 65 desenhos já estavam entregues; o aperto final de texto foi feito no Opus | infra |

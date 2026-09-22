# Falhas — OSWork Quick

Uma linha por falha real: data, o que quebrou, a menor correção, e se era PROMPT ou INFRA.
Mais recente no topo.

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 2026-09-22 | seletor de idioma só existia em `en/` e `es/`: quem chegava pela página em português — a que o portal linka — não tinha caminho para os outros idiomas | build insere o seletor no PT também, e o portão passou a cobrar isso nas 6 páginas | prompt |
| 2026-09-22 | ao ganhar seletor, o PT passou a exportá-lo para EN/ES com caminhos da raiz (`en/curso.html` de dentro de `en/`) | o build remove qualquer seletor herdado antes de inserir o do idioma | prompt |
| 2026-09-22 | trocar de idioma perdia a aula aberta e voltava para a trilha | script inline que acrescenta `location.hash` ao destino | prompt |
| 2026-09-22 | nomes de idioma ("English", "Español") entraram na tradução e virariam "Portuguese/Spanish" em inglês | conjunto NAO_TRADUZ compartilhado pelo extrator e pelo build | prompt |
| 2026-09-21 | páginas EN/ES carregavam `../assets/curso.js` — o motor em PORTUGUÊS — porque o build mandava todo `assets/` subir um nível; a interface voltava ao PT sem nenhum erro aparecer | manter `assets/curso.js` local em cada idioma; só CSS e capa sobem | prompt |
| 2026-09-21 | rótulos gerados por `content:` no CSS (PROMESSA, "seguro") ficavam em português nos três idiomas; nenhum portão de HTML os alcança | extrator cobre os rótulos do CSS e o build emite `<lang>/assets/i18n.css` | prompt |
| 2026-09-21 | rótulos de interface de uma palavra minúscula (escuro, papel, bom, copiar, feito, pendente, resetar) eram descartados pelo extrator como nome de classe | âncoras por deslocamento que capturam a ocorrência exata — resolve inclusive `['papel','papel']`, onde só o segundo é rótulo | prompt |
| 2026-09-21 | 16 unidades EN e 19 ES perderam o espaço de borda; fragmentos concatenados em runtime renderizariam "12read" | `i18n_repair.py` restaura o espaço exato da fonte antes do build | prompt |
| 2026-09-21 | "roteiro de laboratório" traduzido como "lab script" — `script` está na lista de jargão que o curso promete não usar | corrigido para "lab worksheet"; portão dos idiomas passou a varrer a lista-sentinela traduzida | prompt |
| 2026-09-21 | reparo rejeitava os blocos colável por "markup divergente": `<cole o material>` era contado como tag HTML | contar só nomes de tag conhecidos | prompt |
| 2026-09-21 | teste de navegador acusava o ES de estar em português porque "revisar" e "tema" coincidem nas duas línguas | asserção positiva por idioma em vez de lista de palavras proibidas | prompt |
| 2026-09-21 | portão dos idiomas lia o manifesto de completude como se fosse cartão: o comentário contém literalmente `<script id="cards-1">` | contar cartões com os comentários removidos | prompt |
| 2026-09-21 | manifestos de completude citavam um `data-tempo` antigo depois que o tempo da aula mudou (aulas 3, 6 e 7) — o manifesto mentia e nada acusava | o portão passou a comparar o tempo citado no manifesto com o real | prompt |
| 2026-09-21 | copiei o `validate.py` do Quick por cima do v5; as regras exclusivas do Quick (teto de palavras, `.colfig`) reprovaram o v5 com 36 falhas | reverter pelo git e portar só a checagem nova | prompt |
| 2026-09-21 | teto de palavras fixo por aula reprovava a Aula 7 por ela ter 5 steps, não por ser prolixa | teto por step (205/step) em vez de por aula | prompt |
| 2026-09-21 | traços das figuras invisíveis nos temas papel e sépia: fundo da caixa é escuro nos 3 temas, mas `currentColor` seguia `--ink` (contraste medido 1,10 e 1,36) | token `--figink` claro em `.figstage`, `.colfig` e `.mobfig` | infra |
| 2026-09-21 | limite de uso do Fable estourou no meio da geração; 6 de 7 subagentes caíram com HTTP 429 | os 65 desenhos já estavam entregues; o aperto final de texto foi feito no Opus | infra |

| 2026-09-22 | Junção dos vídeos iniciou antes de existir o estado da primeira renderização | Aguardar production.json antes de consultar blocos; serviço reiniciado | infra |

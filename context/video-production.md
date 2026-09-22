# OSWork Quick em vídeo — 22/09/2026

Pedido: produzir no mesmo estilo aprovado do Astra Básico. Mantidos avatar/voz do Nei, assinatura HeyGen, 1080p, diagramas e legendas. Escopo adotado: PT/ES/EN, sete aulas em um filme por idioma.

Fonte: curso.html e versões en/es. Extração em video-production/extract_course.py; artefatos em /home/nmaldaner/projetos/output/oswork-quick. 50 cenas por idioma, 21 blocos de voz <=4400 caracteres. Corrigidas no roteiro (não nas aulas) as alegações absolutas sobre memória/contexto e o trecho que poderia soar como garantia de privacidade.

Verificações: os 21 projetos de prévia passaram no HyperFrames check. Contact sheet do primeiro bloco PT inspecionada. Prévia sem voz não é vídeo final; o avatar entra quando os arquivos HeyGen chegarem.

Serviços systemd de usuário: oswork-quick-submit-blocks; oswork-quick-monitor-blocks; oswork-quick-produce-blocks; oswork-quick-assemble-languages; oswork-quick-publish-finished.

Estado canônico: output/oswork-quick/blocos/manifest.json; verification/blocos-downloads.json; verification/production.json; verification/publication.json; verification/telegram-final.json. Nunca reenviar bloco com ID confirmado.

Fluxo persistente: geração pela sessão autenticada do promoavatar3; download; transcrição Groq com tempos reais; alinhamento; verificação; render; junção dos sete blocos por idioma; publicação MP4/SRT em release v1.1.0, página videos/ e links no botv3. Publicação depende de todos os 21 blocos renderizados, alinhamento >0.90 e decodificação integral sem erros.

Alterações anteriores do usuário em scripts/browser-locales.cjs e scripts/i18n_translate.py foram preservadas e não entram nos commits da produção de vídeo.

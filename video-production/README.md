# Produção dos vídeos

Reutiliza o fluxo aprovado do Astra Básico: Nei no HeyGen, ilustrações do curso, transcrição medida, composição HyperFrames e verificação antes da entrega.

- `extract_course.py`: adapta os três cursos para roteiros e blocos de voz.
- `build_scene_templates.py`: preserva o estilo de animação aprovado.
- `build_final_block.py`: sincroniza diagramas e legendas com a fala real.
- `produce_blocks.py`: verifica e renderiza os blocos disponíveis.
- `assemble_languages.py`: junta os blocos e desloca os tempos das legendas.
- `wait_publication.py`: só publica depois das verificações; envia os links ao bot v3.

Os caminhos locais correspondem ao ambiente de produção INEMA. Nenhuma chave é armazenada aqui. Áudios, vídeos, transcrições e manifestos ficam em `~/projetos/output/oswork-quick`.

Não execute novamente a extração durante uma geração: os IDs confirmados ficam no manifesto de produção. Consulte `context/video-production.md` antes de retomar.

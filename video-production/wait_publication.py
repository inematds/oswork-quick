"""Wait for all verified assemblies, publish, then deliver the links to bot v3."""
import time,json,subprocess
from pathlib import Path
from publish_finished import publish,ROOT,REPO
for attempt in range(720):
 if all((ROOT/f'verification/assembled-{lang}.json').exists() for lang in ['pt','es','en']):
  blocks=json.loads((ROOT/'blocos/manifest.json').read_text())
  for b in blocks:
   key=f"{b['language']}-b{b['part']:02d}"
   alignment=json.loads((ROOT/'final'/key/'alignment.json').read_text())
   assert alignment['ratio']>.90, 'Needs speech review: '+key
   assert 'Check passed' in (ROOT/f'verification/check-final-{key}.log').read_text()
  publish()
  subprocess.run(['node','video-production/send_final_v3.mjs'],cwd=REPO,check=True)
  (ROOT/'STATUS.md').write_text('# OSWork Quick — concluído\n\nTrês vídeos completos, MP4 e SRT, publicados na release v1.1.0. Guia atualizado por git e links enviados ao bot v3.\nhttps://inematds.github.io/oswork-quick/videos/\nhttps://github.com/inematds/oswork-quick/releases/tag/v1.1.0\n')
  break
 time.sleep(60)

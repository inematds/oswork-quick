"""Publish verified OSWork Quick films without changing the course's lesson sources."""
from pathlib import Path
import json,subprocess,urllib.request,time,html
ROOT=Path('/home/nmaldaner/projetos/output/oswork-quick');REPO=Path(__file__).resolve().parents[1]
def run(args,**kw):return subprocess.run(args,cwd=REPO,check=True,**kw)
def publish():
 receipts={l:json.loads((ROOT/f'verification/assembled-{l}.json').read_text()) for l in ['pt','es','en']}
 production=json.loads((ROOT/'verification/production.json').read_text());assert len(production)==21 and all(s['status']=='rendered' for s in production.values())
 for l,r in receipts.items():
  assert Path(r['file']).stat().st_size==r['bytes'] and r['duration']>1200 and len(r['chapters'])==50
  assert (ROOT/f'verification/decode-full-{l}.log').read_text()==''
 tag='v1.1.0';repo='inematds/oswork-quick';notes=ROOT/'final/RELEASE.md'
 notes.write_text('OSWork Quick em vídeo: as sete aulas em português, espanhol e inglês. Avatar e voz do Nei, 50 cenas ilustradas por idioma e legendas SRT.\n\n'+ '\n'.join(f"- {l.upper()}: {int(r['duration']//60)}min{int(r['duration']%60):02d}s" for l,r in receipts.items()))
 existing=subprocess.run(['gh','release','view',tag,'--repo',repo],cwd=REPO,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 if existing.returncode:run(['gh','release','create',tag,'--repo',repo,'--draft','--title','OSWork Quick — vídeos completos PT, ES e EN','--notes-file',str(notes)])
 assets=[str(ROOT/f'final/oswork-quick-{l}.{ext}') for l in receipts for ext in ['mp4','srt']]
 run(['gh','release','upload',tag,'--repo',repo,'--clobber',*assets])
 videos={l:{'url':f'https://github.com/{repo}/releases/download/{tag}/oswork-quick-{l}.mp4','srt':f'https://github.com/{repo}/releases/download/{tag}/oswork-quick-{l}.srt','duration':r['duration']} for l,r in receipts.items()}
 folder=REPO/'videos';folder.mkdir(exist_ok=True)
 (folder/'delivery.json').write_text(json.dumps(videos,indent=2)+'\n')
 names={'pt':('Português','As sete aulas com Nei','Curso completo','Baixar vídeo','Legendas SRT'),'es':('Español','Las siete lecciones con Nei','Curso completo','Descargar video','Subtítulos SRT'),'en':('English','All seven lessons with Nei','Full course','Download video','SRT subtitles')}
 for l,item in videos.items():
  labels=names[l];filename='index.html' if l=='pt' else l+'.html';course='../'+('' if l=='pt' else l+'/')+'curso.html'
  nav=' · '.join(f'<a href="{"index.html" if k=="pt" else k+".html"}" lang="{k}">{v[0]}</a>' for k,v in names.items())
  duration=f"{int(item['duration']//60)}:{int(item['duration']%60):02d}"
  page=f'''<!doctype html><html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OSWork Quick — {labels[1]}</title><style>:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:#171b20;color:#f7f1e7;font:18px/1.6 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:32px 24px}}a{{color:#efbe69}}nav{{display:flex;gap:16px;flex-wrap:wrap}}h1{{font-size:clamp(30px,4vw,52px);line-height:1.15}}video{{display:block;width:100%;aspect-ratio:16/9;background:#101419;border-radius:14px}}.meta{{color:#c5cbd0}}:focus-visible{{outline:3px solid #efbe69;outline-offset:4px}}</style></head><body><main><nav><a href="https://inema.club">INEMA.CLUB</a><a href="{course}">{labels[2]}</a><span>{nav}</span></nav><p class="meta">OSWORK QUICK · {labels[0]} · 1080p · {duration}</p><h1>{labels[1]}</h1><video controls preload="metadata" aria-label="{labels[1]}"><source src="{item['url']}" type="video/mp4"></video><p><a href="{item['url']}">{labels[3]}</a> · <a href="{item['srt']}">{labels[4]}</a></p><p class="meta">Nei Maldaner · INEMA · v1.1.0</p></main></body></html>'''
  (folder/filename).write_text(page)
 (REPO/'VERSION').write_text('1.1.0\n');readme=REPO/'README.md';text=readme.read_text();marker='## Vídeos completos'
 if marker not in text:readme.write_text(text+'\n\n'+marker+'\n\n[Assistir em português, espanhol e inglês](https://inematds.github.io/oswork-quick/videos/). Avatar e voz do Nei, sete aulas, ilustrações e legendas.\n')
 run(['git','config','user.name','inematds']);run(['git','config','user.email','inematds@gmail.com'])
 run(['git','add','videos','VERSION','README.md'])
 if subprocess.run(['git','diff','--cached','--quiet'],cwd=REPO).returncode:run(['git','commit','-m','feat: publica vídeos ilustrados do OSWork Quick em três idiomas'])
 run(['git','push','origin','HEAD:main']);run(['gh','release','edit',tag,'--repo',repo,'--draft=false'])
 for item in videos.values():
  with urllib.request.urlopen(urllib.request.Request(item['url'],method='HEAD'),timeout=60) as response:assert response.status==200
 for attempt in range(20):
  try:
   with urllib.request.urlopen('https://inematds.github.io/oswork-quick/videos/',timeout=30) as f:page=f.read().decode()
   if videos['pt']['url'] in page:break
  except Exception:pass
  time.sleep(30)
 else:raise RuntimeError('Release and push complete; Pages still needs verification')
 (ROOT/'verification/publication.json').write_text(json.dumps({'release':f'https://github.com/{repo}/releases/tag/{tag}','videos':videos},indent=2))
if __name__=='__main__':publish()

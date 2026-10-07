#!/usr/bin/env python3
"""Portão do OSWork Quick (na prática), formato INEMA v2.

Confere nos três idiomas: meta e manifesto em toda página, manifesto batendo com os
tópicos reais, ids únicos, links e âncoras locais, ≥1 SVG por módulo, comando +
"você vê" + 3 seções + "deu erro?" em cada tópico, e comandos idênticos entre idiomas
(fora os nomes de exemplo, que cada idioma traduz).
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re
ROOT=Path(__file__).resolve().parents[1]
LANGS=('pt','en','es')
EXAMPLES={'en':[('projects','projetos'),('my-site','meu-site'),('YourName','SeuNome'),('YOUR-USER','SEU-USUARIO'),('VPS-IP','IP-DA-VPS'),('Your Name','Seu Nome'),('you@email.com','seu@email.com'),('yourdomain.com','seudominio.com.br'),('first version','primeira versão'),('what changed','o que mudou'),('new version','nova versão')],
 'es':[('proyectos','projetos'),('mi-sitio','meu-site'),('TuNombre','SeuNome'),('TU-USUARIO','SEU-USUARIO'),('IP-DE-LA-VPS','IP-DA-VPS'),('Tu Nombre','Seu Nome'),('tu@correo.com','seu@email.com'),('tudominio.com','seudominio.com.br'),('primera versión','primeira versão'),('qué cambió','o que mudou'),('nueva versión','nova versão')]}
class Parse(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.topics=[];self.scripts=[];self.cur=None;self.svg=0;self.meta={};self.lang=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.lang=a.get('lang')
  if 'id' in a:self.ids.append(a['id'])
  if tag in ('a','link','script','iframe'):
   v=a.get('href',a.get('src'))
   if v:self.links.append(v)
  if 'data-inema-topic' in a:self.topics.append(a['data-inema-topic'])
  if tag=='svg':self.svg+=1
  if tag=='meta':self.meta[a.get('name')]=a.get('content')
  if tag=='script' and 'data-inema-manifest' in a:self.cur=''
 def handle_data(self,s):
  if self.cur is not None:self.cur+=s
 def handle_endtag(self,tag):
  if tag=='script' and self.cur is not None:self.scripts.append(json.loads(self.cur));self.cur=None
def lang_of(path):
 first=path.relative_to(ROOT).parts[0];return first if first in ('en','es') else 'pt'
pages={}
for path in ROOT.rglob('*.html'):
 parts=path.relative_to(ROOT).parts
 if parts[0] in ('videos','capa','video-production','.verificacao') or (len(parts)>1 and parts[1]=='videos'):continue
 p=Parse();p.feed(path.read_text());pages[path]=p
errors=[]
for path,p in pages.items():
 lang=lang_of(path);cid='oswork-quick' if lang=='pt' else 'oswork-quick-'+lang
 if len(p.ids)!=len(set(p.ids)):errors.append(f'IDs duplicados: {path}')
 if p.meta.get('inema-course')!=cid:errors.append(f'Meta inema-course: {path}')
 if len(p.scripts)!=1:errors.append(f'Manifesto ausente: {path}')
 for link in p.links:
  u=urlsplit(link)
  if u.scheme or u.netloc:continue
  target=(path.parent/unquote(u.path)).resolve() if u.path else path
  if target.is_dir():target=target/'index.html'
  if not target.exists():errors.append(f'Link ausente: {path.relative_to(ROOT)}: {link}')
  elif u.fragment and target in pages and u.fragment not in pages[target].ids:errors.append(f'Âncora ausente: {path.relative_to(ROOT)}: {link}')
 if path.name.startswith('modulo-'):
  if len(p.topics)<6:errors.append(f'Menos de 6 tópicos: {path}')
  if not p.svg:errors.append(f'Diagrama ausente: {path}')
 for manifest in p.scripts:
  for track in manifest['tracks']:
   for module in track['modules']:
    target=(path.parent/module['href']).resolve()
    if target not in pages or len(pages[target].topics)!=module['topics']:errors.append(f'Manifesto divergente: {path.relative_to(ROOT)} -> {module["href"]}')
# Conteúdo: estrutura e comandos entre idiomas
data={l:json.loads((ROOT/f'conteudo/{l}.json').read_text()) for l in LANGS}
for l in ('en','es'):
 for i,(mp,ml) in enumerate(zip(data['pt']['modules'],data[l]['modules'])):
  if len(mp['topics'])!=len(ml['topics']) or len(mp['steps'])!=len(ml['steps']):errors.append(f'{l}: módulo {i+1} com contagem diferente')
  for j,(tp,tl) in enumerate(zip(mp['topics'],ml['topics']),1):
   for k in ('cmd','see','what','why','keys','fix','title'):
    if not tl.get(k):errors.append(f'{l}: {i+1}.{j} sem {k}')
   cmd=tl['cmd']
   for a,b in EXAMPLES[l]:cmd=cmd.replace(a,b)
   if cmd!=tp['cmd']:errors.append(f'{l}: comando diferente em {i+1}.{j}: {tl["cmd"]!r}')
   if l!='pt' and tl['what']==tp['what']:errors.append(f'{l}: {i+1}.{j} parece não traduzido')
  if set(mp.get('figures',{}))!=set(ml.get('figures',{})):errors.append(f'{l}: figuras divergentes no módulo {i+1}')
 for key in data['pt']['ui']:
  if key not in data[l]['ui']:errors.append(f'{l}: ui sem {key}')
# Sobras de português nas páginas EN/ES
PT=re.compile(r'\b(você|não|também|então|pasta pessoal|Marcar como lido|Próximo|meu-site|projetos|SeuNome|SEU-USUARIO|IP-DA-VPS|seu@email)\b',re.I)
for path,p in pages.items():
 if lang_of(path)!='pt':
  text=re.sub(r'<script[\s\S]*?</script>','',path.read_text())
  for hit in set(PT.findall(re.sub(r'<[^>]+>',' ',text))):errors.append(f'Sobra PT "{hit}" em {path.relative_to(ROOT)}')
assert not errors,'\n'.join(errors)
n=len(pages);topics=sum(len(p.topics) for p in pages.values() if p.topics and pages)
mods=sum(1 for x in pages if x.name.startswith('modulo-'))
assert n==30, f'Esperava 30 páginas (10 × 3 idiomas), achei {n}'
print(f'OK: {n} páginas, {mods} módulos, {sum(len(pages[x].topics) for x in pages if x.name.startswith("modulo-"))} tópicos nos três idiomas; meta, manifesto, links, âncoras, SVG, comandos iguais entre idiomas e sem sobras de PT.')

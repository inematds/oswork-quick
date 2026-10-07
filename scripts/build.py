#!/usr/bin/env python3
"""Gera o OSWork Quick (na prática) em PT, EN e ES a partir de conteudo/<lang>.json.

Formato INEMA v2: camada de aprendizagem (assets/learn.*), manifesto em toda página,
anti-FOUC, ids estáveis. Cada idioma é renderizado do seu próprio JSON; comandos,
nomes de arquivo e ids são idênticos nos três.
"""
import json,os,re,html,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from figures import diagram,figure
E=html.escape
BASE='https://inematds.github.io/oswork-quick/'
LANGS={'pt':('pt-BR','Português'),'en':('en','English'),'es':('es','Español')}
COLORS=['#34d399','#60a5fa','#c084fc','#fbbf24'];LIGHT=['#047857','#1d4ed8','#7e22ce','#92400e']
TIMES=[25,20,20,10]
# Nomes de exemplo dentro dos comandos, por idioma. O resto do comando é sempre o do PT.
EXAMPLES={'en':[('projetos','projects'),('meu-site','my-site'),('SeuNome','YourName'),('SEU-USUARIO','YOUR-USER'),('IP-DA-VPS','VPS-IP'),('Seu Nome','Your Name'),('seu@email.com','you@email.com'),('seudominio.com.br','yourdomain.com'),('primeira versão','first version'),('o que mudou','what changed'),('nova versão','new version')],
 'es':[('projetos','proyectos'),('meu-site','mi-sitio'),('SeuNome','TuNombre'),('SEU-USUARIO','TU-USUARIO'),('IP-DA-VPS','IP-DE-LA-VPS'),('Seu Nome','Tu Nombre'),('seu@email.com','tu@correo.com'),('seudominio.com.br','tudominio.com'),('primeira versão','primera versión'),('o que mudou','qué cambió'),('nova versão','nueva versión')]}
def localize_cmd(cmd,lang):
 for a,b in EXAMPLES.get(lang,[]):cmd=cmd.replace(a,b)
 return cmd
ANTI="""(function(){try{var p=JSON.parse(localStorage.getItem('inema.prefs')||'{}'),d=document.documentElement;d.classList.toggle('dark',p.theme?p.theme!=='claro':true);if(p.theme)d.dataset.theme=p.theme;if(p.fontScale)d.style.setProperty('--fs-root',p.fontScale+'%');if(p.font)d.dataset.font=p.font;if(p.accent)d.dataset.accent=p.accent;if(p.lineWidth)d.style.setProperty('--measure',p.lineWidth+'ch');if(p.leading)d.style.setProperty('--leading',p.leading)}catch(e){document.documentElement.classList.add('dark')}})();"""

def course_id(lang):return 'oswork-quick' if lang=='pt' else 'oswork-quick-'+lang
def outdir(lang):return ROOT if lang=='pt' else ROOT/lang

def build(lang):
 C=json.loads((ROOT/f'conteudo/{lang}.json').read_text());U=C['ui'];MODS=C['modules'];TR=C['tracks']
 if lang!='pt':
  PT=json.loads((ROOT/'conteudo/pt.json').read_text())
  for m,mp in zip(MODS,PT['modules']):
   for tp,tpp in zip(m['topics'],mp['topics']):tp['cmd']=localize_cmd(tpp['cmd'],lang)
 for i,m in enumerate(MODS):m.update(id=f'{i+1}-1',track=i+1,href=f'curso/trilha{i+1}/modulo-{i+1}-1.html',time=TIMES[i])
 total=sum(len(m['topics']) for m in MODS)
 manifest_base={'course':course_id(lang),'tracks':[{'n':str(t+1),'title':tr[0],'modules':[{'id':m['id'],'title':m['title'],'topics':len(m['topics']),'href':m['href']}]} for t,(tr,m) in enumerate(zip(TR,MODS))]}
 OUT=outdir(lang)

 def meter(scope):return f'<div class="meter" data-inema-meter="{scope}" role="progressbar" aria-label="{U["progress"]}" aria-valuemin="0" aria-valuemax="100"><span class="inema-meter-pct" data-inema-meter-pct>0%</span><span class="inema-meter-count" data-inema-meter-frac>0 {U["of"]} 0</span></div>'

 def page(title,body,rel,track=1):
  dest=OUT/rel;root=os.path.relpath(OUT,dest.parent).replace(os.sep,'/');root='' if root=='.' else root+'/'
  nav=''.join(f'<a href="{root}curso/trilha{i+1}/index.html" '+('aria-current="page"' if track==i+1 else '')+f'>T{i+1}<span class="long"> · {E(t[0])}</span></a>' for i,t in enumerate(TR))
  manifest=json.loads(json.dumps(manifest_base))
  for tr in manifest['tracks']:
   for m in tr['modules']:m['href']=root+m['href']
  langs=''
  for code,(locale,label) in LANGS.items():
   target=outdir(code)/rel;href=os.path.relpath(target,dest.parent).replace(os.sep,'/')
   langs+=f'<a href="{href}" hreflang="{locale}" lang="{locale}"'+(' aria-current="page"' if code==lang else '')+f'>{label}</a>'
  alt=''.join(f'<link rel="alternate" hreflang="{locale}" href="{BASE}{"" if code=="pt" else code+"/"}{rel}">' for code,(locale,_) in LANGS.items())
  canon=BASE+('' if lang=='pt' else lang+'/')+rel
  themes=''.join(f'<button type="button" data-inema-set-theme="{v}">{l}</button>' for v,l in zip(['inema-dark','claro','sepia','foco','contraste'],U['themes']))
  out=f'''<!doctype html><html lang="{C['lang']}" class="dark"><head><meta charset="utf-8"><script>{ANTI}</script>
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="inema-course" content="{course_id(lang)}"><title>{E(title)} · OSWork Quick</title><meta name="description" content="{E(C['home']['lead'])}"><meta property="og:title" content="OSWork Quick — {E(C['home']['title_b'])}"><meta property="og:image" content="{BASE}capa/capa.png">
<link rel="canonical" href="{canon}">{alt}<link rel="alternate" hreflang="x-default" href="{BASE}{rel}">
<script type="application/json" data-inema-manifest>{json.dumps(manifest,ensure_ascii=False)}</script>
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{root}assets/site.css"><link rel="stylesheet" href="{root}assets/learn.css">
<style>:root{{--track:{COLORS[track-1]}}}html:not(.dark){{--track:{LIGHT[track-1]}}}pre code{{white-space:pre-wrap}}.see{{border-left:3px solid var(--track);padding:6px 0 6px 14px;margin:12px 0}}.cmdbox{{margin:14px 0}}.hero>*{{min-width:0}}pre{{overflow-wrap:anywhere}}</style></head><body>
<a class="skip" href="#conteudo">{U['skip']}</a>
<nav class="topnav" aria-label="{U['nav']}"><div class="wrap"><div class="nav-main"><a class="brand" href="{root}index.html">OSWork Quick<span aria-hidden="true">_</span></a><span aria-hidden="true">/</span><a class="text-sky-400" href="https://inema.club">INEMA.CLUB</a><span aria-hidden="true">-</span><a class="text-amber-700 dark:text-slate-300" href="https://inema.pro">PRO</a><span class="spacer"></span><button data-inema-journey-open>{U['journey']}</button><button data-inema-appearance-toggle="#aparencia" aria-expanded="false">{U['appearance']}</button><button onclick="toggleTheme()" aria-label="{U['theme_label']}">{U['theme']}</button></div><div class="nav-tracks">{nav}<a href="{root}materiais/index.html">{U['cheat']}</a></div><div class="language-nav" data-os-languages>{langs}</div>
<div id="aparencia" class="appearance" data-inema-appearance hidden><div class="row">{themes}</div><div class="row"><span>{U['size']}</span><button data-inema-set-fontscale="100">100%</button><button data-inema-set-fontscale="112">112%</button><button data-inema-set-fontscale="125">125%</button><button data-inema-set-font="inter">{U['sans']}</button><button data-inema-set-font="leitura">{U['serif']}</button><button data-inema-set-linewidth="60">{U['narrow']}</button><button data-inema-set-linewidth="75">{U['wide']}</button><button data-inema-set-leading="1.7">{U['leading']}</button></div></div></div></nav>
<main id="conteudo" class="wrap">{body}</main><footer><div class="wrap">{U['footer']}<br><a href="{root}FONTES.md">{U['sources']}</a></div></footer>
<dialog id="module-dialog" aria-labelledby="modal-title"><div class="actions"><strong id="modal-title">{U['modal_title']}</strong><button onclick="document.getElementById('module-dialog').close()">{U['close']}</button></div><iframe title="{U['modal_iframe']}"></iframe></dialog>
<script src="{root}assets/learn.js"></script><script src="{root}assets/site.js"></script></body></html>'''
  out=re.sub(r'>(?=<(?:/?(?:html|head|body|nav|div|section|article|h[1-6]|p|ul|li|ol|main|footer|header|table|tr|figure|details|summary|aside|pre|dialog)\b))','>\n',out)
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(out)

 H=C['home']
 hero=f'''<header class="hero"><div><p class="kicker">{H['kicker']}</p><h1>{E(H['title_a'])}<span class="accent">{E(H['title_b'])}</span></h1><p>{E(H['lead'])}</p><div class="actions"><a class="button primary" href="{MODS[0]['href']}">{U['start']}</a><button data-os-resume>{U['resume']}</button><a class="button" href="materiais/index.html">{U['cheat']}</a></div>{meter('curso')}<p class="help-note">{E(H['help'])}</p></div><figure class="hero-panel">{diagram(H['hero_items'])}<figcaption class="help-note">{E(H['hero_caption'])}</figcaption></figure></header>'''
 stats='<div class="stats">'+''.join(f'<div><strong>{E(a)}</strong><span>{E(b)}</span></div>' for a,b in H['stats'])+'</div>'
 cards=''.join(f'<a class="card" href="curso/trilha{i+1}/index.html"><div class="overline"><span>{U["track"].upper()} 0{i+1}</span><span>{len(m["topics"])} {U["steps_word"].upper()} · ~{m["time"]} {U["min"].upper()}</span></div><h2>{E(tr[0])}</h2><p>{E(tr[1])}</p><span class="accent">{U["explore"]}</span></a>' for i,(tr,m) in enumerate(zip(TR,MODS)))
 old_href=('videos/' if lang=='pt' else '../videos/'+lang+'.html')
 body=hero+stats+f'<section class="band"><p class="kicker">{H["path_kicker"]}</p><h2>{E(H["path_title"])}</h2><div class="grid">{cards}</div></section><section class="band grid"><div><p class="kicker">{H["end_kicker"]}</p><h2>{E(H["end_title"])}</h2><ul>'+''.join(f'<li>{E(x)}</li>' for x in H['end_items'])+f'</ul><p class="help-note">{E(U["real_note"])}</p></div><div class="card"><h3>{E(H["old_title"])}</h3><p>{E(H["old_text"])}</p><a class="button" href="{old_href}">{E(H["old_link"])}</a></div></section>'
 page('OSWork Quick',body,'index.html')

 for t,(tr,m) in enumerate(zip(TR,MODS),1):
  mid=m['id']
  body=f'<header class="hero"><div><p class="kicker">{U["track"].upper()} 0{t} / OSWORK QUICK</p><h1>{E(tr[0])}</h1><p>{E(tr[1])}</p>{meter("trilha:"+str(t))}</div><figure class="hero-panel">{diagram([x["title"] for x in m["topics"]][:6],COLORS[t-1])}<figcaption class="help-note">{E(U["track_hero_caption"])}</figcaption></figure></header>'
  body+=f'<div class="stats"><div><strong>1</strong><span>{U["module"].lower()}</span></div><div><strong>{len(m["topics"])}</strong><span>{U["steps_word"]}</span></div><div><strong>~{m["time"]} {U["min"]}</strong><span>{U["lab_kicker"].lower()}</span></div><div><strong>{t}/4</strong><span>{U["track"].lower()}</span></div></div>'
  body+=f'<h2>{U["map"]}</h2><div class="grid"><a class="card" href="#modulo-{mid}"><div class="overline"><span>{t}.1</span><span>~{m["time"]} {U["min"]}</span></div><h3>🧭 {E(m["title"])}</h3><p>{E(m["goal"])}</p></a></div>'
  body+=f'<section class="band"><h2 class="text-2xl font-bold">{U["detail"]}</h2><article class="module-card" id="modulo-{mid}" data-inema-module="{mid}" data-inema-track="{t}"><p class="kicker">{U["module"].upper()} {t}.1</p><h2 class="text-2xl font-bold">{E(m["title"])}</h2><p>{E(m["goal"])}</p>{meter("modulo:"+mid)}'
  for j,tp in enumerate(m['topics'],1):
   pid=f'p-{mid}-{j}'
   body+=f'<div class="topic-item"><button onclick="toggleTopic(this)" aria-expanded="false" aria-controls="{pid}"><span class="number">{j}</span><span>{E(tp["title"])}</span></button><div class="topic-explanation" id="{pid}"><h4>{U["what"]}</h4><p>{E(tp["what"])}</p><h4>{U["why"]}</h4><p>{E(tp["why"])}</p><h4>{U["keys"]}</h4><p>{E(tp["keys"])}</p></div></div>'
  file=Path(m['href']).name
  body+=f'<div class="actions"><a class="button primary" href="{file}">{U["see_full"]}</a><button data-modal-src="{file}">{U["see_modal"]}</button></div></article></section>'
  page(tr[0],body,f'curso/trilha{t}/index.html',t)

 cheat_lines=[]
 for i,m in enumerate(MODS):
  t=m['track'];mid=m['id'];topics=m['topics']
  body=f'<div class="breadcrumbs"><a href="../../index.html">{U["home"]}</a> / <a href="index.html">{E(TR[t-1][0])}</a> / {U["breadcrumb_module"]} {t}.1</div><article id="modulo-{mid}" data-inema-module="{mid}" data-inema-track="{t}"><header class="hero"><div><p class="kicker">{U["module"].upper()} {t}.1 / {t} {U["of_total"]} 4</p><h1>{E(m["title"])}</h1><p>{E(m["goal"])}</p>{meter("modulo:"+mid)}</div><figure class="hero-panel">{diagram([tp["title"] for tp in topics][:6],COLORS[t-1])}<figcaption class="help-note">{E(U["module_hero_caption"])}</figcaption></figure></header>'
  body+=f'<div class="stats"><div><strong>{len(topics)}</strong><span>{U["steps_word"]}</span></div><div><strong>~{m["time"]} {U["min"]}</strong><span>{U["lab_kicker"].lower()}</span></div><div><strong>{t}/4</strong><span>{U["track"].lower()}</span></div><div><strong>3</strong><span>idiomas · languages</span></div></div><div class="reading-layout"><div>'
  cheat_lines.append(f'## {t}. {TR[t-1][0]}')
  for j,tp in enumerate(topics,1):
   body+=f'<section class="topic inema-prose" id="topico-{j}" data-inema-topic="modulo-{mid}#topico-{j}"><h2><span class="number">{j}</span>{E(tp["title"])}</h2>'
   body+=f'<div class="cmdbox"><pre><code>{E(tp["cmd"])}</code></pre><button data-copy-prev>{U["copy"]}</button></div><p class="see" data-inema-block="m{mid}-t{j}-see"><strong>{U["see"]}:</strong> {E(tp["see"])}</p>'
   body+=f'<h3>{U["what"]}</h3><p data-inema-block="m{mid}-t{j}-p1">{E(tp["what"])}</p><h3>{U["why"]}</h3><p data-inema-block="m{mid}-t{j}-p2">{E(tp["why"])}</p><h3>{U["keys"]}</h3><p data-inema-block="m{mid}-t{j}-p3">{E(tp["keys"])}</p>'
   body+=f'<aside class="tip"><h4>{U["fix"]}</h4><p data-inema-block="m{mid}-t{j}-fix">{E(tp["fix"])}</p></aside>'
   fg=m.get('figures',{}).get(str(j))
   if fg:body+=figure(fg,COLORS[t-1],f'{mid}-{j}')
   body+=f'<div class="actions"><button type="button" data-inema-read-toggle aria-pressed="false"><span class="inema-read-icon" aria-hidden="true">○</span><span class="inema-read-label" data-inema-read-label>{U["read"]}</span></button><button type="button" data-inema-doubt-toggle aria-pressed="false">{U["doubt"]}</button></div></section>'
   cheat_lines+=[f'{sum(len(x["topics"]) for x in MODS[:i])+j}. {tp["title"]}']+['   '+x for x in tp['cmd'].split('\n')]+['']
  body+='</div><nav class="toc" data-inema-toc aria-label="'+E(U["toc"])+'"><p class="kicker">'+U["toc"]+'</p><ul>'+''.join(f'<li><a class="inema-toc-link" href="#topico-{j}">{j}. {E(tp["title"])}</a></li>' for j,tp in enumerate(topics,1))+f'</ul><a href="#laboratorio">{U["lab_link"]}</a></nav></div>'
  snippet='\n'.join(tp['cmd'] for tp in topics)
  body+=f'<section class="lab" id="laboratorio"><p class="kicker">{U["lab_kicker"]} / ~{m["time"]} {U["min"].upper()}</p><h2>{E(m["lab"])}</h2><p>{E(U["lab_note"])}</p><ol class="checklist">'
  for k,step in enumerate(m['steps'],1):body+=f'<li><label><input type="checkbox" data-task="{mid}-{k}"><span>{E(step)}</span></label></li>'
  body+=f'</ol><h3>{E(m["snippet_title"])}</h3><pre><code>{E(snippet)}</code></pre><button data-copy-prev>{U["copy"]}</button><h3>{U["ready"]}</h3><p>{E(m["goal"])}</p></section>'
  body+=f'<section class="band"><h2>{U["check_title"]}</h2><p>{E(m["check"])}</p><details><summary>{U["answer"]}</summary><p>{E(m["answer"])}</p></details></section>'
  prev='../../'+MODS[i-1]['href'] if i else '../../index.html';nxt='../../'+MODS[i+1]['href'] if i<len(MODS)-1 else '../../materiais/index.html'
  body+=f'<div class="actions"><a class="button" href="{prev}">{U["prev"]}</a><a class="button" href="index.html">{U["back"]}</a><a class="button primary" href="{nxt}">{U["next"] if i<len(MODS)-1 else U["finish"]}</a></div></article>'
  page(m['title'],body,m['href'],t)

 K=C['cheat'];sheet=f'oswork-quick-{lang}.txt'
 txt='OSWORK QUICK — '+K['kicker']+'\n\n'+'\n'.join(cheat_lines)+'\n'+K['table_title']+'\n'+'\n'.join(f'   {a:<20} {b:<16} {c}' for a,b,c in K['table'])+'\n\n'+BASE+('' if lang=='pt' else lang+'/')+'\n'
 (OUT/'materiais').mkdir(parents=True,exist_ok=True);(OUT/'materiais'/sheet).write_text(txt)
 rows=''.join(f'<tr><td><code>{E(a)}</code></td><td><code>{E(b)}</code></td><td>{E(c)}</td></tr>' for a,b,c in K['table'])
 blocks=''.join(f'<section class="band"><h2>{t}. {E(TR[t-1][0])}</h2>'+''.join(f'<h3>{E(tp["title"])}</h3><pre><code>{E(tp["cmd"])}</code></pre><button data-copy-prev>{U["copy"]}</button>' for tp in m['topics'])+'</section>' for t,m in enumerate(MODS,1))
 body=f'<header class="hero"><div><p class="kicker">{K["kicker"]}</p><h1>{E(K["title"])}</h1><p>{E(K["lead"])}</p><a class="button primary" href="{sheet}" download>{K["download"]}</a></div><div class="card"><h2>{E(K["table_title"])}</h2><div class="table-scroll"><table><thead><tr>'+''.join(f'<th>{E(c)}</th>' for c in K['cols'])+f'</tr></thead><tbody>{rows}</tbody></table></div></div></header>{blocks}<p><a href="../index.html">{K["back"]}</a></p>'
 page(U['cheat'],body,'materiais/index.html')

 (OUT/'FONTES.md').write_text('# '+U['sources']+'\n\n'+'\n'.join(f'- [{a}]({b})' for a,b in C['sources'])+'\n\n'+U['real_note']+'\n')
 return total

def assets(lang):
 """Copia CSS e localiza os JS da camada de aprendizagem (offsets em i18n-v2/js-strings.json)."""
 dest=outdir(lang)/'assets';dest.mkdir(parents=True,exist_ok=True)
 for f in ('favicon.svg','learn.css','site.css'):
  if lang!='pt':shutil.copy2(ROOT/'assets'/f,dest/f)
 tokens=json.loads((ROOT/'i18n-v2/js-strings.json').read_text())
 ui=json.loads((ROOT/f'i18n-v2/ui-{lang}.json').read_text()) if lang!='pt' else {}
 for name in ('learn.js','site.js'):
  src=(ROOT/'assets-src'/name).read_text()
  items=tokens.get('assets/'+name,[])
  for token in sorted(items,key=lambda t:t['start'],reverse=True):
   if token['value'] in ui:src=src[:token['start']]+json.dumps(ui[token['value']],ensure_ascii=False)+src[token['end']:]
  cid=course_id(lang)
  src=src.replace('inema.oswork-v2.meta',f'inema.{cid}.meta').replace('oswork.task.',f'{cid}.task.')
  if lang!='pt':
   labels={'en':{'todas':'all','yellow':'yellow','green':'green','blue':'blue','pink':'pink','doubt':'question'},'es':{'todas':'todos','yellow':'amarillo','green':'verde','blue':'azul','pink':'rosa','doubt':'duda'}}[lang]
   src=src.replace(json.dumps(ui['Marcar com cor '],ensure_ascii=False)+' + c',json.dumps(ui['Marcar com cor '],ensure_ascii=False)+' + '+json.dumps(labels,ensure_ascii=False)+'[c]')
   src=src.replace('o.textContent = c;','o.textContent = '+json.dumps(labels,ensure_ascii=False)+'[c];')
   src=src.replace("'inema-journey__tag', 'duvida'","'inema-journey__tag', "+json.dumps('question' if lang=='en' else 'duda'))
  (dest/name).write_text(src)

if __name__=='__main__':
 for lang in LANGS:
  if not (ROOT/f'conteudo/{lang}.json').exists():print('sem conteúdo:',lang);continue
  n=build(lang);assets(lang);print(f'{lang}: 10 páginas, {n} tópicos')

from pathlib import Path
from bs4 import BeautifulSoup
import json,re
REPO=Path(__file__).resolve().parents[1];OUT=Path('/home/nmaldaner/projetos/output/oswork-quick')
def clean(s):
 s=re.sub(r'\s+',' ',s).strip();s=re.sub(r'\s+([.,;:?!])',r'\1',s);return s

def text(node):return clean(node.get_text(' ',strip=True)) if node else ''
LABEL={'pt':('Aula','Pratique agora','Resumo e próximo passo','Pause o vídeo para fazer a atividade no seu ritmo.'),'es':('Lección','Practica ahora','Resumen y siguiente paso','Pausa el video para hacer la actividad a tu ritmo.'),'en':('Lesson','Practice now','Recap and next step','Pause the video to do the activity at your own pace.')}
for d in ['docs','blocos','assets','scripts','verification','compositions']:(OUT/d).mkdir(exist_ok=True)
manifest=[]
for lang in ['pt','es','en']:
 path=REPO/('' if lang=='pt' else lang)/'curso.html';doc=BeautifulSoup(path.read_text(),'html.parser');scenes=[];L=LABEL[lang]
 for aula in range(1,8):
  view=doc.select_one(f'#v-aula-{aula}');assert view
  title=text(view.select_one('h1'));chapter=f'{L[0]} {aula} · OSWork Quick'
  intro=' '.join([title+'.',text(view.select_one('.promise')),text(view.select_one('.why'))])
  hero=view.select_one('.herofig svg')
  scenes.append(dict(title=title,chapter=chapter,aula=aula,speech=clean(intro),svg=str(hero),takeaway=text(view.select_one('.promise')),kind='diagram',source=f'{path.relative_to(REPO)}#v-aula-{aula}'))
  for step in view.select('.col > .step'):
   title=re.sub(r'^\d+\s*','',text(step.select_one('h2')))
   copy=BeautifulSoup(str(step),'html.parser')
   quiz=copy.select_one('.quiz');quiztext=''
   if quiz:
    answer=quiz.select_one('[data-k="'+quiz['data-answer']+'"]')
    quiztext=' '.join([text(quiz.select_one('.q')),text(answer)+'.',answer.get('data-fb','')]);quiz.decompose()
   for el in copy.select('svg,button,input,h2,.mobfig,.qfb'):el.decompose()
   content=text(copy);speech=clean(title+'. '+content+' '+quiztext)
   fig=step.select_one('.colfig svg');cap=text(step.select_one('figcaption'));assert fig and cap
   scenes.append(dict(title=title,chapter=chapter,aula=aula,speech=speech,svg=str(fig),takeaway=cap,kind='diagram',source=f'{path.relative_to(REPO)}#v-aula-{aula}/step-{step["data-fig"]}'))
  practice=view.select_one('.practice');title=text(practice.select_one('.ph'))
  ps=[text(x) for x in practice.select('.psteps li')]
  copy=BeautifulSoup(str(practice),'html.parser')
  for el in copy.select('button,input,svg,.pk,.pcount,.ph,pre'):el.decompose()
  speech=clean(L[1]+'. '+title+'. '+text(copy)+' '+L[3])
  scenes.append(dict(title=title,chapter=chapter,aula=aula,speech=speech,labels=ps,kind='steps',takeaway=text(practice.select_one('.pdone')) or L[3],source=f'{path.relative_to(REPO)}#v-aula-{aula}/practice'))
  rec=[text(x) for x in view.select('.recap-autor li')];nexts=[text(x) for x in view.select('.next-action .na-action,.next-action .na-hook')]
  scenes.append(dict(title=L[2],chapter=chapter,aula=aula,speech=clean(' '.join(rec+nexts)),labels=rec,kind='steps',takeaway=text(view.select_one('.na-win')),source=f'{path.relative_to(REPO)}#v-aula-{aula}/recap'))
 # Do not teach an absolute claim that ignores memory or project instructions.
 if lang=='pt':
  corrections={'A IA começa cada conversa sem saber nada de você':'Não presuma que a IA conhece seu contexto','Numa conversa nova, ninguém do outro lado conhece sua escola nem sua equipe. O sistema lê só a caixa. O resto ele preenche pela média.':'Numa conversa nova, não presuma que a ferramenta já conhece sua escola ou sua equipe. Ela pode ter instruções e informações salvas, mas você precisa conferir o contexto disponível e fornecer o material necessário.','A IA começa cada conversa do zero: o que não recebe, preenche pela média.':'Não conte com um contexto que você não conferiu: forneça o material necessário para a tarefa.'}
  for s in scenes:
   for key in ['speech','title']:
    for a,b in corrections.items():s[key]=s[key].replace(a,b)
 if lang in ['es','en']:
  corrections={
   'es':{'La IA empieza cada conversación sin saber nada de ti':'No supongas que la IA conoce tu contexto','En una conversación nueva, nadie del otro lado conoce tu escuela ni tu equipo. El sistema lee solo la caja. Lo demás lo completa con el promedio.':'En una conversación nueva, no supongas que la herramienta ya conoce tu escuela o tu equipo. Puede tener instrucciones e información guardadas, pero debes comprobar el contexto disponible y aportar el material necesario.','La IA empieza cada conversación desde cero: lo que no recibe, lo completa por el promedio.':'No dependas de un contexto que no has comprobado: aporta el material necesario para la tarea.','It didn’t use the plan, and it didn’t say the grade level.':'It did not receive the lesson plan or the grade level.'},
   'en':{'The AI starts each conversation without knowing anything about you':'Do not assume the AI knows your context','In a new conversation, nobody on the other side knows your school or your team. The system reads only the box. The rest it fills in using the average.':'In a new conversation, do not assume the tool already knows your school or your team. It may have saved instructions and information, but you need to check the available context and supply the necessary material.','The AI starts each conversation from scratch: what it doesn’t get, it fills in by the average.':'Do not rely on context you have not checked: supply the material needed for the task.','It didn’t use the plan, and it didn’t say the grade level.':'The teacher did not provide the lesson plan or specify the grade level.'}
  }[lang]
  for s in scenes:
   for key in ['speech','title']:
    for a,b in corrections.items():s[key]=s[key].replace(a,b)
 for s in scenes:
  s['speech']=s['speech'].replace('Nada aqui sai da sua conversa.','Esta é uma atividade de treino: use material fictício ou sem dados pessoais.').replace('Nada de aquí sale de tu conversación.','Esta es una actividad de práctica: usa material ficticio o sin datos personales.').replace('Nothing here leaves your conversation.','This is a practice activity: use fictional material or material without personal data.')
  if 'labels' in s:
   for a,b in (corrections.items() if lang in ['pt','es','en'] else []):s['labels']=[v.replace(a,b) for v in s['labels']]
 (OUT/f'docs/lesson-{lang}.json').write_text(json.dumps(scenes,ensure_ascii=False,indent=2))
 (OUT/f'docs/ROTEIRO-{lang.upper()}.md').write_text(f'# OSWork Quick — {lang.upper()}\n\n'+'\n\n'.join(f'## {i+1}. {s["chapter"]}: {s["title"]}\n\n{s["speech"]}' for i,s in enumerate(scenes)))
 group=[];n=0
 def flush():
  global n,group
  if not group:return
  n+=1;content=' '.join(scenes[i-1]['speech'] for i in group);file=OUT/f'blocos/{lang}-{n:02d}.txt';file.write_text(content)
  manifest.append(dict(language=lang,part=n,title=f'OSWORKQ-{lang.upper()}-B{n:02d}-v1',scenes=group,chars=len(content),file=str(file),status='prepared'));group=[]
 for i,s in enumerate(scenes,1):
  assert len(s['speech'])<=4500
  if sum(len(scenes[j-1]['speech'])+1 for j in group)+len(s['speech'])>4400:flush()
  group.append(i)
 flush()
 print(lang,len(scenes),'scenes',sum(len(s['speech'].split()) for s in scenes),'words',n,'blocks')
(OUT/'blocos/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))

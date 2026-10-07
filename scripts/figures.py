"""Desenhos SVG do formato INEMA v2, herdados do OSWork v2 sem alteração."""
import html
E=html.escape

def diagram(labels,color='#34d399',hero=False):
 rows=[]
 for i,label in enumerate(labels):
  x=20+(i%2)*235;y=25+(i//2)*90
  rows.append(f'<rect x="{x}" y="{y}" width="215" height="65" rx="10" fill="#152234" stroke="{color if i%2==0 else "#38bdf8"}"/><text x="{x+16}" y="{y+25}" fill="#cbd5e1" font-size="10" font-family="monospace">0{i+1} / OSWORK</text><text x="{x+16}" y="{y+47}" fill="#f1f5f9" font-size="14" font-family="sans-serif">{E(label)}</text>')
  if i+2<len(labels):rows.append(f'<path d="M{x+100} {y+65}v25" stroke="{color}" stroke-width="2"/>')
 return f'<svg class="w-full h-auto" viewBox="0 0 490 {50+((len(labels)+1)//2)*90}" role="img" aria-label="{E(" → ".join(labels))}"><defs><filter id="glow"><feGaussianBlur stdDeviation="1"/></filter></defs><path d="M10 10H480V{35+((len(labels)+1)//2)*90}H10Z" fill="none" stroke="#334155" stroke-dasharray="3 7"/>{"".join(rows)}</svg>'

def _box(x,y,w,h,color,title,sub=None):
 out=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#152234" stroke="{color}"/>'
 fs=max(10,min(14,int((w-26)/(max(len(title),1)*1.25*0.55))))
 out+=f'<text x="{x+12}" y="{y+(26 if sub else h/2+5)}" fill="#f1f5f9" font-size="{fs}" font-family="sans-serif">{E(title)}</text>'
 if sub:out+=f'<text x="{x+12}" y="{y+45}" fill="#94a3b8" font-size="11" font-family="sans-serif">{E(sub)}</text>'
 return out

def figure(spec,color,uid):
 kind=spec['kind'];alt2={'#34d399':'#38bdf8','#60a5fa':'#34d399','#c084fc':'#38bdf8','#fbbf24':'#38bdf8'}.get(color,'#38bdf8')
 if kind=='grid':
  items=spec['items'];per=4;w=110;gap=10;rows=(len(items)+per-1)//per;h=44
  svg=''
  for i,label in enumerate(items):
   r,c=divmod(i,per);n=min(per,len(items)-r*per);x=(490-(n*w+(n-1)*gap))/2+c*(w+gap);y=14+r*(h+16)
   svg+=_box(x,y,w,h,color if i%2==0 else alt2,label)
  height=14+rows*(h+16)
 elif kind=='columns':
  items=spec['items'];base=spec.get('base',[]);n=len(items);gap=8;w=(478-(n-1)*gap)/n
  svg=''.join(_box(12+i*(w+gap),14,w,58,color if i%2==0 else alt2,t,sub) for i,(t,sub) in enumerate(items))
  height=86
  if base:
   bw=(478-(len(base)-1)*gap)/len(base)
   svg+=''.join(f'<path d="M{12+i*(bw+gap)+bw/2} 72v14" stroke="#475569" stroke-width="2"/>' for i in range(len(base)))
   svg+=''.join(_box(12+i*(bw+gap),86,bw,40,'#475569',t) for i,t in enumerate(base))
   height=134
 elif kind=='flow':
  items=spec['items'];per=2 if len(spec['items'])==4 else 3;gap=34;w=(478-(per-1)*gap)/per;h=48;rows=(len(items)+per-1)//per
  svg=''
  for k,it in enumerate(items):
   r,c=divmod(k,per);n=min(per,len(items)-r*per);x=12+(478-(n*w+(n-1)*gap))/2+c*(w+gap);y=14+r*(h+30)
   t,sub=(it,None) if isinstance(it,str) else it
   svg+=_box(x,y,w,h,color if k%2==0 else alt2,t,sub)
   if c<n-1:svg+=f'<path d="M{x+w+6} {y+h/2}h{gap-12}" stroke="#475569" stroke-width="2"/><path d="M{x+w+gap-12} {y+h/2-5}l6 5-6 5" fill="none" stroke="#475569" stroke-width="2"/>'
   elif k+1<len(items):
    nn=min(per,len(items)-(r+1)*per);nx=12+(478-(nn*w+(nn-1)*gap))/2+w/2
    svg+=f'<path d="M{x+w/2} {y+h+4}v10H{nx}v10" fill="none" stroke="#475569" stroke-width="2"/><path d="M{nx-5} {y+h+18}l5 6 5-6" fill="none" stroke="#475569" stroke-width="2"/>'
  height=14+rows*(h+30)-16
 elif kind=='stack':
  items=spec['items'];h=42;gap=8
  svg=''
  for k,it in enumerate(items):
   t,sub=(it,None) if isinstance(it,str) else it;y=12+k*(h+gap);inset=k*10
   svg+=_box(12+inset,y,466-inset*2,h,color if k%2==0 else alt2,t)
   if sub:svg+=f'<text x="{478-inset-12}" y="{y+h/2+4}" text-anchor="end" fill="#94a3b8" font-size="11" font-family="sans-serif">{E(sub)}</text>'
  height=12+len(items)*(h+gap)
 elif kind=='tree':
  items=spec['items'];svg='';y=26
  for label,depth in items:
   svg+=f'<text x="{16+depth*26}" y="{y}" fill="{"#f1f5f9" if depth<2 else "#94a3b8"}" font-size="14" font-family="monospace">{E(label)}</text>'
   y+=26
  svg=f'<rect x="4" y="8" width="482" height="{y-18}" rx="10" fill="#152234" stroke="{color}"/>'+svg
  height=y-4
 elif kind=='timeline':
  items=spec['items'];svg=f'<path d="M30 40h430" stroke="#475569" stroke-width="2"/>';n=len(items)
  for k,it in enumerate(items):
   t,sub=(it,None) if isinstance(it,str) else it;x=30+k*(430/max(n-1,1))
   svg+=f'<circle cx="{x}" cy="40" r="9" fill="#152234" stroke="{color if k%2==0 else "#38bdf8"}" stroke-width="3"/>'
   anchor='start' if k==0 else ('end' if k==n-1 else 'middle')
   svg+=f'<text x="{x}" y="72" text-anchor="{anchor}" fill="#f1f5f9" font-size="14" font-family="sans-serif">{E(t)}</text>'
   if sub:svg+=f'<text x="{x}" y="22" text-anchor="{anchor}" fill="#94a3b8" font-size="11" font-family="monospace">{E(sub)}</text>'
  height=88
 alt=' · '.join(x if isinstance(x,str) else x[0] for x in spec['items'])
 return (f'<figure class="module-figure"><svg class="w-full h-auto" viewBox="0 0 490 {height}" role="img" '
  f'aria-label="{E(alt)}">{svg}</svg><figcaption class="help-note">{E(spec["caption"])}</figcaption></figure>')


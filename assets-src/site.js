function toggleTopic(b){var p=document.getElementById(b.getAttribute('aria-controls')),open=b.getAttribute('aria-expanded')!=='true';b.closest('.module-card').querySelectorAll('.topic-item>button').forEach(x=>{x.setAttribute('aria-expanded','false');document.getElementById(x.getAttribute('aria-controls')).hidden=true});p.hidden=!open;b.setAttribute('aria-expanded',String(open))}
function toggleTheme(){if(window.INEMA)INEMA.setPref('theme',document.documentElement.classList.contains('dark')?'claro':'inema-dark')}
document.addEventListener('DOMContentLoaded',()=>{
 if(window.INEMA)INEMA.init();
 document.querySelectorAll('.topic-explanation').forEach(p=>p.hidden=true);
 document.querySelectorAll('[data-modal-src]').forEach(b=>b.addEventListener('click',()=>{const d=document.getElementById('module-dialog');d.querySelector('iframe').src=b.dataset.modalSrc;d.showModal()}));
 document.querySelectorAll('[data-os-resume]').forEach(b=>b.addEventListener('click',()=>{try{const m=JSON.parse(localStorage.getItem('inema.oswork-v2.meta')||'{}');if(m.lastModuleHref){const u=new URL(m.lastModuleHref,location.href);if(u.origin===location.origin){u.hash=(m.lastTopicAnchor||'').split('#')[1]||'';location.href=u.href;return}}}catch(e){}location.href='curso/trilha1/modulo-1-1.html'}));
 document.querySelectorAll('[data-task]').forEach(c=>{try{c.checked=localStorage.getItem('oswork.task.'+c.dataset.task)==='true'}catch(e){}c.addEventListener('change',()=>{try{localStorage.setItem('oswork.task.'+c.dataset.task,String(c.checked))}catch(e){}})});
 document.querySelectorAll('[data-copy-prev]').forEach(b=>b.addEventListener('click',async()=>{const text=b.previousElementSibling.innerText;try{await navigator.clipboard.writeText(text);b.textContent='Copiado'}catch(e){b.textContent='Selecione o bloco e copie manualmente'}}));
});

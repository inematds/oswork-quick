// Teste de navegador do OSWork Quick: BASE_URL=http://localhost:PORTA node scripts/browser-test.cjs
const {chromium}=require(process.env.PLAYWRIGHT_PATH||(process.env.HOME+'/.npm-global/lib/node_modules/playwright'));
const BASE=(process.env.BASE_URL||'http://localhost:8080').replace(/\/$/,'');
const PAGES=['index.html','curso/trilha1/index.html','curso/trilha1/modulo-1-1.html','curso/trilha2/modulo-2-1.html','curso/trilha3/modulo-3-1.html','curso/trilha4/modulo-4-1.html','materiais/index.html'];
(async()=>{const b=await chromium.launch();let fails=[];let checks=0;
for(const lang of ['','en/','es/']){
 for(const w of [1366,390]){
  const ctx=await b.newContext({viewport:{width:w,height:900},permissions:['clipboard-read','clipboard-write']});const p=await ctx.newPage();
  p.on('pageerror',e=>fails.push(`${lang}${w} pageerror ${e.message}`));
  for(const u of PAGES){const r=await p.goto(`${BASE}/${lang}${u}`,{waitUntil:'networkidle'});checks++;
   if(!r.ok())fails.push(`${lang}${u} HTTP ${r.status()}`);
   const ov=await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);if(ov>0)fails.push(`${lang}${u} @${w} overflow ${ov}px`);}
  if(w===1366){
   await p.goto(`${BASE}/${lang}curso/trilha1/modulo-1-1.html`,{waitUntil:'networkidle'});
   const btn=p.locator('#topico-1 [data-inema-read-toggle]');await btn.click();await p.reload({waitUntil:'networkidle'});
   if(await p.locator('#topico-1 [data-inema-read-toggle]').getAttribute('aria-pressed')!=='true')fails.push(`${lang} marcar-lido não persistiu`);
   const pct=await p.locator('[data-inema-meter-pct]').first().textContent();if(pct.trim()==='0%')fails.push(`${lang} medidor não mudou`);
   await p.locator('#topico-2 [data-copy-prev]').click();const clip=await p.evaluate(()=>navigator.clipboard.readText());
   if(!clip.includes('mkdir'))fails.push(`${lang} copiar não levou o comando`);
   const n=await p.locator('[data-os-languages] a').count();if(n!==3)fails.push(`${lang} seletor de idioma com ${n} links`);
   checks+=4;}
  await ctx.close();}}
await b.close();
if(fails.length){console.error('FALHOU:\n'+fails.join('\n'));process.exit(1)}
console.log(`OK: ${checks} verificações em PT/EN/ES, desktop e celular: HTTP, sem erro de script, sem overflow, marcar-lido persiste, medidor, copiar e seletor de idioma.`);})();

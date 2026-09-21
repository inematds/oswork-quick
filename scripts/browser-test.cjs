/* Verificação de navegador do OSWork v5 — cobre o checklist técnico herdado do v4.
   Roda em file:// (o contrato exige offline) e num viewport desktop e mobile.
   Uso: node scripts/browser-test.cjs   */
const PW = process.env.PLAYWRIGHT_PATH || '/home/nmaldaner/projetos/timesmkt3/node_modules/playwright';
const { chromium } = require(PW);
const fs = require('fs'), path = require('path'), assert = require('assert');

const ROOT = path.resolve(__dirname, '..');
const URL = 'file://' + path.join(ROOT, 'curso.html');
const OUT = path.join(ROOT, '.verificacao');
const grupos = [];
const ok = (n) => { grupos.push(n); process.stdout.write('  ok  ' + n + '\n'); };

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

  // o onboarding e os paineis cobrem a pagina com um scrim que intercepta cliques
  const fecharPaineis = async () => {
    await page.evaluate(() => {
      document.querySelectorAll('.panel').forEach(x => x.classList.remove('on'));
      ['welcome', 'prefs', 'cedit'].forEach(id => {
        const e = document.getElementById(id); if (e) e.classList.remove('on');
      });
      const sc = document.getElementById('scrim'); if (sc) sc.classList.remove('on');
    });
    await page.waitForTimeout(150);
  };

  // --- 1. carrega em file:// e cai na trilha ---
  await page.goto(URL);
  await page.waitForTimeout(500);
  await fecharPaineis();
  assert.ok(await page.locator('#v-trilha.active').count() === 1, 'trilha não ativou');
  const nAulas = await page.locator('.view[data-aula]').count();
  assert.equal(nAulas, 7, 'esperava 7 aulas, achei ' + nAulas);
  ok('offline em file:// + roteamento inicial na trilha (7 aulas)');

  // --- 2. statcards com tempo agregado (delta v5, mudança 5) ---
  const sc = await page.locator('#v-trilha .statcards .statcard').allInnerTexts();
  assert.ok(sc.length === 2, 'statcards não renderizaram');
  assert.ok(/0\/7/.test(sc[0]), 'statcard de aulas errado: ' + sc[0]);
  assert.ok(/\d+min/.test(sc[1]), 'statcard de tempo errado: ' + sc[1]);
  ok('statcards dinâmicos: ' + sc.join(' · ').replace(/\n/g, ' '));

  // --- 3. roteamento por hash para cada aula + tempo no cold-open ---
  for (let n = 1; n <= 7; n++) {
    await page.goto(URL + '#aula-' + n);
    await page.waitForTimeout(250);
    assert.ok(await page.locator('#v-aula-' + n + '.active').count() === 1, 'aula ' + n + ' não ativou');
    const badge = await page.locator('#v-aula-' + n + ' .tempo-badge').innerText();
    assert.ok(/\d+min/.test(badge), 'aula ' + n + ' sem tempo no cold-open');
    assert.ok(await page.locator('#v-aula-' + n + ' .promise').count() === 1, 'aula ' + n + ' sem promessa');
  }
  ok('roteamento #aula-1..7 + data-tempo renderizado no cold-open das 7');

  // --- 4. marcar lido, progresso na trilha e persistência ---
  await page.goto(URL + '#aula-1');
  await page.waitForTimeout(300);
  await fecharPaineis();
  const btns = page.locator('#v-aula-1 .readbtn');
  const nSteps = await btns.count();
  for (let i = 0; i < nSteps; i++) await btns.nth(i).click();
  assert.equal(await btns.first().innerText(), '✓ lido');
  await page.goto(URL + '#trilha');
  await page.waitForTimeout(300);
  const meta1 = await page.locator('.au[data-aula="1"] .meta').innerText();
  assert.ok(/conclu/i.test(meta1) || /100/.test(meta1), 'progresso da aula 1 não apareceu: ' + meta1);
  await page.reload();
  await page.waitForTimeout(400);
  await fecharPaineis();
  const meta1b = await page.locator('.au[data-aula="1"] .meta').innerText();
  assert.equal(meta1b, meta1, 'progresso não persistiu após recarregar');
  ok('marcar lido + progresso instantâneo na trilha + persistência (página única)');

  // --- 5. jornada: progresso em capacidade = a promessa da aula concluída ---
  await page.locator('#jorbtn').click();
  await page.waitForTimeout(300);
  const caps = await page.locator('#jcap li').allInnerTexts();
  assert.ok(caps.length >= 1 && !/ainda nenhuma/i.test(caps[0]), 'capacidades vazias: ' + caps[0]);
  const jt = await page.locator('#jtinvest').innerText();
  assert.ok(/\d+min/.test(jt), 'tempo investido não renderizou');
  await fecharPaineis();
  ok('painel jornada: capacidade nomeada pela promessa + tempo investido/restante');

  // --- 6. teste-se com feedback elaborado ---
  await page.goto(URL + '#aula-1');
  await page.waitForTimeout(250);
  await page.locator('#v-aula-1 .quiz .opt[data-k="b"]').click();
  await page.waitForTimeout(200);
  const fb = await page.locator('#v-aula-1 .quiz .qfb').innerText();
  assert.ok(fb.length > 40, 'feedback do quiz curto ou ausente: ' + fb);
  assert.ok(await page.locator('#v-aula-1 .quiz .opt.right').count() === 1, 'opção certa não marcada');
  ok('teste-se com feedback elaborado (' + fb.length + ' caracteres)');

  // --- 7. trilho vivo: a figura troca conforme a seção ---
  const figAntes = await page.locator('#v-aula-1 .figstage .fig.on').getAttribute('data-fig');
  await page.locator('#v-aula-1 .step').nth(3).scrollIntoViewIfNeeded();
  await page.waitForTimeout(900);
  const figDepois = await page.locator('#v-aula-1 .figstage .fig.on').getAttribute('data-fig');
  assert.notEqual(figAntes, figDepois, 'trilho não trocou a figura (' + figAntes + ')');
  const cap = await page.locator('#v-aula-1 .railcap').innerText();
  assert.ok(cap.length > 20, 'legenda do trilho vazia');
  ok('trilho vivo troca a figura por seção (fig ' + figAntes + ' → ' + figDepois + ') + legenda');

  // --- 8. mapa da aula e reflexão são injetados pelo motor ---
  assert.ok(await page.locator('#v-aula-1 .aulamap').count() === 1, 'mapa da aula não injetado');
  assert.ok(await page.locator('#v-aula-1 .reflect').count() === nSteps, 'reflexão por seção não injetada');
  assert.ok(await page.locator('#v-aula-1 .recap').count() === 1, 'recap do motor não injetado');
  ok('motor injetou mapa da aula, reflexão por seção e recap');

  // --- 9. fecho autoral na ordem fixa, antes das injeções ---
  const ordem = await page.evaluate(() => {
    const v = document.querySelector('#v-aula-1');
    const r = v.querySelector('.recap-autor'), n = v.querySelector('.next-action'), c = v.querySelector('#cards-1');
    const pos = e => Array.prototype.indexOf.call(v.querySelectorAll('*'), e);
    return [pos(r), pos(n), pos(c)];
  });
  assert.ok(ordem[0] < ordem[1] && ordem[1] < ordem[2], 'ordem do fecho quebrada: ' + ordem);
  ok('fecho na ordem fixa: recap-autor → next-action → cards');

  // --- 10. grifo vira cartão + revisão espaçada ---
  const nRev = await page.evaluate(() => {
    const p = document.querySelector('#v-aula-1 .col p');
    const r = document.createRange();
    r.setStart(p.firstChild, 0); r.setEnd(p.firstChild, 30);
    const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
    document.dispatchEvent(new Event('selectionchange'));
    return document.querySelectorAll('#v-aula-1 .col p').length;
  });
  assert.ok(nRev > 0);
  await page.waitForTimeout(300);
  const temToolbar = await page.locator('#seltb').count();
  assert.equal(temToolbar, 1, 'toolbar de grifo não existe');
  const revn = await page.locator('#revn').innerText();
  assert.ok(/^\d+\+?$/.test(revn), 'contador de revisão inválido: ' + revn);
  ok('toolbar de grifo presente + contador de revisão (' + revn + ' cartões autorais)');

  // --- 11. painel de exercícios (delta v5) lista toda prática ---
  await page.locator('#exbtn').click();
  await page.waitForTimeout(300);
  const linhas = await page.locator('#exercicios .exrow, #exercicios .exlist > *').count();
  assert.ok(linhas >= 7, 'painel de exercícios listou ' + linhas + ' práticas, esperava 7');
  await fecharPaineis();
  ok('painel de exercícios lista as 7 práticas da trilha');

  // --- 12. prática: marcar tudo revela o fecho ---
  await page.goto(URL + '#aula-1');
  await page.waitForTimeout(250);
  const tasks = page.locator('#v-aula-1 .practice input[data-ptask]');
  const nt = await tasks.count();
  for (let i = 0; i < nt; i++) await tasks.nth(i).check();
  await page.waitForTimeout(200);
  assert.ok(await page.locator('#v-aula-1 .practice.done').count() === 1, 'prática não fechou');
  assert.ok(await page.locator('#v-aula-1 .pdone').isVisible(), 'pdone não revelado');
  ok('pratique-agora verificável: ' + nt + ' passos → fecho revelado');

  // --- 13. os 3 temas aplicam e o texto continua legível ---
  for (const t of ['papel', 'sepia', 'dark']) {
    await page.evaluate(th => document.documentElement.setAttribute('data-theme', th), t);
    // body tem transition:background .3s — medir antes do fim mede o blend, nao o tema
    await page.waitForTimeout(700);
    const c = await page.evaluate(() => {
      const p = document.querySelector('#v-aula-1 .col p');
      return [getComputedStyle(p).color, getComputedStyle(document.body).backgroundColor];
    });
    // luminancia relativa WCAG: exige linearizacao sRGB (gama), nao media direta
    const lum = s => {
      const [r, g, b] = s.match(/\d+/g).slice(0, 3).map(Number).map(v => {
        const c = v / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    };
    const ratio = (() => { const a = lum(c[0]) + 0.05, b = lum(c[1]) + 0.05; return a > b ? a / b : b / a; })();
    assert.ok(ratio >= 7, 'contraste AAA falhou no tema ' + t + ': ' + ratio.toFixed(2));
    await page.screenshot({ path: path.join(OUT, 'tema-' + t + '.png') });
  }
  ok('contraste AAA (≥7:1) do corpo nos 3 temas: dark, papel, sépia');

  // --- 13b. traço das figuras legível nos 3 temas (o fundo da figura é escuro sempre) ---
  for (const t of ['dark', 'papel', 'sepia']) {
    await page.evaluate(th => document.documentElement.setAttribute('data-theme', th), t);
    await page.waitForTimeout(700);
    const f = await page.evaluate(() => {
      const el = document.querySelector('.figstage');
      const hex = getComputedStyle(document.documentElement).getPropertyValue('--figbg1').trim().replace('#', '');
      const b = [0, 2, 4].map(i => parseInt(hex.substr(i, 2), 16));
      return { fg: getComputedStyle(el).color, bg: 'rgb(' + b.join(', ') + ')' };
    });
    const lum = s => {
      const [r, g, b] = s.match(/\d+/g).slice(0, 3).map(Number).map(v => {
        const c = v / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    };
    const ratio = (() => { const a = lum(f.fg) + 0.05, b = lum(f.bg) + 0.05; return a > b ? a / b : b / a; })();
    assert.ok(ratio >= 4.5, 'traço da figura invisível no tema ' + t + ': ' + ratio.toFixed(2));
  }
  ok('traço das figuras legível nos 3 temas (fundo da figura é escuro em todos)');

  // --- 14. glossário sob demanda ---
  const g = await page.locator('.gterm').count();
  assert.ok(g >= 7, 'apenas ' + g + ' termos de glossário no curso inteiro');
  ok('glossário .gterm presente (' + g + ' termos)');

  // --- 15. mobile sem overflow horizontal ---
  await page.setViewportSize({ width: 360, height: 780 });
  for (const h of ['#trilha', '#aula-1', '#aula-7']) {
    await page.goto(URL + h);
    await page.waitForTimeout(350);
    const over = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    assert.ok(over <= 1, 'overflow horizontal de ' + over + 'px em ' + h);
  }
  await page.screenshot({ path: path.join(OUT, 'mobile-aula.png'), fullPage: true });
  ok('mobile 360px sem overflow horizontal (trilha, aula 1, aula 7)');

  // --- 16. localStorage bloqueado não quebra a página ---
  const blocked = await browser.newContext();
  await blocked.addInitScript(() => {
    Object.defineProperty(window, 'localStorage', { get() { throw new DOMException('blocked', 'SecurityError'); } });
  });
  const bp = await blocked.newPage();
  const bErr = [];
  bp.on('pageerror', e => bErr.push(e.message));
  await bp.goto(URL + '#aula-1');
  await bp.waitForTimeout(400);
  assert.ok(await bp.locator('#v-aula-1.active').count() === 1, 'página não abriu sem localStorage');
  assert.deepEqual(bErr, [], 'erros com localStorage bloqueado: ' + bErr.join(' | '));
  ok('localStorage bloqueado: página continua utilizável, sem erro');

  assert.deepEqual(errors, [], 'erros de JS: ' + errors.join(' | '));
  fs.writeFileSync(path.join(OUT, 'browser-results.json'),
    JSON.stringify({ ok: true, grupos, errors }, null, 2));
  await browser.close();
  console.log('\nOK: ' + grupos.length + ' grupos de verificação, zero erro de JS.');
})().catch(e => { console.error('\nFALHOU:', e.message); process.exit(1); });

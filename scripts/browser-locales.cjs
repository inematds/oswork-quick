/* Verificação de navegador das edições EN e ES do OSWork Quick.
   O risco específico dos idiomas: o motor foi recortado por deslocamento, então um
   literal mal fechado quebra o JavaScript inteiro — e o estado tem de ficar isolado
   por idioma, senão os cartões de um idioma aparecem na revisão do outro.
   Uso: node scripts/browser-locales.cjs   */
const PW = process.env.PLAYWRIGHT_PATH || '/home/nmaldaner/projetos/timesmkt3/node_modules/playwright';
const { chromium } = require(PW);
const fs = require('fs'), path = require('path'), assert = require('assert');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, '.verificacao');
const grupos = [];
const ok = n => { grupos.push(n); process.stdout.write('  ok  ' + n + '\n'); };

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true });

  for (const lang of ['en', 'es']) {
    const url = 'file://' + path.join(ROOT, lang, 'curso.html');
    const ctx = await browser.newContext({ viewport: { width: 1400, height: 1000 }, reducedMotion: 'reduce' });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

    await page.goto(url);
    await page.waitForTimeout(600);
    await page.evaluate(() => {
      document.querySelectorAll('.panel').forEach(x => x.classList.remove('on'));
      ['welcome', 'prefs', 'cedit'].forEach(i => { const e = document.getElementById(i); if (e) e.classList.remove('on'); });
      const s = document.getElementById('scrim'); if (s) s.classList.remove('on');
    });

    // 1. o motor recortado carrega e roteia
    assert.equal(await page.locator('.view[data-aula]').count(), 7, lang + ': não achou 7 aulas');
    assert.equal(await page.locator('#v-trilha.active').count(), 1, lang + ': trilha não ativou');
    assert.deepEqual(errors, [], lang + ': erro de JS no motor recortado: ' + errors.join(' | '));
    ok(lang + ': motor traduzido carrega, 7 aulas, zero erro de JS');

    // 2. a interface do motor está no idioma (nada de português sobrando)
    // Asserção POSITIVA por idioma: 'revisar' e 'tema' também são espanhol, então
    // uma lista de palavras portuguesas proibidas acusaria o ES corretamente traduzido.
    const barra = await page.locator('.bar-inner').innerText();
    const ESPERADO = { en: [/review/i, /journey/i, /theme:/i, /exercises/i],
                       es: [/revisar/i, /trayecto/i, /tema:/i, /ejercicios/i] };
    const SOBRA_PT = { en: [/revisar/i, /jornada/i, /exerc[íi]cios/i, /tema:/i, /escuro/i],
                       es: [/jornada/i, /exerc[íi]cios/i, /escuro/i] };
    for (const re of ESPERADO[lang])
      assert.ok(re.test(barra), lang + ': barra sem ' + re + ': ' + barra.replace(/\n/g, ' '));
    for (const re of SOBRA_PT[lang])
      assert.ok(!re.test(barra), lang + ': português sobrando na barra (' + re + '): ' + barra.replace(/\n/g, ' '));
    ok(lang + ': barra do motor traduzida (' + barra.replace(/\n/g, ' ').slice(0, 60) + '…)');

    // 3. os fragmentos concatenados mantiveram o espaço de borda
    await page.goto(url + '#aula-1');
    await page.waitForTimeout(400);
    const btns = page.locator('#v-aula-1 .readbtn');
    const n = await btns.count();
    for (let i = 0; i < n; i++) await btns.nth(i).click();
    await page.goto(url + '#trilha');
    await page.waitForTimeout(400);
    const meta = await page.locator('.au[data-aula="1"] .meta').innerText();
    assert.ok(!/\w\d|\d\w/.test(meta.replace(/\d+\s*min/gi, '')),
      lang + ': fragmento colado sem espaço no card: ' + meta);
    ok(lang + ': fragmentos concatenados com espaçamento correto ("' + meta.trim() + '")');

    // 4. estado isolado do PT e do outro idioma
    const chave = await page.evaluate(() => document.querySelector('meta[name=curso]').content);
    assert.equal(chave, 'osworkq-' + lang, lang + ': chave de estado errada: ' + chave);
    const chaves = await page.evaluate(() => Object.keys(localStorage));
    assert.ok(!chaves.includes('osworkq'), lang + ': escreveu no estado do PT');
    ok(lang + ': estado isolado em "' + chave + '" (não toca o do PT)');

    // 5. o seletor de idioma leva aos outros dois
    const alvos = await page.locator('.langsel a').evaluateAll(as => as.map(a => a.getAttribute('href')));
    assert.equal(alvos.length, 2, lang + ': seletor com ' + alvos.length + ' destinos');
    for (const a of alvos) {
      const dest = path.resolve(path.join(ROOT, lang), a);
      assert.ok(fs.existsSync(dest), lang + ': seletor aponta para arquivo inexistente: ' + a);
    }
    ok(lang + ': seletor de idioma aponta para dois destinos existentes');

    // 6. os desenhos vieram junto e o trilho continua trocando
    assert.equal(await page.locator('#v-aula-1 .figstage .fig').count(), 4, lang + ': figuras do trilho faltando');
    assert.equal(await page.locator('#v-aula-1 .colfig').count(), 4, lang + ': figuras inline faltando');
    await page.goto(url + '#aula-1');
    await page.waitForTimeout(300);
    const f1 = await page.locator('#v-aula-1 .figstage .fig.on').getAttribute('data-fig');
    await page.locator('#v-aula-1 .step').nth(3).scrollIntoViewIfNeeded();
    await page.waitForTimeout(900);
    const f2 = await page.locator('#v-aula-1 .figstage .fig.on').getAttribute('data-fig');
    assert.notEqual(f1, f2, lang + ': trilho não troca a figura');
    ok(lang + ': 8 desenhos presentes na aula 1, trilho vivo funcionando');

    // 7. quiz traduzido com feedback
    await page.locator('#v-aula-1 .quiz .opt[data-k="b"]').click();
    await page.waitForTimeout(250);
    const fb = await page.locator('#v-aula-1 .quiz .qfb').innerText();
    assert.ok(fb.length > 30, lang + ': feedback do quiz vazio');
    ok(lang + ': teste-se traduzido com feedback (' + fb.length + ' caracteres)');

    // 8. mobile sem transbordamento
    await page.setViewportSize({ width: 360, height: 780 });
    for (const h of ['#trilha', '#aula-7']) {
      await page.goto(url + h);
      await page.waitForTimeout(400);
      const over = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      assert.ok(over <= 1, lang + ': transbordamento de ' + over + 'px em ' + h);
    }
    await page.screenshot({ path: path.join(OUT, 'mobile-' + lang + '.png'), fullPage: false });
    ok(lang + ': 360px sem transbordamento horizontal');

    assert.deepEqual(errors, [], lang + ': erros de JS: ' + errors.join(' | '));
    await ctx.close();
  }

  fs.writeFileSync(path.join(OUT, 'browser-locales.json'), JSON.stringify({ ok: true, grupos }, null, 2));
  await browser.close();
  console.log('\nOK: ' + grupos.length + ' grupos nos dois idiomas, zero erro de JS.');
})().catch(e => { console.error('\nFALHOU:', e.message); process.exit(1); });

// Banc de test v39.1 : vrai fichier HTML, CDN simulés, API rejouée depuis des réponses prod enregistrées.
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const FILE = process.argv[2]; const DB = path.join(__dirname, 'responses.json');
const db = fs.existsSync(DB) ? JSON.parse(fs.readFileSync(DB, 'utf8')) : {};
const canon = o => JSON.stringify(Object.keys(o).sort().reduce((a, k) => (a[k] = o[k], a), {}));

// Bornes relevées sur l'API de prod le 15/11/2026 (k=8, alpha 0,05, KimDeMets / HSD(-2), testType 3)
const PROD = {
  0.2: [[0.1357,3.725,-1.4542],[0.2714,3.1895,-0.886],[0.4071,2.847,-0.4025],[0.5428,2.5754,0.0339],[0.6785,2.3411,0.4429],[0.8142,2.1284,0.8366],[0.9499,1.9236,1.2273],[1.0856,1.6737,1.6737]],
  0.1: [[0.1364,3.725,-1.5356],[0.2727,3.1895,-0.9272],[0.4091,2.847,-0.4173],[0.5454,2.5755,0.0371],[0.6818,2.3414,0.4569],[0.8181,2.129,0.8546],[0.9545,1.9244,1.2417],[1.0908,1.671,1.671]] };
const zPooled = (vA,cA,vB,cB) => { const pp=(cA+cB)/(vA+vB); return (cB/vB-cA/vA)/Math.sqrt(pp*(1-pp)*(1/vA+1/vB)); };
if (Math.abs(zPooled(40000,2000,40000,2120)-1.9196) > 5e-5) { console.log('Formule Z ≠ prod'); process.exit(2); }
function respond(b) {
  b = Object.assign({}, b); if (b.beta === undefined) b.beta = 0.2; // comme le script R : params$beta %||% 0.20
  if (b.k!==8 || b.alpha!==0.05 || b.sfu!=='KimDeMets' || b.sfl!=='HSD' || b.testType!==3 || !PROD[b.beta]) return null;
  const r = { boundaries: PROD[b.beta].map((x,i)=>({stage:i+1, infoFraction:x[0], efficacyZ:x[1], futilityZ:x[2]})), parameters:{k:8, alpha:0.05, beta:b.beta, testType:3, sfu:'KimDeMets', sfl:'HSD(-2)'} };
  if (b.visitors_a!==undefined) r.observedZ = +zPooled(b.visitors_a,b.conversions_a,b.visitors_b,b.conversions_b).toFixed(4);
  return r;
}
const missing = new Set(); const results = []; let fails = 0;
const ok = (name, cond, info) => { results.push(`${cond ? '✅' : '❌'} ${name}${info !== undefined ? ' — ' + JSON.stringify(info) : ''}`); if (!cond) fails++; };
const STUBS = {
  jstat: `window.jStat={normal:{inv:function(p){var a=[-39.69683028665376,220.9460984245205,-275.9285104469687,138.357751867269,-30.66479806614716,2.506628277459239],b=[-54.47609879822406,161.5858368580409,-155.6989798598866,66.80131188771972,-13.28068155288572],c=[-0.007784894002430293,-0.3223964580411365,-2.400758277161838,-2.549732539343734,4.374664141464968,2.938163982698783],d=[0.007784695709041462,0.3224671290700398,2.445134137142996,3.754408661907416],q,r;if(p<0.02425){q=Math.sqrt(-2*Math.log(p));return(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)}if(p>1-0.02425){q=Math.sqrt(-2*Math.log(1-p));return-(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)}q=p-0.5;r=q*q;return(((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q/(((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)}}};`,
  highcharts: `window.__charts=[];window.Highcharts={chart:function(id,o){var s=(o.series||[]).map(function(){return{setData:function(){},update:function(){}}});var c={series:s,xAxis:[{categories:(o.xAxis&&o.xAxis.categories)||[],setCategories:function(){}}],yAxis:[{update:function(){}}],destroy:function(){}};window.__charts.push(id);return c}};`,
  jquery: `window.$=window.jQuery=function(){return{collapse:function(){}}};`,
};
async function newPage(browser, apiLog) {
  const page = await browser.newPage(); const errors = [];
  page.on('pageerror', e => errors.push(String(e))); page.on('dialog', d => d.accept());
  await page.route('**/*', async route => {
    const u = route.request().url();
    if (u.startsWith('file://')) return route.continue();
    if (u.includes('/api/calculate-boundaries')) {
      const body = JSON.parse(route.request().postData()); const key = canon(body); apiLog.push(body);
      const resp = respond(body); if (resp) return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(resp) });
      missing.add(key); return route.fulfill({ status: 599, contentType: 'application/json', body: '{"error":true,"message":"MISSING"}' });
    }
    if (u.includes('jstat')) return route.fulfill({ contentType: 'application/javascript', body: STUBS.jstat });
    if (u.includes('highcharts')) return route.fulfill({ contentType: 'application/javascript', body: u.endsWith('highcharts.js') ? STUBS.highcharts : '' });
    if (u.includes('jquery')) return route.fulfill({ contentType: 'application/javascript', body: STUBS.jquery });
    return route.fulfill({ status: 200, body: '' });
  });
  await page.goto('file://' + path.resolve(FILE)); await page.waitForTimeout(300);
  return { page, errors };
}
const setVal = (page, id, v) => page.evaluate(([id, v]) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event(e.tagName === 'SELECT' || e.type === 'date' ? 'change' : 'input', { bubbles: true })); }, [id, String(v)]);
const click = (page, sel) => page.evaluate(s => document.querySelector(s).click(), sel);
const settle = page => page.waitForTimeout(400);
async function plan(page, { traffic, conv, sec, power, week }) {
  await setVal(page, 'baselineTraffic', traffic); await setVal(page, 'baselineTotalConversions', conv);
  if (sec) { await click(page, '#toggleBaselineSecondaryKpi'); await setVal(page, 'baselineTotalConversionsSecondary', sec); }
  if (power) await setVal(page, 'mdePower', power);
  await settle(page); await click(page, `#mde-forecast-tbody tr[data-week="${week}"]`);
  await setVal(page, 'testStartDate', '2026-11-02'); await click(page, '#startAnalysisButton'); await settle(page);
}
async function addWeek(page, d) {
  for (const [id, v] of Object.entries(d)) await setVal(page, id, v);
  await click(page, '#addDataButton'); await settle(page);
}
const tableCol = (page, col) => page.evaluate(c => [...document.querySelectorAll('#boundaries-tbody tr')].map(r => r.cells[c] && r.cells[c].textContent), col);
(async () => {
  const browser = await chromium.launch();
  // S1 — nouveau test, puissance 90 %, k=8, KPI de sécurité
  { const log = []; const { page, errors } = await newPage(browser, log);
    await plan(page, { traffic: 20000, conv: 1000, sec: 4000, power: '0.90', week: 8 });
    await addWeek(page, { controlVisitors: 10000, controlConversions: 500, controlConversionsSecondary: 2000, variantVisitors: 10300, variantConversions: 560, variantConversionsSecondary: 2050 });
    ok('S1 appels API émis', log.length >= 2, log.length);
    ok('S1 toutes les requêtes portent beta=0.1 (puissance 90 %)', log.length > 0 && log.every(b => b.beta === 0.1), log.map(b => b.beta));
    ok('S1 requête KPI sécurité présente (testType 3, beta 0.1)', log.some(b => b.conversions_a === 2000 && b.beta === 0.1));
    const fr = await tableCol(page, 1); ok('S1 fraction d\'info normalisée 0.125…1.000', fr[0] === '0.1250' && fr[fr.length - 1] === '1.0000', fr);
    const srm = await page.evaluate(() => document.getElementById('srmCheckIndicator').textContent);
    ok('S1 SRM non déclenché pour χ²=4,43 (10000 vs 10300)', /Ok/.test(srm), srm);
    const dec = await page.evaluate(() => document.getElementById('decision').textContent.trim());
    ok('S1 décision affichée', dec.length > 10, dec.slice(0, 90));
    ok('S1 aucune erreur JS', errors.length === 0, errors); await page.close(); }
  // S1b — SRM réel toujours détecté (10000 vs 10700, χ²=23,7)
  { const log = []; const { page, errors } = await newPage(browser, log);
    await plan(page, { traffic: 20000, conv: 1000, week: 8 });
    await addWeek(page, { controlVisitors: 10000, controlConversions: 500, variantVisitors: 10700, variantConversions: 540 });
    const srm = await page.evaluate(() => document.getElementById('srmCheckIndicator').textContent);
    ok('S1b SRM détecté pour χ²=23,7', /SRM/.test(srm), srm);
    ok('S1b puissance par défaut 80 % → beta=0.2', log.every(b => b.beta === 0.2), log.map(b => b.beta));
    ok('S1b aucune erreur JS', errors.length === 0, errors); await page.close(); }
  // S2 — horizon fixe k=1 : aucun appel réseau
  { const log = []; const { page, errors } = await newPage(browser, log);
    await plan(page, { traffic: 20000, conv: 1000, week: 1 });
    const eff = await tableCol(page, 2); ok('S2 borne k=1 = 1.645 (α 5 % unilatéral)', eff[0] === '1.645', eff);
    await addWeek(page, { controlVisitors: 20000, controlConversions: 1000, variantVisitors: 20000, variantConversions: 1100 });
    ok('S2 aucun appel API', log.length === 0, log.length);
    const z = await page.evaluate(() => document.getElementById('zScorePrincipal').textContent);
    ok('S2 Z observé = 2.242 (calcul indépendant)', z === '2.242', z);
    const dec = await page.evaluate(() => document.getElementById('decision').textContent.trim());
    ok('S2 décision « positif » à k=1', /ARRÊTER/.test(dec), dec.slice(0, 90));
    ok('S2 aucune erreur JS', errors.length === 0, errors); await page.close(); }
  // S3 — test sauvegardé avant v39.1 (sans beta, puissance 90 %) : bornes figées à beta=0.2
  { const log = []; const { page, errors } = await newPage(browser, log);
    const initKey = canon({ k: 4, alpha: 0.05, power: 0.9, beta: 0.2, sfu: 'KimDeMets', sfl: 'HSD', testType: 3 });
    const saved = { name: 'legacy', timestamp: '2026-10-01T00:00:00Z', baselineTraffic: '20000', baselineTotalConversions: '1000', baselineTotalConversionsSecondary: '', isSecondaryKpiPlanned: false, testStartDate: '2026-10-05', mdeConfidence: '0.05', mdePower: '0.90', mdeTestType: '3', designSpendingFunction: 'KimDeMets', designSpendingFunctionLower: 'HSD', designK: '8', currentDesignParams: { k: 8, alpha: 0.05, power: 0.9, sfu: 'KimDeMets', sfl: 'HSD', testTypePrincipal: 3, testStartDate: '2026-10-05' }, currentBoundariesApiResultPrincipal: respond({k:8,alpha:0.05,beta:0.2,sfu:'KimDeMets',sfl:'HSD',testType:3}), currentBoundariesApiResultSecondary: null, weeklyEnteredData: [{ week: 1, visitorsACumul: 10000, conversionsACumul_P: 500, visitorsBCumul: 10000, conversionsBCumul_P: 520 }], observedZDataPrincipal: new Array(8).fill(null), observedZDataSecondary: [], apiUrl: 'https://my-gst-api.onrender.com/api/calculate-boundaries' };
    await page.evaluate(s => { localStorage.setItem('gstSequentialAnalysis_v321_legacy', JSON.stringify(s)); }, saved);
    await page.reload(); await page.waitForTimeout(300);
    await setVal(page, 'saved-tests-list-top', 'legacy'); await click(page, '#load-test-button-top'); await settle(page);
    await addWeek(page, { controlVisitors: 20000, controlConversions: 1000, variantVisitors: 20000, variantConversions: 1050 });
    ok('S3 test v39.0 rechargé → beta reste 0.2 (bornes inchangées en cours de test)', log.length > 0 && log.every(b => b.beta === 0.2), log.map(b => b.beta));
    ok('S3 aucune erreur JS', errors.length === 0, errors); await page.close(); }
  // S3b — test antérieur rechargé puis « Lancer » recliqué sans rien changer : beta reste 0.2, puissance affichée 80 %
  { const log = []; const { page, errors } = await newPage(browser, log); const dialogs = []; page.on('dialog', d => dialogs.push(d.message()));
    const saved = { name: 'legacy2', baselineTraffic: '20000', baselineTotalConversions: '1000', baselineTotalConversionsSecondary: '', isSecondaryKpiPlanned: false, testStartDate: '2026-10-05', mdeConfidence: '0.05', mdePower: '0.90', mdeTestType: '3', designSpendingFunction: 'KimDeMets', designSpendingFunctionLower: 'HSD', designK: '8', currentDesignParams: { k: 8, alpha: 0.05, power: 0.9, sfu: 'KimDeMets', sfl: 'HSD', testTypePrincipal: 3, testStartDate: '2026-10-05' }, currentBoundariesApiResultPrincipal: respond({k:8,alpha:0.05,beta:0.2,sfu:'KimDeMets',sfl:'HSD',testType:3}), currentBoundariesApiResultSecondary: null, weeklyEnteredData: [{ week: 1, visitorsACumul: 10000, conversionsACumul_P: 500, visitorsBCumul: 10000, conversionsBCumul_P: 520 }], observedZDataPrincipal: new Array(8).fill(null), observedZDataSecondary: [], apiUrl: 'https://my-gst-api.onrender.com/api/calculate-boundaries' };
    await page.evaluate(s => localStorage.setItem('gstSequentialAnalysis_v321_legacy2', JSON.stringify(s)), saved); await page.reload(); await page.waitForTimeout(300);
    await setVal(page, 'saved-tests-list-top', 'legacy2'); await click(page, '#load-test-button-top'); await settle(page);
    const pw = await page.evaluate(() => document.getElementById('mdePower').value);
    ok('S3b puissance affichée = celle réellement utilisée (0.80)', pw === '0.80', pw);
    dialogs.length = 0; await click(page, '#startAnalysisButton'); await settle(page);
    ok('S3b reclic sans changement : beta 0.2, pas de confirmation', log.length > 0 && log.every(b => b.beta === 0.2) && !dialogs.some(m => /réinitialisera/.test(m)), { betas: log.map(b => b.beta), dialogs });
    const n = await page.evaluate(() => document.querySelectorAll('#history-tbody tr').length);
    ok('S3b données conservées (1 semaine = 2 lignes A/B)', n === 2, n);
    ok('S3b aucune erreur JS', errors.length === 0, errors); await page.close(); }
  // S5 — puissance changée en cours de test : confirmation demandée, données remises à zéro, nouveau beta
  { const log = []; const { page, errors } = await newPage(browser, log); const dialogs = []; page.on('dialog', d => dialogs.push(d.message()));
    await plan(page, { traffic: 20000, conv: 1000, week: 8 });
    await addWeek(page, { controlVisitors: 10000, controlConversions: 500, variantVisitors: 10000, variantConversions: 520 });
    log.length = 0; dialogs.length = 0; await setVal(page, 'mdePower', '0.90'); await settle(page); await click(page, '#mde-forecast-tbody tr[data-week="8"]');
    await click(page, '#startAnalysisButton'); await settle(page);
    ok('S5 confirmation demandée au changement de puissance', dialogs.some(m => /réinitialisera/.test(m)), dialogs);
    ok('S5 nouveau plan envoyé avec beta 0.1', log.length > 0 && log.every(b => b.beta === 0.1), log.map(b => b.beta));
    ok('S5 aucune erreur JS', errors.length === 0, errors); await page.close(); }
  // S6 — suppression de la semaine 3 sur 3 : il reste 2 semaines
  { const log = []; const { page, errors } = await newPage(browser, log);
    await plan(page, { traffic: 20000, conv: 1000, week: 8 });
    await addWeek(page, { controlVisitors: 10000, controlConversions: 500, variantVisitors: 10000, variantConversions: 520 });
    await addWeek(page, { controlVisitors: 20000, controlConversions: 1000, variantVisitors: 20000, variantConversions: 1040 });
    await addWeek(page, { controlVisitors: 30000, controlConversions: 1500, variantVisitors: 30000, variantConversions: 1560 });
    await page.evaluate(() => window.deleteWeeklyCumulativeData(2)); await page.waitForTimeout(800);
    const n = await page.evaluate(() => document.querySelectorAll('#history-tbody tr').length);
    const stage = await page.evaluate(() => document.getElementById('resultStage').textContent);
    ok('S6 après suppression de S3 : 2 semaines (4 lignes A/B), étape 2', n === 4 && stage === '2', { lignes: n, stage });
    const z = await page.evaluate(() => document.getElementById('zScorePrincipal').textContent);
    ok('S6 Z affiché = Z de la semaine 2 (0.909)', z === '0.909', z);
    ok('S6 aucune erreur JS', errors.length === 0, errors); await page.close(); }
  await browser.close();
  if (missing.size) { fs.writeFileSync(path.join(__dirname, 'missing.json'), JSON.stringify([...missing].map(k => JSON.parse(k)), null, 1)); console.log(`REPONSES MANQUANTES : ${missing.size} → missing.json`); }
  console.log(results.join('\n')); console.log(`\n${results.length - fails}/${results.length} OK`); process.exit(fails ? 1 : 0);
})();

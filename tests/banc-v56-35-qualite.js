// Banc v56.35 : contrôles de qualité des données (trafic face au plan, semaine atypique, détail dépliable).
const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-35.html');
const res=[]; let fails=0; const ok=(n,c,i)=>{res.push((c?'✅ ':'❌ ')+n+(c||i===undefined?'':' — '+JSON.stringify(i)));if(!c)fails++;};
const SRC=fs.readFileSync(FILE,'utf8'); const EX=SRC.slice(SRC.indexOf('var EXEMPLE="')+13).split('"')[0].split('\\n').join('\n');
// Exemple modifié : 150 achats retirés au contrôle en semaine 3 (cumul), pour créer une semaine atypique.
const ATY=EX.split('\n').map((l,i)=>{if(!i)return l;const c=l.split(';');if(+c[0]>=3&&/Contr/.test(c[3]))c[5]=String(+c[5]-150);return c.join(';');}).join('\n');
(async()=>{ const b=await chromium.launch();
 for(const w of [360,1280]){ const p=await b.newPage({viewport:{width:w,height:900}}); const errs=[]; p.on('pageerror',e=>errs.push(String(e))); p.on('dialog',d=>d.accept());
  await p.goto('file://'+path.resolve(FILE)); await p.waitForTimeout(300);
  const ov=()=>p.evaluate(()=>document.scrollingElement.scrollWidth-innerWidth);
  const side=()=>p.evaluate(()=>document.querySelector('#gst-app .v-side').innerText.replace(/\n+/g,' | '));
  const tab=async t=>{await p.locator('#gst-app .tabs button',{hasText:t}).first().click();await p.waitForTimeout(300);};
  await p.click('#gst-app [data-act=example]'); await p.waitForSelector('#gst-app .verdict'); await p.waitForTimeout(1500);
  let s=await side();
  ok(`[${w}] exemple : trois contrôles, aucun en alerte, trafic comparé au rythme de la semaine 1`, /Aucune alerte \| Trois contrôles lus en semaine 5/.test(s)&&/Répartition A\/B équilibrée \(SRM\)/.test(s)&&/Trafic conforme au rythme de la semaine 1/.test(s)&&/Aucune semaine atypique détectée/.test(s)&&(await p.locator('#gst-app .v-side .chk').count())===3&&(await p.locator('#gst-app .tp-dt').count())===0&&(await ov())<=0, s);
  await p.click('#gst-app [data-act=qdetail]'); await p.waitForTimeout(200);
  let d=await p.evaluate(()=>{const e=document.querySelector('#gst-app .tp-dt');const b=document.querySelector('#gst-app [data-act=qdetail]');return e?{t:e.innerText.replace(/\s+/g,' '),rows:[...e.querySelectorAll('table')].map(t=>t.querySelectorAll('tbody tr').length),hi:[...e.querySelectorAll('td.hi')].map(x=>x.textContent),bh:b.getBoundingClientRect().height,exp:b.getAttribute('aria-expanded'),bt:b.textContent.trim()}:null;});
  ok(`[${w}] détail déplié : répartition (p = 0,57), 5 semaines de trafic, 5 semaines de taux, semaine 5 du contrôle repérée à 2,8 écarts-types sous le seuil, sans débordement`, !!d&&/50 089 · Variante 49 909, soit 180 visiteurs/.test(d.t)&&/p = 0,57/.test(d.t)&&d.rows.join()==='5,5'&&/20 059/.test(d.t)&&d.hi.join()==='4,44 %'&&/contrôle en S5, à 2,8 écarts-types.*Sous le seuil/.test(d.t)&&d.bh>=44&&d.exp==='true'&&/^Masquer/.test(d.bt)&&(await ov())<=0, d);
  await p.click('#gst-app [data-act=qdetail]'); await p.waitForTimeout(150);
  ok(`[${w}] détail replié au second clic`, (await p.locator('#gst-app .tp-dt').count())===0);
  // trafic conforme, puis sous le plan
  const setT=async v=>{await p.click('#gst-app [data-v=plan]');await p.waitForTimeout(300);await p.fill('#gst-app [data-mde=traffic]',String(v));await p.keyboard.press('Tab');await p.waitForTimeout(300);await p.click('#gst-app [data-act=applyplan]');await p.waitForTimeout(3000);await p.click('#gst-app [data-v=resultats]');await p.waitForTimeout(600);};
  await setT(20000); s=await side(); const st1=await p.evaluate(()=>({t:GST.getState().plan.traffic,dw:GST.compute().decisionWeek}));
  ok(`[${w}] trafic prévu 20 000 par semaine : « Trafic conforme au plan », 99 998 sur 100 000, aucune alerte`, st1.t===20000&&/Trafic conforme au plan \| [\d\s]+ visiteurs sur [\d\s]+ prévus à fin S\d\./.test(s)&&/Aucune alerte/.test(s), [s,st1]);
  await setT(30000); s=await side();
  ok(`[${w}] trafic prévu 30 000 par semaine : alerte « Trafic sous le plan » (67 %), effet détectable recalculé, 1 alerte comptée, sans débordement`, /1 alerte \| Trois contrôles lus/.test(s)&&/Trafic sous le plan \| [\d\s]+ visiteurs sur [\d\s]+ prévus à fin S\d, soit 6\d %\. À ce rythme, l'effet détectable en 8 semaines passe d'environ \d,\d % à \d,\d %\./.test(s)&&(await ov())<=0, s);
  await p.click('#gst-app [data-act=qdetail]'); await p.waitForTimeout(150); d=await p.evaluate(()=>document.querySelector('#gst-app .tp-dt').innerText.replace(/\s+/g,' '));
  ok(`[${w}] détail : part du plan par semaine (67 % en S1)`, /Plan : 30 000 visiteurs par semaine/.test(d)&&/S1 20 059 67 %/.test(d), d.slice(0,400));
  // semaine atypique
  await p.evaluate(c=>window.GST.openCSV(c,'atypique.csv'),ATY); await p.waitForTimeout(400);
  await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()})); await p.waitForTimeout(200);
  if(await p.locator('#gst-app [data-act=apply]').count()){await p.click('#gst-app [data-act=apply]');await p.waitForTimeout(2000);}
  s=await side(); const z=await p.evaluate(()=>{const S=GST.getState();return S.weeks.length;});
  ok(`[${w}] 150 achats retirés au contrôle en semaine 3 : alerte « Semaine 3 atypique », écarts-types et taux cités, sans débordement`, /Semaine 3 atypique \| Taux de l'objectif du contrôle à \d+,\d écarts-types des autres semaines \(\d,\d\d % contre \d,\d\d %\)\. Vérifiez/.test(s)&&/alerte/.test(s)&&(await ov())<=0, [s,z]);
  ok(`[${w}] aucune erreur JS`, errs.length===0, errs);
  await p.close(); }
 await b.close(); console.log(res.join('\n')); console.log(`\n${res.length-fails}/${res.length} OK`); process.exit(fails?1:0); })();

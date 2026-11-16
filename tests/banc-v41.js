// Banc v41. Bornes réelles relevées en prod pour k=8, α 5 % : type 3 (plan) et type 1 (efficacité seule).
// Les autres demandes (α/m, autres durées) reçoivent des bornes APPROCHÉES de banc : elles ne servent qu'aux contrôles d'interface.
const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v41.html'); const SHOTS=process.argv[3];
const T3=[[3.725,-1.4542],[3.1895,-0.886],[2.847,-0.4025],[2.5754,0.0339],[2.3411,0.4429],[2.1284,0.8366],[1.9236,1.2273],[1.6737,1.6737]];
const T1=[3.725,3.189,2.847,2.576,2.342,2.132,1.937,1.753];
const D=JSON.parse(fs.readFileSync(path.join(__dirname,'donnees-fictives.json'),'utf8'));
const res=[]; let fails=0; const ok=(n,c,i)=>{res.push((c?'✅ ':'❌ ')+n+(i!==undefined?' — '+JSON.stringify(i):''));if(!c)fails++;};
const ninv=p=>{let lo=-8,hi=8;const cdf=x=>{const t=1/(1+0.2316419*Math.abs(x)),d=0.3989423*Math.exp(-x*x/2);let q=d*t*(0.3193815+t*(-0.3565638+t*(1.781478+t*(-1.821256+t*1.330274))));return x>0?1-q:q;};for(let i=0;i<60;i++){const m=(lo+hi)/2;cdf(m)<p?lo=m:hi=m;}return (lo+hi)/2;};
let csv='Test;Semaine;Variation;Visiteurs;Visiteurs convertis (principal);Visiteurs convertis (sécurité)\n';
for(const [t,ws] of Object.entries(D)) ws.forEach((w,i)=>{csv+=`${t};${i+1};A - Contrôle;${w[0].join(';')}\n${t};${i+1};B - Variante;${w[1].join(';')}\n`;});
(async()=>{ const b=await chromium.launch();
 const mk=async(vw,vh)=>{const p=await b.newPage({viewport:{width:vw,height:vh},deviceScaleFactor:1}); p.errs=[]; p.calls=[]; p.on('pageerror',e=>p.errs.push(String(e))); p.on('dialog',d=>d.accept());
  await p.route('**/*',r=>{const u=r.request().url(); if(u.startsWith('file://'))return r.continue();
   if(u.includes('calculate-boundaries')){const q=JSON.parse(r.request().postData()); p.calls.push(q); let bd;
    if(q.k===8&&q.alpha===0.05&&q.beta===0.2&&q.testType===3) bd=T3.map((x,i)=>({stage:i+1,infoFraction:(i+1)/8*1.0856,efficacyZ:x[0],futilityZ:x[1]}));
    else if(q.k===8&&q.alpha===0.05&&q.testType===1) bd=T1.map((x,i)=>({stage:i+1,infoFraction:(i+1)/8*1.0423,efficacyZ:x,futilityZ:null}));
    else { const f=ninv(1-q.alpha)/ninv(0.95); bd=Array.from({length:q.k},(_,i)=>({stage:i+1,infoFraction:(i+1)/q.k*1.08,efficacyZ:(q.k===8?T1[i]:1.75+1.95*(1-(i+1)/q.k))*f,futilityZ:q.testType===1?null:(1.75*f)*(2*(i+1)/q.k-1)})); }
    return r.fulfill({contentType:'application/json',body:JSON.stringify({boundaries:bd})});}
   return r.fulfill({status:200,body:''});});
  await p.goto('file://'+path.resolve(FILE)); await p.waitForTimeout(200); return p;};
 const overflow=p=>p.evaluate(()=>document.scrollingElement.scrollWidth-window.innerWidth);
 const shot=async(p,n)=>{ if(SHOTS) await p.screenshot({path:path.join(SHOTS,n+'.png'),fullPage:true}); };
 { const p=await mk(1280,900); const exp={'T1 - Gagnant':[6,'2,014'],'T2 - Sans effet':[4,'-0,246'],'T3 - Gagnant mais régression sécurité':[2,'1,500']}; const out={};
  for(const [t,e] of Object.entries(exp)){ await p.evaluate(c=>window.GST.openCSV(c,'fictif.csv'),csv);
   await p.selectOption('[data-d=test]',t); await p.click('[data-act=apply]'); await p.waitForTimeout(400);
   const r=await p.evaluate(()=>{const c=window.GST.compute(),s=window.GST.getState();const w=c.weeks[c.decisionWeek];return {dw:c.decisionWeek,title:w&&w.dec.title,z:w&&w.rows[0].st.zAdj,effP:w.rows[0].eff,effG:w.rows[1].eff,stG:w.rows[1].status,banner:document.querySelector('.v-main h3').textContent,g:!!s.boundsG};});
   out[t]=r; ok(`Principale inchangée vs v39.1/v40 — ${t} : arrêt en S${e[0]+1}, Z ${e[1]}`, r.dw===e[0]&&r.z.toFixed(3).replace('.',',')===e[1]&&r.banner===r.title, {titre:r.title,gardeFou:r.stG,borneP:+r.effP.toFixed(4),borneGF:+r.effG.toFixed(4)});
   await p.click('[data-act=new]'); }
  ok('Garde-fou lu sur la borne « efficacité seule » (2,847 en S3 ; 1,937 en S7), pas sur celle du plan (1,9236)', Math.abs(out['T1 - Gagnant'].effG-1.937)<1e-9&&Math.abs(out['T1 - Gagnant'].effP-1.9236)<1e-9, [out['T1 - Gagnant'].effP,out['T1 - Gagnant'].effG]);
  ok('T3 : régression du garde-fou toujours démontrée en S3', /ne pas déployer/.test(out['T3 - Gagnant mais régression sécurité'].title), out['T3 - Gagnant mais régression sécurité'].title);
  ok('Parité : aucune erreur JS', p.errs.length===0, p.errs); await p.close(); }
 for(const [vw,vh,tag] of [[360,740,'360'],[1280,900,'1280']]){ const p=await mk(vw,vh);
  ok(`[${tag}] état zéro sans débordement, 3 étapes, encart confidentialité`, await overflow(p)<=0 && (await p.locator('.steps .card').count())===3 && (await p.locator('.privacy').count())===1, await overflow(p)); await shot(p,tag+'-1-accueil');
  await p.click('[data-act=example]'); await p.waitForTimeout(200); await p.click('[data-act=apply]'); await p.waitForTimeout(600);
  const r=await p.evaluate(()=>{const s=window.GST.getState(),c=window.GST.compute();const w=c.weeks[c.decisionWeek!=null?c.decisionWeek:5];return {rows:document.querySelectorAll('.mrw').length,groups:[...document.querySelectorAll('.grp h3')].map(e=>e.textContent),st:w.rows.map(r=>r.status),effs:w.rows.map(r=>+r.eff.toFixed(3)),chips:[...document.querySelectorAll('.chips .pill')].map(e=>e.textContent),segs:document.querySelectorAll('.segs span').length,dec:document.querySelectorAll('.segs .dec').length,legend:document.querySelectorAll('.legend').length,detail:document.querySelectorAll('.detail table').length,chartBg:getComputedStyle(document.querySelector('.detail svg rect')).fill,vol:document.querySelector('.mrw .hint').textContent,int:document.querySelector('.mrw .int').textContent};});
  ok(`[${tag}] résultats : 7 lignes en 3 blocs, 8 segments dont 1 « décision », légende et détail repliés`, r.rows===7&&r.groups.length===3&&r.segs===8&&r.dec===1&&r.legend===0&&r.detail===0&&/255, 255, 255/.test(r.chartBg), r);
  ok(`[${tag}] volumes et intervalle sous l'écart`, /2.498 \/ 2.688 conversions/.test(r.vol)&&/^de \+/.test(r.int), [r.vol,r.int]);
  ok(`[${tag}] rebond (Z −1,17) affiché « À surveiller », contact « Non conclusif »`, r.st[1]==='WATCH'&&r.st[5]==='AUCUN_SIGNAL', r.st);
  ok(`[${tag}] trois jeux de bornes distincts (plan, garde-fous, secondaires α/4)`, r.effs[0]!==r.effs[1]&&r.effs[2]>r.effs[1]&&r.effs[1]===r.effs[5], r.effs);
  ok(`[${tag}] résultats sans débordement`, await overflow(p)<=0, await overflow(p)); await shot(p,tag+'-2-resultats');
  await p.click('[data-act=legend]'); await p.click('[data-act=detail]'); await p.click('[data-act=unit][data-v=z]'); await p.waitForTimeout(150);
  ok(`[${tag}] légende, détail et bascule Z s'ouvrent sans débordement`, (await p.locator('.legend').count())===1&&(await p.locator('.detail table').count())===1&&(await p.locator('[data-act=unit][data-v=z].on').count())===1&&await overflow(p)<=0, await overflow(p)); await shot(p,tag+'-3-resultats-ouverts');
  await p.selectOption('[data-act=weeksel]','5'); await p.waitForTimeout(200); ok(`[${tag}] historique : relire la semaine 6 ne change pas la décision`, /Vous relisez la semaine 6/.test(await p.textContent('.v-main')));
  await p.click('[data-v=plan]'); await p.waitForTimeout(300); await p.fill('[data-mde=traffic]','20000'); await p.keyboard.press('Tab'); await p.waitForTimeout(80); await p.fill('[data-mde=conv]','1000'); await p.keyboard.press('Tab'); await p.waitForTimeout(1200);
  const pl=await p.evaluate(()=>({big:document.querySelector('.mdebig .num').textContent,rows:[...document.querySelectorAll('.mr2')].map(e=>e.textContent.replace(/\s+/g,' ').trim()),opts:document.querySelectorAll('label.opt').length,mt:document.querySelectorAll('.mt').length,txt:document.querySelector('.pmde').textContent}));
  ok(`[${tag}] plan : MDE séquentiel 8 semaines = 5,65 % (5,42 % × √1,0856), traduit en taux`, pl.big==='5,65 %'&&/5,00 % à 5,28 %/.test(pl.txt)&&/5,42 %/.test(pl.txt), pl.big);
  ok(`[${tag}] plan : tableau des durées, 2 options d'arrêt expliquées, tableau métriques aligné (7 + en-tête)`, pl.rows.length===6&&pl.opts===2&&pl.mt===8&&await overflow(p)<=0, pl.rows); await shot(p,tag+'-4-plan');
  await p.click('[data-v=donnees]'); await p.waitForTimeout(100); ok(`[${tag}] Données sans débordement`, await overflow(p)<=0, await overflow(p));
  ok(`[${tag}] aucune erreur JS`, p.errs.length===0, p.errs); await p.close(); }
 { const p=await mk(1280,900); const T=D['T1 - Gagnant']; const head='Variation;Visiteurs;Visiteurs convertis (principal);Visiteurs convertis (sécurité)\n'; const snap=i=>head+`B - Variante;${T[i][1].join(';')}\nA - Contrôle;${T[i][0].join(';')}\n`;
  await p.evaluate(c=>window.GST.openCSV(c,'s1.csv'),snap(0)); await p.fill('[data-d=k]','8'); await p.locator('[data-d=k]').blur(); await p.fill('[data-d=name]','Mon test'); await p.locator('[data-d=name]').blur(); await p.click('[data-act=apply]'); await p.waitForTimeout(300);
  await p.evaluate(c=>window.GST.openCSV(c,'s2.csv'),snap(1)); await p.click('[data-act=apply]'); await p.waitForTimeout(300);
  let s=await p.evaluate(()=>{const s=window.GST.getState();return {n:s.weeks.length,lab:s.labels.A};}); ok('Instantanés hebdomadaires : 2 fichiers → 2 semaines', s.n===2&&s.lab==='A - Contrôle', s);
  await p.click('[data-act=save]'); await p.reload(); await p.waitForTimeout(200); await p.selectOption('[data-act=load]',{label:'Mon test'}); await p.waitForTimeout(400);
  s=await p.evaluate(()=>{const s=window.GST.getState();return {n:s.weeks.length,b:!!s.bounds,g:!!s.boundsG};}); ok('Sauvegarde puis rechargement (bornes des garde-fous incluses)', s.n===2&&s.b&&s.g, s);
  const old={name:'ancien',isSecondaryKpiPlanned:true,niMarginRel:'1.0',designK:'8',currentDesignParams:{k:8,alpha:0.05,power:0.9,sfu:'KimDeMets',sfl:'HSD',testTypePrincipal:3,testStartDate:'2026-10-05'},weeklyEnteredData:D['T3 - Gagnant mais régression sécurité'].slice(0,3).map((w,i)=>({week:i+1,visitorsACumul:w[0][0],conversionsACumul_P:w[0][1],conversionsASecondaryCumul:w[0][2],visitorsBCumul:w[1][0],conversionsBCumul_P:w[1][1],conversionsBSecondaryCumul:w[1][2]}))};
  await p.evaluate(o=>localStorage.setItem('gstSequentialAnalysis_v321_ancien',JSON.stringify(o)),old); await p.reload(); await p.waitForTimeout(200); await p.selectOption('[data-act=load]',{label:'ancien (ancien format)'}); await p.waitForTimeout(400);
  s=await p.evaluate(()=>{const s=window.GST.getState(),c=window.GST.compute();return {beta:s.plan.beta,dw:c.decisionWeek,t:document.querySelector('.v-main h3').textContent};}); ok('Ancien test v38/v39 converti', s.beta===0.2&&s.dw===2&&/ne pas déployer/.test(s.t), s);
  ok('Parcours 3 : aucune erreur JS', p.errs.length===0, p.errs); await p.close(); }
 await b.close(); console.log(res.join('\n')); console.log(`\n${res.length-fails}/${res.length} OK`); process.exit(fails?1:0); })();

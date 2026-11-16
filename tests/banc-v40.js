// Banc v40 : vrai fichier, API rejouée avec les bornes relevées en prod (k=8, α 5 %, KimDeMets/HSD, β 0,20).
const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v40.html'); const SHOTS=process.argv[3];
const PROD=[[3.725,-1.4542],[3.1895,-0.886],[2.847,-0.4025],[2.5754,0.0339],[2.3411,0.4429],[2.1284,0.8366],[1.9236,1.2273],[1.6737,1.6737]];
const D=JSON.parse(fs.readFileSync(path.join(__dirname,'donnees-fictives.json'),'utf8'));
const res=[]; let fails=0; const ok=(n,c,i)=>{res.push((c?'✅ ':'❌ ')+n+(i!==undefined?' — '+JSON.stringify(i):''));if(!c)fails++;};
let csv='Test;Semaine;Variation;Visiteurs;Visiteurs convertis (principal);Visiteurs convertis (sécurité)\n';
for(const [t,ws] of Object.entries(D)) ws.forEach((w,i)=>{csv+=`${t};${i+1};A - Contrôle;${w[0].join(';')}\n${t};${i+1};B - Variante;${w[1].join(';')}\n`;});
(async()=>{ const b=await chromium.launch();
 const mk=async(vw,vh)=>{const p=await b.newPage({viewport:{width:vw,height:vh},deviceScaleFactor:1}); p.errs=[]; p.calls=[]; p.on('pageerror',e=>p.errs.push(String(e))); p.on('dialog',d=>d.accept());
  await p.route('**/*',r=>{const u=r.request().url(); if(u.startsWith('file://'))return r.continue();
   if(u.includes('calculate-boundaries')){const q=JSON.parse(r.request().postData()); p.calls.push(q);
    if(q.k!==8||q.alpha!==0.05||q.beta!==0.2||q.testType!==3) return r.fulfill({status:500,contentType:'application/json',body:'{"error":true,"message":"plan non enregistré dans le banc"}'});
    return r.fulfill({contentType:'application/json',body:JSON.stringify({boundaries:PROD.map((x,i)=>({stage:i+1,infoFraction:(i+1)/8*1.0856,efficacyZ:x[0],futilityZ:x[1]}))})});}
   return r.fulfill({status:200,body:''});});
  await p.goto('file://'+path.resolve(FILE)); await p.waitForTimeout(200); return p;};
 const overflow=p=>p.evaluate(()=>document.scrollingElement.scrollWidth-window.innerWidth);
 const shot=async(p,n)=>{ if(SHOTS) await p.screenshot({path:path.join(SHOTS,n+'.png'),fullPage:true}); };
 // 1. Parité avec la v39.1 sur les trois scénarios fictifs
 { const p=await mk(1280,900); const exp={'T1 - Gagnant':[6,'déploiement recommandé','2,014'],'T2 - Sans effet':[4,'non concluant','-0,246'],'T3 - Gagnant mais régression sécurité':[2,'ne pas déployer','1,500']};
  for(const [t,e] of Object.entries(exp)){ await p.evaluate(c=>window.GST.openCSV(c,'fictif.csv'),csv);
   await p.selectOption('[data-d=test]',t); await p.click('[data-act=apply]'); await p.waitForTimeout(300);
   const r=await p.evaluate(()=>{const c=window.GST.compute();const w=c.weeks[c.decisionWeek];return {dw:c.decisionWeek,title:w&&w.dec.title,z:w&&w.rows[0].st.zAdj,zS:w&&w.rows[1].st.zAdj,banner:document.querySelector('.banner h3').textContent,roles:window.GST.getState().metrics.map(m=>m.role)};});
   ok(`Parité v39.1 ${t} : décision S${e[0]+1} « ${e[1]} »`, r.dw===e[0]&&r.title.toLowerCase().includes(e[1])&&r.z.toFixed(3).replace('.',',').replace('−','-')===e[2]&&r.banner===r.title, {dw:r.dw,title:r.title,z:+r.z.toFixed(3),zS:+r.zS.toFixed(3),roles:r.roles});
   await p.click('[data-act=new]'); }
  ok('Un seul appel API par test (3 tests)', p.calls.length===3, p.calls.length); ok('Parité : aucune erreur JS', p.errs.length===0, p.errs); await p.close(); }
 // 2. Exemple 7 métriques, aux deux largeurs
 for(const [vw,vh,tag] of [[360,740,'360'],[1280,900,'1280']]){ const p=await mk(vw,vh);
  ok(`[${tag}] accueil sans débordement horizontal`, await overflow(p)<=0, await overflow(p)); await shot(p,tag+'-1-accueil');
  await p.click('[data-act=example]'); await p.waitForTimeout(200); ok(`[${tag}] import : 7 métriques détectées, pas de débordement`, (await p.locator('.mrow').count())===7 && await overflow(p)<=0, [await p.locator('.mrow').count(), await overflow(p)]); await shot(p,tag+'-2-import');
  await p.click('[data-act=apply]'); await p.waitForTimeout(400);
  const r=await p.evaluate(()=>{const s=window.GST.getState(),c=window.GST.compute();const w=c.weeks[5];return {k:s.plan.k,n:s.weeks.length,roles:s.metrics.map(m=>m.role+'/'+m.sens+'/'+m.type),rows:document.querySelectorAll('.sc .mr').length,dw:c.decisionWeek,title:document.querySelector('.banner h3').textContent,ca:w.rows[6].st,achat:w.rows[0].st.zAdj,rebond:w.rows[1].st,chart:!!document.querySelector('.detail svg path'),bg:getComputedStyle(document.querySelector('.detail svg rect')).fill};});
  ok(`[${tag}] résultats : 7 lignes, 6 semaines sur 8, graphique à fond blanc`, r.rows===7&&r.n===6&&r.k===8&&r.chart&&/255, 255, 255/.test(r.bg), {roles:r.roles,dw:r.dw,title:r.title,bg:r.bg});
  ok(`[${tag}] Z achat S6 = 3,703 (calcul indépendant)`, Math.abs(r.achat-3.7029)<5e-4, r.achat);
  ok(`[${tag}] Z continu CA S6 = 2,774 (Welch, calcul indépendant)`, Math.abs(r.ca.zAdj-2.7739)<5e-4, r.ca.zAdj);
  ok(`[${tag}] rebond « baisse favorable » : Z orienté = −Z brut`, Math.abs(r.rebond.zAdj+r.rebond.z)<1e-12&&r.rebond.z>0, [r.rebond.z,r.rebond.zAdj]);
  ok(`[${tag}] résultats sans débordement horizontal`, await overflow(p)<=0, await overflow(p)); await shot(p,tag+'-3-resultats');
  await p.click('.sc .mr >> nth=1'); await p.waitForTimeout(100); ok(`[${tag}] clic sur un garde-fou : détail mis à jour`, (await p.textContent('.detail h3'))==='Visiteurs avec rebond'); await shot(p,tag+'-4-detail-garde-fou');
  await p.click('[data-v=donnees]'); await p.waitForTimeout(100); ok(`[${tag}] Données sans débordement`, await overflow(p)<=0, await overflow(p)); await shot(p,tag+'-5-donnees');
  await p.click('[data-v=plan]'); await p.waitForTimeout(100); await p.click('[data-mde=traffic]'); await p.keyboard.type('20000'); await p.keyboard.press('Tab'); await p.waitForTimeout(80); const foc=await p.evaluate(()=>document.activeElement.getAttribute('data-mde')); await p.keyboard.type('1000'); await p.keyboard.press('Tab'); await p.waitForTimeout(100); ok(`[${tag}] le focus suit la tabulation après une saisie`, foc==='conv', foc);
  const mde=await p.evaluate(()=>document.querySelectorAll('tr.pick')[7].cells[1].textContent);
  ok(`[${tag}] MDE 8 semaines = 5,42 % (identique v39.1) ; Plan sans débordement`, mde==='5,42 %'&&await overflow(p)<=0, [mde, await overflow(p)]); await shot(p,tag+'-6-plan');
  ok(`[${tag}] aucune erreur JS`, p.errs.length===0, p.errs); await p.close(); }
 // 3. Instantané hebdomadaire (sans colonne Semaine), contrôles de saisie, sauvegarde, ancien format
 { const p=await mk(1280,900); const T=D['T1 - Gagnant']; const head='Variation;Visiteurs;Visiteurs convertis (principal);Visiteurs convertis (sécurité)\n';
  const snap=i=>head+`B - Variante;${T[i][1].join(';')}\nA - Contrôle;${T[i][0].join(';')}\n`;
  await p.evaluate(c=>window.GST.openCSV(c,'s1.csv'),snap(0)); await p.fill('[data-d=k]','8'); await p.locator('[data-d=k]').blur(); await p.fill('[data-d=name]','Mon test'); await p.locator('[data-d=name]').blur(); await p.click('[data-act=apply]'); await p.waitForTimeout(300);
  await p.evaluate(c=>window.GST.openCSV(c,'s2.csv'),snap(1)); await p.click('[data-act=apply]'); await p.waitForTimeout(300);
  let s=await p.evaluate(()=>{const s=window.GST.getState();return {n:s.weeks.length,a:s.weeks[1].A.n,lab:s.labels.A,calls:0};});
  ok('Instantanés : 2 fichiers → 2 semaines, contrôle reconnu même en 2e ligne', s.n===2&&s.a===T[1][0][0]&&s.lab==='A - Contrôle', s);
  await p.evaluate(c=>window.GST.openCSV(c,'s1.csv'),snap(0)); await p.click('[data-act=apply]'); await p.waitForTimeout(200);
  ok('Fichier non cumulé refusé avec message', /cumul/.test(await p.textContent('.err')), (await p.textContent('.err')).slice(0,90)); await p.click('[data-act=cancel]');
  await p.evaluate(()=>window.GST.openCSV('Variation;Visiteurs;Visiteurs convertis (principal);Visiteurs convertis (sécurité)\nA - Contrôle;30000;40000;10\nB - Variante;30000;5;10\n','bad.csv')); await p.click('[data-act=apply]'); await p.waitForTimeout(200);
  ok('Conversions > visiteurs refusées', /dépasse/.test(await p.textContent('.err'))); await p.click('[data-act=cancel]');
  await p.click('[data-act=save]'); await p.reload(); await p.waitForTimeout(200); await p.selectOption('[data-act=load]',{label:'Mon test'}); await p.waitForTimeout(300);
  s=await p.evaluate(()=>{const s=window.GST.getState();return {n:s.weeks.length,name:s.name,b:!!s.bounds};}); ok('Sauvegarde puis rechargement', s.n===2&&s.name==='Mon test'&&s.b, s);
  const old={name:'ancien',isSecondaryKpiPlanned:true,niMarginRel:'1.0',designK:'8',currentDesignParams:{k:8,alpha:0.05,power:0.9,sfu:'KimDeMets',sfl:'HSD',testTypePrincipal:3,testStartDate:'2026-10-05'},weeklyEnteredData:D['T3 - Gagnant mais régression sécurité'].slice(0,3).map((w,i)=>({week:i+1,visitorsACumul:w[0][0],conversionsACumul_P:w[0][1],conversionsASecondaryCumul:w[0][2],visitorsBCumul:w[1][0],conversionsBCumul_P:w[1][1],conversionsBSecondaryCumul:w[1][2]}))};
  await p.evaluate(o=>localStorage.setItem('gstSequentialAnalysis_v321_ancien',JSON.stringify(o)),old); await p.reload(); await p.waitForTimeout(200); await p.selectOption('[data-act=load]',{label:'ancien (ancien format)'}); await p.waitForTimeout(300);
  s=await p.evaluate(()=>{const s=window.GST.getState(),c=window.GST.compute();return {beta:s.plan.beta,dw:c.decisionWeek,t:document.querySelector('.banner h3').textContent};});
  ok('Test v38/v39 converti : β 0,20 conservé, régression sécurité en S3', s.beta===0.2&&s.dw===2&&/ne pas déployer/.test(s.t), s);
  ok('Parcours 3 : aucune erreur JS', p.errs.length===0, p.errs); await p.close(); }
 await b.close(); console.log(res.join('\n')); console.log(`\n${res.length-fails}/${res.length} OK`); process.exit(fails?1:0); })();

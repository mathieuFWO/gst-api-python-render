// Banc v56-35 : pas d'arrêt pour futilité avant la semaine 2 (jour 14 en suivi quotidien) ; référence de trafic sans plan.
const { chromium } = require('playwright'); const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-35.html');
const res=[]; let fails=0; const ok=(n,c,i)=>{res.push((c?'✅ ':'❌ ')+n+(i!==undefined?' — '+JSON.stringify(i):''));if(!c)fails++;};
const csv=(a,b)=>'MVT - Variante;Visiteurs;Visiteurs convertis\n0Original;'+a.join(';')+'\n2093615Variation 1;'+b.join(';')+'\n';
(async()=>{ const b=await chromium.launch();
 for(const vw of [360,1280]){ const p=await b.newPage({viewport:{width:vw,height:900}});p.errs=[];p.on('pageerror',e=>p.errs.push(String(e)));p.on('dialog',d=>d.accept());
  await p.route('**/*',r=>r.request().url().startsWith('file://')?r.continue():r.fulfill({status:200,body:''}));await p.goto('file://'+path.resolve(FILE));await p.waitForTimeout(200);
  const setD=async(f,v)=>{await p.fill('[data-d='+f+']',v);await p.dispatchEvent('[data-d='+f+']','change');await p.waitForTimeout(250);};
  const imp=async(c,end)=>{await p.evaluate(c=>window.GST.openCSV(c,'t.csv'),c);await p.waitForTimeout(300);if(end)await setD('endDate',end);else await setD('startDate','2026-10-07');await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()}));await p.waitForTimeout(250);await p.click('[data-act=apply]');await p.waitForTimeout(2500);};
  const snap=()=>p.evaluate(()=>{const c=window.GST.compute(),s=window.GST.getState();return {dw:c.decisionWeek,kind:c.weeks[c.weeks.length-1].dec.kind,h3:document.querySelector('#gst-app .verdict h3').textContent,nofut:(document.querySelector('#gst-app .nofut')||{}).textContent||'',fut:s.bounds.fut.map(x=>x==null?null:+x.toFixed(3)),z:+c.weeks[c.weeks.length-1].rows[0].st.zAdj.toFixed(2),q:[...document.querySelectorAll('#gst-app .tp-k')].map(x=>x.textContent.replace(/\s+/g,' ').trim())[1],al:document.querySelector('#gst-app .tp-q h4').textContent,dash:document.querySelectorAll('#gst-app [data-chart] path[stroke-dasharray="3 8"]').length,ov:document.scrollingElement.scrollWidth-innerWidth};});
  await imp(csv([83028,4259],[83460,4098]));let s=await snap();
  ok(vw+' : semaine 1, Z = -2,05 : le test continue, aucune borne de futilité en semaine 1, mention affichée',s.dw===null&&s.h3==='Continuer le test'&&s.fut[0]===null&&s.fut[1]!==null&&s.z===-2.05&&/avant la semaine 2/.test(s.nofut),s);
  ok(vw+' : la ligne de futilité du graphique existe et l\'écran ne déborde pas',s.dash===1&&s.ov<=0,s);
  ok(vw+' : sans trafic prévu, la semaine 1 sert de référence et donne l\'effet détectable (2,7 %)',/Trafic de référence : semaine 1/.test(s.q)&&/166 488 visiteurs/.test(s.q.replace(/ | /g,' '))&&/environ 2,7 %/.test(s.q)&&s.al==='Aucune alerte',s.q);
  await imp(csv([166056,8518],[166920,8400]),'2026-10-20');s=await snap();
  ok(vw+' : semaine 2, écart toujours défavorable : la futilité arrête le test en semaine 2',s.dw===1&&s.kind==='fut'&&s.h3==='Arrêter le test'&&!s.nofut,s);
  ok(vw+' : semaine 2 au même rythme : « Trafic conforme au rythme de la semaine 1 »',/Trafic conforme au rythme de la semaine 1/.test(s.q)&&s.al==='Aucune alerte',s.q);
  ok(vw+' : aucune erreur de script',p.errs.length===0,p.errs);await p.close();
  // trafic en chute en semaine 2 : alerte
  const q=await b.newPage({viewport:{width:vw,height:900}});q.on('dialog',d=>d.accept());await q.route('**/*',r=>r.request().url().startsWith('file://')?r.continue():r.fulfill({status:200,body:''}));await q.goto('file://'+path.resolve(FILE));await q.waitForTimeout(200);
  const run=async(c,f,v)=>{await q.evaluate(c=>window.GST.openCSV(c,'t.csv'),c);await q.waitForTimeout(300);await q.fill('[data-d='+f+']',v);await q.dispatchEvent('[data-d='+f+']','change');await q.waitForTimeout(250);await q.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()}));await q.waitForTimeout(250);await q.click('[data-act=apply]');await q.waitForTimeout(2500);};
  await run(csv([83028,4259],[83460,4290]),'startDate','2026-10-07');await run(csv([110000,5640],[110500,5690]),'endDate','2026-10-20');
  const t=await q.evaluate(()=>({q:[...document.querySelectorAll('#gst-app .tp-k')].map(x=>x.textContent.replace(/\s+/g,' ').trim())[1],al:document.querySelector('#gst-app .tp-q h4').textContent}));
  ok(vw+' : semaine 2 à 66 % du rythme de la semaine 1 : alerte « Trafic sous le rythme de la semaine 1 »',/Trafic sous le rythme de la semaine 1/.test(t.q)&&/66 %/.test(t.q)&&/alerte/.test(t.al)&&!/Aucune/.test(t.al),t);await q.close();
 }
 // règle « Seulement s'il gagne » et plan à trafic saisi : inchangés ; plans lus directement
 const p=await b.newPage();await p.route('**/*',r=>r.request().url().startsWith('file://')?r.continue():r.fulfill({status:200,body:''}));await p.goto('file://'+path.resolve(FILE));await p.waitForTimeout(200);
 const D=await p.evaluate(()=>{const P=(o)=>window.GST.design(Object.assign({alpha:0.05,power:0.8,beta:0.2,sfu:'KimDeMets',sfl:'HSD',unit:'semaine'},o));return {t1:P({k:4,testType:1}).fut,k2:P({k:2,testType:3}).fut,k8:P({k:8,testType:3}).fut,j28:P({k:28,testType:3,unit:'jour'}).fut,j10:P({k:10,testType:3,unit:'jour'}).fut};});
 ok('plans : efficacité seule sans futilité ; 2 semaines : futilité à la fin seulement ; 8 semaines : à partir de la 2e',D.t1.every(x=>x==null)&&D.k2[0]===null&&D.k2[1]!=null&&D.k8[0]===null&&D.k8.slice(1).every(x=>x!=null),{k2:D.k2,k8:D.k8.slice(0,3)});
 ok('suivi quotidien : aucune futilité avant le jour 14 (28 jours) ; sur 10 jours, seulement le dernier',D.j28.slice(0,13).every(x=>x==null)&&D.j28.slice(13).every(x=>x!=null)&&D.j10.slice(0,9).every(x=>x==null)&&D.j10[9]!=null,{j28:D.j28.slice(11,15)});
 console.log(res.join('\n'));console.log(fails?`❌ ${fails} échec(s) sur ${res.length}`:`✅ ${res.length}/${res.length}`);await b.close();process.exit(fails?1:0);})();

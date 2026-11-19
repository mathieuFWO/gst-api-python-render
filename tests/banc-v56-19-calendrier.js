// v56.19 : numérotation par le calendrier (semaines sautées), durée par défaut, cohérence date de début / lectures
const {chromium}=require('playwright');const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-19.html');
let n=0,okc=0;const ok=(l,c,d)=>{n++;if(c)okc++;console.log((c?'✅ ':'❌ ')+l+(d!==undefined?' — '+JSON.stringify(d):''));};
const D=k=>{const d=new Date();d.setDate(d.getDate()+k);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};const fr=i=>i.slice(8)+'/'+i.slice(5,7)+'/'+i.slice(0,4);
const F=(m,cr)=>'Variation;Visiteurs;Achats\nA - Contrôle;'+Math.round(10000*m)+';'+Math.round(500*m)+'\nB - Variante;'+Math.round(10030*m)+';'+Math.round(500*m*(cr||1.02))+'\n';
(async()=>{const b=await chromium.launch();
const mk=async(w)=>{const p=await b.newPage({viewport:{width:w,height:900}});p.__errs=[];p.on('pageerror',e=>p.__errs.push(String(e)));p.on('dialog',d=>d.accept());await p.goto('file://'+path.resolve(FILE));await p.waitForSelector('.cta button');
  p.txt=s=>p.evaluate(s=>{const e=document.querySelector('#gst-app '+s);return e?e.innerText:'';},s);p.set=async(s,v)=>{await p.fill(s,v);await p.locator(s).blur();await p.waitForTimeout(250);};
  p.imp=async(csv,o)=>{if(await p.locator('[data-act=tab][data-v=donnees]').count()){await p.locator('[data-act=tab][data-v=donnees]').click();await p.waitForTimeout(200);}await p.evaluate(c=>window.GST.openCSV(c,'s.csv'),csv);await p.waitForSelector('.dv');if(o.start)await p.set('[data-d=startDate]',o.start);if(o.end)await p.set('[data-d=endDate]',o.end);if(o.k)await p.set('[data-d=k]',String(o.k));};
  p.go=async()=>{await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()})).then(()=>p.waitForTimeout(200)).then(()=>p.click('[data-act=apply]'));await p.waitForTimeout(1100);};p.st=()=>p.evaluate(()=>{const s=GST.getState(),c=GST.compute();return {n:s.weeks.length,wk:s.weeks.map(x=>x.wk),eff:s.bounds?s.bounds.eff.map(v=>Math.round(v*1e4)/1e4):null,fut:s.bounds?s.bounds.fut.map(v=>v==null?null:Math.round(v*1e4)/1e4):null,dec:c.weeks.map(x=>x.dec.title),stop:c.weeks.map(x=>x.dec.stop),k:s.plan.k};});p.ov=()=>p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);return p;};
for(const w of [360,1280]){
 // A. plan de 4 semaines, semaine 2 sautée
 const p=await mk(w);await p.imp(F(1),{start:D(-28),end:D(-22),k:4});
 ok(`[${w}] 1er import : 7 jours → lecture de la semaine 1 sur 4`,/lecture de la semaine 1 sur 4/.test(await p.txt('.dv-gate')));await p.go();const E1=(await p.st()).eff[0];
 await p.imp(F(3),{end:D(-8)});const g=await p.txt('.dv-gate');
 ok(`[${w}] import à J21 après une lecture à J7 : semaine 3, la semaine 2 annoncée sans lecture`,/lecture de la semaine 3 sur 4/.test(g)&&/La semaine 2 reste sans lecture/.test(g)&&/semaine 3/.test(await p.txt('.dv .muted')),g);await p.go();
 let s=await p.st();const side=await p.txt('.v-side'),main=await p.txt('.v-main');
 ok(`[${w}] état : 2 lectures en semaines 1 et 3, plan recalculé sur 3 lectures`,s.n===2&&s.wk.join()==='1,3'&&s.eff.length===3&&s.k===4,s);
 ok(`[${w}] affichage : « Semaine 3 sur 4 », semaine 2 en pointillé, prochaine analyse en semaine 4, sans débordement`,/Sans lecture : S2/.test(main)&&/semaine 3 sur les 4 prévues/i.test(main)&&(/semaine 4 nécessaire/.test(main)||s.stop[1])&&(await p.evaluate(()=>[...document.querySelectorAll('#gst-app .segs span')].map(e=>e.className.split(' ')[0]).join()))==='done,skip,done,todo'&&(await p.ov())<=0,(await p.evaluate(()=>[...document.querySelectorAll('#gst-app .segs span')].map(e=>e.className).join())));
 ok(`[${w}] historique et tableau numérotés par semaine réelle`,(await p.evaluate(()=>[...document.querySelectorAll('#gst-app [data-act=weeksel] option')].map(o=>o.text.replace(/ : décision/,'')).join()))==='Semaine 1,Semaine 3');
 await p.imp(F(4),{end:D(-1)});ok(`[${w}] import à J28 : lecture de la semaine 4 sur 4`,/lecture de la semaine 4 sur 4/.test(await p.txt('.dv-gate')));await p.go();s=await p.st();
 ok(`[${w}] J28 : dernière lecture, décision finale (plus de « Continuer »), 3 lectures en semaines 1, 3, 4`,s.n===3&&s.wk.join()==='1,3,4'&&s.stop[2]===true&&!/^Continuer/.test(s.dec[2])&&/semaine 4 sur les 4 prévues|4 semaines sur 4|Semaine 4 importée après la décision/i.test(await p.txt('.verdict')),s.dec);
 const A=s;
 // B. le seuil de la semaine 1 ne bouge pas quand une semaine est sautée ensuite ; le risque suit le calendrier
 const q=await mk(w);await q.imp(F(1),{start:D(-28),end:D(-22),k:4});await q.go();const B1=await q.st();await q.imp(F(2),{end:D(-15)});await q.go();await q.imp(F(3),{end:D(-8)});await q.go();await q.imp(F(4),{end:D(-1)});await q.go();const B=await q.st();
 ok(`[${w}] semaine 1 : même seuil avec ou sans saut ensuite (${B1.eff[0]}), et identique avant et après le saut`,A.eff[0]===B.eff[0]&&B1.eff[0]===B.eff[0]&&E1===A.eff[0],{sansSaut:B.eff,avecSaut:A.eff,avant:E1});
 ok(`[${w}] sans saut : 4 lectures en semaines 1 à 4, seuil final proche de celui avec saut`,B.n===4&&B.wk.join()==='1,2,3,4'&&Math.abs(B.eff[3]-A.eff[2])<0.05,{sansSaut:B.eff[3],avecSaut:A.eff[2]});
 await q.close();
 // C. cinquième lecture impossible
 await p.imp(F(5),{end:D(-1)});await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()})).then(()=>p.waitForTimeout(200)).then(()=>p.click('[data-act=apply]'));await p.waitForTimeout(400);ok(`[${w}] après la semaine 4 sur 4 : plus aucun import accepté`,(await p.locator('.dv').count())===1,(await p.txt('.dv .err')).slice(0,90));
 ok(`[${w}] aucune erreur JS (scénario A)`,p.__errs.length===0,p.__errs);await p.close();
 // D. premier import tardif
 const r=await mk(w);await r.imp(F(3),{start:D(-22),end:D(-1)});
 ok(`[${w}] 1er import avec 22 jours : durée proposée 4 (plus 2), lecture de la semaine 3 sur 4`,(await r.inputValue('[data-d=k]'))==='4'&&/lecture de la semaine 3 sur 4/.test(await r.txt('.dv-gate')),await r.inputValue('[data-d=k]'));await r.go();let t=await r.st();
 ok(`[${w}] 1 lecture en semaine 3, plan réduit à 2 lectures, « semaine 3 sur 4 » affiché`,t.n===1&&t.wk[0]===3&&t.eff.length===2&&/semaine 3 sur les 4 prévues/i.test(await r.txt('.verdict')),t);await r.close();
 const r2=await mk(w);await r2.imp(F(4),{start:D(-28),end:D(-1)});ok(`[${w}] 1er import avec 28 jours : semaine 4 sur 4`,/lecture de la semaine 4 sur 4/.test(await r2.txt('.dv-gate')));await r2.go();t=await r2.st();
 ok(`[${w}] lecture unique en semaine 4 sur 4 : décision finale rendue, sans erreur`,t.n===1&&t.wk[0]===4&&t.stop[0]===true&&r2.__errs.length===0&&!/impossible/.test(await r2.txt('')),{dec:t.dec,eff:t.eff,errs:r2.__errs});await r2.close();
 const r3=await mk(w);await r3.imp(F(6),{start:D(-43),end:D(-1),k:4});ok(`[${w}] données au-delà de la durée prévue : refusé, date d'arrêt de l'export donnée`,/plus que la durée prévue \(4\)/.test(await r3.txt('.dv-gate'))&&(await r3.txt('.dv-gate')).includes(fr(D(-16))),await r3.txt('.dv-gate'));await r3.close();
 // E. règle des 7 jours et date de début modifiée dans le Plan
 const u=await mk(w);await u.imp(F(1),{start:D(-9),end:D(-2),k:4});await u.go();
 await u.locator('[data-act=tab][data-v=plan]').click();await u.waitForTimeout(300);await u.set('[data-p=startDate]',D(-15));await u.click('[data-act=applyplan]');await u.waitForTimeout(900);t=await u.st();
 ok(`[${w}] Plan : début reculé de 6 jours → la lecture existante passe en semaine 2`,t.wk[0]===2,t.wk);
 await u.imp(F(1.2),{end:D(-1)});const g2=await u.txt('.dv-gate');await u.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()})).then(()=>u.waitForTimeout(200)).then(()=>u.click('[data-act=apply]'));await u.waitForTimeout(400);
 ok(`[${w}] contournement fermé : import le lendemain refusé même après avoir déplacé le début`,(await u.locator('.dv').count())===1&&/Pas de nouvelle semaine complète/.test(g2),g2.slice(0,110));await u.click('[data-act=cancel]');
 await u.locator('[data-act=tab][data-v=plan]').click();await u.waitForTimeout(300);await u.set('[data-p=startDate]',D(-4));await u.click('[data-act=applyplan]');await u.waitForTimeout(500);
 ok(`[${w}] Plan : début postérieur aux données déjà lues → refusé avec explication`,/ne correspond pas aux lectures déjà importées/.test(await u.txt(''))&&(await u.st()).wk[0]===2);
 await u.set('[data-p=startDate]','1900-01-01');await u.click('[data-act=applyplan]');await u.waitForTimeout(400);ok(`[${w}] Plan : début au 01/01/1900 refusé`,/Date de début invalide/.test(await u.txt('')));
 ok(`[${w}] aucune erreur JS (scénario E)`,u.__errs.length===0,u.__errs);await u.close();}
console.log('\n'+okc+'/'+n+' OK');await b.close();process.exit(okc===n?0:1);})();

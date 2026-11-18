// v44 : trafic prévu, fin anticipée quand le volume prévu est atteint, stabilité des bornes. Calcul réel (aucune borne simulée).
const { chromium } = require('playwright'); const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-14.html');
let fails=0; const ok=(n,c,i)=>{console.log((c?'✅ ':'❌ ')+n+(i!==undefined?' — '+JSON.stringify(i):''));if(!c)fails++;};
(async()=>{const b=await chromium.launch(); for(const vw of [360,1280]){ const p=await b.newPage({viewport:{width:vw,height:900}}); const errs=[]; p.on('pageerror',e=>errs.push(String(e))); p.on('dialog',d=>d.accept());
 await p.route('**/*',r=>r.request().url().startsWith('file://')?r.continue():r.fulfill({status:200,body:''}));
 await p.goto('file://'+path.resolve(FILE)); await p.click('[data-act=example]'); await p.waitForTimeout(2700);
 const a=await p.evaluate(()=>{const s=GST.getState(),c=GST.compute();return {eff:s.bounds.eff.slice(),end:s.bounds.end,dw:c.decisionWeek,t:c.weeks[c.decisionWeek].dec.title,src:s.bounds.src};});
 ok(`[${vw}] sans trafic prévu : calcul local, pas de fin anticipée, décision en S5`, a.src==='local'&&a.end==null&&a.dw===4, a.t);
 await p.click('[data-v=plan]'); await p.waitForTimeout(300); await p.fill('[data-mde=traffic]','5000'); await p.keyboard.press('Tab'); await p.waitForTimeout(300); await p.click('[data-act=applyplan]'); await p.waitForTimeout(3000);
 await p.click('[data-v=resultats]'); await p.waitForTimeout(800);
 const c=await p.evaluate(()=>{const s=GST.getState(),c=GST.compute();return {traffic:s.plan.traffic,eff:s.bounds.eff,fut:s.bounds.fut,end:s.bounds.end,dw:c.decisionWeek,after:c.weeks.map(w=>w.dec.title),svg:document.querySelectorAll('.detail svg').length,ov:document.scrollingElement.scrollWidth-innerWidth,minB:Math.min(...s.bounds.eff.filter(x=>x!=null))};});
 ok(`[${vw}] trafic prévu au tiers du réel : fin anticipée, aucune borne à −40, graphique tracé, pas de débordement`, c.traffic===5000&&c.end!=null&&c.minB>0&&c.svg===1&&c.ov<=0&&c.dw!=null&&c.dw<=c.end, {end:c.end,dw:c.dw,eff:c.eff.map(x=>x==null?null:+x.toFixed(3))});
 ok(`[${vw}] après la dernière lecture : « En attente », jamais « gain démontré »`, c.after.slice(c.end+1).every(t=>t==='En attente'), c.after);
 ok(`[${vw}] bornes des semaines déjà lues inchangées par le trafic prévu côté efficacité S1`, Math.abs(c.eff[0]-a.eff[0])<1e-9);
 ok(`[${vw}] aucune erreur JS`, errs.length===0, errs); await p.close(); }
 await b.close(); process.exit(fails?1:0);})();

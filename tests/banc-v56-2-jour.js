const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
(async()=>{const b=await chromium.launch();const out={};
for(const w of [360,1280]){const p=await b.newPage({viewport:{width:w,height:900}});const errs=[];p.on('pageerror',e=>errs.push(String(e)));p.on('dialog',d=>d.accept());
await p.goto('file://'+path.join(__dirname,'..','calculateur-sequentiel-v56-2.html'));await p.waitForSelector('.imp');
const txt=async()=>p.evaluate(()=>document.querySelector('#gst-app').innerText);const ov=async()=>p.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
const home=await txt();
await p.click('[data-act=howto][data-v=manuel]');await p.fill('[data-man=name]','Promo semaine 12');await p.fill('[data-man=m0name]','Visiteurs avec achat');await p.fill('[data-man=m1name]','Rebond semaine');await p.locator('[data-man=m1name]').blur();await p.click('[data-act=manstep]');await p.waitForTimeout(200);await p.click('[data-act=mank][data-v="4"]');await p.waitForTimeout(150);await p.click('[data-act=manstart]');await p.waitForTimeout(300);
await p.click('[data-v=plan]');await p.waitForTimeout(300);const planS=await txt();
await p.selectOption('[data-p=unit]','jour');await p.waitForTimeout(300);
await p.fill('[data-mde=traffic]','40000');await p.keyboard.press('Tab');await p.fill('[data-mde=conv]','2000');await p.keyboard.press('Tab');await p.waitForTimeout(6000);
const planJ=await txt();const kJ=await p.inputValue('[data-p=k]');await p.screenshot({path:(process.argv[2]||'.')+'/'+w+'-plan-jour.png',fullPage:true});const ovPlan=await ov();
await p.click('[data-act=applyplan]');await p.waitForTimeout(500);
const ids=await p.evaluate(()=>GST.getState().metrics.map(m=>m.id));
const add=async(n,a,bb,r1,r2)=>{if(!(await p.locator('[data-mw="A|n"]').count())){await p.click('[data-v=donnees]');await p.waitForTimeout(150);if(!(await p.locator('[data-mw="A|n"]').count()))await p.click('[data-act=manual]');await p.waitForTimeout(150);}
 await p.fill('[data-mw="A|n"]',String(n));await p.fill('[data-mw="B|n"]',String(n));await p.fill(`[data-mw="A|${ids[0]}|c"]`,String(a));await p.fill(`[data-mw="B|${ids[0]}|c"]`,String(bb));await p.fill(`[data-mw="A|${ids[1]}|c"]`,String(r1));await p.fill(`[data-mw="B|${ids[1]}|c"]`,String(r2));await p.click('[data-act=addweek]');await p.waitForTimeout(1500);};
await add(600,30,36,240,238);const r1=await txt();await p.screenshot({path:(process.argv[2]||'.')+'/'+w+'-jour1.png',fullPage:true});
await p.click('[data-v=donnees]');await p.waitForTimeout(200);const donn=await txt();
await add(5700,285,420,2280,2270);await add(11400,570,840,4560,4550);await p.waitForTimeout(600);const r3early=await txt();for(let d=4;d<=8;d++)await add(5700*d,285*d,420*d,2280*d,2270*d);await p.waitForTimeout(800);
const r3=await txt();const ovR=await ov();await p.screenshot({path:(process.argv[2]||'.')+'/'+w+'-jour3.png',fullPage:true});
const st=await p.evaluate(()=>{const s=GST.getState(),c=GST.compute();return {unit:s.plan.unit,k:s.plan.k,dw:c.decisionWeek,eff:s.bounds.eff.slice(0,9),fut:s.bounds.fut.slice(0,9),skip:s.bounds.skip};});
const all=[planJ,r1,donn,r3].join('\n');const left=all.split('\n').filter(l=>/semaine/i.test(l));
out[w]={kJ,st,early:[/Pas de décision avant le jour 7/.test(r3early),/ACQUISE/i.test(r3early)],ovPlan,ovR,errs,semaineHomePlanS:[/semaine/i.test(home),/Chaque semaine \(recommandé\)/.test(planS)],ctl:/[\u0001\u0002]/.test(all+home+planS),left};
if(w===360)fs.writeFileSync((process.argv[2]||'.')+'/texte-jour.txt',['--- PLAN',planJ,'--- JOUR 1',r1,'--- DONNEES',donn,'--- JOUR 3',r3].join('\n'));await p.close();}
console.log(JSON.stringify(out,null,1));await b.close();})();

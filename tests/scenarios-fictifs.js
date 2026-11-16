const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
const H=fs.readFileSync(path.join(__dirname,'banc-front.js'),'utf8');
const STUB_J=H.match(/jstat: `([^`]+)`/)[1], STUB_H=H.match(/highcharts: `([^`]+)`/)[1];
const PROD02=[[0.1357,3.725,-1.4542],[0.2714,3.1895,-0.886],[0.4071,2.847,-0.4025],[0.5428,2.5754,0.0339],[0.6785,2.3411,0.4429],[0.8142,2.1284,0.8366],[0.9499,1.9236,1.2273],[1.0856,1.6737,1.6737]];
const zP=(vA,cA,vB,cB)=>{const p=(cA+cB)/(vA+vB);return (cB/vB-cA/vA)/Math.sqrt(p*(1-p)*(1/vA+1/vB));};
const D=JSON.parse(fs.readFileSync(path.join(__dirname,'donnees-fictives.json'),'utf8'));
(async()=>{ const b=await chromium.launch();
 for(const name of Object.keys(D)){ const p=await b.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(String(e))); p.on('dialog',d=>d.accept()); const calls=[];
  await p.route('**/*',r=>{const u=r.request().url(); if(u.startsWith('file://'))return r.continue();
   if(u.includes('calculate-boundaries')){const q=JSON.parse(r.request().postData()); calls.push(q);
     if(q.k!==8||q.beta!==0.2||q.testType!==3) return r.fulfill({status:599,body:'{"error":true}'});
     const res={boundaries:PROD02.map((x,i)=>({stage:i+1,infoFraction:x[0],efficacyZ:x[1],futilityZ:x[2]})),parameters:{k:8,testType:3}};
     if(q.visitors_a!==undefined) res.observedZ=+zP(q.visitors_a,q.conversions_a,q.visitors_b,q.conversions_b).toFixed(5);
     return r.fulfill({contentType:'application/json',body:JSON.stringify(res)});}
   if(u.includes('jstat'))return r.fulfill({contentType:'application/javascript',body:STUB_J});
   if(u.includes('highcharts'))return r.fulfill({contentType:'application/javascript',body:u.endsWith('highcharts.js')?STUB_H:''});
   if(u.includes('jquery'))return r.fulfill({contentType:'application/javascript',body:'window.$=window.jQuery=function(){return{collapse:function(){}}};'});
   return r.fulfill({body:''});});
  await p.goto('file://'+path.resolve(process.argv[2])); await p.waitForTimeout(300);
  const set=(id,v)=>p.evaluate(([id,v])=>{const e=document.getElementById(id);e.value=String(v);e.dispatchEvent(new Event(e.tagName==='SELECT'||e.type==='date'?'change':'input',{bubbles:true}));},[id,v]);
  const clk=s=>p.evaluate(s=>document.querySelector(s).click(),s);
  await set('baselineTraffic',20000); await set('baselineTotalConversions',1000); await clk('#toggleBaselineSecondaryKpi'); await set('baselineTotalConversionsSecondary',4000); await p.waitForTimeout(400);
  await clk('#mde-forecast-tbody tr[data-week="8"]'); await set('testStartDate','2026-10-05'); await clk('#startAnalysisButton'); await p.waitForTimeout(400);
  console.log('== '+name);
  for(const [a,bb] of D[name]){ for(const [id,v] of Object.entries({controlVisitors:a[0],controlConversions:a[1],controlConversionsSecondary:a[2],variantVisitors:bb[0],variantConversions:bb[1],variantConversionsSecondary:bb[2]})) await set(id,v);
   await clk('#addDataButton'); await p.waitForTimeout(400);
   const r=await p.evaluate(()=>({s:document.getElementById('resultStage').textContent,zP:document.getElementById('zScorePrincipal').textContent,zS:(document.getElementById('zScoreSecondary')||{}).textContent,zNi:(document.getElementById('zScoreNiSecondary')||{}).textContent,dec:document.getElementById('decision').textContent.replace(/\s+/g,' ').trim()}));
   console.log(`S${r.s} zP=${r.zP} zS=${r.zS} | ${r.dec.slice(0,175)}`);
   if(/^ARRÊTER/.test(r.dec)) break; }
  if(errs.length) console.log('ERREURS JS',errs); await p.close(); }
 await b.close(); })();

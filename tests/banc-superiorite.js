// Mode Supériorité (testType 1) : l'API prod renvoie futilityZ = null (relevé 15/11, k=8).
const { chromium } = require('playwright'); const path = require('path');
const EFF = [3.725,3.189,2.847,2.576,2.342,2.132,1.937,1.753];
const zP=(vA,cA,vB,cB)=>{const p=(cA+cB)/(vA+vB);return (cB/vB-cA/vA)/Math.sqrt(p*(1-p)*(1/vA+1/vB));};
const STUB_J = require('fs').readFileSync(path.join(__dirname,'banc-front.js'),'utf8').match(/jstat: `([^`]+)`/)[1];
const STUB_H = require('fs').readFileSync(path.join(__dirname,'banc-front.js'),'utf8').match(/highcharts: `([^`]+)`/)[1];
(async () => {
  const b = await chromium.launch();
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(String(e))); p.on('dialog',d=>d.accept());
    await p.route('**/*', r => { const u=r.request().url();
      if (u.startsWith('file://')) return r.continue();
      if (u.includes('calculate-boundaries')) { const q=JSON.parse(r.request().postData());
        const res={boundaries:EFF.map((e,i)=>({stage:i+1,infoFraction:(i+1)/8*1.0423,efficacyZ:e,futilityZ:null})),parameters:{k:8,testType:1}};
        if (q.visitors_a!==undefined) res.observedZ=+zP(q.visitors_a,q.conversions_a,q.visitors_b,q.conversions_b).toFixed(5);
        return r.fulfill({contentType:'application/json',body:JSON.stringify(res)}); }
      if (u.includes('jstat')) return r.fulfill({contentType:'application/javascript',body:STUB_J});
      if (u.includes('highcharts')) return r.fulfill({contentType:'application/javascript',body:u.endsWith('highcharts.js')?STUB_H:''});
      if (u.includes('jquery')) return r.fulfill({contentType:'application/javascript',body:'window.$=window.jQuery=function(){return{collapse:function(){}}};'});
      return r.fulfill({body:''}); });
    await p.goto('file://'+path.resolve(f)); await p.waitForTimeout(300);
    const set=(id,v)=>p.evaluate(([id,v])=>{const e=document.getElementById(id);e.value=v;e.dispatchEvent(new Event(e.tagName==='SELECT'||e.type==='date'?'change':'input',{bubbles:true}));},[id,String(v)]);
    const clk=s=>p.evaluate(s=>document.querySelector(s).click(),s);
    await set('baselineTraffic',20000); await set('baselineTotalConversions',1000); await set('mdeTestType','1'); await p.waitForTimeout(400);
    await clk('#mde-forecast-tbody tr[data-week="8"]'); await set('testStartDate','2026-11-02'); await clk('#startAnalysisButton'); await p.waitForTimeout(400);
    // Semaine 1 : B légèrement sous A (z ≈ -0,46)
    for (const [id,v] of Object.entries({controlVisitors:10000,controlConversions:500,variantVisitors:10000,variantConversions:490})) await set(id,v);
    await clk('#addDataButton'); await p.waitForTimeout(500);
    const dec = await p.evaluate(()=>document.getElementById('decision').textContent.replace(/\s+/g,' ').trim());
    const z = await p.evaluate(()=>document.getElementById('zScorePrincipal').textContent);
    console.log(`${path.basename(f)} | Z=${z} | ${dec.slice(0,120)} | erreurs JS=${errs.length}`);
    await p.close();
  }
  await b.close();
})();

const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const out={};
for(const v of ['v53','v54'])for(const w of [345,1280]){const p=await b.newPage({viewport:{width:w,height:900}});p.on('dialog',d=>d.accept());await p.goto('file://'+path.join(__dirname,'..','calculateur-sequentiel-'+v+'.html'));await p.addStyleTag({content:'button{white-space:nowrap}'});await p.waitForSelector('.imp');
const ov=()=>p.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);const r={accueil:await ov()};
if(v==='v54'){await p.click('[data-act=howto][data-v=adobe]');await p.waitForTimeout(150);r.adobe=await ov();if(w===345)await p.locator('#gst-import').screenshot({path:(process.argv[2]||'.')+'/adobe-360.png'});await p.click('[data-act=howto][data-v=manuel]');await p.waitForTimeout(150);r.manuel=await ov();}
await p.click('[data-act=example]');await p.waitForTimeout(300);r.apercu=await ov();await p.click('[data-act=apply]');await p.waitForTimeout(2500);r.resultats=await ov();
await p.click('[data-act=share]').catch(()=>{});await p.waitForTimeout(600);r.partage=await ov();
await p.click('[data-v=donnees]');await p.waitForTimeout(300);r.donnees=await ov();await p.click('[data-v=plan]');await p.waitForTimeout(2500);r.plan=await ov();out[v+'-'+w]=r;await p.close();}
console.log(JSON.stringify(out));await b.close();})();

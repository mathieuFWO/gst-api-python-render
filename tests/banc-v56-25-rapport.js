// Banc du rapport .pptx (v56.24) : la bibliothèque est servie depuis la copie locale, sous le même contrôle d'intégrité que celui du CDN.
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
const FILE=path.join(__dirname,'..','calculateur-sequentiel-v56-25.html');const LIB=fs.readFileSync('/usr/local/lib/node_modules_global/pptxgenjs/dist/pptxgen.bundle.js');
let pass=0,fail=0;const ok=(n,c,d)=>{c?pass++:fail++;console.log((c?'✅ ':'❌ ')+n+(c?'':' — '+JSON.stringify(d)));};
const OUT=process.argv[2]||'/tmp';
(async()=>{const b=await chromium.launch();
 for(const W of [360,1280]){const T='['+W+'] ';const errs=[];const ctx=await b.newContext({viewport:{width:W,height:900},acceptDownloads:true});const p=await ctx.newPage();p.on('pageerror',e=>errs.push(String(e)));
  let lib=0,mode='ok';await ctx.route('https://cdn.jsdelivr.net/**',r=>{lib++;return mode==='ok'?r.fulfill({status:200,contentType:'application/javascript',headers:{'access-control-allow-origin':'*'},body:LIB}):mode==='bad'?r.fulfill({status:200,contentType:'application/javascript',headers:{'access-control-allow-origin':'*'},body:Buffer.concat([LIB,Buffer.from('\n//x')])}):r.abort();});
  await ctx.route('https://gst.test/**',r=>r.fulfill({status:200,contentType:'text/html; charset=utf-8',body:'<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0;padding:0 8px}</style></head><body>'+fs.readFileSync(FILE,'utf8')+'</body></html>'}));
  await p.goto('https://gst.test/');await p.waitForTimeout(500);
  ok(T+'aucun appel à la bibliothèque avant le clic',lib===0);
  await p.click('[data-act=example]');await p.waitForTimeout(2500);
  const btn=p.locator('[data-act=report]');ok(T+'bouton d\'export présent, 44 px au moins, sans débordement',await btn.count()===1&&(await btn.boundingBox()).height>=44&&(await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth))<=0);
  mode='bad';await btn.click();await p.waitForTimeout(1500);
  ok(T+'bibliothèque altérée : refusée par le contrôle d\'intégrité, message clair',/Rapport impossible/.test(await p.locator('.err').innerText().catch(()=>''))&&!(await p.evaluate(()=>!!window.PptxGenJS)));
  mode='ok';const [dl]=await Promise.all([p.waitForEvent('download',{timeout:20000}),btn.click()]);const f=path.join(OUT,'rapport-'+W+'.pptx');await dl.saveAs(f);await p.waitForTimeout(600);
  ok(T+'fichier téléchargé, nommé d\'après le test',/^rapport-exemple-7-metriques\.pptx$/.test(dl.suggestedFilename())&&fs.statSync(f).size>15000,[dl.suggestedFilename(),fs.statSync(f).size]);
  ok(T+'confirmation affichée',/Rapport téléchargé/.test(await p.locator('.ok').innerText().catch(()=>'')));
  ok(T+'aucune erreur JS',errs.length===0,errs);await ctx.close();}
 await b.close();console.log(pass+'/'+(pass+fail)+(fail?' KO':' OK'));})();

// Banc v56-35 : p-value dans l'infobulle de chaque métrique et de chaque valeur d'une segmentation. Les valeurs attendues sont recalculées ici, par une autre formule (intégration numérique de la loi normale).
const { chromium } = require('playwright'); const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-35.html');
const res=[]; let fails=0; const ok=(n,c,i)=>{res.push((c?'✅ ':'❌ ')+n+(i!==undefined?' — '+JSON.stringify(i):''));if(!c)fails++;};
const sf=z=>{let s=0;const n=200000,a=Math.abs(z),h=(12-a)/n;for(let i=0;i<n;i++){const x=a+(i+0.5)*h;s+=Math.exp(-x*x/2);}return s*h/Math.sqrt(2*Math.PI);};
const pv=(a,b)=>{const pa=a[1]/a[0],pb=b[1]/b[0],pp=(a[1]+b[1])/(a[0]+b[0]),se=Math.sqrt(pp*(1-pp)*(1/a[0]+1/b[0]));return sf((pb-pa)/se);};
const fr=p=>p<0.001?'< 0,001':p.toLocaleString('fr-FR',{minimumFractionDigits:p<0.1?3:2,maximumFractionDigits:p<0.1?3:2});
const R=[['Desktop','0Original',7326,541,2930],['Desktop','2093615Variation 1',7240,526,2975],['Mobile Phone','0Original',37900,1560,17400],['Mobile Phone','2093615Variation 1',38119,1453,17900],['Tablet','0Original',335,23,150],['Tablet','2093615Variation 1',289,11,131]];
const csv='Appareil - Type;MVT - Variante;Visiteurs;Visiteurs convertis;Visiteurs avec rebond\n'+R.map(r=>r.join(';')).join('\n')+'\n';
(async()=>{ const b=await chromium.launch();
 for(const vw of [360,1280]){ const p=await b.newPage({viewport:{width:vw,height:900}});p.errs=[];p.on('pageerror',e=>p.errs.push(String(e)));p.on('dialog',d=>d.accept());
  await p.route('**/*',r=>r.request().url().startsWith('file://')?r.continue():r.fulfill({status:200,body:''}));await p.goto('file://'+path.resolve(FILE));await p.waitForTimeout(200);
  await p.evaluate(c=>window.GST.openCSV(c,'t.csv'),csv);await p.waitForTimeout(300);await p.fill('[data-d=startDate]','2026-10-07');await p.dispatchEvent('[data-d=startDate]','change');await p.waitForTimeout(300);
  await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()}));await p.waitForTimeout(250);await p.click('[data-act=apply]');await p.waitForTimeout(3000);await p.click('#gst-app .sgl');await p.waitForTimeout(300);
  const d=await p.evaluate(()=>({tips:[...document.querySelectorAll('#gst-app .mrw:not(.hd) > .tip')].map(t=>({pv:(t.querySelector('.tpv b')||{}).textContent,sens:(t.querySelector('.tpv span')||{}).textContent,txt:t.innerText.replace(/\s+/g,' '),avantTable:!!(t.querySelector('.tpv')&&t.querySelector('table.tv')&&(t.querySelector('.tpv').compareDocumentPosition(t.querySelector('table.tv'))&4))})),pvs:[...document.querySelectorAll('#gst-app .pvs')].map(x=>x.textContent),mob:[...document.querySelectorAll('#gst-app .mrw:not(.hd):not(.sub) .mob')].map(x=>x.textContent),eff:window.GST.getState().bounds.eff,ov:document.scrollingElement.scrollWidth-innerWidth}));
  const G=pv([45561,2124],[45648,1990]),M=pv([37900,1560],[38119,1453]),D=pv([7326,541],[7240,526]),T=pv([335,23],[289,11]),RB=pv([45561,20480],[45648,21006]);
  ok(vw+' : infobulle de l\'objectif : p-value juste ('+fr(G)+'), sens de l\'écart, placée avant le tableau des volumes',d.tips[0].pv==='p-value '+fr(G)&&/défavorable/.test(d.tips[0].sens)&&d.tips[0].avantTable,d.tips[0].pv);
  const s1=sf(d.eff[0]),s4=sf(d.eff[3]),f4=x=>x.toLocaleString('fr-FR',{minimumFractionDigits:x<0.01?4:3,maximumFractionDigits:x<0.01?4:3});
  ok(vw+' : seuils affichés : à cette lecture ('+f4(s1)+') et en fin de test ('+f4(s4)+')',d.tips[0].txt.includes('Seuil à franchir à cette lecture : '+f4(s1)+' · en fin de test : '+f4(s4)),d.tips[0].txt.slice(60,220));
  ok(vw+' : infobulles des trois appareils : p-values justes ('+[M,D,T].map(fr).join(' ; ')+'), marquées « Exploratoire » et « Non corrigée »',[M,D,T].every((x,i)=>d.tips[i+1].pv==='p-value '+fr(x)&&/Exploratoire/.test(d.tips[i+1].txt)&&/Non corrigée/.test(d.tips[i+1].txt)&&!/borne/.test(d.tips[i+1].txt)),d.tips.slice(1,4).map(x=>x.pv));
  ok(vw+' : p-value de chaque appareil visible sans survol, à droite de la ligne',d.pvs.join('|')===[M,D,T].map(x=>'p '+fr(x)).join('|'),d.pvs);
  ok(vw+' : garde-fou : p-value de l\'écart ('+fr(RB)+') et ligne de non-régression',d.tips[4].pv==='p-value '+fr(RB)&&/Non-régression : p-value/.test(d.tips[4].txt),d.tips[4].txt.slice(0,260));
  if(vw<500)ok(vw+' : sur mobile, où il n\'y a pas de survol, la p-value figure sous le nom de la métrique',d.mob[0].includes('p '+fr(G))&&d.mob[1].includes('p '+fr(RB)),d.mob);
  ok(vw+' : aucun débordement, aucune erreur de script',d.ov<=0&&p.errs.length===0,[d.ov,p.errs]);await p.close(); }
 console.log(res.join('\n'));console.log(fails?`❌ ${fails} échec(s) sur ${res.length}`:`✅ ${res.length}/${res.length}`);await b.close();process.exit(fails?1:0);})();

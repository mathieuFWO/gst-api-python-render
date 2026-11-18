// v56.10 : survol sans déplacement (règles du thème injectées), écran « Vérifiez la lecture du fichier », alerte d'export non cumulé
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-10.html');
const THEME='button,input,optgroup,select,textarea{font-family:inherit;font-size:1rem;line-height:1.5;margin:0}[type="button"],[type="submit"],button{background-color:transparent;border:1px solid #c36;border-radius:3px;color:#c36;display:inline-block;font-size:1rem;font-weight:400;padding:.5rem 1rem;text-align:center;transition:.3s;user-select:none;white-space:nowrap}[type="button"]:focus,[type="button"]:hover,[type="submit"]:focus,[type="submit"]:hover,button:focus,button:hover{background-color:#c36;color:#fff;text-decoration:none}.elementor-kit-5072 button{background-color:#028D6A;font-size:16px;font-weight:700;color:#fff}.elementor-kit-5072 button:hover,.elementor-kit-5072 button:focus{background-color:#015a44;border-radius:2px}';
let n=0,okc=0;const ok=(l,c,d)=>{n++;if(c)okc++;console.log((c?'✅ ':'❌ ')+l+(d!==undefined?' — '+JSON.stringify(d):''));};
const PROPS=['fontFamily','fontSize','fontWeight','lineHeight','letterSpacing','paddingTop','paddingLeft','paddingRight','paddingBottom','borderTopWidth','borderLeftWidth','borderRadius','minHeight','textTransform','whiteSpace','display'];
(async()=>{const b=await chromium.launch();
for(const w of [360,1280]){const p=await b.newPage({viewport:{width:w,height:900}});const errs=[];p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('file://'+path.resolve(FILE));await p.evaluate(()=>document.body.classList.add('elementor-kit-5072'));await p.addStyleTag({content:THEME});await p.waitForSelector('.cta button');
  const hoverAll=async(lab)=>{const bad=[];const L=p.locator('#gst-app button:visible');const c=await L.count();
    for(let i=0;i<c;i++){const e=L.nth(i);await p.mouse.move(0,0);const snap=()=>e.evaluate((x,P)=>{const s=getComputedStyle(x),r=x.getBoundingClientRect();const o={w:Math.round(r.width*10)/10,h:Math.round(r.height*10)/10};P.forEach(k=>o[k]=s[k]);return o;},PROPS);
      const a=await snap();try{await e.hover({timeout:2000,force:true});}catch(_){continue;}await p.waitForTimeout(350);const h=await snap();
      const d=Object.keys(a).filter(k=>a[k]!==h[k]);if(d.length)bad.push((await e.textContent()).trim().slice(0,30)+' : '+d.map(k=>k+' '+a[k]+'→'+h[k]).join(', '));}
    await p.mouse.move(0,0);ok(`[${w}] ${lab} : aucun bouton ne change de taille, de police ni de bordure au survol (${c} boutons)`,bad.length===0,bad.slice(0,6));};
  await hoverAll('accueil');
  const h1=await p.evaluate(()=>{const e=document.querySelector('h1.gst-h1');return e?parseFloat(getComputedStyle(e).paddingTop):-1;});
  ok(`[${w}] air au-dessus du titre de l'outil (≥ 28 px)`,h1>=28,h1);
  ok(`[${w}] accueil : plus de FAQ dans l'outil (FAQ unique côté page)`,(await p.locator('#gst-app .fq').count())===0);
  // fichier cumulé
  await p.setInputFiles('input[type=file]',path.join(__dirname,'exemple-8-metriques.csv'));await p.waitForSelector('.dv');
  const ov=()=>p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
  ok(`[${w}] écran de vérification : 3 parties, sans débordement, sans case « cumuler », sans alerte pour un fichier cumulé`,(await ov())<=0&&(await p.locator('.dv-sec').count())===3&&(await p.locator('#gst-cum,[data-d=cumulate]').count())===0&&(await p.locator('.dv-warn').count())===0&&!/les cumuler/.test(await p.textContent('#gst-app')),await ov());
  ok(`[${w}] rappel du dernier cumul lu`,/Dernier cumul lu : 60.132 visiteurs pour A - Contrôle, 60.016 pour B - Variante/.test((await p.textContent('.dv-read')).replace(/\s/g,' ')),await p.textContent('.dv-read'));
  const rows=await p.evaluate(()=>[...document.querySelectorAll('.dv-m')].map(r=>{const q=s=>r.querySelector(s).getBoundingClientRect();const c=x=>Math.round(x.top+x.height/2);const nm=q('input[data-dm=name]'),pl=q('.pill'),ro=q('select[data-dm=role]'),se=q('select[data-dm=sens]'),ck=q('input[type=checkbox]');return {nm:c(nm),pl:c(pl),ro:c(ro),se:c(se),ck:c(ck),roW:Math.round(ro.width),seW:Math.round(se.width),nmW:Math.round(nm.width),roL:Math.round(ro.left),seL:Math.round(se.left),h:Math.round(r.getBoundingClientRect().height)};}));
  if(w===1280){ok('[1280] lignes de métriques : case, nom, type, rôle et sens sur la même ligne, toutes de même hauteur, colonnes alignées',rows.length===7&&rows.every(r=>Math.abs(r.nm-r.pl)<=1&&Math.abs(r.nm-r.ro)<=1&&Math.abs(r.nm-r.se)<=1&&Math.abs(r.nm-r.ck)<=1&&r.h===rows[0].h&&r.roL===rows[0].roL&&r.seL===rows[0].seL),rows[0]);
    const g=await p.evaluate(()=>[...document.querySelectorAll('.dv-g')].map(g=>[...g.querySelectorAll('input,select')].map(e=>Math.round(e.getBoundingClientRect().top))));ok('[1280] champs de configuration alignés : une ligne pour le test, la colonne du test seule puis les 4 colonnes sur une ligne',g[0].every(t=>t===g[0][0])&&g[1].length===5&&g[1].slice(1).every(t=>t===g[1][1])&&g[1][0]<g[1][1],g);}
  else ok('[360] lignes de métriques : nom et type sur une ligne, rôle et sens dessous, liste déroulantes ≥ 100 px, lignes de même hauteur',rows.every(r=>Math.abs(r.nm-r.pl)<=1&&r.ro===r.se&&r.ro>r.nm&&r.roW>=100&&r.seW>=100&&r.nmW>=140&&r.h===rows[0].h),rows[0]);
  await hoverAll('écran de vérification');
  await p.locator('.dv').screenshot({path:path.join(process.argv[3]||'.','ecran-'+w+'.png')});
  await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()})).then(()=>p.waitForTimeout(200)).then(()=>p.click('[data-act=apply]'));await p.waitForTimeout(500);
  ok(`[${w}] import du fichier cumulé : 6 semaines chargées, décision affichée`,/6 semaine\(s\) de données chargée/.test(await p.textContent('#gst-app')));
  await hoverAll('résultats');
  // fichier non cumulé
  await p.evaluate(()=>{try{localStorage.clear();}catch(e){}});await p.reload();await p.evaluate(()=>document.body.classList.add('elementor-kit-5072'));await p.addStyleTag({content:THEME});await p.waitForSelector('.cta button');
  await p.setInputFiles('input[type=file]',path.join(__dirname,'non-cumule.csv'));await p.waitForSelector('.dv');
  const wt=(await p.locator('.dv-warn').count())?await p.textContent('.dv-warn'):'';
  ok(`[${w}] export semaine par semaine : alerte affichée dès l'ouverture, chiffres cités, sans débordement`,/export semaine par semaine/.test(wt)&&/20.059/.test(wt)&&/cumul depuis le premier jour/.test(wt)&&(await ov())<=0,wt.slice(0,90));
  await p.locator('.dv').screenshot({path:path.join(process.argv[3]||'.','ecran-noncumul-'+w+'.png')});
  await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()})).then(()=>p.waitForTimeout(200)).then(()=>p.click('[data-act=apply]'));await p.waitForTimeout(400);
  const et=(await p.locator('.dv .err').count())?await p.textContent('.dv .err'):'';
  ok(`[${w}] export semaine par semaine : import refusé avec la marche à suivre, aucune donnée chargée`,/visiteurs cumulés baissent/.test(et)&&/refaites l'export/.test(et)&&(await p.locator('.dv').count())===1,et.slice(0,120));
  ok(`[${w}] aucune erreur JS`,errs.length===0,errs);await p.close();}
// règle de détection : pas de fausse alerte sur un trafic régulier ou croissant ; alerte sur un cumul qui stagne
const p=await b.newPage();await p.goto('file://'+path.resolve(FILE));await p.waitForSelector('.cta button');
const csv=(ns)=>'Semaine;Variation;Visiteurs;Achats\n'+ns.map((x,i)=>`${i+1};A;${x};${Math.round(x*0.05)}\n${i+1};B;${x+3};${Math.round(x*0.052)}`).join('\n')+'\n';
const warn=async(ns)=>{await p.evaluate(c=>window.GST.openCSV(c,'t.csv'),csv(ns));await p.waitForTimeout(150);const r=await p.locator('.dv-warn').count();await p.click('[data-act=cancel]');return r;};
const cases=[[[1000,2000],0],[[1000,2000,3000,4000],0],[[1000,1700,2300,2800],0],[[3000,4500,5600,6300,6800,7100],1],[[3000,3700,4300,4800,5300,5700],1],[[1000,1050],1],[[1000,1010,1020,1030],1],[[1000,990,1005],1],[[1000,1100,1200,1300,1400,1500],1]];
const res=[];for(const c of cases)res.push(await warn(c[0]));
ok('règle de détection : 3 cumuls à progression franche sans alerte, 6 séries à progression faible ou en baisse avec alerte et confirmation demandée',res.every((r,i)=>r===cases[i][1]),res);
console.log('\n'+okc+'/'+n+' OK');await b.close();process.exit(okc===n?0:1);})();

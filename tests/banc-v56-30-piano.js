// v56.30 : lecture d'un export Piano Analytics réel (structure reprise d'un vrai fichier, noms anonymisés)
const {chromium}=require('playwright');const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-30.html');
let n=0,okc=0;const ok=(l,c,d)=>{n++;if(c)okc++;console.log((c?'✅ ':'❌ ')+l+(d!==undefined?' — '+JSON.stringify(d):''));};
(async()=>{const b=await chromium.launch();for(const w of [360,1280]){const p=await b.newPage({viewport:{width:w,height:900}});const errs=[];p.on('pageerror',e=>errs.push(String(e)));
await p.goto('file://'+path.resolve(FILE));await p.waitForSelector('.cta button');await p.setInputFiles('input[type=file]',path.join(__dirname,'piano-export-anonyme.csv'));await p.waitForSelector('.dv');
const opts=s=>p.evaluate(s=>[...document.querySelector('#gst-app '+s).options].map(o=>o.text),s);const val=s=>p.evaluate(s=>{const e=document.querySelector('#gst-app '+s);return e.options[e.selectedIndex].text;},s);
const tests=await opts('[data-d=test]');
ok(`[${w}] colonne « MVT - Test » reconnue : 4 tests proposés, la ligne « N/A » écartée`,tests.length===4&&!tests.includes('N/A'),tests.length);
ok(`[${w}] colonnes lues : variations « MVT - Variante », visiteurs « Utilisateurs », métrique « Utilisateurs convertis »`,(await val('[data-d=cVar]'))==='MVT - Variante'&&(await val('[data-d=cVis]'))==='Utilisateurs'&&(await p.inputValue('.dv-m input[data-dm=name]'))==='Utilisateurs convertis');
await p.selectOption('[data-d=test]',{label:'1680001[FR] Visuel A vs B'});await p.waitForTimeout(400);
const vars=(await opts('[data-d=control]')).concat(await opts('[data-d=variant]'));
ok(`[${w}] variations limitées au test choisi, contrôle « Original » détecté, identifiants Piano retirés des listes`,(await val('[data-d=control]'))==='Original'&&(await val('[data-d=variant]'))==='Variation 1'&&vars.every(v=>/^(Original|Variation 1)$/.test(v)),vars);
ok(`[${w}] rappel du cumul lu, identifiants retirés des libellés`,/19.765 visiteurs pour Original, 20.065 pour Variation 1/.test((await p.textContent('.dv-read')).replace(/\s/g,' ')),await p.textContent('.dv-read'));
await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()})).then(()=>p.waitForTimeout(200)).then(()=>p.click('[data-act=apply]'));await p.waitForTimeout(900);const t=await p.evaluate(()=>document.querySelector('#gst-app').innerText);
ok(`[${w}] import accepté : décision affichée, taux 12,88 % → 12,87 %, sans débordement`,/1 semaine\(s\) de données chargée/.test(t)&&/Contrôle 12,88 % · Variante 12,87 %/.test(t)&&(await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth))<=0&&(await p.locator('.dv').count())===0,(t.match(/\d+,\d+ % → \d+,\d+ %/)||[])[0]);
await p.locator('[data-act=tab][data-v=donnees]').click();await p.waitForTimeout(300);const t2=await p.evaluate(()=>document.querySelector('#gst-app').innerText);
ok(`[${w}] libellés enregistrés sans identifiant`,/Original/.test(t2)&&/Variation 1/.test(t2)&&!/0Original|2098001Variation/.test(t2));
await p.setInputFiles('input[type=file]',path.join(__dirname,'piano-export-anonyme.csv'));await p.waitForSelector('.dv');
await p.evaluate(()=>{const b=document.querySelector('#gst-app [data-act=dvfull]');if(b)b.click();});await p.waitForTimeout(250);ok(`[${w}] import suivant le même jour : le même test est repris par défaut, et l'outil dit qu'aucune nouvelle semaine n'est complète`,(await val('[data-d=test]'))==='1680001[FR] Visuel A vs B'&&/Pas de nouvelle semaine complète/.test(await p.textContent('.dv-gate')));await p.click('[data-act=cancel]');
ok(`[${w}] aucune erreur JS`,errs.length===0,errs);await p.close();}
console.log('\n'+okc+'/'+n+' OK');await b.close();process.exit(okc===n?0:1);})();

// v56.12 : « Données jusqu'au », semaines complètes, colonne du test au choix, choix de colonnes mémorisés
const {chromium}=require('playwright');const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-12.html');
let n=0,okc=0;const ok=(l,c,d)=>{n++;if(c)okc++;console.log((c?'✅ ':'❌ ')+l+(d!==undefined?' — '+JSON.stringify(d):''));};
const D=k=>{const d=new Date();d.setDate(d.getDate()+k);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};const fr=i=>i.slice(8)+'/'+i.slice(5,7)+'/'+i.slice(0,4);
const snap=(m)=>'Campagne;Bras;Clients uniques;Clients acheteurs\n"N/A";"N/A";99;999\n"Test fiche";"Témoin";'+Math.round(1000*m)+';'+Math.round(50*m)+'\n"Test fiche";"Nouvelle";'+Math.round(1004*m)+';'+Math.round(58*m)+'\n"Autre test";"Témoin";10;1\n"Autre test";"Nouvelle";11;1\n';
(async()=>{const b=await chromium.launch();for(const w of [360,1280]){const p=await b.newPage({viewport:{width:w,height:900}});const errs=[];p.on('pageerror',e=>errs.push(String(e)));
await p.goto('file://'+path.resolve(FILE));await p.waitForSelector('.cta button');const ov=()=>p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);const txt=s=>p.evaluate(s=>{const e=document.querySelector('#gst-app '+s);return e?e.innerText:'';},s);const sel=s=>p.evaluate(s=>{const e=document.querySelector('#gst-app '+s);return e&&e.selectedIndex>=0?e.options[e.selectedIndex].text:null;},s);const set=async(s,v)=>{await p.fill(s,v);await p.locator(s).blur();await p.waitForTimeout(250);};const pick=async(s,l)=>{await p.selectOption(s,{label:l});await p.waitForTimeout(350);};
const open=async(m)=>{await p.evaluate(c=>window.GST.openCSV(c,'export.csv'),snap(m));await p.waitForSelector('.dv');};
// 1. en-têtes inconnus : rien n'est deviné pour le test, l'utilisateur choisit
await open(1);
ok(`[${w}] en-têtes inhabituels : la colonne du test n'est pas devinée, elle se choisit`,(await sel('[data-d=cTest]'))==='Aucune : un seul test'&&(await p.locator('[data-d=test]').count())===0);
await pick('[data-d=cTest]','Campagne');await pick('[data-d=cVar]','Bras');await pick('[data-d=cVis]','Clients uniques');await pick('[data-d=test]','Test fiche');
ok(`[${w}] après choix : 2 tests proposés (« N/A » écarté), témoin et variante du test choisi, cumul lu`,(await p.locator('[data-d=test] option').count())===2&&(await sel('[data-d=control]'))==='Témoin'&&(await sel('[data-d=variant]'))==='Nouvelle'&&/1.000 visiteurs pour Témoin, 1.004 pour Nouvelle/.test((await txt('.dv-read')).replace(/\s/g,' ')),await txt('.dv-read'));
// 2. dates par défaut
ok(`[${w}] par défaut : données jusqu'à hier, début supposé 6 jours avant, 1 semaine complète, rappel de vérifier le début`,(await p.inputValue('[data-d=endDate]'))===D(-1)&&(await p.inputValue('[data-d=startDate]'))===D(-7)&&/7 jours de données/.test(await txt('.dv-gate'))&&/Vérifiez la date de début/.test(await txt('.dv-gate')),await txt('.dv-gate'));
await set('[data-d=startDate]',D(-4));
ok(`[${w}] 4 jours de données : première semaine pas terminée, date de la prochaine lecture donnée`,/première semaine du test n'est pas terminée : 4 jours/.test(await txt('.dv-gate'))&&(await txt('.dv-gate')).includes(fr(D(2))),await txt('.dv-gate'));
await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()})).then(()=>p.waitForTimeout(200)).then(()=>p.click('[data-act=apply]'));await p.waitForTimeout(300);ok(`[${w}] import refusé tant que la semaine n'est pas complète`,(await p.locator('.dv').count())===1&&/première semaine/.test(await txt('.dv .err')));
await set('[data-d=startDate]',D(-16));await set('[data-d=endDate]',D(3));ok(`[${w}] date de fin dans le futur refusée`,/dans le futur/.test(await txt('.dv-gate')));
await set('[data-d=endDate]',D(-10));ok(`[${w}] début J-16, données jusqu'à J-10 : 7 jours, 1 semaine complète, sans débordement`,/7 jours de données/.test(await txt('.dv-gate'))&&!/Vérifiez la date de début/.test(await txt('.dv-gate'))&&(await ov())<=0);
await set('[data-d=k]','4');await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()})).then(()=>p.waitForTimeout(200)).then(()=>p.click('[data-act=apply]'));await p.waitForTimeout(900);
ok(`[${w}] lecture 1 enregistrée, période affichée jusqu'à la vraie date de fin`,(await txt('.v-side')).includes('Du '+fr(D(-16))+' au '+fr(D(-10))),(await txt('.v-side')).match(/Du [^.]*/)?.[0]);
// 3. import suivant : choix retenus, règle des 7 jours
await p.locator('[data-act=tab][data-v=donnees]').click();await p.waitForTimeout(200);await open(2);
ok(`[${w}] import suivant : colonne du test, test, colonnes, témoin et variante repris sans rien redemander`,(await sel('[data-d=cTest]'))==='Campagne'&&(await sel('[data-d=test]'))==='Test fiche'&&(await sel('[data-d=cVar]'))==='Bras'&&(await sel('[data-d=cVis]'))==='Clients uniques'&&(await sel('[data-d=control]'))==='Témoin'&&(await sel('[data-d=variant]'))==='Nouvelle');
await set('[data-d=endDate]',D(-6));
ok(`[${w}] 4 jours après la lecture 1 : pas de nouvelle semaine complète, prochaine date donnée`,/Pas de nouvelle semaine complète depuis la dernière lecture/.test(await txt('.dv-gate'))&&(await txt('.dv-gate')).includes(fr(D(-3))),await txt('.dv-gate'));
await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()})).then(()=>p.waitForTimeout(200)).then(()=>p.click('[data-act=apply]'));await p.waitForTimeout(300);ok(`[${w}] import refusé, la lecture 1 reste seule`,(await p.locator('.dv').count())===1);
await set('[data-d=endDate]',D(-1));ok(`[${w}] données jusqu'à hier : 16 jours, 2 semaines complètes`,/16 jours de données/.test(await txt('.dv-gate'))&&/lecture de la semaine 2 sur 4/.test(await txt('.dv-gate')));
await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()})).then(()=>p.waitForTimeout(200)).then(()=>p.click('[data-act=apply]'));await p.waitForTimeout(900);
ok(`[${w}] lecture 2 ajoutée, période jusqu'à hier`,/2 semaine\(s\) de données chargée/.test(await txt(''))&&(await txt('.v-side')).includes('au '+fr(D(-1))));
// 4. persistance
await p.click('[data-act=save]');await p.waitForTimeout(300);await p.reload();await p.waitForSelector('#gst-app');await p.waitForTimeout(600);
const key=await p.evaluate(()=>Object.keys(localStorage).filter(k=>/^gstSeq_v40_/.test(k))[0]);const st=await p.evaluate(k=>JSON.parse(localStorage.getItem(k)),key);
ok(`[${w}] sauvegarde : dates de fin et choix de colonnes conservés`,st&&st.weeks.length===2&&st.weeks[0].end===D(-10)&&st.weeks[1].end===D(-1)&&st.map&&st.map.test==='Campagne'&&st.map.tv==='Test fiche',st&&st.map);
ok(`[${w}] aucune erreur JS`,errs.length===0,errs);await p.close();}
console.log('\n'+okc+'/'+n+' OK');await b.close();process.exit(okc===n?0:1);})();

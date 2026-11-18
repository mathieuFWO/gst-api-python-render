// v56.12 : période de l'export lue hors du tableau (en-tête commenté, nom du fichier, date du fichier)
const {chromium}=require('playwright');const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-12.html');
let n=0,okc=0;const ok=(l,c,d)=>{n++;if(c)okc++;console.log((c?'✅ ':'❌ ')+l+(d!==undefined?' — '+JSON.stringify(d):''));};
const D=k=>{const d=new Date();d.setDate(d.getDate()+k);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};const c8=i=>i.replace(/-/g,'');const fr=i=>i.slice(8)+'/'+i.slice(5,7)+'/'+i.slice(0,4);
const T=(m)=>'MVT - Test;MVT - Variante;Utilisateurs;Utilisateurs convertis\n"1[FR] Test";"2Variation 1";'+(4600*m)+';'+(935*m)+'\n"1[FR] Test";"0Original";'+(4610*m)+';'+(923*m)+'\n';
const TC=(m)=>T(m).replace(/;/g,',');
(async()=>{const b=await chromium.launch();for(const w of [360,1280]){const p=await b.newPage({viewport:{width:w,height:900}});const errs=[];p.on('pageerror',e=>errs.push(String(e)));
const fresh=async()=>{await p.goto('file://'+path.resolve(FILE));await p.evaluate(()=>{try{localStorage.clear()}catch(e){}});await p.reload();await p.waitForSelector('.cta button');};
const open=async(txt,name,lm)=>{await p.evaluate(a=>window.GST.openCSV(a[0],a[1],a[2]),[txt,name,lm]);await p.waitForSelector('.dv');await p.waitForTimeout(200);};
const val=s=>p.inputValue('#gst-app '+s);const gate=()=>p.evaluate(()=>{const e=document.querySelector('#gst-app .dv-gate');return e?e.innerText:'';});const ov=()=>p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
const at=k=>{const d=new Date();d.setDate(d.getDate()+k);d.setHours(10,0,0,0);return d.getTime();};
// 1. rien d'exploitable : comportement de la v56.5 (hier), aucune mention de source
await fresh();await open(T(1),'rapport_sans_titre_1.csv');
ok(`[${w}] ni en-tête, ni date dans le nom, ni date de fichier : « hier », sans mention de source`,(await val('[data-d=endDate]'))===D(-1)&&!/lue dans|déduite/.test(await gate()),await gate());
// 2. fichier exporté aujourd'hui : identique
await fresh();await open(T(1),'rapport_sans_titre_1.csv',Date.now());
ok(`[${w}] fichier daté d'aujourd'hui : « hier », sans mention`,(await val('[data-d=endDate]'))===D(-1)&&!/déduite/.test(await gate()));
// 3. fichier exporté il y a 3 jours : fin = veille de l'export, source dite
await fresh();await open(T(1),'rapport_sans_titre_1.csv',at(-3));
ok(`[${w}] fichier daté d'il y a 3 jours : fin proposée ${D(-4)}, source affichée avec la date d'export`,(await val('[data-d=endDate]'))===D(-4)&&new RegExp('déduite de la date du fichier \\(exporté le '+fr(D(-3))).test(await gate()),await gate());
await p.fill('#gst-app [data-d=endDate]',D(-2));await p.locator('#gst-app [data-d=endDate]').blur();await p.waitForTimeout(300);
ok(`[${w}] date corrigée à la main : la mention de source disparaît, pas de débordement`,!/déduite/.test(await gate())&&(await ov())<=0,await gate());
// 4. nom du fichier avec période
await fresh();await open(T(1),'export_'+D(-10)+'_'+D(-4)+'.csv',at(-1));
ok(`[${w}] période dans le nom (${D(-10)} → ${D(-4)}) : début et fin repris, prioritaire sur la date du fichier`,(await val('[data-d=endDate]'))===D(-4)&&(await val('[data-d=startDate]'))===D(-10)&&/Période lue dans le nom du fichier/.test(await gate())&&/semaine 1 sur/.test(await gate()),await gate());
// 5. nom avec une seule date compacte
await fresh();await open(T(1),'piano-'+c8(D(-2))+'.csv');
ok(`[${w}] une seule date dans le nom (${c8(D(-2))}) : fin reprise, début supposé et signalé`,(await val('[data-d=endDate]'))===D(-2)&&/Date de fin lue dans le nom/.test(await gate())&&/Vérifiez la date de début/.test(await gate()),await gate());
// 6. en-tête commenté façon GA4 (rapport standard)
await fresh();await open('# ----------------------------------------\n# Compte : X\n# Start date: '+c8(D(-14))+'\n# End date: '+c8(D(-1))+'\n# ----------------------------------------\n\n'+TC(1),'download.csv',at(-5));
ok(`[${w}] en-tête « # Start date / # End date » : fichier lu, période reprise (14 jours → semaine 2), prioritaire`,(await val('[data-d=endDate]'))===D(-1)&&(await val('[data-d=startDate]'))===D(-14)&&/Période lue dans l.en-tête/.test(await gate())&&/semaine 2 sur/.test(await gate()),await gate());
// 7. en-tête façon exploration GA4 : « # 20261101-20261107 »
await fresh();await open('# ----------------------------------------\n# Forme libre 1\n# '+c8(D(-7))+'-'+c8(D(-1))+'\n# ----------------------------------------\n\n'+TC(1),'download.csv');
ok(`[${w}] en-tête « # AAAAMMJJ-AAAAMMJJ » : période reprise`,(await val('[data-d=endDate]'))===D(-1)&&(await val('[data-d=startDate]'))===D(-7),await gate());
// 8. dates impossibles ou futures : ignorées
const M=await p.evaluate(a=>[window.GST.meta('a;b;c\n1;2;3','export_2026-13-45.csv'),window.GST.meta('a;b;c\n1;2;3','export_'+a[0]+'.csv'),window.GST.meta('a;b;c\n1;2;3','test-12345678.csv'),window.GST.meta('#x;y;z\n1;2;3','f.csv'),window.GST.meta('a;b;c','f.csv',a[1])],[D(5),at(3)]);
ok(`[${w}] dates impossibles, futures, identifiants à 8 chiffres, en-tête de colonnes commençant par # : rien n'est retenu`,M.every(m=>!m.end&&!m.src),M);
// 9. second import : le début du test ne bouge pas, seule la fin vient du fichier
await fresh();await open(T(1),'export_'+D(-21)+'_'+D(-15)+'.csv');await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()})).then(()=>p.waitForTimeout(200)).then(()=>p.click('#gst-app [data-act=apply]'));await p.waitForTimeout(900);
const s1=await p.evaluate(()=>{const s=window.GST.getState();return {n:s.weeks.length,start:s.plan.startDate,end:s.weeks[0]&&s.weeks[0].end};});
await open(T(2),'export_'+D(-21)+'_'+D(-8)+'.csv');const g2=await gate();await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()})).then(()=>p.waitForTimeout(200)).then(()=>p.click('#gst-app [data-act=apply]'));await p.waitForTimeout(900);
const s2=await p.evaluate(()=>{const s=window.GST.getState();return {n:s.weeks.length,start:s.plan.startDate,end:s.weeks[1]&&s.weeks[1].end,wk:s.weeks.map(x=>x.wk)};});
ok(`[${w}] deux imports successifs sans rien saisir : lectures des semaines 1 et 2, dates venues des noms de fichier`,s1.n===1&&s1.start===D(-21)&&s1.end===D(-15)&&s2.n===2&&s2.start===D(-21)&&s2.end===D(-8)&&s2.wk.join()==='1,2'&&/semaine 2 sur/.test(g2),{s1,s2,g2});
ok(`[${w}] aucune erreur JS`,errs.length===0,errs);await p.close();}
console.log(okc+'/'+n+(okc===n?' OK':' ÉCHEC'));await b.close();})();

// v56.22 : confirmations (date de fin, cumul), test ancien sans dates, colonnes mémorisées dans le lien, assistant sans test vide, alignement du Plan
const {chromium}=require('playwright');const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-22.html');
let n=0,okc=0;const ok=(l,c,d)=>{n++;if(c)okc++;console.log((c?'✅ ':'❌ ')+l+(d!==undefined?' — '+JSON.stringify(d):''));};
const D=k=>{const d=new Date();d.setDate(d.getDate()+k);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};const fr=i=>i.slice(8)+'/'+i.slice(5,7)+'/'+i.slice(0,4);const c8=i=>i.replace(/-/g,'');
const T=(m)=>'MVT - Test;MVT - Variante;Utilisateurs;Utilisateurs convertis\n"9900001[FR] Essai";"8800001Variation 1";'+Math.round(4600*m)+';'+Math.round(935*m)+'\n"9900001[FR] Essai";"0Original";'+Math.round(4610*m)+';'+Math.round(923*m)+'\n';
(async()=>{const b=await chromium.launch();for(const w of [360,1280]){const p=await b.newPage({viewport:{width:w,height:900}});const errs=[];p.on('pageerror',e=>errs.push(String(e)));
const fresh=async()=>{await p.goto('file://'+path.resolve(FILE));await p.evaluate(()=>{try{localStorage.clear()}catch(e){}});await p.reload();await p.waitForSelector('.cta button');};
const open=async(txt,name,lm)=>{await p.evaluate(a=>window.GST.openCSV(a[0],a[1],a[2]),[txt,name,lm]);await p.waitForSelector('.dv');await p.waitForTimeout(200);};
const txt=s=>p.evaluate(s=>{const e=document.querySelector('#gst-app '+s);return e?e.innerText:'';},s);const cnt=s=>p.locator('#gst-app '+s).count();const ov=()=>p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);const st=()=>p.evaluate(()=>{const s=window.GST.getState();return {n:s.weeks.length,start:s.plan.startDate,wk:s.weeks.map(x=>x.wk||null),end:s.weeks.map(x=>x.end||null),map:s.map||null};});
const apply=async()=>{await p.click('#gst-app [data-act=apply]');await p.waitForTimeout(700);};const set=async(s,v)=>{await p.fill('#gst-app '+s,v);await p.locator('#gst-app '+s).blur();await p.waitForTimeout(300);};
// A. fichier de Mat (ni période, ni date dans le nom) : la date proposée doit être confirmée
await fresh();await open(T(1),'rapport_sans_titre_1.csv');
ok(`[${w}] export sans période : case « Je confirme … jusqu'au ${fr(D(-1))} inclus » affichée, non cochée, sans débordement`,(await cnt('[data-d=endOk]'))===1&&new RegExp("jusqu.au "+fr(D(-1))+" inclus").test(await txt('.dv-ck'))&&!(await p.isChecked('#gst-app [data-d=endOk]'))&&(await ov())<=0,await txt('.dv-ck'));
await apply();ok(`[${w}] import sans confirmation : refusé, rien n'est chargé, message clair`,(await st()).n===0&&/Confirmez la date de fin/.test(await txt('.dv .err')),await txt('.dv .err'));
await p.check('#gst-app [data-d=endOk]');await p.waitForTimeout(250);await apply();let s=await st();
ok(`[${w}] case cochée : import accepté, lecture de la semaine 1 datée du ${D(-1)}`,s.n===1&&s.end[0]===D(-1)&&s.wk[0]===1,s);
// B. date saisie à la main : plus de case
await fresh();await open(T(1),'rapport_sans_titre_1.csv');await set('[data-d=endDate]',D(-3));
ok(`[${w}] date saisie à la main : pas de case à cocher`,(await cnt('[data-d=endOk]'))===0);await set('[data-d=startDate]',D(-9));await apply();s=await st();ok(`[${w}] … et import accepté`,s.n===1&&s.end[0]===D(-3),s);
// C. période lue dans l'en-tête du fichier : pas de case
await fresh();await open('# Start date: '+c8(D(-7))+'\n# End date: '+c8(D(-1))+'\n'+T(1).replace(/;/g,','),'d.csv');
ok(`[${w}] période lue dans l'en-tête : pas de case`,(await cnt('[data-d=endOk]'))===0);
// D. date déduite du fichier : case portant la date déduite
await fresh();const lm=(()=>{const d=new Date();d.setDate(d.getDate()-3);d.setHours(10,0,0,0);return d.getTime();})();await open(T(1),'rapport_sans_titre_1.csv',lm);
ok(`[${w}] date déduite de celle du fichier : case sur le ${fr(D(-4))}`,new RegExp(fr(D(-4))+" inclus").test(await txt('.dv-ck')));
// E. date refusée par la règle des semaines : pas de case tant que la date ne convient pas
await set('[data-d=startDate]',D(-6));ok(`[${w}] semaine incomplète : message de refus, pas de case`,(await cnt('.dv-gate.ko'))===1&&(await cnt('[data-d=endOk]'))===0,await txt('.dv-gate'));
// F. 2e import non cumulé : alerte avec case, refus sans la case
await fresh();await open(T(1),'a.csv');await set('[data-d=startDate]',D(-14));await set('[data-d=endDate]',D(-8));await apply();
await open(T(1.04),'b.csv');await set('[data-d=endDate]',D(-1));const wn=await txt('.dv-warn');
ok(`[${w}] 2e instantané à +4 % : alerte au texte exact et case de confirmation du cumul`,/\+4 % en 1 semaine/.test(wn)&&(await cnt('[data-d=cumOk]'))===1&&(await ov())<=0,wn.slice(0,200));
await apply();ok(`[${w}] sans la case : refusé`,(await st()).n===1&&/bien cumulés/.test(await txt('.dv .err')));
await p.check('#gst-app [data-d=cumOk]');await p.waitForTimeout(250);await apply();ok(`[${w}] case cochée : accepté`,(await st()).n===2);
// G. test ancien (lectures sans date, début = jour du 1er import) : la date de début se corrige dans l'écran d'import
await fresh();await p.evaluate(a=>{const s=window.GST.getState();},0);await open(T(1),'a.csv');await set('[data-d=startDate]',D(-14));await set('[data-d=endDate]',D(-8));await apply();
await p.evaluate(a=>{const s=window.GST.getState();s.weeks.forEach(x=>{delete x.end;delete x.wk;});s.plan.startDate=a;},D(-8));
await open(T(2),'b.csv');await set('[data-d=endDate]',D(-1));
ok(`[${w}] test ancien : champ « Date de début du test » présent dans l'écran d'import, refus expliqué`,(await cnt('[data-d=startDate]'))===1&&/Vérifiez la date de début du test ci-dessus/.test(await txt('.dv-gate')),await txt('.dv-gate'));
await set('[data-d=startDate]',D(-14));ok(`[${w}] début corrigé au ${fr(D(-14))} : lecture de la semaine 2 acceptée`,/lecture de la semaine 2 sur/.test(await txt('.dv-gate')),await txt('.dv-gate'));
await apply();s=await st();ok(`[${w}] import : 2 lectures, date de début enregistrée dans le plan`,s.n===2&&s.start===D(-14)&&s.end[1]===D(-1),s);
// H. lien de partage : colonnes mémorisées conservées
const tok=await p.evaluate(()=>window.GST.share());const cx=await b.newContext({viewport:{width:w,height:900}});const q=await cx.newPage();await q.goto('file://'+path.resolve(FILE)+'#t='+tok);await q.waitForTimeout(1500);const mp=await q.evaluate(()=>{const s=window.GST.getState();return {map:s.map||null,n:s.weeks.length,keys:Object.keys(localStorage).length};});await cx.close();
ok(`[${w}] lien de partage ouvert dans un navigateur vierge : 2 lectures et colonnes mémorisées retrouvées`,mp.n===2&&mp.map&&mp.map.vis==='Utilisateurs'&&mp.map.tv==='9900001[FR] Essai',mp);
// I. listes : identifiants Piano retirés, valeurs intactes
await fresh();await open('T;V;U;C\n"9900001[FR] Essai";"8800001Variation 1";10;1\n"9900001[FR] Essai";"0Original";10;1\n"9900002[FR] Autre";"8800002Variation 1";10;1\n"9900002[FR] Autre";"0Original";10;1\n','x.csv');await p.selectOption('#gst-app [data-d=cTest]',{label:'T'});await p.waitForTimeout(300);await p.selectOption('#gst-app [data-d=cVar]',{label:'V'});await p.waitForTimeout(300);
const o=await p.evaluate(()=>['test','control','variant'].map(k=>[...document.querySelector('#gst-app [data-d='+k+']').options].map(x=>x.text+'|'+x.value)));
ok(`[${w}] listes : libellés sans identifiant, valeurs d'origine conservées`,o[0].join()==='[FR] Essai|9900001[FR] Essai,[FR] Autre|9900002[FR] Autre'&&o[1].includes('Original|0Original')&&o[2].every(x=>/^Variation 1\|\d+Variation 1$/.test(x)),o);
// J. assistant : pas de test vide enregistré
// K. onglet Plan : champs alignés
await fresh();await p.click('#gst-app [data-act=example]');await p.waitForTimeout(900);await p.click('#gst-app [data-act=tab][data-v=plan]').catch(()=>{});await p.waitForTimeout(400);
const al=await p.evaluate(()=>[...document.querySelectorAll('#gst-app .form2 > div input')].slice(0,2).map(e=>Math.round(e.getBoundingClientRect().top)));
ok(`[${w}] onglet Plan : « Durée prévue » et « Date de début » à la même hauteur`,al.length===2&&al[0]===al[1],al);
ok(`[${w}] aucune erreur JS`,errs.length===0,errs);await p.close();}
console.log(okc+'/'+n+(okc===n?' OK':' ÉCHEC'));await b.close();})();

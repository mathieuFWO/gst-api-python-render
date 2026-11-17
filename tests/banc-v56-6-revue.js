// v56.6 : corrections issues de la relecture indépendante (constats 1, 2, 3, 7, 10, 11, 12, 13, 15)
const {chromium}=require('playwright');const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-6.html');
let n=0,okc=0;const ok=(l,c,d)=>{n++;if(c)okc++;console.log((c?'✅ ':'❌ ')+l+(d!==undefined?' — '+JSON.stringify(d):''));};
const D=k=>{const d=new Date();d.setDate(d.getDate()+k);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
const F=(rows)=>'MVT - Test;MVT - Variante;Utilisateurs convertis;Utilisateurs\n'+rows.map(r=>'"'+r[0]+'";"'+r[1]+'";'+r[2]+';'+r[3]).join('\n')+'\n';
const T1=m=>[['111[FR] Test A','0Original',Math.round(500*m),Math.round(10000*m)],['111[FR] Test A','2222001Variation 1',Math.round(540*m),Math.round(10020*m)]],T2=[['222[FR] Test B','0Original',30,900],['222[FR] Test B','3333001Variation 1',41,905]];
(async()=>{const b=await chromium.launch();const F0=F;for(const w of [360,1280]){const ctx=await b.newContext({viewport:{width:w,height:900}});const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));
await p.goto('file://'+path.resolve(FILE));await p.evaluate(()=>{window.__mail=[];window.GST_NOMAIL=u=>window.__mail.push(u);});await p.waitForSelector('.cta button');
const txt=s=>p.evaluate(s=>{const e=document.querySelector('#gst-app '+s);return e?e.innerText:'';},s);const set=async(s,v)=>{await p.fill(s,v);await p.locator(s).blur();await p.waitForTimeout(250);};const open=async c=>{await p.evaluate(c=>window.GST.openCSV(c,'export.csv'),c);await p.waitForSelector('.dv');};const data=async()=>{await p.locator('[data-act=tab][data-v=donnees]').click();await p.waitForTimeout(200);};const ov=()=>p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
// lecture 1 : début J-22, données jusqu'à J-15
await open(F(T1(1).concat(T2)));await p.selectOption('[data-d=test]',{label:'111[FR] Test A'});await p.waitForTimeout(300);await set('[data-d=startDate]',D(-21));await set('[data-d=endDate]',D(-15));await set('[data-d=k]','4');await p.click('[data-act=apply]');await p.waitForTimeout(800);
ok(`[${w}] lecture 1 enregistrée`,/1 semaine\(s\) de données chargée/.test(await txt('')));
// constat 1 : le test suivi est absent du fichier
await data();await open(F(T2));
ok(`[${w}] constat 1 : test suivi absent du fichier → alerte dès l'ouverture, sans débordement`,/ne contient pas le test suivi/.test(await txt('.dv .err'))&&(await ov())<=0,(await txt('.dv .err')).slice(0,70));
await set('[data-d=endDate]',D(-8));await p.click('[data-act=apply]');await p.waitForTimeout(400);
ok(`[${w}] constat 1 : import refusé, aucune lecture ajoutée`,(await p.locator('.dv').count())===1&&/ne contient pas le test suivi/.test(await txt('.dv .err')));await p.click('[data-act=cancel]');
// constat 1 bis : autre test choisi à la main
await open(F(T1(2).concat(T2)));await set('[data-d=endDate]',D(-8));await p.selectOption('[data-d=test]',{label:'222[FR] Test B'});await p.waitForTimeout(300);
ok(`[${w}] constat 1 : un autre test choisi à la main est refusé avec la marche à suivre`,/choisissez ce test, ou créez un nouveau test/.test(await txt('.dv .err')));
await p.selectOption('[data-d=test]',{label:'111[FR] Test A'});await p.waitForTimeout(300);
// constat 2 : contrôle et variante inversés
await p.selectOption('[data-d=control]',{label:'2222001Variation 1'});await p.waitForTimeout(300);
ok(`[${w}] constat 2 : contrôle et variante inversés → alerte`,/doivent rester ceux des lectures précédentes/.test(await txt('.dv .err')),(await txt('.dv .err')).slice(0,60));
await p.click('[data-act=apply]');await p.waitForTimeout(400);ok(`[${w}] constat 2 : import refusé`,(await p.locator('.dv').count())===1);
await p.selectOption('[data-d=control]',{label:'0Original'});await p.waitForTimeout(300);await p.selectOption('[data-d=variant]',{label:'2222001Variation 1'}).catch(()=>{});await p.waitForTimeout(300);
ok(`[${w}] retour au bon contrôle : plus d'alerte`,(await p.locator('.dv .err').count())===0&&(await p.locator('.dv-warn').count())===0);
await p.click('[data-act=apply]');await p.waitForTimeout(800);ok(`[${w}] lecture 2 ajoutée (cumul doublé, pas d'alerte)`,/2 semaine\(s\) de données chargée/.test(await txt('')));
// constat 7 : aujourd'hui refusé
await open(F(T1(3)));await p.evaluate(d=>{const e=document.querySelector('#gst-app [data-d=endDate]');e.value=d;e.dispatchEvent(new Event('change',{bubbles:true}));},D(0));await p.waitForTimeout(300);
ok(`[${w}] constat 7 : « Données jusqu'au » = aujourd'hui refusé`,/n'est pas terminée : indiquez hier/.test(await txt('.dv-gate')));await p.click('[data-act=cancel]');
// constats 10 et 12 : email
await p.locator('[data-act=tab][data-v=resultats]').click();await p.waitForTimeout(200);await p.click('[data-act=share]');await p.waitForSelector('[data-f=shareurl]');
for(const bad of ['a@b.fr?bcc=x%40y.z&x=','a@b.fr?body=pirate&x=','a@b.fr#x','a b@c.fr']){await p.fill('[data-f=shareto]',bad);await p.click('[data-act=sharemail]');await p.waitForTimeout(200);}
const m=await p.evaluate(()=>window.__mail);ok(`[${w}] constat 12 : adresses piégées → aucun paramètre injecté, messagerie ouverte sans destinataire`,m.length===4&&m.every(u=>/^mailto:\?subject=/.test(u)&&!/bcc=|body=pirate/.test(u)),m.map(u=>u.slice(0,24)));
await p.fill('[data-f=shareto]','claire.martin+test@exemple.fr');await p.click('[data-act=sharemail]');await p.waitForTimeout(200);ok(`[${w}] constat 12 : adresse normale conservée`,/^mailto:claire\.martin%2Btest@exemple\.fr\?subject=/.test((await p.evaluate(()=>window.__mail)).pop()));
await p.click('[data-act=shareclose]');await set('[data-f=name]','Test '+'très long '.repeat(45));await p.evaluate(()=>{navigator.clipboard.writeText=()=>Promise.reject(new Error('refus'));});await p.click('[data-act=share]');await p.waitForSelector('[data-f=shareurl]');await p.click('[data-act=sharemail]');await p.waitForTimeout(400);
const sh=await txt('.share');ok(`[${w}] constat 10 : copie impossible → pas de « Lien copié », consigne de copier à la main`,!/Lien copié\./.test(sh)&&/cliquez sur « Copier le lien »/.test(sh));
ok(`[${w}] aucune erreur JS (import)`,errs.length===0,errs);await ctx.close();
// constats 11, 13, 15 : assistant
const p2=await b.newPage({viewport:{width:w,height:900}});const e2=[];p2.on('pageerror',e=>e2.push(String(e)));await p2.goto('file://'+path.resolve(FILE));await p2.waitForSelector('.cta button');
await p2.click('[data-act=howto][data-v=manuel]');await p2.fill('[data-man=m0name]','Visiteurs avec achat');await p2.locator('[data-man=m0name]').blur();await p2.click('[data-act=manstep]');await p2.waitForTimeout(250);
await p2.fill('[data-mde=traffic]','20.000');await p2.keyboard.press('Tab');await p2.waitForTimeout(100);await p2.fill('[data-mde=conv]','1.000');await p2.keyboard.press('Tab');await p2.waitForTimeout(1800);
const v=await p2.locator('.wz .mr2 b').allInnerTexts();ok(`[${w}] constat 15 : « 20.000 » et « 1.000 » lus comme vingt mille et mille (4 semaines : 8,04 %)`,v[1]==='8,04 %',v);
await p2.click('[data-act=manstart]');const ins=p2.locator('.card.wz [data-mw]');await ins.nth(0).waitFor();await ins.nth(0).type('10062',{delay:5});await ins.nth(1).type('10069',{delay:5});await p2.waitForTimeout(1200);
ok(`[${w}] constat 11 : chiffres tapés juste après « Continuer » conservés`,(await ins.nth(0).inputValue())==='10062'&&(await ins.nth(1).inputValue())==='10069',[await ins.nth(0).inputValue(),await ins.nth(1).inputValue()]);
await p2.click('[data-act=addweek]');await p2.waitForTimeout(400);ok(`[${w}] constat 11 : après une erreur, les chiffres déjà saisis restent`,(await p2.locator('.card.wz').count())===1&&(await ins.nth(0).inputValue())==='10062'&&(await ins.nth(1).inputValue())==='10069');
await ins.nth(2).fill('520');await ins.nth(3).fill('541');await p2.click('[data-act=addweek]');await p2.waitForTimeout(900);ok(`[${w}] assistant : décision affichée`,(await p2.locator('.card.wz').count())===0&&/Continuer|Arrêter|Déployer/.test(await p2.evaluate(()=>document.querySelector('#gst-app').innerText)));
const p3=await b.newPage({viewport:{width:w,height:900}});await p3.goto('file://'+path.resolve(FILE));await p3.waitForSelector('.cta button');const t3=s=>p3.evaluate(s=>{const e=document.querySelector('#gst-app '+s);return e?e.innerText:'';},s);const set3=async(s,v)=>{await p3.fill(s,v);await p3.locator(s).blur();await p3.waitForTimeout(250);};
await p3.evaluate(c=>window.GST.openCSV(c,'v.csv'),'Variation;Visiteurs;Achats\n3D viewer;1000;50\n4K video;1004;61\n');await p3.waitForSelector('.dv');
ok(`[${w}] constat 13 : « 3D viewer » et « 4K video » laissés intacts`,/pour 3D viewer, 1.004 pour 4K video/.test((await t3('.dv-read')).replace(/\s/g,' ')),await t3('.dv-read'));await p3.click('[data-act=cancel]');
await p3.evaluate(c=>window.GST.openCSV(c,'s1.csv'),F(T1(1)));await p3.waitForSelector('.dv');await set3('[data-d=startDate]',D(-21));await set3('[data-d=endDate]',D(-15));await set3('[data-d=k]','4');await p3.click('[data-act=apply]');await p3.waitForTimeout(800);
await p3.locator('[data-act=tab][data-v=donnees]').click();await p3.waitForTimeout(200);await p3.evaluate(c=>window.GST.openCSV(c,'s2.csv'),F(T1(1.04)));await p3.waitForSelector('.dv');await set3('[data-d=endDate]',D(-8));
const wn=await t3('.dv-warn');ok(`[${w}] constat 3 : 2e instantané à +4 % → alerte « pas un cumul », chiffres cités, texte juste, sans débordement`,/ne ressemblent pas à un cumul/.test(wn)&&/20.020/.test(wn)&&/c'est peu pour 2 semaines de cumul/.test(wn)&&!/presque pas/.test(wn)&&(await p3.evaluate(()=>document.documentElement.scrollWidth-innerWidth))<=0,wn.slice(0,110));await p3.close();
ok(`[${w}] aucune erreur JS (assistant)`,e2.length===0,e2);await p2.close();}
console.log('\n'+okc+'/'+n+' OK');await b.close();process.exit(okc===n?0:1);})();

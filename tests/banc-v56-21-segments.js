const pk=async p=>{const u=p.locator('#gst-app [data-act=unpick]');if(await u.count())await u.first().click();};
// v56.21 : requête Piano reprise en entier (segment compris), variations définies par deux segments, exclusions BigQuery, textes corrigés
const {chromium}=require('playwright');const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-21.html');
let n=0,okc=0;const ok=(l,c,d)=>{n++;if(c)okc++;console.log((c?'✅ ':'❌ ')+l+(d!==undefined?' — '+JSON.stringify(d):''));};
const D=k=>{const d=new Date();d.setDate(d.getDate()+k);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
const AK='ACCESSKEYFACTICE01',SK='SECRETFACTICE0000000002';
const U=o=>'https://api.atinternet.io/v3/data/getData?param='+encodeURIComponent(JSON.stringify(o));
const ROWS={columns:['mv_test','mv_creation','m_users','m_conv_users'],space:{s:[999001]},period:{p1:[{type:'D',start:'2020-01-01',end:'2020-01-07'}]},filter:{property:{mv_test:{$eq:'9900001[FR] Essai'}}},segment:{section:{mode:'include',items:[{device_type:{$eq:'Mobile'}}]}},evo:{granularity:'D'},cohorte:{x:1},'max-results':50,'page-num':1,options:{ignore_null_properties:true}};
const SEG=(id)=>({columns:['m_users','m_atc_users','m_conv_users'],space:{s:[999001]},period:{p1:[{type:'D',start:'2020-01-01',end:'2020-01-07'}]},segment:{id:id},'max-results':50,'page-num':1,options:{}});
(async()=>{const b=await chromium.launch();for(const w of [360,1280]){const cx=await b.newContext({viewport:{width:w,height:900}});const p=await cx.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));
const calls=[];let mult=1,mode='ok';
await cx.route('**/*',async r=>{const u=r.request().url();if(u.startsWith('file:'))return r.continue();if(!u.startsWith('https://api.atinternet.io/'))return r.abort();
  const h={'access-control-allow-origin':'*','access-control-allow-headers':'x-api-key','access-control-allow-methods':'GET,OPTIONS'};if(r.request().method()==='OPTIONS')return r.fulfill({status:204,headers:h});
  const P=JSON.parse(new URL(u).searchParams.get('param'));calls.push(P);let body;
  if(P.columns.includes('mv_creation'))body={DataFeed:{Columns:[{Name:'mv_test',Label:'MVT - Test'},{Name:'mv_creation',Label:'MVT - Variante'},{Name:'m_users',Label:'Utilisateurs'},{Name:'m_conv_users',Label:'Utilisateurs convertis'}],Rows:[{mv_test:'9900001[FR] Essai',mv_creation:'8800001Variation 1',m_users:4600*mult,m_conv_users:935*mult},{mv_test:'9900001[FR] Essai',mv_creation:'0Original',m_users:4610*mult,m_conv_users:923*mult}]}};
  else{const B=P.segment&&P.segment.id===72;const row={m_users:Math.round((B?1134500:1136245)*mult),m_atc_users:Math.round((B?115622:114788)*mult),m_conv_users:Math.round((B?27742:27644)*mult)};let Cols=[{Name:'m_users',Label:'Visiteurs'},{Name:'m_atc_users',Label:'Ajout au panier (visiteurs)'},{Name:'m_conv_users',Label:'Visiteurs avec achat'}];let Rows=[row];
    if(mode==='2lignes'&&B)Rows=[row,row];if(mode==='colonnes'&&B)Cols=[{Name:'m_users',Label:'Visiteurs'},{Name:'m_atc_users',Label:'Autre nom'},{Name:'m_conv_users',Label:'Visiteurs avec achat'}];body={DataFeed:{Columns:Cols,Rows}};}
  return r.fulfill({status:200,headers:h,contentType:'application/json',body:JSON.stringify(body)});});
const fresh=async()=>{await p.goto('file://'+path.resolve(FILE));await p.evaluate(()=>{try{localStorage.clear()}catch(e){}});await p.reload();await p.waitForSelector('.cta button');};
const txt=s=>p.evaluate(s=>{const e=document.querySelector('#gst-app '+s);return e&&!e.hidden?e.innerText:'';},s);const cnt=s=>p.locator('#gst-app '+s).count();const ov=()=>p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
const openForm=async()=>{await pk(p);await p.click('#gst-app [data-act=howto][data-v=piano]').catch(()=>{});await p.waitForTimeout(200);await p.click('#gst-app [data-act=apiopen]');await p.waitForSelector('#gst-app #gst-purl');};
// 1. nettoyage de la requête
const cl=await p.goto('file://'+path.resolve(FILE)).then(()=>p.evaluate(a=>{const q=window.GST.piano.param(a[0]);const evil=JSON.parse('{"columns":["a","b","c"],"space":{"s":[1]},"__proto__":{"pollue":1},"constructor":{"x":1},"cle bizarre":1,"gros":"'+'x'.repeat(10)+'"}');const q2=window.GST.piano.clean(evil);let big=null;try{window.GST.piano.clean({columns:['a','b','c'],space:{s:[1]},segment:'y'.repeat(5000)});}catch(e){big=e.message;}return {q,k2:Object.keys(q2),pol:({}).pollue,big};},[U(ROWS)]));
ok(`[${w}] requête recopiée : le segment et les paramètres inconnus sont repris tels quels ; la période, l'évolution et la pagination sont remplacées`,JSON.stringify(cl.q.segment)===JSON.stringify(ROWS.segment)&&JSON.stringify(cl.q.cohorte)==='{"x":1}'&&!('evo' in cl.q)&&!('period' in cl.q)&&cl.q['max-results']===1000&&cl.q.options.ignore_null_properties===true,cl.q);
ok(`[${w}] requête piégée : pas de pollution de prototype, clés invalides écartées, paramètre trop long refusé`,cl.pol===undefined&&!cl.k2.includes('constructor')&&!cl.k2.includes('cle bizarre')&&cl.k2.includes('gros')&&/trop long/.test(cl.big||''),cl);
// 2. variations en lignes : le segment part bien à Piano
await fresh();await openForm();await p.fill('#gst-purl',U(ROWS));await p.fill('#gst-pstart',D(-10));await p.fill('#gst-pak',AK);await p.fill('#gst-psk',SK);await p.click('[data-act=apigo]');await p.waitForSelector('.dv');
ok(`[${w}] variations en lignes : l'appel porte le segment et le filtre de la requête d'origine, sur la période du test`,calls.length===1&&JSON.stringify(calls[0].segment)===JSON.stringify(ROWS.segment)&&!!calls[0].filter&&calls[0].period.p1[0].start===D(-10),calls[0]);
ok(`[${w}] écran de vérification : « Repris de votre requête : filtre, segment… » affiché, sans débordement`,/Repris de votre requête : .*filtre.*segment/.test(await txt('.dv-gate'))&&(await ov())<=0,await txt('.dv-gate'));
// 3. deux segments
await fresh();await openForm();ok(`[${w}] formulaire : choix « en lignes » par défaut, un seul champ de requête`,(await p.isChecked('#gst-app [data-api=mode][value=lignes]'))&&!(await p.isVisible('#gst-app #gst-purl2')));
await p.fill('#gst-pak',AK);await p.fill('#gst-psk',SK);await p.check('#gst-app [data-api=mode][value=segments]');await p.waitForTimeout(200);
ok(`[${w}] choix « par deux segments » : second champ affiché, clés déjà saisies conservées, sans débordement`,(await p.isVisible('#gst-app #gst-purl2'))&&(await p.inputValue('#gst-pak'))===AK&&/Requête du contrôle/.test(await txt('.apif'))&&(await ov())<=0);
await p.fill('#gst-purl',U(SEG(71)));await p.fill('#gst-pstart',D(-10));calls.length=0;await p.click('[data-act=apigo]');await p.waitForTimeout(600);
ok(`[${w}] une seule requête fournie : refus clair, aucun appel`,/Requêtes par segment/.test(await txt('.api-err'))&&calls.length===0,await txt('.api-err'));
await p.fill('#gst-purl2',U(SEG(72)));mode='2lignes';await p.click('[data-act=apigo]');await p.waitForTimeout(900);
ok(`[${w}] une requête qui renvoie deux lignes : refusée (« une seule ligne »)`,/une seule ligne \(2 reçues\)/.test(await txt('.api-err'))&&(await cnt('.dv'))===0,await txt('.api-err'));
mode='colonnes';await p.click('[data-act=apigo]');await p.waitForTimeout(900);ok(`[${w}] colonnes différentes entre les deux requêtes : refusé`,/ne renvoient pas les mêmes colonnes/.test(await txt('.api-err')),await txt('.api-err'));
mode='ok';calls.length=0;await p.click('[data-act=apigo]');await p.waitForSelector('.dv');
ok(`[${w}] deux appels, chacun avec son segment, même période (${D(-10)} → ${D(-4)})`,calls.length===2&&calls[0].segment.id===71&&calls[1].segment.id===72&&calls.every(c=>c.period.p1[0].start===D(-10)&&c.period.p1[0].end===D(-4)&&c.columns.join()==='m_users,m_atc_users,m_conv_users'),calls.map(c=>[c.segment,c.period.p1[0]]));
ok(`[${w}] écran de vérification : Contrôle 1 136 245, Variante 1 134 500, deux métriques, mention « Deux requêtes, une par variation », sans débordement`,/1.136.245 visiteurs pour Contrôle, 1.134.500 pour Variante/.test(await txt('.dv-read:last-of-type'))||/1.136.245 visiteurs pour Contrôle, 1.134.500 pour Variante/.test(await p.evaluate(()=>[...document.querySelectorAll('#gst-app .dv-read')].map(e=>e.innerText).join(' ')))&&(await p.locator('#gst-app [data-dm=include]:checked').count())===2&&/Deux requêtes, une par variation/.test(await txt('.dv-gate'))&&(await ov())<=0,[await txt('.dv-gate')]);
await p.click('[data-act=apply]');await p.waitForTimeout(1200);
let s=await p.evaluate(()=>{const s=window.GST.getState();return {n:s.weeks.length,A:s.weeks[0]&&s.weeks[0].A.n,B:s.weeks[0]&&s.weeks[0].B.n,seg:!!(s.api&&s.api.q&&s.api.q.seg),labs:s.labels,mets:s.metrics.map(m=>m.name),all:JSON.stringify(s)};});
ok(`[${w}] import : lecture enregistrée avec les deux variations, requête double gardée avec le test, sans la clé`,s.n===1&&s.A===1136245&&s.B===1134500&&s.seg&&s.mets.length===2&&!s.all.includes(AK)&&!s.all.includes(SK),{n:s.n,A:s.A,B:s.B,labs:s.labs,mets:s.mets});
ok(`[${w}] bandeau : site interrogé affiché`,/Site Piano 999001/.test(await txt('.apibar')),await txt('.apibar'));
// semaine suivante : deux appels à nouveau
await p.evaluate(a=>{const s=window.GST.getState();s.plan.startDate=a[0];s.weeks[0].end=a[1];s.weeks[0].wk=1;},[D(-17),D(-11)]);mult=2;calls.length=0;await p.click('#gst-app [data-act=tab][data-v=donnees]').catch(()=>{});await p.waitForTimeout(200);await p.click('#gst-app [data-act=tab][data-v=resultats]').catch(()=>{});await p.waitForTimeout(300);await p.click('#gst-app [data-act=apiupd]');await p.waitForTimeout(1500);
s=await p.evaluate(()=>{const s=window.GST.getState();return {n:s.weeks.length,B:s.weeks[1]&&s.weeks[1].B.n};});
ok(`[${w}] semaine suivante : collecte en deux appels, lecture ajoutée`,calls.length===2&&s.n===2&&s.B===2269000,{calls:calls.length,s});
// rechargement : la requête double survit au nettoyage de l'état
await p.reload();await p.waitForSelector('#gst-app');await p.waitForTimeout(400);await p.selectOption('#gst-app [data-act=load]',{index:1});await p.waitForTimeout(600);
ok(`[${w}] après rechargement : le test garde sa requête double`,await p.evaluate(()=>{const q=window.GST.getState().api;return !!(q&&q.q.seg&&q.q.seg.length===2&&q.q.seg[1].segment.id===72);}));
// 4. BigQuery : colonne des exclus
await fresh();await p.evaluate(a=>window.GST.openCSV('debut_test,fin_donnees,variation,visiteurs,visiteurs_avec_achat,exclus_deux_variations\n'+a[0]+','+a[1]+',A,20124,1041,412\n'+a[0]+','+a[1]+',B,20139,1082,412\n','bq.csv'),[D(-14),D(-1)]);await p.waitForSelector('.dv');
const rd=await p.evaluate(()=>[...document.querySelectorAll('#gst-app .dv-read')].map(e=>e.innerText).join(' | '));
ok(`[${w}] résultat BigQuery avec la colonne des exclus : elle n'est pas prise pour une métrique, et « 412 visiteurs vus dans les deux variations… 1,01 % » s'affiche avec l'alerte, sans débordement`,(await p.locator('#gst-app [data-dm=include]').count())===1&&/412 visiteurs vus dans les deux variations ont été écartés par la requête, soit 1,01 %/.test(rd)&&/vérifiez l.affectation/.test(rd)&&(await ov())<=0,rd);
await fresh();await pk(p);await p.click('#gst-app [data-act=howto][data-v=bigquery]');await p.waitForTimeout(200);const sql=await p.evaluate(()=>document.querySelector('#gst-app pre.sql').textContent);
ok(`[${w}] requête modèle : compte les exclus (exclus_deux_variations) ; note sur l'identifiant et le délai de trois jours`,/exclus AS \(/.test(sql)&&/\(SELECT n FROM exclus\) AS exclus_deux_variations/.test(sql)&&/trois jours/.test(await txt('.imp-r .cap'))&&(await ov())<=0);
// 5. textes
await pk(p);await p.click('#gst-app [data-act=howto][data-v=ga4]');await p.waitForTimeout(200);await p.click('#gst-app details.tips summary');const g=await txt('.imp');
ok(`[${w}] tutoriel GA4 : plus de « session_start donne les visiteurs exposés » ; exposition, portée utilisateur et renvoi vers BigQuery`,!/session_start<\/code> donne|session_start donne les visiteurs exposés/.test(g)&&/événement d.exposition/.test(g)&&/N.utilisez pas session_start/.test(g)&&/portée utilisateur/.test(g)&&/onglet BigQuery/.test(g)&&(await ov())<=0,g.slice(0,120));
await pk(p);await p.click('#gst-app [data-act=howto][data-v=piano]');await p.waitForTimeout(200);await p.click('#gst-app details.tips summary');const pt=await txt('.imp'),all=await txt('');
ok(`[${w}] tutoriel Piano : attribution à vérifier, segments, mode éco`,/visite suivante/.test(pt)&&/par deux segments/.test(pt)&&/mode éco/.test(pt));
const page=await p.evaluate(()=>document.querySelector('#gst-app').innerText);
ok(`[${w}] confidentialité : plus de « Vos chiffres ne quittent pas votre poste » ; « Sans compte, vos chiffres restent dans votre navigateur » et « jamais envoyé » pour le fichier`,!/Vos chiffres ne quittent pas votre poste/.test(page)&&/Sans compte, vos chiffres restent dans votre navigateur/.test(page)&&/Fichier lu dans votre navigateur, jamais envoyé/.test(page),null);
ok(`[${w}] aucune erreur JS`,errs.length===0,errs);await cx.close();}
console.log(okc+'/'+n+(okc===n?' OK':' ÉCHEC'));await b.close();})();

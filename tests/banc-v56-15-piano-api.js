// v56.15 : import par l'API Piano (API simulée : aucune clé réelle, aucun appel à Piano)
const {chromium}=require('playwright');const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-15.html');
let n=0,okc=0;const ok=(l,c,d)=>{n++;if(c)okc++;console.log((c?'✅ ':'❌ ')+l+(d!==undefined?' — '+JSON.stringify(d):''));};
const D=k=>{const d=new Date();d.setDate(d.getDate()+k);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};const fr=i=>i.slice(8)+'/'+i.slice(5,7)+'/'+i.slice(0,4);
const AK='ACCESSKEYFACTICE01',SK='SECRETFACTICE0000000002',KEY=AK+'_'+SK;
const PARAM={columns:['mv_test','mv_creation','m_users','m_conv_users'],sort:['-m_users'],space:{s:[999001]},period:{p1:[{type:'D',start:'2020-01-01',end:'2020-01-07'}]},'max-results':50,'page-num':1,options:{},evo:{granularity:'D'}};
const URLQ='https://api.atinternet.io/v3/data/getData?param='+encodeURIComponent(JSON.stringify(PARAM));
const feed=(m,extra)=>({DataFeed:{Columns:[{Name:'mv_test',Label:'MVT - Test'},{Name:'mv_creation',Label:'MVT - Variante'},{Name:'m_users',Label:'Utilisateurs'},{Name:'m_conv_users',Label:'Utilisateurs convertis'}],Rows:[{mv_test:'9900001[FR] Essai',mv_creation:'8800001Variation 1',m_users:Math.round(4600*m),m_conv_users:Math.round(935*m)},{mv_test:'9900001[FR] Essai',mv_creation:'0Original',m_users:Math.round(4610*m),m_conv_users:Math.round(923*m)}].concat(extra||[])}});
(async()=>{const b=await chromium.launch();for(const w of [360,1280]){const cx=await b.newContext({viewport:{width:w,height:900}});const p=await cx.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));
const calls=[];let mode='ok',mult=1,delay=0,dn=0;const others=[];
await cx.route('**/*',async r=>{const u=r.request().url();if(u.startsWith('file:'))return r.continue();
  if(!u.startsWith('https://api.atinternet.io/')){if(!/^https:\/\/(fonts\.googleapis\.com|fonts\.gstatic\.com|fwoptimisation\.com\/wp-content\/uploads)\//.test(u)||r.request().method()!=='GET'||u.includes(AK)||u.includes(SK))others.push(u);return r.abort();}
  const h={'access-control-allow-origin':'*','access-control-allow-headers':'x-api-key','access-control-allow-methods':'GET,OPTIONS'};
  if(r.request().method()==='OPTIONS')return r.fulfill({status:204,headers:h});
  const rq=r.request(),U=new URL(u);calls.push({path:U.origin+U.pathname,param:JSON.parse(U.searchParams.get('param')),key:rq.headers()['x-api-key'],keyInUrl:u.includes(AK)||u.includes(SK),cookie:rq.headers()['cookie']||'',referer:rq.headers()['referer']||''});
  if(mode==='401')return r.fulfill({status:401,headers:h,contentType:'application/json',body:'{"ErrorMessage":"Unauthorized"}'});
  if(mode==='xss')return r.fulfill({status:200,headers:h,contentType:'application/json',body:JSON.stringify(feed(mult,[{mv_test:'<img src=x onerror=window.__x=1>',mv_creation:'<script>window.__x=1</script>',m_users:5,m_conv_users:1}]))});
  if(mode==='vide')return r.fulfill({status:200,headers:h,contentType:'application/json',body:'{"DataFeed":{"Columns":[],"Rows":[]}}'});
  if(delay&&dn++===0){const m0=mult;await new Promise(z=>setTimeout(z,delay));return r.fulfill({status:200,headers:h,contentType:'application/json',body:JSON.stringify(feed(m0))});}
  return r.fulfill({status:200,headers:h,contentType:'application/json',body:JSON.stringify(feed(mult))});});
const fresh=async()=>{await p.goto('file://'+path.resolve(FILE));await p.evaluate(()=>{try{localStorage.clear()}catch(e){}});await p.reload();await p.waitForSelector('.cta button');};
const txt=s=>p.evaluate(s=>{const e=document.querySelector('#gst-app '+s);return e&&!e.hidden?e.innerText:'';},s);const cnt=s=>p.locator('#gst-app '+s).count();const ov=()=>p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
const st=()=>p.evaluate(()=>{const s=window.GST.getState();return {n:s.weeks.length,start:s.plan.startDate,wk:s.weeks.map(x=>x.wk||null),end:s.weeks.map(x=>x.end||null),api:s.api?JSON.stringify(s.api):null,vis:s.weeks.map(x=>x.A.n)};});
const leak=()=>p.evaluate(a=>{const out=[];const all=JSON.stringify(Object.keys(localStorage).map(k=>[k,localStorage.getItem(k)]))+document.documentElement.outerHTML+location.href+JSON.stringify(window.GST.getState());a.forEach(k=>{if(all.includes(k))out.push(k.slice(0,6));});[...document.querySelectorAll('input')].forEach(i=>{if(a.includes(i.getAttribute('value')))out.push('attr');});return out;},[AK,SK,KEY]);
const openForm=async()=>{await p.click('#gst-app [data-act=howto][data-v=piano]').catch(()=>{});await p.waitForTimeout(200);await p.click('#gst-app [data-act=apiopen]');await p.waitForSelector('#gst-app #gst-purl');};
const fill=async(o)=>{if(o.url!==undefined)await p.fill('#gst-app #gst-purl',o.url);if(o.start)await p.fill('#gst-app #gst-pstart',o.start);if(o.ak!==undefined)await p.fill('#gst-app #gst-pak',o.ak);if(o.sk!==undefined)await p.fill('#gst-app #gst-psk',o.sk);};
const go=async()=>{await p.click('#gst-app [data-act=apigo]');await p.waitForTimeout(900);};
// 1. formulaire
await fresh();await openForm();
ok(`[${w}] formulaire : adresse, date de début, deux champs de clé masqués, choix de mémorisation « Non » par défaut, sans débordement`,(await cnt('#gst-purl'))===1&&(await cnt('#gst-pstart'))===1&&(await p.getAttribute('#gst-app #gst-pak','type'))==='password'&&(await p.getAttribute('#gst-app #gst-psk','type'))==='password'&&(await p.isChecked('#gst-app [data-api=mem][value=non]'))&&(await ov())<=0);
// 2. adresses refusées : la clé ne part nulle part
const bads=['https://evil.example/v3/data/getData?param='+encodeURIComponent(JSON.stringify(PARAM)),'https://api.atinternet.io.evil.example/v3/data/getData?param=%7B%7D','http://api.atinternet.io/v3/data/getData?param='+encodeURIComponent(JSON.stringify(PARAM)),'https://user:pw@api.atinternet.io/v3/data/getData?param=%7B%7D','https://api.atinternet.io:8443/v3/data/getData?param=%7B%7D','https://api.atinternet.io/v3/data/getData/../../x?param=%7B%7D','javascript:alert(1)','https://api.atinternet.io/v2/x?param=%7B%7D'];
const rb=[];for(const u of bads){await fill({url:u,start:D(-8),ak:AK,sk:SK});await go();rb.push(/n.est pas celle de l.API Piano|illisible/.test(await txt('.api-err')));}
ok(`[${w}] ${bads.length} adresses piégées (autre domaine, sous-domaine trompeur, http, identifiants, port, autre chemin, javascript:) : toutes refusées, aucun appel réseau`,rb.every(x=>x)&&calls.length===0&&others.length===0,{rb,calls:calls.length,others});
ok(`[${w}] après un refus : les champs de clé gardent leur saisie (pas de ré-affichage), rien n'est écrit dans la page ni sur le poste`,(await p.inputValue('#gst-app #gst-pak'))===AK&&(await leak()).length===0,await leak());
// 3. clé refusée par Piano
mode='401';await fill({url:URLQ});await go();
ok(`[${w}] clé refusée (401) : message clair, pas d'import, la clé n'apparaît pas dans le message`,/Piano refuse cette clé \(erreur 401\)/.test(await txt('.api-err'))&&!(await txt('.api-err')).includes(AK)&&(await cnt('.dv'))===0,await txt('.api-err'));
mode='vide';await go();ok(`[${w}] aucune ligne : message clair`,/aucune ligne sur cette période/.test(await txt('.api-err')),await txt('.api-err'));
// 4. appel correct
mode='ok';calls.length=0;await fill({start:D(-17)});await go();await p.waitForSelector('#gst-app .dv');const c=calls[0];
ok(`[${w}] appel : adresse fixe de Piano, clé dans l'en-tête seulement, ni cookie ni référent`,calls.length===1&&c.path==='https://api.atinternet.io/v3/data/getData'&&c.key===KEY&&!c.keyInUrl&&!c.cookie&&!c.referer,{n:calls.length,path:c.path,keyInUrl:c.keyInUrl,cookie:c.cookie,referer:c.referer});
ok(`[${w}] requête : période = début du test → fin de la 2e semaine complète (${D(-17)} → ${D(-4)}), colonnes et site conservés, champs inconnus retirés, 1 000 lignes`,c.param.period.p1[0].start===D(-17)&&c.param.period.p1[0].end===D(-4)&&c.param.period.p1.length===1&&c.param.columns.join()===PARAM.columns.join()&&c.param.space.s[0]===999001&&!('evo' in c.param)&&c.param['max-results']===1000,c.param);
ok(`[${w}] écran de vérification : colonnes reconnues, dates verrouillées, période « demandée à Piano », pas de case de confirmation, sans débordement`,(await p.isDisabled('#gst-app [data-d=endDate]'))&&(await p.inputValue('#gst-app [data-d=endDate]'))===D(-4)&&/Période demandée à Piano/.test(await txt('.dv-gate'))&&/semaine 2 sur/.test(await txt('.dv-gate'))&&(await cnt('[data-d=endOk]'))===0&&/4.610 visiteurs pour Original, 4.600 pour Variation 1/.test(await txt('.dv-read'))&&(await ov())<=0,[await txt('.dv-gate'),await txt('.dv-read')]);
await p.click('#gst-app [data-act=apply]');await p.waitForTimeout(900);let s=await st();
ok(`[${w}] import : lecture de la semaine 2 datée, requête gardée avec le test, sans la clé`,s.n===1&&s.wk[0]===2&&s.end[0]===D(-4)&&s.start===D(-17)&&s.api&&s.api.includes('mv_creation')&&!s.api.includes('period'),s);
ok(`[${w}] aucune trace de la clé : ni stockage local, ni page, ni adresse, ni état du test`,(await leak()).length===0,await leak());
const tok=await p.evaluate(()=>window.GST.share());const c2=await b.newContext({viewport:{width:w,height:900}});const q2=await c2.newPage();await q2.goto('file://'+path.resolve(FILE)+'#t='+tok);await q2.waitForTimeout(1500);const sh=await q2.evaluate(()=>{const s=window.GST.getState();return {n:s.weeks.length,api:s.api||null,bar:document.querySelectorAll('#gst-app .apibar').length,all:JSON.stringify(s)};});await c2.close();
ok(`[${w}] lien de partage ouvert ailleurs : les données y sont, mais ni la requête Piano, ni l'identifiant du site, ni la clé, ni le bandeau`,sh.n===1&&sh.api===null&&sh.bar===0&&!sh.all.includes('mv_creation')&&!sh.all.includes('999001')&&!sh.all.includes(AK)&&!tok.includes(AK),{n:sh.n,api:sh.api,len:tok.length});
// 5. bandeau : rien à collecter tant qu'une semaine n'est pas écoulée
ok(`[${w}] bandeau « Piano connecté », pas de collecte possible avant une nouvelle semaine complète`,/Piano connecté/.test(await txt('.apibar'))&&(await cnt('[data-act=apiupd]'))===0&&(await ov())<=0,await txt('.apibar'));
// 6. une semaine plus tard (début reculé de 7 jours) : collecte automatique, clé encore en mémoire
await p.evaluate(a=>{const s=window.GST.getState();s.plan.startDate=a[0];s.weeks[0].end=a[1];},[D(-24),D(-11)]);mult=1.5;calls.length=0;
await p.click('#gst-app [data-act=tab][data-v=donnees]').catch(()=>{});await p.waitForTimeout(300);await p.click('#gst-app [data-act=tab][data-v=resultats]').catch(()=>{});await p.waitForTimeout(300);
ok(`[${w}] nouvelle semaine : bandeau « Nouvelle semaine complète disponible », sans champ de clé (clé en mémoire), sans débordement`,/Nouvelle semaine complète disponible dans Piano : semaine 3/.test(await txt('.apibar'))&&(await cnt('.apibar input'))===0&&(await ov())<=0,await txt('.apibar'));
await p.click('#gst-app [data-act=apiupd]');await p.waitForTimeout(1200);s=await st();
ok(`[${w}] collecte : semaine 3 ajoutée sans écran intermédiaire, message affiché, période ${D(-24)} → ${D(-4)}`,s.n===2&&s.wk.join()==='2,3'&&s.end[1]===D(-4)&&s.vis[1]===6915&&(await cnt('.dv'))===0&&/Semaine 3 récupérée automatiquement depuis Piano/.test(await txt('.ok'))&&calls.length===1&&calls[0].param.period.p1[0].start===D(-24)&&calls[0].param.period.p1[0].end===D(-4),{s,ok:await txt('.ok')});
// 7. rechargement de la page : la clé a disparu, le test et sa requête restent
await p.reload();await p.waitForSelector('#gst-app');await p.waitForTimeout(500);const keyL=await p.evaluate(()=>Object.keys(localStorage).filter(k=>/gstSeq_v40_/.test(k))[0]);await p.evaluate(k=>{const o=JSON.parse(localStorage.getItem(k));o.plan.startDate=o.plan.startDate.replace(/.*/,window.__s);localStorage.setItem(k,JSON.stringify(o));},keyL).catch(()=>{});
await p.evaluate(a=>{const k=Object.keys(localStorage).filter(k=>/gstSeq_v40_/.test(k))[0];const o=JSON.parse(localStorage.getItem(k));o.plan.startDate=a[0];o.weeks[0].end=a[1];o.weeks[1].end=a[2];o.weeks[0].wk=1;o.weeks[1].wk=2;localStorage.setItem(k,JSON.stringify(o));},[D(-24),D(-18),D(-11)]);
await p.reload();await p.waitForSelector('#gst-app');await p.waitForTimeout(400);await p.selectOption('#gst-app [data-act=load]',{index:1});await p.waitForTimeout(700);calls.length=0;
ok(`[${w}] après rechargement : la clé n'est plus en mémoire, le bandeau demande la clé d'accès et la clé secrète, aucun appel fait seul`,/semaine 3/.test(await txt('.apibar'))&&(await cnt('.apibar #gst-pak'))===1&&(await cnt('.apibar #gst-psk'))===1&&calls.length===0,await txt('.apibar'));
await p.click('#gst-app [data-act=apiupd]');await p.waitForTimeout(500);ok(`[${w}] collecte sans clé : refusée avec message, aucun appel`,/Saisissez la clé d.accès et la clé secrète/.test(await txt('.api-err'))&&calls.length===0,await txt('.api-err'));
// 8. réponse piégée : rien n'est exécuté
mode='xss';mult=2.2;await p.fill('#gst-app #gst-pak',AK);await p.fill('#gst-app #gst-psk',SK);await p.click('#gst-app [data-act=apiupd]');await p.waitForTimeout(1200);
ok(`[${w}] réponse de Piano contenant des balises : aucun script exécuté, aucune balise injectée`,(await p.evaluate(()=>window.__x))===undefined&&(await p.evaluate(()=>document.querySelectorAll('#gst-app img[src=x],#gst-app script').length))===0,await st());
// 8 bis. deux tests, réponse lente : une réponse n'est jamais ajoutée à un autre test que celui qui l'a demandée
p.on('dialog',d=>d.accept());mode='ok';mult=1;await fresh();
for(const nm of ['Test B','Test C']){await openForm();await fill({url:URLQ,start:D(-10),ak:AK,sk:SK});await go();await p.waitForSelector('#gst-app .dv');await p.fill('#gst-app [data-d=name]',nm);await p.locator('#gst-app [data-d=name]').blur();await p.waitForTimeout(200);await p.click('#gst-app [data-act=apply]');await p.waitForTimeout(700);await p.click('#gst-app [data-act=new]');await p.waitForTimeout(400);}
await p.evaluate(a=>{Object.keys(localStorage).filter(k=>/gstSeq_v40_Test/.test(k)).forEach(k=>{const o=JSON.parse(localStorage.getItem(k));o.plan.startDate=a[0];o.weeks[0].end=a[1];localStorage.setItem(k,JSON.stringify(o));});},[D(-17),D(-11)]);
calls.length=0;delay=1500;dn=0;mult=5;const optB=await p.evaluate(()=>[...document.querySelectorAll('#gst-app [data-act=load] option')].map(o=>o.text));
await p.selectOption('#gst-app [data-act=load]',{label:'Test B'});await p.waitForTimeout(250);mult=9;await p.click('#gst-app [data-act=new]');await p.waitForTimeout(250);await p.selectOption('#gst-app [data-act=load]',{label:'Test C'});await p.waitForTimeout(3000);
const sc=await p.evaluate(()=>{const s=window.GST.getState();const b=JSON.parse(localStorage.getItem('gstSeq_v40_Test B'));return {cur:s.name,n:s.weeks.length,vis:s.weeks.map(x=>x.A.n),bn:b.weeks.length};});
ok(`[${w}] réponse lente du test B arrivée pendant que le test C est ouvert : rien n'est ajouté à C avec les chiffres de B, B reste intact`,sc.cur==='Test C'&&sc.bn===1&&(sc.n===1||(sc.n===2&&sc.vis[1]===Math.round(4610*9))),{sc,calls:calls.length,optB});
delay=0;
// 8 ter. clé refusée en cours de visite : elle est oubliée et redemandée
await p.click('#gst-app [data-act=new]');await p.waitForTimeout(300);await p.reload();await p.waitForSelector('#gst-app');await p.waitForTimeout(300);await p.selectOption('#gst-app [data-act=load]',{label:'Test B'});await p.waitForTimeout(500);
if(await cnt('.apibar #gst-pak')){await p.fill('#gst-app #gst-pak',AK);await p.fill('#gst-app #gst-psk',SK);mode='401';await p.click('#gst-app [data-act=apiupd]');await p.waitForTimeout(900);}
ok(`[${w}] clé refusée (401) lors d'une collecte : message, et les champs de clé restent proposés (clé non gardée)`,/Piano refuse cette clé/.test(await txt('.api-err'))&&(await cnt('.apibar #gst-pak'))===1,await txt('.api-err'));mode='ok';
ok(`[${w}] le bandeau nomme le site interrogé`,/Site Piano 999001/.test(await txt('.apibar')),await txt('.apibar'));
// 9. mémorisation chiffrée
mode='ok';mult=1;await fresh();await openForm();await fill({url:URLQ,start:D(-10),ak:AK,sk:SK});await p.check('#gst-app [data-api=mem][value=code]');await p.waitForTimeout(200);
ok(`[${w}] choix « chiffrée par un code » : le champ du code apparaît, les clés déjà saisies ne sont pas effacées`,(await p.isVisible('#gst-app #gst-pcode'))&&(await p.inputValue('#gst-app #gst-pak'))===AK);
await p.fill('#gst-app #gst-pcode','court');await go();ok(`[${w}] code trop court : refusé, aucun appel`,/au moins 12 caractères/.test(await txt('.api-err')));
await p.fill('#gst-app #gst-pcode','un code assez long');await go();await p.waitForSelector('#gst-app .dv',{timeout:20000});
const sto=await p.evaluate(()=>localStorage.getItem('fwoPianoCle_v1'));const so=JSON.parse(sto||'{}');
ok(`[${w}] clé mémorisée : chiffrée (sel, vecteur, texte chiffré), illisible en clair, ni la clé ni le code dans le stockage`,so.v===1&&so.s&&so.i&&so.c&&!sto.includes(AK)&&!sto.includes(SK)&&!sto.includes('un code')&&(await leak()).length===0,{len:(sto||'').length});
await p.click('#gst-app [data-act=apply]');await p.waitForTimeout(800);
await p.evaluate(a=>{const k=Object.keys(localStorage).filter(k=>/gstSeq_v40_/.test(k))[0];const o=JSON.parse(localStorage.getItem(k));o.plan.startDate=a[0];o.weeks[0].end=a[1];localStorage.setItem(k,JSON.stringify(o));},[D(-17),D(-11)]);
await p.reload();await p.waitForSelector('#gst-app');await p.waitForTimeout(400);await p.selectOption('#gst-app [data-act=load]',{index:1});await p.waitForTimeout(700);calls.length=0;mult=5;
ok(`[${w}] après rechargement : le bandeau demande seulement le code`,(await cnt('.apibar #gst-pcode'))===1&&(await cnt('.apibar #gst-pak'))===0,await txt('.apibar'));
await p.fill('#gst-app #gst-pcode','mauvais code 123');await p.click('#gst-app [data-act=apiupd]');await p.waitForTimeout(2500);
ok(`[${w}] mauvais code : « Code incorrect », aucun appel à Piano`,/Code incorrect/.test(await txt('.api-err'))&&calls.length===0,await txt('.api-err'));
await p.fill('#gst-app #gst-pcode','un code assez long');await p.click('#gst-app [data-act=apiupd]');await p.waitForTimeout(3500);s=await st();
ok(`[${w}] bon code : semaine 2 collectée avec la clé déchiffrée`,s.n===2&&s.wk.join()==='1,2'&&calls.length===1&&calls[0].key===KEY,{s,calls:calls.length,err:await txt('.api-err'),dv:await cnt('.dv'),e:await txt('.dv .err'),g:await txt('.dv-gate'),w:await txt('.dv-warn')});
await p.evaluate(()=>{const s=window.GST.getState();});await p.click('#gst-app [data-act=apiforget]').catch(()=>{});await p.waitForTimeout(300);
ok(`[${w}] « Oublier la clé mémorisée » : entrée effacée du poste`,(await p.evaluate(()=>localStorage.getItem('fwoPianoCle_v1')))===null);
await p.click('#gst-app [data-act=apioff]').catch(()=>{});await p.waitForTimeout(300);ok(`[${w}] « Déconnecter Piano de ce test » : requête retirée, bandeau disparu`,(await st()).api===null&&(await cnt('.apibar'))===0);
ok(`[${w}] aucune requête vers un autre domaine, aucune erreur JS`,others.length===0&&errs.length===0,{others,errs});await cx.close();}
console.log(okc+'/'+n+(okc===n?' OK':' ÉCHEC'));await b.close();})();

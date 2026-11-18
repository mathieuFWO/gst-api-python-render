const pk=async p=>{const u=p.locator('#gst-app [data-act=unpick]');if(await u.count())await u.first().click();};
// v56.18 : barre de compte, écran « Nouveau test », onglet BigQuery, mise à jour des tests depuis Piano à l'ouverture du tableau de bord (extension et API Piano simulées)
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
const FILE=path.join(__dirname,'..','calculateur-sequentiel-v56-18.html'),SHOTS=process.argv[2];const HTML='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>button{white-space:nowrap}body{margin:0;padding:0 8px}</style></head><body>'+fs.readFileSync(FILE,'utf8')+'</body></html>';
let pass=0,fail=0;const ok=(n,c,d)=>{c?pass++:fail++;console.log((c?'✅ ':'❌ ')+n+(c?'':' — '+JSON.stringify(d)));};
function mock(plugin){const db={tests:[],seq:100,mails:[],tokens:{}};let session=null; // session = email
  const row=(t,me)=>({id:t.id,name:t.name,sum:t.sum,updated:'2026-11-16',mine:t.owner===me,owner:t.owner,shared:t.owner===me?t.shared.slice():[]});
  const handler=async route=>{const req=route.request(),u=new URL(req.url()),m=req.method(),J=(o,s)=>route.fulfill({status:s||200,contentType:'application/json',body:JSON.stringify(o)});
    if(u.pathname==='/'||u.pathname==='/outil/')return route.fulfill({status:200,contentType:'text/html; charset=utf-8',body:HTML});
    if(u.pathname==='/wp-admin/admin-ajax.php')return route.fulfill({status:200,contentType:'text/plain',body:session&&plugin?'abcdef1234':'0'});
    if(!u.pathname.startsWith('/wp-json/fwo-gst/v1/')||!plugin)return J({code:'rest_no_route',message:'Aucune route'},404);
    const p=u.pathname.slice('/wp-json/fwo-gst/v1/'.length),nonce=req.headers()['x-wp-nonce']==='abcdef1234',me=nonce?session:null;let body={};try{body=req.postData()?JSON.parse(req.postData()):{};}catch(e){}
    if(p==='me')return J({enabled:true,user:me?{email:me,name:me.split('@')[0]}:null});
    if(p==='login-link'&&m==='POST'){const tk='tk'+(++db.seq);db.tokens[tk]={email:String(body.email).toLowerCase(),test:body.test||0};db.mails.push({to:body.email,tk});return J({sent:true});}
    if(p==='login'){const tk=m==='POST'?new URLSearchParams(req.postData()||'').get('token'):u.searchParams.get('token');const d=db.tokens[tk];if(d&&m!=='POST')return route.fulfill({status:200,contentType:'text/html; charset=utf-8',body:'<main><p>Vous allez être connecté avec <strong>'+d.email+'</strong></p><form method="post" action="/wp-json/fwo-gst/v1/login"><input type="hidden" name="token" value="'+tk+'"><button type="submit">Ouvrir mon espace</button></form></main>'});delete db.tokens[tk];const go=h=>route.fulfill({status:200,contentType:'text/html',body:'<script>location.replace("/'+h+'")</script>'});/* le vrai serveur répond par une redirection 302 */if(!d)return go('#lien-expire');session=d.email;return go(d.test?'#test='+d.test:'#compte');}
    if(!me)return J({code:'rest_forbidden',message:'Connexion requise.'},401);
    if(p==='logout'){session=null;return J({ok:true});}
    if(p==='account'&&m==='DELETE'){db.tests=db.tests.filter(t=>t.owner!==me);session=null;return J({ok:true});}
    if(p==='tests'&&m==='GET')return J({tests:db.tests.filter(t=>t.owner===me||t.shared.includes(me)).map(t=>row(t,me))});
    if(p==='tests'&&m==='POST'){if(!body.name||!body.state||!body.state.plan)return J({message:'Test illisible.'},400);const t={id:++db.seq,name:body.name,state:body.state,sum:body.sum||null,owner:me,shared:[]};db.tests.push(t);return J(row(t,me));}
    const mm=/^tests\/(\d+)(\/share)?$/.exec(p);if(!mm)return J({message:'Aucune route'},404);const t=db.tests.find(x=>x.id===+mm[1]),acc=t?(t.owner===me?'owner':t.shared.includes(me)?'guest':null):null;
    if(!acc||(acc!=='owner'&&(m!=='GET'||mm[2])))return J({message:'Test introuvable.'},404);
    if(mm[2]){const e=String(body.email||'').toLowerCase();if(m==='POST'){if(!t.shared.includes(e)){t.shared.push(e);db.mails.push({to:e,invite:t.id});}}else t.shared=t.shared.filter(x=>x!==e);return J({shared:t.shared});}
    if(m==='GET')return J(Object.assign(row(t,me),{state:t.state}));
    if(m==='PUT'){t.name=body.name;t.state=body.state;t.sum=body.sum||null;return J(row(t,me));}
    if(m==='DELETE'){db.tests=db.tests.filter(x=>x!==t);return J({ok:true});}
    return J({message:'Aucune route'},404);};
  return {db,handler,setSession:e=>{session=e;}};}
const D=k=>{const d=new Date();d.setDate(d.getDate()+k);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
const AK='ACCESSKEYFACTICE01',SK='SECRETFACTICE0000000002';
const PARAM={columns:['mv_test','mv_creation','m_users','m_conv_users'],space:{s:[999001]},period:{p1:[{type:'D',start:'2020-01-01',end:'2020-01-07'}]},'max-results':50,'page-num':1,options:{}};
const URLQ='https://api.atinternet.io/v3/data/getData?param='+encodeURIComponent(JSON.stringify(PARAM));
const feed=m=>({DataFeed:{Columns:[{Name:'mv_test',Label:'MVT - Test'},{Name:'mv_creation',Label:'MVT - Variante'},{Name:'m_users',Label:'Utilisateurs'},{Name:'m_conv_users',Label:'Utilisateurs convertis'}],Rows:[{mv_test:'9900001[FR] Essai',mv_creation:'8800001Variation 1',m_users:Math.round(4600*m),m_conv_users:Math.round(935*m)},{mv_test:'9900001[FR] Essai',mv_creation:'0Original',m_users:Math.round(4610*m),m_conv_users:Math.round(923*m)}]}});
(async()=>{const b=await chromium.launch();
 for(const [W,tag] of [[360,'360'],[1280,'1280']]){
  const mk=mock(true),ctx=await b.newContext({viewport:{width:W,height:900}}),p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));p.on('dialog',d=>d.accept());await ctx.route('https://gst.test/**',async r=>{if(hang&&/\/tests\/\d+$/.test(new URL(r.request().url()).pathname))return;if(putDelay&&r.request().method()==='PUT')await new Promise(z=>setTimeout(z,putDelay));return mk.handler(r);});
  const calls=[];let mode='ok',mult=1,delay=0,feedNoTest=false,hang=false,putDelay=0;
  await ctx.route('https://api.atinternet.io/**',async r=>{const h={'access-control-allow-origin':'*','access-control-allow-headers':'x-api-key','access-control-allow-methods':'GET,OPTIONS'};if(r.request().method()==='OPTIONS')return r.fulfill({status:204,headers:h});
    const U=new URL(r.request().url());calls.push({param:JSON.parse(U.searchParams.get('param')),key:r.request().headers()['x-api-key']});const m0=mult;if(delay)await new Promise(z=>setTimeout(z,delay));
    if(mode==='401')return r.fulfill({status:401,headers:h,contentType:'application/json',body:'{}'});const fd=feed(m0);if(feedNoTest){fd.DataFeed.Columns=fd.DataFeed.Columns.filter(c=>c.Name!=='mv_test').concat([{Name:'m_extra',Label:'Autre'}]);fd.DataFeed.Rows.forEach(x=>{delete x.mv_test;x.m_extra=3;});}return r.fulfill({status:200,headers:h,contentType:'application/json',body:JSON.stringify(fd)});});
  await ctx.route(/fonts\.(googleapis|gstatic)\.com|fwoptimisation\.com/,r=>r.abort());
  const ov=()=>p.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth),cnt=s=>p.locator('#gst-app '+s).count(),txt=s=>p.evaluate(s=>{const e=document.querySelector('#gst-app '+s);return e&&!e.hidden?e.innerText:'';},s);
  const login=async email=>{await p.goto('https://gst.test/');await p.waitForSelector('.accbar');await p.click('[data-act=acclogin]');await p.fill('[data-f=accemail]',email);await p.click('[data-act=accsend]');await p.waitForSelector('text=Consultez votre messagerie');const tk=mk.db.mails.filter(m=>m.tk).pop().tk;await p.goto('https://gst.test/wp-json/fwo-gst/v1/login?token='+tk);await p.click('button[type=submit]');await p.waitForSelector('.dash-h');};
  const dash=async()=>{await p.click('#gst-app [data-act=dash]');await p.waitForSelector('.dash-h');await p.waitForTimeout(300);};
  const due=(t,start,ends)=>{t.state.plan.startDate=start;t.state.weeks.forEach((w,i)=>{w.end=ends[i];w.wk=i+1;});};
  // --- barre de compte, déconnecté
  await p.goto('https://gst.test/');await p.waitForSelector('.accbar');
  const geo=()=>p.evaluate(()=>{const b=document.querySelector('#gst-app .accbar'),r=b.getBoundingClientRect(),k=[...b.children].map(c=>c.getBoundingClientRect()),a=document.querySelector('#gst-app').getBoundingClientRect();return {logo:b.querySelectorAll('.logo').length,right:Math.round(a.right-Math.max(...k.map(x=>x.right))),left:Math.round(Math.min(...k.map(x=>x.left))-a.left),h:Math.round(r.height),border:getComputedStyle(b).borderBottomWidth};});
  let g=await geo();ok(`[${tag}] barre de compte déconnecté : plus de logo en double, calée à droite, sans filet, sans débordement`,g.logo===0&&g.right<=20&&g.left>=0&&g.border==='0px'&&/Se connecter/.test(await txt('.accbar'))&&await ov()<=0,g);
  await login('mat@fwo.test');g=await geo();
  ok(`[${tag}] barre de compte connecté : « Tableau de bord » en bouton actif, email, déconnexion, calés à droite, une hauteur contenue`,g.logo===0&&g.right<=20&&g.left>=0&&(await cnt('.accbar button.acc-d.on'))===1&&/mat@fwo\.test/.test(await txt('.accbar'))&&(await cnt('.accbar [data-act=acclogout]'))===1&&g.h<=(W<500?90:50)&&await ov()<=0,g);
  // --- Nouveau test : écran de départ
  await p.click('[data-act=accnew]');await p.waitForSelector('.imp');
  ok(`[${tag}] « Nouveau test » : écran de départ sans la page d'accueil (ni titre commercial, ni démonstration animée), retour au tableau de bord, 6 sources, zone de dépôt, connexion Piano, saisie manuelle`,(await cnt('.hero2'))===0&&(await cnt('.start-h'))===1&&/Nouveau test/.test(await txt('.start-h h2'))&&(await cnt('.start-h [data-act=dash]'))===1&&(await cnt('.imp.ch .tc'))===5&&(await cnt('.lp'))===0&&(await cnt('[data-act=howto][data-v=manuel]'))===1&&await ov()<=0,await ov());
  ok(`[${tag}] barre de compte hors tableau de bord : bouton non actif`,(await cnt('.accbar button.acc-d.on'))===0);
  // --- import par l'API puis enregistrement dans le compte
  await p.click('#gst-app .tc[data-v=piano]');await p.waitForTimeout(150);await p.click('#gst-app [data-act=apiopen]');await p.waitForSelector('#gst-purl');await p.fill('#gst-purl',URLQ);await p.fill('#gst-pstart',D(-10));await p.fill('#gst-pak',AK);await p.fill('#gst-psk',SK);await p.click('[data-act=apigo]');await p.waitForSelector('.dv');
  ok(`[${tag}] un seul test dans la réponse : nom proposé et liste sans l'identifiant Piano`,(await p.inputValue('#gst-app [data-d=name]'))==='[FR] Essai'&&(await p.evaluate(()=>[...document.querySelectorAll('#gst-app [data-d=test] option')].map(o=>o.text+'|'+o.value).join()))==='[FR] Essai|9900001[FR] Essai',await p.inputValue('#gst-app [data-d=name]'));
  const selOv=await p.evaluate(()=>[...document.querySelectorAll('#gst-app .dv-g select')].filter(s=>s.scrollWidth>s.clientWidth+1).map(s=>s.id+':'+s.scrollWidth+'>'+s.clientWidth));
  ok(`[${tag}] écran d'import : aucune liste dont le texte dépasse`,selOv.length===0,selOv);
  await p.click('[data-act=apply]');await p.waitForTimeout(800);await p.click('[data-act=save]');await p.waitForTimeout(700);
  const T=mk.db.tests[0],srv=JSON.stringify(T||{});const loc=await p.evaluate(()=>localStorage.getItem('fwoPianoReq_v1'));
  ok(`[${tag}] test enregistré : le serveur ne reçoit ni la requête Piano, ni l'identifiant du site, ni la clé ; la requête reste sur le poste`,!!T&&!srv.includes('999001')&&!srv.includes('mv_creation')&&!srv.includes(AK)&&!srv.includes(SK)&&!('api' in T.state)&&loc&&loc.includes('999001')&&!loc.includes(AK)&&!loc.includes(SK),{srv:srv.slice(0,60),loc:(loc||'').slice(0,80)});
  // --- nouvelle semaine : mise à jour sans demande, clé en mémoire
  await dash();await p.click('[data-act=accnew]');await p.waitForSelector('.imp');due(T,D(-17),[D(-11)]);mult=5;calls.length=0;await dash();await p.waitForTimeout(1500);
  const loc1=await p.evaluate(()=>{const k=Object.keys(localStorage).filter(k=>/gstSeq_v40_/.test(k));return k.map(x=>JSON.parse(localStorage.getItem(x)).weeks.length);});
  ok(`[${tag}] ouverture du tableau de bord une semaine plus tard : le test passe à 2 lectures sur le serveur sans aucun clic, un seul appel à Piano, ligne à jour, message`,T.state.weeks.length===2&&T.sum&&T.sum.n===2&&calls.length===1&&/2\/4 sem\./.test(await txt('.dash'))&&/1 test mis à jour depuis Piano/.test(await txt('.ok'))&&T.state.weeks[1].end===D(-4)&&!JSON.stringify(T).includes('999001'),{w:T.state.weeks.length,sum:T.sum,calls:calls.length,ok:await txt('.ok')});
  ok(`[${tag}] la mise à jour n'écrit pas de copie locale du test`,loc1.every(n=>n===1),loc1);
  calls.length=0;await dash();await p.waitForTimeout(600);ok(`[${tag}] retour sur le tableau de bord : repère « Piano » sur le test, pas de second appel le même jour, sans débordement`,calls.length===0&&(await cnt('.dr .tbadge'))===1&&await ov()<=0);
  // --- après rechargement : la clé est redemandée une fois pour tous les tests
  due(T,D(-24),[D(-18),D(-11)]);mult=9;await p.goto('https://gst.test/#compte');await p.reload();await p.waitForSelector('.dash-h');await p.waitForTimeout(600);calls.length=0;
  ok(`[${tag}] nouvelle visite : bandeau « 1 test connecté à Piano » avec les deux champs de clé, aucun appel fait seul, sans débordement`,/1 test connecté à Piano/.test(await txt('.apibar'))&&(await cnt('.apibar #gst-pak'))===1&&calls.length===0&&await ov()<=0,await txt('.apibar'));
  // --- verrou pendant la mise à jour
  delay=1200;await p.fill('#gst-app #gst-pak',AK);await p.fill('#gst-app #gst-psk',SK);await p.click('[data-act=dashkey]');await p.waitForTimeout(400);
  const mid=await txt('.apibar');await p.click('#gst-app .dr:not(.dh)',{timeout:2000}).catch(()=>{});await p.waitForTimeout(200);const stillDash=(await cnt('.dash-h'))===1;await p.waitForTimeout(2600);delay=0;
  ok(`[${tag}] pendant la mise à jour : bandeau de progression, un clic sur une ligne est ignoré ; à la fin le test a 3 lectures`,/Mise à jour depuis Piano/.test(mid)&&stillDash&&(await cnt('.dash-h'))===1&&T.state.weeks.length===3&&T.sum.n===3,{mid,stillDash,w:T.state.weeks.length});
  // --- chiffres douteux : le test n'est pas modifié
  const before=JSON.stringify(T.state);T.state.plan.k=6;due(T,D(-31),[D(-25),D(-18),D(-11)]);const b2=JSON.stringify(T.state);mult=9.2;await p.evaluate(()=>{});await p.goto('https://gst.test/#compte');await p.reload();await p.waitForSelector('.dash-h');await p.waitForTimeout(500);await p.fill('#gst-app #gst-pak',AK);await p.fill('#gst-app #gst-psk',SK);await p.click('[data-act=dashkey]');await p.waitForTimeout(1800);
  ok(`[${tag}] chiffres qui ne ressemblent pas à un cumul : test laissé tel quel, message « demande une vérification »`,JSON.stringify(T.state)===b2&&/1 test demande une vérification/.test(await txt('.ok')),{ok:await txt('.ok'),err:await txt('.err')});
  // --- clé refusée
  mode='401';await p.goto('https://gst.test/#compte');await p.reload();await p.waitForSelector('.dash-h');await p.waitForTimeout(500);await p.fill('#gst-app #gst-pak',AK);await p.fill('#gst-app #gst-psk','MAUVAISSECRET000');await p.click('[data-act=dashkey]');await p.waitForTimeout(1500);
  ok(`[${tag}] clé refusée par Piano : message, test inchangé, la clé est redemandée`,/Piano refuse cette clé/.test(await txt('.err'))&&JSON.stringify(T.state)===b2,await txt('.err'));mode='ok';
  // --- relecture v56.10 : arrêt possible, interface jamais figée ; requête locale modifiée refusée
  { due(T,D(-31),[D(-25),D(-18),D(-11)]);mult=30;delay=2500;await p.goto('https://gst.test/#compte');await p.reload();await p.waitForSelector('.dash-h');await p.waitForTimeout(500);await p.fill('#gst-app #gst-pak',AK);await p.fill('#gst-app #gst-psk',SK);await p.click('[data-act=dashkey]');await p.waitForTimeout(500);
    const hasStop=(await cnt('[data-act=syncstop]'))===1;await p.click('#gst-app [data-act=syncstop]');await p.waitForTimeout(300);const b3=JSON.stringify(T.state);await p.click('#gst-app [data-act=dashwho][data-v=compte]');await p.waitForTimeout(200);const free=(await cnt('[data-act=accdelete]'))===1;await p.click('#gst-app [data-act=dashwho][data-v=mes]');await p.waitForTimeout(3000);delay=0;
    ok(`[${tag}] mise à jour en cours : bouton « Arrêter », l'interface redevient utilisable aussitôt, la réponse tardive n'est pas enregistrée`,hasStop&&free&&JSON.stringify(T.state)===b3&&T.state.weeks.length===3,{hasStop,free,w:T.state.weeks.length});
    await p.evaluate(()=>{const m=JSON.parse(localStorage.getItem('fwoPianoReq_v1'));Object.keys(m).forEach(k=>{m[k].q.columns=m[k].q.columns.filter(c=>c!=='mv_test').concat(['m_extra']);});localStorage.setItem('fwoPianoReq_v1',JSON.stringify(m));});
    feedNoTest=true;await p.goto('https://gst.test/#compte');await p.reload();await p.waitForSelector('.dash-h');await p.waitForTimeout(500);await p.fill('#gst-app #gst-pak',AK);await p.fill('#gst-app #gst-psk',SK);await p.click('[data-act=dashkey]');await p.waitForTimeout(1800);feedNoTest=false;
    ok(`[${tag}] requête locale modifiée (colonne du test retirée) : rien n'est enregistré, le test demande une vérification`,JSON.stringify(T.state)===b3&&/demande une vérification/.test(await txt('.ok')),{ok:await txt('.ok'),err:await txt('.err')});
    await p.evaluate(()=>{const m=JSON.parse(localStorage.getItem('fwoPianoReq_v1'));Object.keys(m).forEach(k=>{m[k].q.columns=['mv_test','mv_creation','m_users','m_conv_users'];});localStorage.setItem('fwoPianoReq_v1',JSON.stringify(m));});await p.goto('https://gst.test/#compte');await p.reload();await p.waitForSelector('.dash-h');await p.waitForTimeout(400); }
  // --- v56.18 : serveur de comptes muet → délai de 20 s, l'interface se libère seule
  { due(T,D(-31),[D(-25),D(-18),D(-11)]);mult=30;hang=true;await p.goto('https://gst.test/#compte');await p.reload();await p.waitForSelector('.dash-h');await p.waitForTimeout(500);await p.fill('#gst-app #gst-pak',AK);await p.fill('#gst-app #gst-psk',SK);await p.click('[data-act=dashkey]');await p.waitForTimeout(3000);
    const locked=/Mise à jour depuis Piano/.test(await txt('.apibar'));await p.waitForTimeout(19500);hang=false;const b4=JSON.stringify(T.state);await p.click('#gst-app [data-act=dashwho][data-v=compte]');await p.waitForTimeout(300);
    ok(`[${tag}] serveur de comptes sans réponse : après 20 s la mise à jour s'arrête seule avec un message, l'interface répond, rien n'est enregistré`,locked&&(await cnt('[data-act=accdelete]'))===1&&T.state.weeks.length===3,{locked,w:T.state.weeks.length});
    await p.click('#gst-app [data-act=dashwho][data-v=mes]');await p.waitForTimeout(300);ok(`[${tag}] … et le message parle d'une panne à retenter`,/ne répond pas|Mise à jour incomplète/.test(await txt('.err')),await txt('.err')); }
  // --- v56.18 : un test modifié ailleurs n'est pas écrasé
  { await p.goto('https://gst.test/#compte');await p.reload();await p.waitForSelector('.dash-h');await p.waitForTimeout(400);await p.click('#gst-app .dr:not(.dh)');await p.waitForTimeout(900);
    const extra=JSON.parse(JSON.stringify(T.state.weeks[T.state.weeks.length-1]));extra.A.n+=5000;extra.B.n+=5000;extra.end=D(-4);extra.wk=4;T.state.weeks.push(extra);const n1=T.state.weeks.length;
    await p.fill('#gst-app input[data-f=name]','Nom changé sur ce poste');await p.locator('#gst-app input[data-f=name]').blur();await p.waitForTimeout(200);await p.click('#gst-app [data-act=save]');await p.waitForTimeout(900);
    ok(`[${tag}] test modifié ailleurs entre l'ouverture et l'enregistrement : enregistrement refusé avec explication, la version du serveur est intacte`,/modifié ailleurs depuis son ouverture/.test(await txt('.err'))&&T.state.weeks.length===n1&&T.name!=='Nom changé sur ce poste',{err:await txt('.err'),n:T.state.weeks.length,name:T.name});
    T.state.weeks.pop();await p.click('#gst-app [data-act=save]');await p.waitForTimeout(900);ok(`[${tag}] sans modification concurrente : enregistrement accepté`,T.name==='Nom changé sur ce poste',{name:T.name,err:await txt('.err')});await p.click('#gst-app [data-act=dash]');await p.waitForSelector('.dash-h');await p.waitForTimeout(600); }
  // --- v56.18 : relecture des correctifs
  { // C1 : clé refusée puis bonne clé aussitôt
    due(T,D(-31),[D(-25),D(-18),D(-11)]);mult=30;mode='401';await p.goto('https://gst.test/#compte');await p.reload();await p.waitForSelector('.dash-h');await p.waitForTimeout(500);await p.fill('#gst-app #gst-pak',AK);await p.fill('#gst-app #gst-psk','MAUVAISSECRET000');await p.click('[data-act=dashkey]');await p.waitForTimeout(1200);
    mode='ok';calls.length=0;const again=(await cnt('.apibar #gst-pak'))===1;if(again){await p.fill('#gst-app #gst-pak',AK);await p.fill('#gst-app #gst-psk',SK);await p.click('[data-act=dashkey]');await p.waitForTimeout(2000);}
    ok(`[${tag}] clé refusée puis bonne clé saisie aussitôt : la mise à jour repart sans attendre, le test passe à 4 lectures`,again&&calls.length===1&&T.state.weeks.length===4,{again,calls:calls.length,w:T.state.weeks.length});
    // C2 : test ouvert alors qu'une semaine est disponible : collectée ET enregistrée
    T.state.plan.k=8;due(T,D(-38),[D(-32),D(-25),D(-18),D(-11)]);mult=60;calls.length=0;await p.click('#gst-app .dr:not(.dh)');await p.waitForTimeout(2500);
    ok(`[${tag}] test ouvert avec une semaine disponible : récupérée seule et enregistrée sur le serveur (5 lectures), message complet`,T.state.weeks.length===5&&calls.length===1&&/récupérée automatiquement depuis Piano.*Enregistrée dans votre espace/.test(await txt('.ok')),{w:T.state.weeks.length,calls:calls.length,ok:await txt('.ok'),err:await txt('.err')});
    // B1 : enregistrement lent du test A, ouverture du test B entre-temps : A n'est pas écrasé par B, B garde son identité
    mk.db.tests.push({id:900,name:'Autre test',state:JSON.parse(JSON.stringify(T.state)),sum:JSON.parse(JSON.stringify(T.sum)),owner:'mat@fwo.test',shared:[],updated:'2026-11-17'});const B=mk.db.tests.find(x=>x.id===900);B.state.weeks=B.state.weeks.slice(0,2);
    await p.fill('#gst-app input[data-f=name]','Test A renommé');await p.locator('#gst-app input[data-f=name]').blur();await p.waitForTimeout(200);putDelay=2500;await p.click('#gst-app [data-act=save]');await p.waitForTimeout(600);
    await p.evaluate(()=>{location.hash='#test=900';});await p.waitForTimeout(3500);putDelay=0;
    const cur=await p.evaluate(()=>{const s=window.GST.getState();return {name:s.name,sid:s.sid,n:s.weeks.length};});
    ok(`[${tag}] enregistrement lent de A puis ouverture de B : l'état affiché reste B (identifiant 900, 2 lectures), il ne prend pas l'identifiant de A`,cur.sid===900&&cur.n===2&&cur.name==='Autre test',cur);
    await p.fill('#gst-app input[data-f=name]','Autre test bis');await p.locator('#gst-app input[data-f=name]').blur();await p.waitForTimeout(200);await p.click('#gst-app [data-act=save]');await p.waitForTimeout(1200);
    ok(`[${tag}] … et enregistrer B écrit dans B seulement : A garde ses 5 lectures`,B.name==='Autre test bis'&&B.state.weeks.length===2&&T.state.weeks.length===5&&T.name!=='Autre test bis',{A:[T.name,T.state.weeks.length],B:[B.name,B.state.weeks.length]});
    // B2 : plan modifié ailleurs sans changer le nombre de lectures
    B.state.plan.k=7;await p.fill('#gst-app input[data-f=name]','Autre test ter');await p.locator('#gst-app input[data-f=name]').blur();await p.waitForTimeout(200);await p.click('#gst-app [data-act=save]');await p.waitForTimeout(1000);
    ok(`[${tag}] durée du plan modifiée ailleurs (même nombre de lectures) : enregistrement refusé, le serveur garde 7 semaines`,/modifié ailleurs/.test(await txt('.err'))&&B.state.plan.k===7&&B.name==='Autre test bis',{err:await txt('.err'),k:B.state.plan.k});
    mk.db.tests=mk.db.tests.filter(x=>x.id!==900);
    // C3 : fichier déposé sans la colonne du test
    await p.evaluate(()=>{location.hash='#compte';});await p.waitForSelector('.dash-h');await p.waitForTimeout(500);await p.click('#gst-app .dr:not(.dh)');await p.waitForTimeout(1500);
    await p.evaluate(a=>window.GST.openCSV('MVT - Variante;Utilisateurs;Utilisateurs convertis\n"8800001Variation 1";'+a[0]+';'+a[1]+'\n"0Original";'+a[2]+';'+a[3]+'\n','export.csv'),[4600*90,935*90,4610*90,923*90]);await p.waitForSelector('.dv');
    const hasCk=(await cnt('[data-d=sameOk]'))===1,errTxt=await txt('.dv .err');await p.check('#gst-app [data-d=sameOk]');await p.waitForTimeout(300);
    ok(`[${tag}] fichier déposé sans la colonne du test : refus expliqué, puis case « ce fichier ne contient que le test … » qui lève le refus (témoin et variante toujours contrôlés)`,hasCk&&/absente ici/.test(errTxt)&&!/absente ici/.test(await txt('.dv .err')),{hasCk,errTxt:errTxt.slice(0,80),after:(await txt('.dv .err')).slice(0,80)});
    await p.click('[data-act=cancel]');await p.click('#gst-app [data-act=dash]');await p.waitForSelector('.dash-h');await p.waitForTimeout(600); }
  // --- ouvrir le test depuis le compte : Piano est reconnu sur ce poste
  await p.click('#gst-app .dr:not(.dh)');await p.waitForTimeout(900);ok(`[${tag}] test ouvert depuis le tableau de bord : bandeau Piano présent (requête retrouvée sur le poste)`,(await cnt('.apibar'))===1&&/Piano/.test(await txt('.apibar')),await txt('.apibar'));
  // --- BigQuery
  await p.click('#gst-app [data-act=dash]');await p.waitForSelector('.dash-h');await p.click('[data-act=accnew]');await p.waitForSelector('.imp');await pk(p);await p.click('#gst-app [data-act=howto][data-v=bigquery]');await p.waitForTimeout(300);
  const sql=await p.evaluate(()=>document.querySelector('#gst-app pre.sql').textContent);
  ok(`[${tag}] onglet BigQuery : 5 étapes, requête modèle (dates, exposition, objectifs, une ligne par variation), bouton de copie, zone de dépôt, sans débordement`,(await cnt('.tuto .stp'))===6&&/DECLARE debut DATE/.test(sql)&&/events_\*/.test(sql)&&/COUNT\(DISTINCT variation\) = 1/.test(sql)&&/GROUP BY variation/.test(sql)&&(await cnt('[data-act=sqlcopy]'))===1&&(await cnt('.imp-d .drop'))===1&&await ov()<=0,await ov());
  await p.evaluate(a=>window.GST.openCSV('debut_test,fin_donnees,variation,visiteurs,visiteurs_avec_achat,visiteurs_avec_ajout_panier\n'+a[0]+','+a[1]+',A,20124,1041,5102\n'+a[0]+','+a[1]+',B,20139,1082,5230\n','bquxjob_1a2b3c.csv'),[D(-14),D(-1)]);await p.waitForSelector('.dv');
  ok(`[${tag}] résultat de la requête déposé : dates lues dans le fichier (pas de case à cocher), semaine 2, deux métriques, visiteurs reconnus`,(await p.inputValue('#gst-app [data-d=startDate]'))===D(-14)&&(await p.inputValue('#gst-app [data-d=endDate]'))===D(-1)&&(await cnt('[data-d=endOk]'))===0&&/semaine 2 sur/.test(await txt('.dv-gate'))&&/20.124 visiteurs pour A, 20.139 pour B/.test(await txt('.dv-read'))&&(await p.locator('#gst-app [data-dm=include]:checked').count())===2,[await txt('.dv-gate'),await txt('.dv-read')]);
  await p.click('[data-act=cancel]');
  // --- accueil : l'API Piano est annoncée
  await p.goto('https://gst.test/');await p.waitForSelector('.hero2');
  ok(`[${tag}] accueil : texte « par l'API », repère « API » sur Piano, encart « connexion directe à Piano » avec son bouton, sans débordement`,/par l.API/.test(await txt('#gst-import .secl'))&&(await cnt('[data-act=howto][data-v=piano] .tbadge'))===1&&/connexion directe/.test(await txt('.tc[data-v=piano] small'))&&await ov()<=0,await ov());
  ok(`[${tag}] aucune erreur JS`,errs.length===0,errs);await ctx.close();}
 console.log(pass+'/'+(pass+fail)+(fail?' ÉCHEC':' OK'));await b.close();})();

// Banc du module comptes : l'extension WordPress est simulée en mémoire (mêmes routes, mêmes règles d'accès).
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
const FILE=path.join(__dirname,'..','calculateur-sequentiel-v56-12.html'),SHOTS=process.argv[2];const HTML='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>button{white-space:nowrap}body{margin:0;padding:0 8px}</style></head><body>'+fs.readFileSync(FILE,'utf8')+'</body></html>';
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
(async()=>{const b=await chromium.launch();
 for(const [W,tag] of [[360,'360'],[1280,'1280']]){
  // 1. extension absente : aucun changement
  { const mk=mock(false),ctx=await b.newContext({viewport:{width:W,height:900}}),p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));await ctx.route('https://gst.test/**',mk.handler);await p.goto('https://gst.test/');await p.waitForSelector('.imp');await p.waitForTimeout(400);
    ok(`[${tag}] sans extension : pas de barre de compte, accueil intact, aucune erreur`,(await p.locator('.accbar').count())===0&&(await p.locator('.hero2').count())===1&&errs.length===0,errs);await ctx.close(); }
  const mk=mock(true),ctx=await b.newContext({viewport:{width:W,height:900}}),p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));p.on('dialog',d=>d.accept());await ctx.route('https://gst.test/**',mk.handler);
  const ov=()=>p.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth),shot=async n=>{if(SHOTS)await p.screenshot({path:path.join(SHOTS,tag+'-'+n+'.png'),fullPage:true});};
  const login=async email=>{await p.goto('https://gst.test/');await p.waitForSelector('.accbar');await p.click('[data-act=acclogin]');await p.fill('[data-f=accemail]',email);await p.click('[data-act=accsend]');await p.waitForSelector('text=Consultez votre messagerie');const tk=mk.db.mails.filter(m=>m.tk).pop().tk;await p.goto('https://gst.test/wp-json/fwo-gst/v1/login?token='+tk);await p.click('button[type=submit]');await p.waitForSelector('.dash-h, .robar',{timeout:8000});};
  await p.goto('https://gst.test/');await p.waitForSelector('.accbar');
  ok(`[${tag}] extension présente, déconnecté : lien « Se connecter », accueil intact`,(await p.locator('[data-act=acclogin]').count())===1&&(await p.locator('.hero2').count())===1&&await ov()<=0,await ov());
  await p.click('[data-act=acclogin]');await p.waitForSelector('.login');await shot('c1-connexion');
  ok(`[${tag}] écran de connexion : un champ email, aucun champ mot de passe, sans débordement`,(await p.locator('.login input').count())===1&&(await p.locator('input[type=password]').count())===0&&await ov()<=0,await ov());
  await p.fill('[data-f=accemail]','pas-un-email');await p.click('[data-act=accsend]');await p.waitForTimeout(150);
  ok(`[${tag}] adresse invalide refusée, aucun email envoyé`,/Adresse email invalide/.test(await p.textContent('.err'))&&mk.db.mails.length===0,mk.db.mails);
  await login('Mat@fwo.test');
  ok(`[${tag}] lien reçu puis cliqué : tableau de bord vide, adresse affichée`,/Aucun test enregistré/.test(await p.textContent('#gst-app'))&&/mat@fwo\.test/.test(await p.textContent('.accbar'))&&await ov()<=0,await ov());
  const tkOld=mk.db.mails[0].tk;await p.goto('https://gst.test/wp-json/fwo-gst/v1/login?token='+tkOld);await p.waitForSelector('.login');
  ok(`[${tag}] lien déjà utilisé : refusé avec un message`,/a expiré ou a déjà servi/.test(await p.textContent('.err')),null);
  await p.goto('https://gst.test/#compte');await p.waitForSelector('.dash-h');await p.click('[data-act=accnew]');await p.waitForSelector('.imp');
  await p.click('[data-act=example]');await p.waitForTimeout(300);await p.waitForTimeout(2500);await p.click('[data-act=save]');await p.waitForSelector('text=enregistré dans votre espace');
  ok(`[${tag}] enregistrement dans l'espace : test créé côté serveur avec son résumé`,mk.db.tests.length===1&&mk.db.tests[0].owner==='mat@fwo.test'&&mk.db.tests[0].sum&&/discussion requise/.test(mk.db.tests[0].sum.t)&&mk.db.tests[0].state.weeks.length===6,mk.db.tests[0]&&mk.db.tests[0].sum);
  await p.click('[data-act=save]');await p.waitForTimeout(400);ok(`[${tag}] second enregistrement : mise à jour, pas de doublon`,mk.db.tests.length===1,mk.db.tests.length);
  await p.click('[data-act=share]');await p.waitForSelector('.inv');await p.fill('[data-f=invite]','pm@client.test');await p.click('[data-act=invite]');await p.waitForSelector('.invl li');await shot('c3-invitation');
  ok(`[${tag}] invitation : invité listé, email d'invitation envoyé, sans débordement`,mk.db.tests[0].shared.join()==='pm@client.test'&&mk.db.mails.some(m=>m.invite===mk.db.tests[0].id)&&await ov()<=0,await ov());
  await p.click('.accbar [data-act=dash]');await p.waitForSelector('.dash .dr[data-act=dashopen]');await shot('c2-tableau-de-bord');
  const rowTxt=(await p.textContent('.dash .dr[data-act=dashopen]')).replace(/\s+/g,' ');
  ok(`[${tag}] tableau de bord : nom, objectif, avancement « 5/8 sem. », écart, décision, partage, corbeille, sans débordement`,/Exemple : 7 métriques/.test(rowTxt)&&/Visiteurs avec achat/.test(rowTxt)&&/5\/8 sem\./.test(rowTxt)&&(await p.locator(".dr button.ic[data-act=dashdel]").count())>=1&&/\+7,99 %/.test(rowTxt)&&/discussion requise/.test(rowTxt)&&/partagé avec 1/.test(rowTxt)&&await ov()<=0,[rowTxt,await ov()]);
  await p.click('.dash .dr[data-act=dashopen] .d-n');await p.waitForSelector('.verdict');
  ok(`[${tag}] réouverture depuis le tableau de bord : même décision, test modifiable`,/discussion requise/.test(await p.textContent('.v-main h3'))&&(await p.locator('.robar').count())===0&&(await p.locator('.tabs').count())===1,null);
  await p.click('[data-act=acclogout]');await p.waitForSelector('text=Vous êtes déconnecté');
  // l'invité
  mk.db.mails.length=0;await p.goto('https://gst.test/#test='+mk.db.tests[0].id);await p.waitForSelector('.login');
  ok(`[${tag}] lien d'invitation sans session : demande de connexion`,/adresse email qui a reçu l'invitation/.test(await p.textContent('#gst-app')),null);
  await p.fill('[data-f=accemail]','pm@client.test');await p.click('[data-act=accsend]');await p.waitForSelector('text=Consultez votre messagerie');const tki=mk.db.mails.pop().tk;await p.goto('https://gst.test/wp-json/fwo-gst/v1/login?token='+tki);ok(`[${tag}] ouvrir le lien ne connecte pas : une confirmation nomme l'adresse`,/pm@client\.test/.test(await p.textContent('main'))&&!!mk.db.tokens[tki],null);await p.click('button[type=submit]');await p.waitForSelector('.robar');await p.waitForTimeout(2500);await shot('c4-invite-lecture-seule');
  ok(`[${tag}] invité : test ouvert en lecture seule, même décision, aucun champ modifiable, sans débordement`,/partagé par mat@fwo\.test/.test(await p.textContent('.robar'))&&/discussion requise/.test(await p.textContent('.v-main h3'))&&(await p.locator('.tabs').count())===0&&(await p.locator('#gst-app input:not([type=hidden]):not([readonly])').count())===0&&(await p.locator('[data-act=save]').count())===0&&await ov()<=0,[await p.textContent('.robar'),await ov()]);
  const hack=await p.evaluate(async id=>{const r=await fetch('/wp-json/fwo-gst/v1/tests/'+id,{method:'DELETE',headers:{'X-WP-Nonce':'abcdef1234'}});return r.status;},mk.db.tests[0].id);
  ok(`[${tag}] invité : suppression refusée par le serveur simulé`,hack===404&&mk.db.tests.length===1,hack);
  await p.click('.robar [data-act=dash]');await p.waitForSelector('.dash-h');await p.click('[data-act=dashwho][data-v=partages]');await p.waitForSelector('.dash .dr[data-act=dashopen]');
  ok(`[${tag}] invité : le test apparaît dans « Partagés avec moi », pas dans « Mes tests », sans bouton Supprimer`,/Partagés avec moi \(1\)/.test(await p.textContent('.tabs'))&&/Mes tests \(0\)/.test(await p.textContent('.tabs'))&&(await p.locator('[data-act=dashdel]').count())===0&&await ov()<=0,await ov());
  await p.click('[data-act=acclogout]');await p.waitForSelector('text=Vous êtes déconnecté');
  // un tiers ne voit rien
  await login('autre@ailleurs.test');const st=await p.evaluate(async id=>{const r=await fetch('/wp-json/fwo-gst/v1/tests/'+id,{headers:{'X-WP-Nonce':'abcdef1234'}});return r.status;},mk.db.tests[0].id);
  ok(`[${tag}] un autre compte : tableau de bord vide et accès au test refusé`,/Aucun test enregistré/.test(await p.textContent('#gst-app'))&&st===404,st);
  await p.click('[data-act=acclogout]');await p.waitForSelector('text=Vous êtes déconnecté');
  // le propriétaire supprime
  await login('mat@fwo.test');await p.waitForSelector('.dash .dr[data-act=dashopen]');await p.click('[data-act=dashdel]');await p.waitForSelector('text=Aucun test enregistré');
  ok(`[${tag}] propriétaire : suppression du test`,mk.db.tests.length===0,mk.db.tests.length);
  await p.click('[data-act=dashwho][data-v=compte]');await p.waitForSelector('[data-act=accdelete]');ok(`[${tag}] onglet « Mon compte » sans débordement`,await ov()<=0,await ov());
  // un autre compte a enregistré un test hostile et l'a partagé avec moi
  { const X='<img src=x onerror="window.__pwn=(window.__pwn||0)+1">',hid='m1" onfocus="window.__pwn=9" autofocus x="',arm=c=>({n:20000,m:{[hid]:{c}}});
    mk.db.tests.push({id:999,name:'Piège '+X,owner:'mechant@x.test',shared:['mat@fwo.test'],sum:{t:'Gagné '+X,c:'win'+X,n:2,k:'8'+X,dw:1,lift:0.1,m:X,u:'jour'+X},state:{plan:{k:'8'+X,alpha:0.05,power:0.8,testType:3,sfu:X,sfl:X,startDate:X,unit:X},metrics:[{id:hid,src:X,name:'Achat '+X,type:'binaire',role:'principale',sens:'hausse',marge:1}],labels:{A:X,B:X},weeks:[{A:arm(1000),B:arm(1100)},{A:arm(2000),B:arm(2300)}]}});
    await p.click('[data-act=dashwho][data-v=partages]');await p.click('[data-act=dashwho][data-v=mes]');await p.click('.accbar [data-act=dash]');await p.waitForTimeout(600);await p.click('[data-act=dashwho][data-v=partages]');await p.waitForSelector('.dash .dr[data-act=dashopen]');
    const r1=await p.evaluate(()=>({pwn:window.__pwn||0,img:document.querySelectorAll('#gst-app img').length,on:[...document.querySelectorAll('#gst-app *')].filter(e=>[...e.attributes].some(a=>/^on/i.test(a.name))).length}));
    await p.click('.dash .dr[data-act=dashopen] .d-n');await p.waitForSelector('.robar');await p.waitForTimeout(2500);
    const r2=await p.evaluate(()=>({pwn:window.__pwn||0,img:document.querySelectorAll('#gst-app img').length,on:[...document.querySelectorAll('#gst-app *')].filter(e=>[...e.attributes].some(a=>/^on/i.test(a.name))).length}));
    ok(`[${tag}] test hostile partagé par un autre compte : aucun script ni balise injectée (liste puis ouverture)`,r1.pwn+r1.img+r1.on+r2.pwn+r2.img+r2.on===0,[r1,r2]); }
  ok(`[${tag}] aucune erreur JS`,errs.length===0,errs);await ctx.close(); }
 console.log(`\n${pass}/${pass+fail} OK`);await b.close();process.exit(fail?1:0);})();

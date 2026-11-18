// v56.10 : barre de compte, écran « Nouveau test », onglet BigQuery, mise à jour des tests depuis Piano à l'ouverture du tableau de bord (extension et API Piano simulées)
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
const FILE=path.join('/tmp/claude-0/-home-claude/f6658268-8fe7-580d-9107-6939e43c6edb/scratchpad/repo','calculateur-sequentiel-v56-10.html'),SHOTS=process.argv[2];const HTML='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>button{white-space:nowrap}body{margin:0;padding:0 8px}</style></head><body>'+fs.readFileSync(FILE,'utf8')+'</body></html>';
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
const sleep=ms=>new Promise(z=>setTimeout(z,ms));const out=(k,v)=>console.log(k+' :: '+JSON.stringify(v));
(async()=>{const b=await chromium.launch();const mk=mock(true),ctx=await b.newContext({viewport:{width:390,height:900}}),p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e).slice(0,200)));p.on('dialog',d=>d.accept());
 const log=[],cfg={hang:null,fail:null,delay:0},ext=[];ctx.on('request',r=>{const h=new URL(r.url()).host;if(h!=='gst.test'&&h!=='api.atinternet.io'&&!/fonts\.|fwoptimisation/.test(h))ext.push(r.url().slice(0,120));});
 await ctx.route('https://gst.test/**',async route=>{const r=route.request(),u=new URL(r.url()),m=r.method(),q=u.pathname.replace('/wp-json/fwo-gst/v1/','');
  if(u.pathname.startsWith('/wp-json/fwo-gst/v1/tests')){log.push({m,q,body:r.postData()||''});if(cfg.hang&&m==='GET'&&q===cfg.hang)return;if(cfg.fail&&m==='GET'&&q===cfg.fail)return route.fulfill({status:500,contentType:'application/json',body:'{"message":"panne"}'});if(cfg.delay&&m===(cfg.dm||m))await sleep(cfg.delay);}
  return mk.handler(route);});
 const calls=[],mults={},pmode={};let pd=0;
 await ctx.route('https://api.atinternet.io/**',async r=>{const h={'access-control-allow-origin':'*','access-control-allow-headers':'x-api-key','access-control-allow-methods':'GET,OPTIONS'};if(r.request().method()==='OPTIONS')return r.fulfill({status:204,headers:h});
  const U=new URL(r.request().url()),prm=JSON.parse(U.searchParams.get('param')),site=(prm.space&&prm.space.s||[])[0];calls.push({site,prm,path:U.origin+U.pathname});if(pd)await sleep(pd);
  if(pmode[site]==='abort')return r.abort();if(pmode[site]==='empty')return r.fulfill({status:200,headers:h,contentType:'application/json',body:'{"DataFeed":{"Columns":[],"Rows":[]}}'});
  return r.fulfill({status:200,headers:h,contentType:'application/json',body:JSON.stringify(feed(mults[site]||1))});});
 await ctx.route(/fonts\.(googleapis|gstatic)\.com|fwoptimisation\.com/,r=>r.abort());
  const ov=()=>p.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth),cnt=s=>p.locator('#gst-app '+s).count(),txt=s=>p.evaluate(s=>{const e=document.querySelector('#gst-app '+s);return e&&!e.hidden?e.innerText:'';},s);
  const login=async email=>{await p.goto('https://gst.test/');await p.waitForSelector('.accbar');await p.click('[data-act=acclogin]');await p.fill('[data-f=accemail]',email);await p.click('[data-act=accsend]');await p.waitForSelector('text=Consultez votre messagerie');const tk=mk.db.mails.filter(m=>m.tk).pop().tk;await p.goto('https://gst.test/wp-json/fwo-gst/v1/login?token='+tk);await p.click('button[type=submit]');await p.waitForSelector('.dash-h');};
  const dash=async()=>{await p.click('#gst-app [data-act=dash]');await p.waitForSelector('.dash-h');await p.waitForTimeout(300);};
  const due=(t,start,ends)=>{t.state.plan.startDate=start;t.state.weeks.forEach((w,i)=>{w.end=ends[i];w.wk=i+1;});};
 const lastW=body=>{try{const j=JSON.parse(body),w=j.state.weeks;return {name:j.name,n:w.length,A:w[w.length-1].A.n,B:w[w.length-1].B.n};}catch(e){return 'x';}};
 const puts=()=>log.filter(l=>l.m==='PUT').map(l=>Object.assign({q:l.q},lastW(l.body)));
 const redue=t=>{const n=t.state.weeks.length;due(t,D(-(n*7+10)),Array.from({length:n},(_,i)=>D(-(n-i)*7-4)));};
 const bar=()=>txt('.apibar');const rekey=async()=>{await p.goto('https://gst.test/#compte');await p.reload();await p.waitForSelector('.dash-h');await p.waitForTimeout(500);await p.fill('#gst-app #gst-pak',AK);await p.fill('#gst-app #gst-psk',SK);await p.click('[data-act=dashkey]');};
 await login('mat@fwo.test');await p.click('[data-act=accnew]');await p.waitForSelector('.imp');
 await p.click('#gst-app [data-act=apiopen]');await p.waitForSelector('#gst-purl');await p.fill('#gst-purl',URLQ);await p.fill('#gst-pstart',D(-10));await p.fill('#gst-pak',AK);await p.fill('#gst-psk',SK);await p.click('[data-act=apigo]');await p.waitForSelector('.dv');
 await p.click('[data-act=apply]');await p.waitForTimeout(800);await p.click('[data-act=save]');await p.waitForTimeout(700);
 const T=mk.db.tests[0];const req0=JSON.parse(await p.evaluate(()=>localStorage.getItem('fwoPianoReq_v1')));out('setup',{id:T.id,w:T.state.weeks.length,sum:T.sum,reqKeys:Object.keys(req0)});
 const q1=req0[T.id].q,qs=s=>({q:Object.assign({},q1,{space:{s:[s]}})});
 const T2={id:500,name:'Deux',state:JSON.parse(JSON.stringify(T.state)),sum:JSON.parse(JSON.stringify(T.sum)),owner:'mat@fwo.test',shared:[]};const T3={id:600,name:'Partage',state:JSON.parse(JSON.stringify(T.state)),sum:JSON.parse(JSON.stringify(T.sum)),owner:'autre@x.test',shared:['mat@fwo.test']};mk.db.tests.push(T2,T3);
 req0[500]=qs(999002);req0[600]=qs(999003);await p.evaluate(s=>localStorage.setItem('fwoPianoReq_v1',s),JSON.stringify(req0));
 // P1 : deux tests, réponses lentes, état utilisateur non enregistré
 const nm=await p.$('#gst-app [data-f=name]');if(nm){await nm.fill('LOCAL-NON-ENREGISTRE');await nm.dispatchEvent('change');}
 [T,T2,T3].forEach(redue);mults[999001]=5;mults[999002]=7;mults[999003]=9;pd=500;cfg.delay=200;log.length=0;calls.length=0;
 await p.click('#gst-app [data-act=dash]');await p.waitForTimeout(700);const mid=await bar();await p.click('#gst-app .dr:not(.dh)',{timeout:1000}).catch(()=>{});await p.waitForTimeout(5000);
 out('P1',{nameField:!!nm,mid:mid.slice(0,70),calls:calls.map(c=>c.site),puts:puts(),lists:log.filter(l=>l.q==='tests').length,gets:log.filter(l=>l.m==='GET'&&l.q!=='tests').map(l=>l.q),bar:(await bar()).slice(0,60),notice:(await txt('.notice,.ok,[role=status]')).slice(0,120),acts:await p.evaluate(()=>[...new Set([...document.querySelectorAll('#gst-app [data-act]')].map(e=>e.getAttribute('data-act')))].join(','))});
 const allPut=log.filter(l=>l.m==='PUT').map(l=>l.body).join('');out('P1.fuite',{site:/99900[123]/.test(allPut),cols:/mv_creation|m_users|columns|"api"|"q"/.test(allPut),cle:allPut.includes(AK)||allPut.includes(SK),keys:[...new Set(log.filter(l=>l.m==='PUT').flatMap(l=>{const j=JSON.parse(l.body);return Object.keys(j).concat(Object.keys(j.state).map(k=>'state.'+k));}))]});
 out('P1.srv',{T1:[T.state.weeks.length,T.state.weeks.map(w=>w.A.n)],T2:[T2.name,T2.state.weeks.map(w=>w.A.n)],T3:T3.state.weeks.length,local:await p.evaluate(()=>Object.keys(localStorage).filter(k=>!/Piano/.test(k)).map(k=>k+'='+localStorage.getItem(k).slice(0,0)+(localStorage.getItem(k).match(/"name":"[^"]*"/)||[''])[0]+' w'+((localStorage.getItem(k).match(/"wk":/g)||[]).length)))});
 // P2 : changement d'adresse pendant la mise à jour (réponse Piano lente)
 [T,T2].forEach(redue);mults[999001]=10;mults[999002]=14;pd=1500;cfg.delay=0;await rekey();log.length=0;calls.length=0;await p.waitForTimeout(500);
 await p.evaluate(()=>{location.hash='#test=500';});await p.waitForTimeout(4500);
 out('P2',{calls:calls.map(c=>c.site),puts:puts(),title:(await p.evaluate(()=>{const e=document.querySelector('#gst-app [data-f=name]');return e?e.value:document.querySelector('#gst-app h2,#gst-app h1')?.innerText;})),bar:(await bar()).slice(0,60),srv:[T.state.weeks.length,T2.state.weeks.length]});
 // P2b : changement d'adresse pendant le PUT lent, puis retour au tableau
 pd=0;cfg.delay=1500;cfg.dm='PUT';await rekey();log.length=0;calls.length=0;await p.waitForTimeout(700);await p.evaluate(()=>{location.hash='#test=600';});await p.waitForTimeout(600);await p.evaluate(()=>{location.hash='#compte';});await p.waitForTimeout(5000);
 out('P2b',{calls:calls.map(c=>c.site),puts:puts(),bar:(await bar()).slice(0,60),srv:[T.state.weeks.map(w=>w.A.n),T2.state.weeks.map(w=>w.A.n)]});cfg.delay=0;cfg.dm=null;
 // P3 : erreurs (500 serveur sur T1, Piano coupé sur T2)
 [T,T2].forEach(redue);mults[999001]=40;mults[999002]=50;cfg.fail='tests/'+T.id;pmode[999002]='abort';await rekey();log.length=0;calls.length=0;await p.waitForTimeout(2500);
 out('P3',{calls:calls.map(c=>c.site),puts:puts(),bar:(await bar()).slice(0,60),msg:(await p.evaluate(()=>[...document.querySelectorAll('#gst-app .err,#gst-app .notice,#gst-app [role=alert],#gst-app [role=status]')].filter(e=>!e.hidden).map(e=>e.innerText.slice(0,140))))});
 cfg.fail=null;out('P3.txt',(await p.evaluate(()=>document.querySelector('#gst-app').innerText.replace(/\s+/g,' ').slice(0,330))));await p.click('#gst-app .dr:not(.dh)');await p.waitForTimeout(600);out('P3.deverrouille',{dash:await cnt('.dash-h')});
 // P3b : réponse Piano vide (contrôle en échec)
 cfg.fail=null;pmode[999002]='empty';pmode[999001]='empty';await rekey();log.length=0;calls.length=0;await p.waitForTimeout(2500);out('P3b',{calls:calls.map(c=>c.site),puts:puts(),bar:(await bar()).slice(0,60)});
 // P4 : serveur qui ne répond jamais
 pmode[999001]=pmode[999002]=null;cfg.hang='tests/'+T.id;await rekey();log.length=0;calls.length=0;await p.waitForTimeout(8000);const b4=await bar();await p.click('#gst-app .dr:not(.dh)',{timeout:1000}).catch(()=>{});await p.click('#gst-app [data-act=acclogout]',{timeout:1000}).catch(()=>{});await p.waitForTimeout(400);
 out('P4',{bar8s:b4.slice(0,60),toujoursDash:await cnt('.dash-h'),connecte:/mat@fwo/.test(await txt('.accbar'))});cfg.hang=null;
 // P5/P6 : stockage forgé + injection
 const big={};for(let i=0;i<10000;i++)big['k'+i]={q:{columns:['a','b','c'],space:{s:[1]}}};const evil='"><img src=x onerror="window.__x=1">';
 big[T.id]={q:{columns:[evil,'mv_creation','m_users','m_conv_users','https://evil.test/x'],space:{s:[999001]},url:'https://evil.test',filter:{x:evil},'max-results':999999,sort:[evil]}};big[500]={q:'https://evil.test'};big.abc={q:q1};big['600']=qs(999003);
 const forged=JSON.stringify(big).replace(/^\{/,'{"__proto__":{"q":'+JSON.stringify(q1)+',"polluted":1},');
 T2.name='" onfocus="window.__x=6" x="<img src=x onerror=window.__x=2>';T3.name='<img src=x onerror=window.__x=3>';T3.owner='"><svg onload=window.__x=5>@x.fr';T3.sum=Object.assign({},T3.sum,{t:'<img src=x onerror=window.__x=4>',m:'<svg onload=window.__x=7>',c:'continue" onmouseover="window.__x=8'});T2.sum=Object.assign({},T2.sum,{m:'<svg onload=window.__x=9>',t:'<b onclick=1>'});
 mk.db.tests.push({id:700,name:'Autre en cours',state:JSON.parse(JSON.stringify(T.state)),sum:JSON.parse(JSON.stringify(T.sum)),owner:'mat@fwo.test',shared:[]});
 [T,T2].forEach(redue);await p.evaluate(s=>localStorage.setItem('fwoPianoReq_v1',s),forged);ext.length=0;const t0=Date.now();await rekey();const t1=Date.now()-t0;log.length=0;calls.length=0;await p.waitForTimeout(3000);await p.click('#gst-app [data-act=dashwho]',{timeout:800}).catch(()=>{});await p.waitForTimeout(300);
 out('P5',{msRechargeEtCle:t1,calls:calls.map(c=>({site:c.site,path:c.path,k:Object.keys(c.prm),cols:c.prm.columns,mr:c.prm['max-results']})),puts:puts().map(x=>x.q),ext,bar:(await bar()).slice(0,60),store:await p.evaluate(()=>localStorage.getItem('fwoPianoReq_v1').length)});
 out('P6',await p.evaluate(()=>({x:window.__x===undefined?'aucun':window.__x,pol:({}).polluted===undefined,els:document.querySelectorAll('#gst-app img[src=x],#gst-app svg[onload],#gst-app [onfocus],#gst-app [onmouseover],#gst-app [onclick]').length,rows:document.querySelectorAll('#gst-app .dr').length,txt:[...document.querySelectorAll('#gst-app .dr')].map(e=>e.innerText.replace(/\s+/g,' ').slice(0,90)).slice(0,5)})));
 const whos=await p.evaluate(()=>[...document.querySelectorAll('#gst-app [data-act=dashwho]')].map(e=>e.getAttribute('data-v')));for(const w of whos){await p.click('#gst-app [data-act=dashwho][data-v="'+w+'"]');await p.waitForTimeout(250);out('P6.'+w,await p.evaluate(()=>({x:window.__x===undefined?'aucun':window.__x,els:document.querySelectorAll('#gst-app img[src=x],#gst-app svg[onload],#gst-app [onfocus],#gst-app [onmouseover],#gst-app [onclick],#gst-app b[onclick]').length,cls:[...document.querySelectorAll('#gst-app .dr [class*=continue]')].map(e=>e.className).slice(0,3),rows:[...document.querySelectorAll('#gst-app .dr:not(.dh)')].map(e=>e.innerText.replace(/\s+/g,' ').slice(0,150))})));}
 out('errs',errs);await b.close();})().catch(e=>{console.log('ECHEC',String(e).slice(0,600));process.exit(1);});

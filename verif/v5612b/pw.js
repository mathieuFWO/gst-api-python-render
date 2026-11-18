// v56.12 : barre de compte, écran « Nouveau test », onglet BigQuery, mise à jour des tests depuis Piano à l'ouverture du tableau de bord (extension et API Piano simulées)
const {chromium}=require(require.resolve('playwright',{paths:["/tmp/claude-0/-home-claude/f6658268-8fe7-580d-9107-6939e43c6edb/scratchpad/repo/tests",process.cwd()].concat(module.paths)}));const path=require('path');const fs=require('fs');
const FILE=path.join("/tmp/claude-0/-home-claude/f6658268-8fe7-580d-9107-6939e43c6edb/scratchpad/repo/tests",'..','calculateur-sequentiel-v56-12.html'),SHOTS=process.argv[2];const HTML='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>button{white-space:nowrap}body{margin:0;padding:0 8px}</style></head><body>'+fs.readFileSync(FILE,'utf8')+'</body></html>';
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
(async()=>{const b=await chromium.launch();const mk=mock(true),ctx=await b.newContext({viewport:{width:390,height:900}}),p=await ctx.newPage();p.setDefaultTimeout(8000);p.on('dialog',d=>d.accept());
 await p.addInitScript(()=>{const f=window.fetch;window.__st=[];window.fetch=function(u,o){if(/fwo-gst\/v1\/tests\/\d+/.test(String(u)))window.__st.push((o&&o.method||'GET')+' '+String(u).slice(-3)+' <- '+(new Error().stack||'').split('\n').slice(2,5).map(s=>s.trim().replace(/https:\/\/gst\.test\//,'').replace(/^at /,'')).join(' < '));return f.apply(this,arguments);};});
 const reqs=[];let putMode='',mult=1;
 await ctx.route('https://gst.test/**',async r=>{const q=r.request(),u=new URL(q.url()),m=q.method();if(u.pathname.startsWith('/wp-json/fwo-gst/v1/tests'))reqs.push(m+' '+u.pathname.slice(20));if(m==='PUT'&&putMode==='slow')await new Promise(z=>setTimeout(z,3000));return mk.handler(r);});
 await ctx.route('https://api.atinternet.io/**',async r=>{const h={'access-control-allow-origin':'*','access-control-allow-headers':'x-api-key','access-control-allow-methods':'GET,OPTIONS'};if(r.request().method()==='OPTIONS')return r.fulfill({status:204,headers:h});return r.fulfill({status:200,headers:h,contentType:'application/json',body:JSON.stringify(feed(mult))});});
 await ctx.route(/fonts\.(googleapis|gstatic)\.com|fwoptimisation\.com/,r=>r.abort());
 const cnt=s=>p.locator('#gst-app '+s).count(),msgs=()=>p.evaluate(()=>[...document.querySelectorAll('#gst-app .err,#gst-app .ok')].filter(e=>!e.hidden).map(e=>e.innerText.replace(/\s+/g,' ').slice(0,140)).join(' || '));
 const w=ms=>p.waitForTimeout(ms),log=(n,o)=>console.log('### '+n+' :: '+(typeof o==='string'?o:JSON.stringify(o)));
 const step=async(n,fn)=>{try{await fn();}catch(e){log(n+' ECHEC TECHNIQUE',String(e).slice(0,300));}};
 const st=async()=>{const s=await p.evaluate(()=>{const a=window.__st.slice();window.__st.length=0;return a;});return s;};
 const due=(t,start,ends)=>{t.state.plan.startDate=start;t.state.weeks.forEach((x,i)=>{x.end=ends[i];x.wk=i+1;});};
 const dash=async()=>{await p.click('#gst-app [data-act=dash]');await p.waitForSelector('.dash-h');await w(400);};
 const open=id=>p.evaluate(id=>{const e=[...document.querySelectorAll('#gst-app [data-v="'+id+'"]')].filter(x=>!/del|share|suppr|rm/i.test(x.getAttribute('data-act')||''))[0];if(!e)return 'introuvable';e.click();return e.getAttribute('data-act');},id);
 const imp=async(name)=>{await p.click('#gst-app [data-act=apiopen]');await p.waitForSelector('#gst-purl');await p.fill('#gst-purl',URLQ);await p.fill('#gst-pstart',D(-10));if(await cnt('#gst-pak')){await p.fill('#gst-app #gst-pak',AK);await p.fill('#gst-app #gst-psk',SK);}await p.click('[data-act=apigo]');await p.waitForSelector('.dv');if(name)await p.fill('#gst-app [data-d=name]',name);await p.click('[data-act=apply]');await w(900);await p.click('[data-act=save]');await w(800);};
 let A,B;
 await step('init',async()=>{await p.goto('https://gst.test/');await p.waitForSelector('.accbar');await p.click('[data-act=acclogin]');await p.fill('[data-f=accemail]','mat@fwo.test');await p.click('[data-act=accsend]');await p.waitForSelector('text=Consultez votre messagerie');const tk=mk.db.mails.filter(m=>m.tk).pop().tk;await p.goto('https://gst.test/wp-json/fwo-gst/v1/login?token='+tk);await p.click('button[type=submit]');await p.waitForSelector('.dash-h');
   await p.click('[data-act=accnew]');await p.waitForSelector('.imp');await imp();A=mk.db.tests[0];await dash();await p.click('[data-act=accnew]');await p.waitForSelector('.imp');await imp('Essai B');B=mk.db.tests[1];log('init',{A:A&&A.id+' '+A.name,B:B&&B.id+' '+B.name});await st();});
 await step('D2',async()=>{await dash();log('D2 ouverture A',await open(A.id));await w(1200);
   if(await cnt('[data-act=share]')){await p.click('[data-act=share]');await w(1500);const lk=await p.evaluate(()=>[...document.querySelectorAll('#gst-app input,#gst-app textarea')].map(e=>e.value).filter(v=>/^https?:.*#/.test(v))[0]||'');let dec='';try{dec=Buffer.from(lk.split('=').pop().replace(/-/g,'+').replace(/_/g,'/'),'base64').toString('latin1');}catch(e){}log('partage : lien',{long:lk.length,debut:lk.slice(0,60),srvNenClair:/srvN/.test(lk)||/srvN/.test(decodeURIComponent(lk)),srvNbase64:/srvN/.test(dec),sidBase64:/"sid"/.test(dec),lisible:/"plan"|weeks/.test(dec)});}
   await st();const r0=reqs.length;putMode='slow';await p.click('[data-act=save]');await w(300);await dash();log('D2 ouverture B pendant le PUT de A',await open(B.id));await w(4000);putMode='';
   const r1=reqs.length;await p.click('[data-act=save]');await w(900);
   log('D2 resultat',{pendant:reqs.slice(r0,r1).join(', '),save:reqs.slice(r1).join(', '),nomA:A.name,nomB:B.name,msg:await msgs(),piles:(await st()).slice(-2)});});
 await step('D1',async()=>{await dash();await p.click('[data-act=accnew]');await p.waitForSelector('.imp');due(A,D(-17),[D(-11)]);mult=5;await dash();await w(2500);log('D1 synchro tableau de bord',{wA:A.state.weeks.length,msg:await msgs()});await st();
   due(A,D(-24),[D(-18),D(-11)]);mult=9;const r0=reqs.length;log('D1 ouverture 1',await open(A.id));await w(2500);log('D1 apres ouverture 1',{reqs:reqs.slice(r0).join(', '),wA:A.state.weeks.length,msg:await msgs(),piles:await st()});
   const r1=reqs.length;await dash();await w(1500);log('D1 retour tableau de bord',{reqs:reqs.slice(r1).join(', '),wA:A.state.weeks.length,piles:await st()});
   const r2=reqs.length;log('D1 ouverture 2',await open(A.id));await w(2500);log('D1 apres ouverture 2',{reqs:reqs.slice(r2).join(', '),wA:A.state.weeks.length,msg:await msgs(),piles:await st()});});
 await b.close();})();

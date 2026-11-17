const {chromium}=require('playwright');const path=require('path');const nodeCrypto=require('crypto');
const FILE=process.argv[2];
const D=k=>{const d=new Date();d.setDate(d.getDate()+k);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
const AK='ACCESSKEYFACTICE01',SK='SECRETFACTICE0000000002',KEY=AK+'_'+SK;
const PARAM={columns:['mv_test','mv_creation','m_users','m_conv_users'],sort:['-m_users'],space:{s:[999001]},'max-results':50,'page-num':1,options:{}};
const enc=o=>encodeURIComponent(JSON.stringify(o));const Q='?param='+enc(PARAM);
const feed=(m,lab,vr)=>({DataFeed:{Columns:[{Name:'mv_test',Label:'MVT - Test'},{Name:'mv_creation',Label:'MVT - Variante'},{Name:'m_users',Label:'Utilisateurs'},{Name:'m_conv_users',Label:lab||'Utilisateurs convertis'}],Rows:[{mv_test:'9900001[FR] Essai',mv_creation:vr||'8800001Variation 1',m_users:Math.round(4600*m),m_conv_users:Math.round(935*m)},{mv_test:'9900001[FR] Essai',mv_creation:'0Original',m_users:Math.round(4550*m),m_conv_users:Math.round(900*m)}]}});
const R=(l,v)=>console.log(l+' => '+(typeof v==='string'?v:JSON.stringify(v)));
(async()=>{const b=await chromium.launch();const cx=await b.newContext({viewport:{width:1280,height:900}});const p=await cx.newPage();
const errs=[],logs=[];p.on('pageerror',e=>errs.push(String(e).slice(0,200)));p.on('console',m=>logs.push(m.text()));
let all=[],mode='ok',xlab=null,xvr=null;
await cx.route('**/*',async r=>{const rq=r.request(),u=rq.url();if(u.startsWith('file:'))return r.continue();
  const hk=rq.headers()['x-api-key']||'';const U=new URL(u);
  const rec={t:Date.now(),m:rq.method(),op:U.origin+U.pathname,key:!!hk,keyUrl:u.includes(AK)||u.includes(SK),cookie:!!rq.headers()['cookie'],ref:rq.headers()['referer']||''};
  if(U.origin!=='https://api.atinternet.io'){all.push(rec);return r.abort();}
  const h={'access-control-allow-origin':'*','access-control-allow-headers':'x-api-key','access-control-allow-methods':'GET,OPTIONS'};
  if(rq.method()==='OPTIONS')return r.fulfill({status:204,headers:h});
  try{rec.param=JSON.parse(U.searchParams.get('param'));}catch(e){rec.param='ILLISIBLE';}all.push(rec);
  const site=rec.param&&rec.param.space&&rec.param.space.s&&rec.param.space.s[0];
  if(mode==='err')return r.fulfill({status:500,headers:h,contentType:'application/json',body:JSON.stringify({ErrorMessage:'<img src=x onerror=window.__x=3> '+KEY.slice(0,0)})});
  if(mode==='race'){const dl=site===999001?1500:(site===999002?3200:50),mu=site===999001?3:(site===999002?5:2);await new Promise(z=>setTimeout(z,dl));return r.fulfill({status:200,headers:h,contentType:'application/json',body:JSON.stringify(feed(mu))}).catch(()=>{});}
  return r.fulfill({status:200,headers:h,contentType:'application/json',body:JSON.stringify(feed(1,xlab,xvr))});});
const fresh=async()=>{await p.goto('file://'+path.resolve(FILE));await p.evaluate(()=>{try{localStorage.clear()}catch(e){}});await p.reload();await p.waitForSelector('.cta button');};
const openForm=async()=>{await p.click('#gst-app [data-act=howto][data-v=piano]').catch(()=>{});await p.waitForTimeout(150);await p.click('#gst-app [data-act=apiopen]');await p.waitForSelector('#gst-app #gst-purl');};
const fill=async(o)=>{if(o.url!==undefined)await p.fill('#gst-app #gst-purl',o.url);if(o.start)await p.fill('#gst-app #gst-pstart',o.start);await p.fill('#gst-app #gst-pak',AK);await p.fill('#gst-app #gst-psk',SK);};
const errTxt=()=>p.evaluate(()=>{const e=document.querySelector('#gst-app .api-err');return e&&!e.hidden?e.innerText.slice(0,90):'';});
// ---- P1
const H='https://api.atinternet.io/v3/data/getData';
const urls={
 backslashAt:'https://api.atinternet.io\\@evil.example/v3/data/getData'+Q, at:'https://api.atinternet.io@evil.example/v3/data/getData'+Q, hashAt:'https://evil.example#@api.atinternet.io/v3/data/getData'+Q,
 casse:'HTTPS://API.ATINTERNET.IO/v3/data/getData'+Q, pointFinal:'https://api.atinternet.io./v3/data/getData'+Q, pointIdeo:'https://api.atinternet。io/v3/data/getData'+Q,
 cyrillique:'https://аpi.atinternet.io/v3/data/getData'+Q, tab:'ht\ttps://api.atinternet.io/v3/da\tta/getData'+Q, espace:'  https://api.atinternet.io/v3/data/getData'+Q+'  ',
 dblSlash:'https://api.atinternet.io//v3/data/getData'+Q, dotdot:'https://api.atinternet.io/v3/data/getData/../../../evil'+Q, pctPath:'https://api.atinternet.io/v3/data/%67etData'+Q,
 port443:'https://api.atinternet.io:443/v3/data/getData'+Q, sansSchema:'//api.atinternet.io/v3/data/getData'+Q, bsl:'https:\\\\api.atinternet.io\\v3\\data\\getData'+Q,
 urlDansParam:'https://evil.example/?u='+encodeURIComponent(H+Q), sousDomaine:'https://api.atinternet.io.evil.example/v3/data/getData'+Q, pctHost:'https://api.atinternet.io%2eevil.example/v3/data/getData'+Q,
 paramUrl:H+'?param='+enc(Object.assign({},PARAM,{url:'https://evil.example/',columns:PARAM.columns.concat(['https://evil.example/x','<img src=x>']),space:{s:[999001],url:'//evil.example'}})),
 jsonProto:'{"__proto__":{"polluted":1,"columns":["a","b","c"]},"constructor":{"prototype":{"polluted":1}},"columns":["mv_test","mv_creation","m_users","m_conv_users","__proto__","constructor"],"space":{"s":[999001],"__proto__":{"polluted":1}},"filter":{"__proto__":{"polluted":1},"metric":{"constructor":{"prototype":{"polluted":2}}}},"options":{"__proto__":true,"ok_opt":true,"Bad":true}}'
};
const p1=[];
for(const k of Object.keys(urls)){await fresh();await openForm();all=[];await fill({url:urls[k],start:D(-17)});await p.click('#gst-app [data-act=apigo]');await p.waitForTimeout(450);
  const keyed=all.filter(x=>x.key||x.keyUrl);p1.push(k+':'+(keyed.length?'ENVOI('+keyed.map(x=>x.op+(x.keyUrl?'[CLE DANS URL]':'')).join(',')+')':'refus')+(all.filter(x=>!x.op.startsWith('https://api.atinternet.io')&&!/fonts\.g|fwoptimisation\.com/.test(x.op)).length?' AUTRES!':''));
  if(k==='paramUrl'||k==='jsonProto'){const c=keyed[0];R('  param envoyé '+k,c&&c.param);R('  pollution ({}).polluted',await p.evaluate(()=>String(({}).polluted)+'/'+String(Object.prototype.columns)));}}
R('P1',p1);
const badKeyed=[];
// ---- ErrorMessage
await fresh();await openForm();mode='err';await fill({url:H+Q,start:D(-17)});await p.click('#gst-app [data-act=apigo]');await p.waitForTimeout(600);
R('P4 ErrorMessage',await p.evaluate(()=>{const e=document.querySelector('#gst-app .api-err');return {txt:e.innerText.slice(0,120),imgs:document.querySelectorAll('img[src=x]').length,x:window.__x||0};}));mode='ok';
// ---- P3 : deux scellements
const blobs=[];for(let i=0;i<2;i++){await fresh();await openForm();await fill({url:H+Q,start:D(-17)});await p.check('#gst-app [data-api=mem][value=code]');await p.fill('#gst-app #gst-pcode','un code assez long');await p.click('#gst-app [data-act=apigo]');await p.waitForSelector('#gst-app .dv',{timeout:30000});await p.waitForTimeout(300);
  blobs.push(await p.evaluate(()=>localStorage.getItem('fwoPianoCle_v1')));}
const B0=JSON.parse(blobs[0]),B1=JSON.parse(blobs[1]);R('P3 blob champs',Object.keys(B0).join(',')+' sel='+Buffer.from(B0.s,'base64').length+'o iv='+Buffer.from(B0.i,'base64').length+'o ; sel/iv/chiffré différents entre 2 scellements: '+[B0.s!==B1.s,B0.i!==B1.i,B0.c!==B1.c].join('/'));
try{const dk=nodeCrypto.pbkdf2Sync('un code assez long',Buffer.from(B0.s,'base64'),600000,32,'sha256');const c=Buffer.from(B0.c,'base64');const de=nodeCrypto.createDecipheriv('aes-256-gcm',dk,Buffer.from(B0.i,'base64'));de.setAuthTag(c.subarray(c.length-16));const pt=Buffer.concat([de.update(c.subarray(0,c.length-16)),de.final()]).toString();R('P3 déchiffrement indépendant (PBKDF2-SHA256 600000, AES-256-GCM)',pt===KEY?'OK = clé':'DIFFERENT');}catch(e){R('P3 déchiffrement indépendant','ECHEC '+e.message);}
try{const dk=nodeCrypto.pbkdf2Sync('un code assez long',Buffer.from(B0.s,'base64'),100000,32,'sha256');const c=Buffer.from(B0.c,'base64');const de=nodeCrypto.createDecipheriv('aes-256-gcm',dk,Buffer.from(B0.i,'base64'));de.setAuthTag(c.subarray(c.length-16));de.update(c.subarray(0,c.length-16));de.final();R('P3 100000 itérations','DECHIFFRE (anormal)');}catch(e){R('P3 100000 itérations','échec attendu');}
// ---- P2 : fuite après import + application
await p.click('#gst-app [data-act=apply]');await p.waitForTimeout(900);
const leak=async()=>p.evaluate(a=>{const out=[];const src={ls:JSON.stringify(Object.keys(localStorage).map(k=>[k,localStorage.getItem(k)])),dom:document.documentElement.outerHTML,url:location.href,state:JSON.stringify(window.GST.getState()),gst:JSON.stringify(window.GST,(k,v)=>typeof v==='function'?String(v).slice(0,0):v),ss:JSON.stringify(Object.keys(sessionStorage).map(k=>sessionStorage.getItem(k))),vals:[...document.querySelectorAll('input,textarea')].map(i=>i.value+'|'+i.getAttribute('value')).join(' '),globals:Object.keys(window).filter(k=>{try{return typeof window[k]==='string'&&a.some(x=>window[k].includes(x));}catch(e){return false;}}).join(',')};Object.keys(src).forEach(k=>{if(a.some(x=>src[k].includes(x)))out.push(k);});return out;},[AK,SK,'un code assez long']);
R('P2 fuites (après import mémorisé + application)',await leak());
R('P2 état',await p.evaluate(()=>{const s=window.GST.getState();return {name:s.name,weeks:s.weeks.length,wk:s.weeks.map(x=>x.wk),end:s.weeks.map(x=>x.end),api:Object.keys(s.api||{}),lsKeys:Object.keys(localStorage)};}));
// ---- P5/P6 : états forgés, course, PTRY (PKEY en mémoire, pas de rechargement)
const made=await p.evaluate(a=>{const k=Object.keys(localStorage).filter(k=>/gstSeq_v40_/.test(k))[0];const o=JSON.parse(localStorage.getItem(k));const mk=(n,site,extra)=>{const c=JSON.parse(JSON.stringify(o));c.name=n;delete c.sid;c.plan.startDate=a[0];c.weeks[0].end=a[1];c.weeks[0].wk=2;c.api.q.space={s:[site]};if(extra)extra(c);localStorage.setItem('gstSeq_v40_'+n,JSON.stringify(c));};
  mk('TB',999001);mk('TC',999002);mk('TF',999003,c=>{c.api={q:{columns:c.api.q.columns.concat(['https://evil.example/x','<img src=x onerror=window.__x=5>']),space:{s:[999003,-1,1.5,'x'],url:'https://evil.example'},url:'https://evil.example/collect',host:'evil.example',period:{p1:[{type:'D',start:'1999-01-01',end:'2030-01-01'}]},'max-results':999999,options:{BAD:true,ok_opt:true,str:'x'},sort:['<script>'],filter:{metric:{'<img src=x onerror=window.__x=6>':{$eq:'</script><script>window.__x=7</script>'}}}},key:'x',url:'https://evil.example'};c.name='TF';});
  return JSON.parse(localStorage.getItem(k)).api;},[D(-24),D(-11)]);
R('P2 api stocké (test d\'origine)',made);
const load=async n=>p.evaluate(key=>{const s=document.querySelector('#gst-app [data-act=load]');if(!s)return 'pas de select';const o=document.createElement('option');o.value=key;s.appendChild(o);s.value=key;s.dispatchEvent(new Event('change',{bubbles:true}));return window.GST.getState().name;},'gstSeq_v40_'+n);
mode='race';all=[];R('charge TF',await load('TF'));await p.waitForTimeout(900);
R('P5 état forgé : api nettoyé',await p.evaluate(()=>window.GST.getState().api));R('P5 appels TF',all.filter(x=>x.m==='GET').map(x=>({op:x.op,key:x.key,keyUrl:x.keyUrl,param:x.param})));R('P5 TF après',await p.evaluate(()=>{const s=window.GST.getState();return {weeks:s.weeks.length,x:window.__x||0,draft:!!document.querySelector('#gst-app .dv')};}));
all=[];R('charge TB',await load('TB'));await p.waitForTimeout(250);R('charge TC',await load('TC'));await p.waitForTimeout(4500);
R('P6 course : appels',all.filter(x=>x.m==='GET').map(x=>x.param&&x.param.space.s[0]));
R('P6 course : état courant',await p.evaluate(()=>{const s=window.GST.getState();const e=document.querySelector('#gst-app .err'),o=document.querySelector('#gst-app .ok');return {name:s.name,weeks:s.weeks.length,visA:s.weeks.map(x=>x.A.n),visB:s.weeks.map(x=>x.B.n),draft:!!document.querySelector('#gst-app .dv'),notice:o?o.innerText.slice(0,120):'',err:e?e.innerText.slice(0,160):''};}));
R('P6 course : TC stocké',await p.evaluate(()=>{const s=JSON.parse(localStorage.getItem('gstSeq_v40_TC'));return {weeks:s.weeks.length,visA:s.weeks.map(x=>x.A.n),visB:s.weeks.map(x=>x.B.n)};}));
all=[];await load('TB');await p.waitForTimeout(2200);await load('TB');await p.waitForTimeout(2200);
R('P6 PTRY : appels après 2 rechargements de TB',{n:all.filter(x=>x.m==='GET').length,etatTB:await p.evaluate(()=>{const s=window.GST.getState();return {name:s.name,weeks:s.weeks.length,visA:s.weeks.map(x=>x.A.n)};})});
R('P2 fuites (fin de session)',await leak());
// ---- P4 : libellés/valeurs piégés
await fresh();mode='ok';xlab='Conv <img src=x onerror=window.__x=1>"\'><svg onload=window.__x=2>';xvr='8800001V"><img src=x onerror=window.__x=4><script>window.__x=8</script>';await openForm();await fill({url:H+Q,start:D(-17)});await p.click('#gst-app [data-act=apigo]');await p.waitForSelector('#gst-app .dv',{timeout:20000});await p.waitForTimeout(300);
const xs=async()=>p.evaluate(()=>({x:window.__x||0,img:document.querySelectorAll('#gst-app img[src=x], #gst-app svg[onload], #gst-app script').length}));
R('P4 écran .dv',await xs());await p.click('#gst-app [data-act=apply]');await p.waitForTimeout(1200);const tabs=await p.evaluate(()=>[...document.querySelectorAll('#gst-app [data-act=tab]')].map(e=>e.getAttribute('data-v')));const xr=[];
for(const t of tabs){await p.click('#gst-app [data-act=tab][data-v="'+t+'"]').catch(()=>{});await p.waitForTimeout(350);xr.push(t+':'+JSON.stringify(await xs()));}
R('P4 après application, onglets',xr);R('P4 libellés en état',await p.evaluate(()=>{const s=window.GST.getState();return {labels:s.labels,metrics:s.metrics.map(m=>m.name)};}));
R('console contient la clé',logs.some(l=>l.includes(AK)||l.includes(SK)));R('erreurs de page',errs);
await b.close();})().catch(e=>{console.log('ERREUR BANC',e.message.slice(0,600));process.exit(1);});

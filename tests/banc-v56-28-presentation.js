// Banc de la présentation du test (v56.23) : l'extension 0.4.0 est simulée en mémoire (mêmes routes, mêmes règles d'accès).
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
const FILE=path.join(__dirname,'..','calculateur-sequentiel-v56-28.html');const HTML='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>button{white-space:nowrap}body{margin:0;padding:0 8px}</style></head><body>'+fs.readFileSync(FILE,'utf8')+'</body></html>';
let pass=0,fail=0;const ok=(n,c,d)=>{c?pass++:fail++;console.log((c?'✅ ':'❌ ')+n+(c?'':' — '+JSON.stringify(d)));};
const JPG=Buffer.from('/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/yQALCAABAAEBAREA/8wABgAQEAX/2gAIAQEAAD8A0s8g/9k=','base64');
const PNG=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==','base64');
function mock(ver){const db={tests:[],seq:100,users:{},keyHits:0,badKey:0};let session=null;
  const row=(t,me)=>({id:t.id,name:t.name,sum:t.sum,updated:'2026-11-20',mine:t.owner===me,owner:t.owner,shared:t.owner===me?t.shared.slice():[]});
  const pv=t=>t.vis.map(v=>({id:v.id,arm:v.arm,w:800,h:600}));
  const handler=async route=>{const req=route.request(),u=new URL(req.url()),m=req.method(),J=(o,s)=>route.fulfill({status:s||200,contentType:'application/json',body:JSON.stringify(o)});
    if(u.pathname==='/')return route.fulfill({status:200,contentType:'text/html; charset=utf-8',body:HTML});
    if(u.pathname==='/wp-admin/admin-ajax.php')return route.fulfill({status:200,contentType:'text/plain',body:session?'abcdef1234':'0'});
    if(!u.pathname.startsWith('/wp-json/fwo-gst/v1/'))return J({message:'Aucune route'},404);
    const p=u.pathname.slice('/wp-json/fwo-gst/v1/'.length),nonce=req.headers()['x-wp-nonce']==='abcdef1234',me=nonce?session:null;let body={};try{body=req.postData()?JSON.parse(req.postData()):{};}catch(e){}
    const usr=()=>me?Object.assign({email:me,name:'x'},ver?{org:db.users[me]||''}:{}):null;
    if(p==='me'&&m==='GET')return J(Object.assign({enabled:true,user:usr()},ver?{v:'0.4.0'}:{}));
    const pm=/^public\/(\d+)(?:\/visuals\/([a-f0-9]{12}))?$/.exec(p);
    if(pm&&ver){const t=db.tests.find(x=>x.id===+pm[1]);if(!t||!t.pkey||req.headers()['x-fwo-key']!==t.pkey||u.search){db.badKey++;return J({message:'Lien introuvable.'},404);}db.keyHits++;if(pm[2]){return t.vis.find(v=>v.id===pm[2])?route.fulfill({status:200,contentType:'image/jpeg',body:JPG}):J({},404);}return J({name:t.name,pres:t.pres||{},visuals:pv(t),org:''});}
    if(!me)return J({message:'Connexion requise.'},401);
    if(p==='me'&&m==='POST'&&ver){db.users[me]=String(body.org||'').slice(0,120);return J({user:usr()});}
    if(p==='tests'&&m==='GET')return J({tests:db.tests.filter(t=>t.owner===me||t.shared.includes(me)).map(t=>row(t,me))});
    if(p==='tests'&&m==='POST'){const t={id:++db.seq,name:body.name,state:body.state,sum:body.sum||null,owner:me,shared:[],pres:body.pres||null,vis:[],pkey:''};db.tests.push(t);return J(row(t,me));}
    const mm=/^tests\/(\d+)(?:\/(share|visuals|publink)(?:\/([a-f0-9]{12}))?)?$/.exec(p);if(!mm)return J({message:'Aucune route'},404);const t=db.tests.find(x=>x.id===+mm[1]),acc=t?(t.owner===me?'owner':t.shared.includes(me)?'guest':null):null;
    if(!acc)return J({message:'Test introuvable.'},404);
    if(mm[2]==='visuals'&&ver){if(m==='GET'&&mm[3])return t.vis.find(v=>v.id===mm[3])?route.fulfill({status:200,contentType:'image/jpeg',body:JPG}):J({},404);if(acc!=='owner')return J({message:'Test introuvable.'},404);
      if(m==='POST'){if(!/^data:image\/(png|jpeg);base64,/.test(body.data||'')||!/^[AB]$/.test(body.arm))return J({message:'Format non accepté.'},415);if(t.vis.filter(v=>v.arm===body.arm).length>=4)return J({message:'Nombre maximal de visuels atteint pour cette variation.'},409);t.vis.push({id:require('crypto').randomBytes(6).toString('hex'),arm:body.arm});return J({visuals:pv(t)});}
      if(m==='DELETE'&&mm[3]){t.vis=t.vis.filter(v=>v.id!==mm[3]);return J({visuals:pv(t)});}}
    if(acc!=='owner'&&(m!=='GET'||mm[2]))return J({message:'Test introuvable.'},404);
    if(mm[2]==='publink'&&ver){if(m==='POST'){if(!t.pkey)t.pkey=require('crypto').randomBytes(24).toString('hex');return J({key:t.pkey});}t.pkey='';return J({ok:true});}
    if(mm[2]==='share'){const e=String(body.email||'').toLowerCase();if(m==='POST'){if(!t.shared.includes(e))t.shared.push(e);}return J({shared:t.shared});}
    if(m==='GET')return J(Object.assign(row(t,me),{state:t.state},ver?{pres:t.pres||{problem:'',page:'',hyp:''},visuals:pv(t)}:{}));
    if(m==='PUT'){t.name=body.name;t.state=body.state;t.sum=body.sum||null;if('pres' in body)t.pres=body.pres;return J(row(t,me));}
    return J({message:'Aucune route'},404);};
  return {db,handler,setSession:e=>{session=e;}};}
(async()=>{const b=await chromium.launch();
 for(const W of [360,1280]){const T='['+W+'] ';const errs=[];
  const open=async(mk,hash)=>{const ctx=await b.newContext({viewport:{width:W,height:900}});const p=await ctx.newPage();p.on('pageerror',e=>errs.push(String(e)));p.on('dialog',d=>d.accept());await ctx.route('https://gst.test/**',mk.handler);await ctx.route(/fonts\.(googleapis|gstatic)\.com|fwoptimisation\.com/,r=>r.abort());await p.goto('https://gst.test/'+(hash||''));await p.waitForTimeout(900);return p;};
  const ov=p=>p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
  // 1. extension 0.3.2 : aucun onglet, aucune demande d'organisation
  let mk=mock(false);mk.setSession('a@x.fr');let p=await open(mk);await p.click('[data-act=example]');await p.waitForTimeout(2500);
  ok(T+'extension 0.3.2 : pas d\'onglet Présentation',!(await p.locator('#gst-app .tabs button',{hasText:'Présentation'}).count()));
  await p.click('[data-act=dash]');await p.waitForTimeout(600);ok(T+'extension 0.3.2 : pas de demande d\'organisation',!(await p.locator('#gst-app .card.org').count()));await p.context().close();
  // 2. sans compte : pas d'onglet
  mk=mock(true);p=await open(mk);await p.click('[data-act=example]');await p.waitForTimeout(2500);
  ok(T+'sans compte : pas d\'onglet Présentation',!(await p.locator('#gst-app .tabs button',{hasText:'Présentation'}).count()));await p.context().close();
  // 3. compte, extension 0.4.0
  mk.setSession('a@x.fr');p=await open(mk);await p.click('[data-act=example]');await p.waitForTimeout(2500);
  const tab=p.locator('#gst-app .tabs button',{hasText:'Présentation'});ok(T+'compte : onglet Présentation présent',await tab.count()===1);
  await tab.click();await p.waitForTimeout(300);
  const XSS='<img src=x onerror="window.__x=1">Les avis sont en bas de page.';
  await p.fill('#gst-pp',XSS);await p.fill('#gst-pg','Fiche produit');await p.fill('#gst-ph','Si nous affichons la note sous le prix,\nalors plus de visiteurs achèteront.');
  ok(T+'avant enregistrement : pas d\'ajout de visuel, consigne affichée',!(await p.locator('[data-act=vispick]').count())&&/Enregistrez d'abord la présentation/.test(await p.locator('.pres').innerText()));
  await p.click('[data-act=pressave]');await p.waitForTimeout(1200);
  const t0=mk.db.tests[0];ok(T+'enregistrement : problème, page et hypothèse reçus par le serveur',t0&&t0.pres&&t0.pres.problem===XSS&&t0.pres.page==='Fiche produit'&&/alors plus de visiteurs/.test(t0.pres.hyp),t0&&t0.pres);
  ok(T+'après enregistrement : champs conservés à l\'écran, deux boutons d\'ajout',(await p.inputValue('#gst-pp'))===XSS&&await p.locator('[data-act=vispick]').count()===2);
  const up=async(arm,file)=>{const [fc]=await Promise.all([p.waitForEvent('filechooser'),p.click('[data-act=vispick][data-v='+arm+']')]);await fc.setFiles(file);await p.waitForTimeout(900);};
  await up('B',{name:'b.png',mimeType:'image/png',buffer:PNG});
  ok(T+'ajout d\'un visuel PNG en B : affiché depuis une adresse locale au navigateur',t0.vis.length===1&&t0.vis[0].arm==='B'&&/^blob:/.test(await p.locator('.pv-f img').first().getAttribute('src')||''),t0.vis);
  await up('A',{name:'a.gif',mimeType:'image/gif',buffer:PNG});ok(T+'GIF refusé avant envoi, message clair',t0.vis.length===1&&/PNG ou JPG/.test(await p.locator('.err').innerText().catch(()=>'')));
  await up('A',{name:'gros.jpg',mimeType:'image/jpeg',buffer:Buffer.alloc(2097153,1)});ok(T+'image de plus de 2 Mo refusée avant envoi',t0.vis.length===1&&/2 Mo au plus/.test(await p.locator('.err').innerText().catch(()=>'')));
  for(let i=0;i<4;i++)await up('A',{name:'a'+i+'.jpg',mimeType:'image/jpeg',buffer:JPG});
  ok(T+'4 visuels en A : le bouton d\'ajout de A disparaît',t0.vis.filter(v=>v.arm==='A').length===4&&!(await p.locator('[data-act=vispick][data-v=A]').count())&&await p.locator('[data-act=vispick][data-v=B]').count()===1);
  await p.locator('[data-act=visdel]').first().click();await p.waitForTimeout(700);ok(T+'retrait d\'un visuel',t0.vis.length===4&&await p.locator('.pv-f').count()===4);
  ok(T+'onglet Présentation sans débordement',(await ov(p))<=0,await ov(p));
  ok(T+'cibles tactiles : boutons de l\'onglet à 44 px au moins',await p.evaluate(()=>[...document.querySelectorAll('.pres button')].every(x=>x.getBoundingClientRect().height>=44)),await p.evaluate(()=>[...document.querySelectorAll('.pres button')].map(x=>[x.textContent.slice(0,14),Math.round(x.getBoundingClientRect().height)])));
  // 4. réouverture depuis le tableau de bord
  await p.click('[data-act=dash]');await p.waitForTimeout(700);
  ok(T+'tableau de bord : demande d\'organisation affichée',await p.locator('.card.org').count()===1);
  await p.fill('#gst-org','Altiplano');await p.click('[data-act=orgsave]');await p.waitForTimeout(700);
  ok(T+'organisation enregistrée, la demande disparaît',mk.db.users['a@x.fr']==='Altiplano'&&!(await p.locator('.card.org').count()));
  await p.click('[data-act=dashwho][data-v=compte]');await p.waitForTimeout(300);ok(T+'Mon compte : organisation modifiable, valeur reprise',(await p.inputValue('#gst-org'))==='Altiplano');
  await p.click('[data-act=dashwho][data-v=mes]');await p.waitForTimeout(300);await p.locator('[data-act=dashopen]').first().click();await p.waitForTimeout(1800);
  await p.locator('#gst-app .tabs button',{hasText:'Présentation'}).click();await p.waitForTimeout(900);
  ok(T+'réouverture : texte et visuels revenus du serveur',(await p.inputValue('#gst-pg'))==='Fiche produit'&&await p.locator('.pv-f img').count()===4,[await p.inputValue('#gst-pg').catch(()=>null),await p.locator('.pv-f img').count()]);
  // 5. lien de partage
  await p.locator('#gst-app .tabs button',{hasText:'Résultats'}).click();await p.click('[data-act=share]');await p.waitForTimeout(1500);
  const link=await p.inputValue('[data-f=shareurl]');const hp=/&p=(\d+)\.([a-f0-9]{48})$/.exec(link);
  ok(T+'lien de partage : clé de lecture ajoutée dans le fragment, jamais avant le #',!!hp&&link.indexOf('#')<link.indexOf('&p=')&&t0.pkey===hp[2],link.slice(-70));
  await mk.db.tests[0].shared.push('b@x.fr');const hash=link.slice(link.indexOf('#'));await p.context().close();
  mk.setSession(null);mk.db.keyHits=0;let q=await open(mk,hash);await q.waitForTimeout(2600);
  const ro=await q.evaluate(()=>{const d=document.querySelector('details.pres.ro');return d?{t:d.innerText,img:d.querySelectorAll('.pv-f img').length,x:window.__x||0,inj:d.querySelectorAll('img[src="x"]').length,ed:d.querySelectorAll('textarea,input,[data-act=visdel],[data-act=vispick]').length}:null;});
  ok(T+'lien, sans compte : présentation en lecture seule avec ses 4 visuels',ro&&/Fiche produit/.test(ro.t)&&/alors plus de visiteurs/.test(ro.t)&&ro.img===4&&ro.ed===0,ro);
  ok(T+'lien : le texte saisi est affiché tel quel, rien ne s\'exécute',ro&&ro.x===0&&ro.inj===0&&ro.t.includes('<img src=x'));
  ok(T+'lien : clé envoyée en en-tête uniquement (aucun paramètre d\'adresse)',mk.db.keyHits>=5&&mk.db.badKey===0,[mk.db.keyHits,mk.db.badKey]);
  ok(T+'lien : lecture seule sans débordement',(await ov(q))<=0,await ov(q));await q.context().close();
  q=await open(mk,hash.replace(/[a-f0-9]{48}$/,'0'.repeat(48)));await q.waitForTimeout(2000);
  const ro2=await q.evaluate(()=>{const d=document.querySelector('details.pres.ro');return d?{t:d.innerText,img:d.querySelectorAll('.pv-f').length}:null;});
  ok(T+'lien avec une clé fausse : le texte reste, aucun visuel servi',ro2&&/Fiche produit/.test(ro2.t)&&ro2.img===0&&mk.db.badKey>0,ro2);await q.context().close();
  // 6. invité
  mk.setSession('b@x.fr');q=await open(mk,'#test='+t0.id);await q.waitForTimeout(2600);
  const g=await q.evaluate(()=>{const d=document.querySelector('details.pres.ro');return d?{img:d.querySelectorAll('.pv-f img').length,ed:d.querySelectorAll('textarea,[data-act=visdel],[data-act=vispick]').length,tab:[...document.querySelectorAll('.tabs button')].length}:null;});
  ok(T+'invité : présentation en lecture seule, visuels chargés, rien de modifiable',g&&g.img===4&&g.ed===0,g);await q.context().close();
  ok(T+'aucune erreur JS',errs.length===0,errs);
 }
 await b.close();console.log(pass+'/'+(pass+fail)+(fail?' KO':' OK'));})();

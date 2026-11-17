// Un lien de partage hostile ne doit exécuter aucun script ni injecter de balise. Usage : node banc-xss-partage.js fichier.html [...]
const {chromium}=require('playwright');const path=require('path');
const X='<img src=x onerror="window.__pwn=(window.__pwn||0)+1">';
const hostile=()=>{const id='m1" onfocus="window.__pwn=9" autofocus x="';const arm=c=>({n:20000,m:{[id]:{c},m2:{c:c+'<b>'}}});
  return {v:1,n:'Test '+X,d:'2026-11-16'+X,p:{k:'8'+X,alpha:'0.05'+X,power:0.8,beta:0.2,testType:'3'+X,sfu:'KimDeMets'+X,sfl:'HSD'+X,startDate:'2026-10-05'+X,unit:'jour'+X,traffic:'1000'+X},
    m:[{id,src:X,name:'Achat '+X,type:'binaire',role:'principale',sens:'hausse',marge:'1'+X},{id:'m2',src:'r',name:X,type:'continue'+X,role:'garde-fou'+X,sens:'baisse'+X,marge:1}],
    l:{A:'A '+X,B:'B '+X},w:[{A:arm(1000),B:arm(1100),label:X},{A:{n:'40000'+X,m:{[id]:{c:2000}}},B:arm(2300)}]};};
(async()=>{const b=await chromium.launch();let bad=0;
 for(const file of process.argv.slice(2))for(const W of [360,1280]){const p=await b.newPage({viewport:{width:W,height:900}});const errs=[];p.on('pageerror',e=>errs.push(String(e).slice(0,120)));p.on('dialog',d=>d.dismiss());
  const tok='j'+Buffer.from(JSON.stringify(hostile()),'utf8').toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
  await p.goto('file://'+path.resolve(file)+'#t='+tok);await p.waitForTimeout(3500);
  for(const sel of ['[data-act=legend]','[data-act=detail]','.mrw','[data-act=rocopy]'])await p.locator(sel).first().click({timeout:1500}).catch(()=>{});await p.waitForTimeout(800);
  for(const v of ['donnees','plan','resultats']){await p.locator('[data-act=tab][data-v='+v+']').click({timeout:1500}).catch(()=>{});await p.waitForTimeout(700);}
  const r=await p.evaluate(()=>({pwn:window.__pwn||0,img:document.querySelectorAll('#gst-app img').length,on:[...document.querySelectorAll('#gst-app *')].filter(e=>[...e.attributes].some(a=>/^on/i.test(a.name))).length,k:window.GST&&String(GST.getState().plan.k),vue:(document.querySelector('.robar,.err,.verdict')||{}).className||''}));
  const ko=r.pwn>0||r.img>0||r.on>0;if(ko)bad++;console.log((ko?'❌ ':'✅ ')+path.basename(file)+' ['+W+'] '+JSON.stringify(r)+(errs.length?' erreurs:'+JSON.stringify(errs.slice(0,2)):''));await p.close();}
 await b.close();process.exit(bad?1:0);})();

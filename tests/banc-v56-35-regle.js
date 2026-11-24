const pk=async p=>{const u=p.locator('#gst-app [data-act=unpick]');if(await u.count())await u.first().click();};
// v56.35 : la règle d'arrêt (type de test) se choisit à la création, dans l'assistant et à l'import
const {chromium}=require('playwright');const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-35.html');
let n=0,okc=0;const ok=(l,c,d)=>{n++;if(c)okc++;console.log((c?'✅ ':'❌ ')+l+(d!==undefined?' — '+JSON.stringify(d):''));};
const D=k=>{const d=new Date();d.setDate(d.getDate()+k);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
const T='Variation;Visiteurs;Achats\nA;20124;1041\nB;20139;1082\n';
(async()=>{const b=await chromium.launch();for(const w of [360,1280]){const p=await b.newPage({viewport:{width:w,height:900},deviceScaleFactor:w===360?2:1});const errs=[];p.on('pageerror',e=>errs.push(String(e)));await p.route(/fonts\.|fwoptimisation\.com/,r=>r.abort());
const fresh=async()=>{await p.goto('file://'+path.resolve(FILE));await p.evaluate(()=>{try{localStorage.clear()}catch(e){}});await p.reload();await p.waitForSelector('.cta button');};
const cnt=s=>p.locator('#gst-app '+s).count(),ov=()=>p.evaluate(()=>document.documentElement.scrollWidth-innerWidth),st=()=>p.evaluate(()=>{const s=window.GST.getState();return {tt:s.plan.testType,n:s.weeks.length,fut:s.bounds?s.bounds.fut:null};});
for(const choix of [3,1]){
 // assistant
 await fresh();await pk(p);await p.click('#gst-app [data-act=howto][data-v=manuel]');await p.waitForTimeout(300);await p.fill('#gst-app [data-man=m0name]','Visiteurs avec achat');await p.locator('#gst-app [data-man=m0name]').blur();await p.click('#gst-app [data-act=manstep]');await p.waitForTimeout(300);await p.fill('#gst-app [data-mde=traffic]','20000');await p.keyboard.press('Tab');await p.waitForTimeout(100);await p.fill('#gst-app [data-mde=conv]','1000');await p.keyboard.press('Tab');await p.waitForTimeout(1800);
 const has=(await cnt('[data-man=testType]'))===2,def=await p.isChecked('#gst-app [data-man=testType][value="3"]');const before=await p.locator('#gst-app .wz .mr2 b').allInnerTexts();
 if(choix===1){await p.check('#gst-app [data-man=testType][value="1"]');await p.waitForTimeout(1800);}const after=await p.locator('#gst-app .wz .mr2 b').allInnerTexts();
 if(choix===3){ok(`[${w}] assistant, étape 2 : la question « Quand le test peut-il s'arrêter avant la fin ? » est posée, « Dès que le résultat est joué » coché par défaut, sans débordement`,has&&def&&(await ov())<=0,{has,def,ov:await ov()});if(w===360||w===1280)await (await p.$('#gst-app .wz')).screenshot({path:'/mnt/user-data/outputs/assistant-regle-arret-v56-35-'+w+'.png'});}
 else ok(`[${w}] assistant : choisir « Seulement s'il gagne » recalcule le tableau des durées (effet détectable différent)`,after.join()!==before.join()&&after.length>0,{before:before.slice(0,3),after:after.slice(0,3)});
 await p.click('#gst-app [data-act=manstart]');await p.waitForTimeout(500);let s=await st();
 ok(`[${w}] assistant, choix ${choix===3?'« dès que le résultat est joué »':'« seulement s\'il gagne »'} : le test est créé avec cette règle`,s.tt===choix,s);
 // import
 await fresh();await p.evaluate(a=>window.GST.openCSV(a,'export.csv'),T);await p.waitForSelector('.dv');
 const hd=(await cnt('[data-d=tt]'))===2;if(choix===3&&w)await (await p.$('#gst-app .dv')).screenshot({path:'/mnt/user-data/outputs/import-regle-arret-v56-35-'+w+'.png'});
 if(choix===1){await p.check('#gst-app [data-d=tt][value="1"]');await p.waitForTimeout(300);}
 await p.fill('#gst-app [data-d=startDate]',D(-7));await p.locator('#gst-app [data-d=startDate]').blur();await p.waitForTimeout(250);await p.fill('#gst-app [data-d=endDate]',D(-1));await p.locator('#gst-app [data-d=endDate]').blur();await p.waitForTimeout(300);
 ok(`[${w}] import : après modification d'une date, le choix de règle est conservé`,await p.isChecked('#gst-app [data-d=tt][value="'+choix+'"]'));
 await p.click('#gst-app [data-act=apply]');await p.waitForTimeout(1200);s=await st();
 ok(`[${w}] premier import, choix ${choix} : question posée, test créé avec cette règle${choix===1?', aucun seuil de futilité':', seuils de futilité présents'}, sans débordement`,hd&&s.n===1&&s.tt===choix&&s.fut&&(choix===1?s.fut.every(x=>x==null):s.fut.some(x=>x!=null))&&(await ov())<=0,s);
 // second import : la règle ne se rechoisit plus
 if(choix===1){await p.evaluate(a=>{const s=window.GST.getState();s.plan.startDate=a[0];s.weeks[0].end=a[1];},[D(-14),D(-8)]);await p.evaluate(a=>window.GST.openCSV(a,'export.csv'),T.replace('20124;1041','40300;2080').replace('20139;1082','40280;2160'));await p.waitForSelector('.dv');ok(`[${w}] second import : la règle n'est plus proposée (elle ne change pas en cours de test)`,(await cnt('[data-d=tt]'))===0);}
}
ok(`[${w}] aucune erreur JS`,errs.length===0,errs);await p.close();}
console.log(okc+'/'+n+(okc===n?' OK':' ÉCHEC'));await b.close();})();

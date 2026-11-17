// v56.2 : boutons d'une même rangée alignés, envoi par email, pied sans lien de contact, démonstration directe
const {chromium}=require('playwright');const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-2.html');
const THEME='button,input,optgroup,select,textarea{font-family:inherit;font-size:1rem;line-height:1.5;margin:0}[type="button"],[type="submit"],button{background-color:transparent;border:1px solid #c36;border-radius:3px;color:#c36;display:inline-block;font-size:1rem;font-weight:400;padding:.5rem 1rem;text-align:center;transition:.3s;user-select:none;white-space:nowrap}.elementor-kit-5072 button{background-color:#028D6A;font-size:16px;font-weight:700;color:#fff}';
let n=0,okc=0;const ok=(l,c,d)=>{n++;if(c)okc++;console.log((c?'✅ ':'❌ ')+l+(d!==undefined?' — '+JSON.stringify(d):''));};
(async()=>{const b=await chromium.launch();
for(const w of [360,1280]){const ctx=await b.newContext({viewport:{width:w,height:900},permissions:['clipboard-read','clipboard-write']});const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('file://'+path.resolve(FILE));await p.evaluate(()=>{document.body.classList.add('elementor-kit-5072');window.__mail=[];window.GST_NOMAIL=u=>window.__mail.push(u);});await p.addStyleTag({content:THEME});await p.waitForSelector('.cta button');
  // rangées de boutons : sur une même ligne visuelle, mêmes centres
  const rows=async(lab)=>{const bad=await p.evaluate(()=>{const out=[];document.querySelectorAll('#gst-app .row').forEach(r=>{const bs=[...r.children].filter(e=>e.tagName==='BUTTON'&&e.offsetParent);const L={};bs.forEach(e=>{const q=e.getBoundingClientRect();const k=[...Object.keys(L)].find(k=>Math.abs(+k-q.top)<q.height*0.8);(L[k!==undefined?k:q.top]=L[k!==undefined?k:q.top]||[]).push(e);});Object.values(L).forEach(g=>{const c=g.map(e=>{const q=e.getBoundingClientRect();return Math.round(q.top+q.height/2);});if(Math.max(...c)-Math.min(...c)>1)out.push(g.map(e=>e.textContent.trim().slice(0,22)).join(' | ')+' '+c.join('/'));});bs.forEach(e=>{const m=getComputedStyle(e);if(parseFloat(m.marginTop)||parseFloat(m.marginBottom))out.push('marge '+e.textContent.trim().slice(0,22)+' '+m.marginTop);});});return out;});ok(`[${w}] ${lab} : boutons d'une même rangée alignés, sans marge parasite`,bad.length===0,bad);};
  await rows('accueil');
  await p.click('[data-act=example]');await p.waitForTimeout(600);
  ok(`[${w}] démonstration : résultats affichés directement, sans écran de vérification`,(await p.locator('.dv').count())===0&&/Exemple chargé/.test(await p.textContent('#gst-app'))&&(await p.locator('.verdict,.vname,.kpis').count())>0);
  await rows('résultats');
  ok(`[${w}] pied : plus de lien de contact, version affichée`,(await p.locator('.foot a').count())===0&&/v56\.2/.test(await p.textContent('.foot')));
  await p.locator('[data-act=tab][data-v=donnees]').click();await p.waitForTimeout(300);await rows('données');
  const al=await p.evaluate(()=>{const r=document.querySelector('#gst-app .drop p.row');return [...r.querySelectorAll('button')].map(e=>{const q=e.getBoundingClientRect();return [Math.round(q.top),Math.round(q.height)];});});
  ok(`[${w}] zone de dépôt : « Télécharger le modèle » et « Essayer avec un exemple » de même hauteur`+(w===1280?' et sur la même ligne':''),al.length===2&&al[0][1]===al[1][1]&&(w===360||al[0][0]===al[1][0]),al);
  // un test déjà chargé : l'exemple repasse par l'écran de vérification (pas d'écrasement silencieux)
  await p.click('.drop [data-act=example]');await p.waitForTimeout(400);ok(`[${w}] test déjà chargé : « Essayer avec un exemple » demande confirmation par l'écran de vérification`,(await p.locator('.dv').count())===1);await p.click('[data-act=cancel]');
  // partage par email
  await p.click('[data-act=share]');await p.waitForSelector('[data-f=shareurl]');await rows('partage');
  await p.fill('[data-f=shareto]','claire.martin@exemple.fr');await p.click('[data-act=sharemail]');await p.waitForTimeout(400);
  const m=await p.evaluate(()=>window.__mail);const url=await p.inputValue('[data-f=shareurl]');let clip='';try{clip=await p.evaluate(()=>navigator.clipboard.readText());}catch(e){clip='(illisible)';}
  ok(`[${w}] email : adresse tapée puis clic immédiat → la messagerie est appelée une fois, à la bonne adresse, lien mailto < 2 000 caractères`,m.length===1&&/^mailto:claire\.martin@exemple\.fr\?subject=/.test(m[0])&&m[0].length<=2000,{n:m.length,len:m[0]&&m[0].length});
  // lien long : nom de test très long
  await p.click('[data-act=shareclose]');await p.fill('[data-f=name]','Test '+'très long '.repeat(40));await p.locator('[data-f=name]').blur();await p.waitForTimeout(200);await p.click('[data-act=share]');await p.waitForSelector('[data-f=shareurl]');await p.fill('[data-f=shareto]','claire.martin@exemple.fr');await p.click('[data-act=sharemail]');await p.waitForTimeout(400);
  const mL=await p.evaluate(()=>window.__mail);const urlL=await p.inputValue('[data-f=shareurl]');try{clip=await p.evaluate(()=>navigator.clipboard.readText());}catch(e){clip='(illisible)';}
  ok(`[${w}] email : lien long → copié dans le presse-papiers, message d'explication ; l'adresse reste dans le champ`,mL.length===2&&mL[1].length<=2000&&clip===urlL&&/collez ici le lien/.test(decodeURIComponent(mL[1]))&&/Lien copié/.test(await p.textContent('.share'))&&(await p.inputValue('[data-f=shareto]'))==='claire.martin@exemple.fr',{url:urlL.length,clip:clip.length,mail:mL[1]&&mL[1].length});
  await p.fill('[data-f=shareto]','pas une adresse');await p.click('[data-act=sharemail]');await p.waitForTimeout(300);const m2=await p.evaluate(()=>window.__mail);
  ok(`[${w}] email : adresse invalide → messagerie ouverte sans destinataire, rien d'injecté`,m2.length===3&&/^mailto:\?subject=/.test(m2[2]));
  ok(`[${w}] sans débordement, aucune erreur JS`,(await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth))<=0&&errs.length===0,errs);await ctx.close();}
// lien court : inséré tel quel
const p=await b.newPage();await p.goto('file://'+path.resolve(FILE));await p.evaluate(()=>{window.__mail=[];window.GST_NOMAIL=u=>window.__mail.push(u);});await p.waitForSelector('.cta button');
await p.evaluate(()=>window.GST.openCSV('Variation;Visiteurs;Achats\nA;1000;50\nB;1003;60\n','court.csv'));await p.click('[data-act=apply]');await p.waitForTimeout(500);await p.click('[data-act=share]');await p.waitForSelector('[data-f=shareurl]');const u=await p.inputValue('[data-f=shareurl]');await p.click('[data-act=sharemail]');await p.waitForTimeout(300);const mm=await p.evaluate(()=>window.__mail[0]);
ok('email : lien court → inséré directement dans le message',decodeURIComponent(mm).includes(u)&&mm.length<=2000&&/s.ouvre dans votre messagerie/.test(await p.textContent('.share')),{url:u.length,mail:mm.length});
console.log('\n'+okc+'/'+n+' OK');await b.close();process.exit(okc===n?0:1);})();

// Vérification indépendante des calculs du haut de page (v56.22) : chaque valeur affichée est recalculée ici, hors de l'outil, à partir du fichier d'exemple.
const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
const FILE=path.join(__dirname,'..','calculateur-sequentiel-v56-22.html');
const res=[]; let fails=0; const ok=(n,c,i)=>{res.push((c?'✅ ':'❌ ')+n+' — '+JSON.stringify(i));if(!c)fails++;};
const SRC=fs.readFileSync(FILE,'utf8'); const EX=SRC.slice(SRC.indexOf('var EXEMPLE="')+13).split('"')[0].split('\\n').join('\n');
const parse=csv=>{const L=csv.trim().split('\n'),H=L[0].split(';');return L.slice(1).map(l=>{const c=l.split(';'),o={};H.forEach((h,i)=>o[h]=c[i]);return o;});};
// fonction d'erreur complémentaire : série de référence (Abramowitz et Stegun 7.1.26), différente de celle de l'outil
const erfc=x=>{const t=1/(1+0.3275911*x);return (((((1.061405429*t-1.453152027)*t)+1.421413741)*t-0.284496736)*t+0.254829592)*t*Math.exp(-x*x);};
const fr=(v,d)=>v.toLocaleString('fr-FR',{minimumFractionDigits:d,maximumFractionDigits:d}).replace(/\s/g,' ');
const zmax=(rows,upto)=>{let best=null;for(const v of ['A','B']){const R=rows.filter(r=>(v==='A')===/Contr/.test(r.Variation)&&+r.Semaine<=upto).sort((a,b)=>a.Semaine-b.Semaine);
  const inc=R.map((r,i)=>({w:+r.Semaine,n:+r.Visiteurs-(i?+R[i-1].Visiteurs:0),c:+r['Visiteurs avec achat']-(i?+R[i-1]['Visiteurs avec achat']:0)}));
  const N=inc.reduce((s,o)=>s+o.n,0),C=inc.reduce((s,o)=>s+o.c,0),p=C/N;
  for(const o of inc){const n2=N-o.n,c2=C-o.c,z=(o.c/o.n-c2/n2)/Math.sqrt(p*(1-p)*(1/o.n+1/n2));if(!best||Math.abs(z)>Math.abs(best.z))best={z,v,w:o.w,r1:o.c/o.n,r2:c2/n2};}}return best;};
(async()=>{ const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1280,height:900}}); p.on('dialog',d=>d.accept());
 await p.goto('file://'+path.resolve(FILE)); await p.waitForTimeout(300);
 await p.click('#gst-app [data-act=example]'); await p.waitForSelector('#gst-app .verdict'); await p.waitForTimeout(1500);
 const st=await p.evaluate(()=>{const s=GST.getState(),c=GST.compute();return {IF:s.bounds.IF,k:s.plan.k,dw:c.decisionWeek,alpha:s.plan.alpha,power:s.plan.power};});
 const txt=async()=>p.evaluate(()=>document.querySelector('#gst-app .verdict').innerText.replace(/\s+/g,' '));
 let t=await txt(); const rows=parse(EX); const wk=st.dw+1;
 const A=rows.find(r=>+r.Semaine===wk&&/Contr/.test(r.Variation)),B=rows.find(r=>+r.Semaine===wk&&!/Contr/.test(r.Variation));
 // 1. écart, taux
 const mA=A['Visiteurs avec achat']/A.Visiteurs,mB=B['Visiteurs avec achat']/B.Visiteurs,lift=mB/mA-1;
 ok('écart relatif de l\'objectif et taux des deux variations', t.includes('+'+fr(lift*100,2)+' %')&&t.includes('Contrôle '+fr(mA*100,2)+' % · Variante '+fr(mB*100,2)+' %'), {lift:fr(lift*100,2),mA:fr(mA*100,2),mB:fr(mB*100,2)});
 // 2. temps gagné = durée du test à horizon fixe équivalent (k / facteur d'inflation) moins la semaine d'arrêt
 const gain=Math.round((st.k/st.IF-wk)*10)/10;
 ok('temps gagné : k / facteur d\'inflation − semaine d\'arrêt', t.includes('économise environ '+fr(gain,1)+' semaines')&&st.IF>1.05&&st.IF<1.12, {IF:+st.IF.toFixed(4),horizonFixe:+(st.k/st.IF).toFixed(2),gain});
 // 3. écarts des garde-fous
 const g=(col)=>{const a=A[col]/A.Visiteurs,b=B[col]/B.Visiteurs;return b/a-1;}; const g1=g('Visiteurs avec rebond'),g2=g('Visiteurs contact service client');
 const sg=v=>(v>0?'+':'')+fr(v*100,2).replace('-','-')+' %';
 ok('écarts des deux garde-fous', t.includes('Visiteurs avec rebond '+sg(g1))&&t.includes('Visiteurs contact service client '+sg(g2)), [sg(g1),sg(g2)]);
 // 4. répartition et test du khi-deux
 const nA=+A.Visiteurs,nB=+B.Visiteurs,tot=nA+nB,chi=(nA-tot/2)**2/(tot/2)*2,pv=erfc(Math.sqrt(chi/2));
 await p.click('#gst-app [data-act=qdetail]'); await p.waitForTimeout(200); t=await txt();
 ok('répartition : parts, écart en visiteurs et p du khi-deux', t.includes('Contrôle '+fr(nA/tot*100,2)+' % · Variante '+fr(nB/tot*100,2)+' %')&&t.includes('soit '+fr(Math.abs(nA-nB),0)+' visiteurs d\'écart')&&t.includes('p = '+fr(pv,2)), {chi:+chi.toFixed(4),p:+pv.toFixed(4)});
 // 5. semaine la plus atypique
 const z=zmax(rows,wk);
 ok('semaine la plus éloignée : variation, semaine et nombre d\'écarts-types', t.includes('taux '+(z.v==='A'?'du contrôle':'de la variante')+' en S'+z.w+', à '+fr(Math.abs(z.z),1)+' écarts-types')&&Math.abs(z.z)<3&&t.includes('Sous le seuil'), {v:z.v,w:z.w,z:+z.z.toFixed(3)});
 // 6. taux hebdomadaires du tableau
 const inc=(v,w,col)=>{const R=rows.filter(r=>(v==='A')===/Contr/.test(r.Variation));const c=R.find(r=>+r.Semaine===w),q=R.find(r=>+r.Semaine===w-1);return +c[col]-(q?+q[col]:0);};
 let okT=true;const tab=[];for(let w=1;w<=wk;w++){const a=fr(inc('A',w,'Visiteurs avec achat')/inc('A',w,'Visiteurs')*100,2)+' %',bb=fr(inc('B',w,'Visiteurs avec achat')/inc('B',w,'Visiteurs')*100,2)+' %',v=fr(inc('A',w,'Visiteurs')+inc('B',w,'Visiteurs'),0);tab.push([w,v,a,bb]);if(!t.includes('S'+w+' '+a+' '+bb)||!t.includes('S'+w+' '+v))okT=false;}
 ok('tableaux : visiteurs et taux de l\'objectif de chaque semaine', okT, tab);
 // 7. trafic sous le plan : part du plan et effet détectable (formule de puissance à deux proportions, itérée)
 const setT=async v=>{await p.click('#gst-app [data-v=plan]');await p.waitForTimeout(300);await p.fill('#gst-app [data-mde=traffic]',String(v));await p.keyboard.press('Tab');await p.waitForTimeout(300);await p.click('#gst-app [data-act=applyplan]');await p.waitForTimeout(3000);await p.click('#gst-app [data-v=resultats]');await p.waitForTimeout(600);};
 await setT(30000); t=await txt(); const s2=await p.evaluate(()=>{const s=GST.getState(),c=GST.compute();const i=c.decisionWeek!=null?c.decisionWeek:s.weeks.length-1;const w=s.weeks[i];const pm=s.metrics.filter(m=>m.role==='principale')[0];return {IF:s.bounds.IF,k:s.plan.k,i,tot:w.A.n+w.B.n,pA:w.A.m[pm.id].c/w.A.n,alpha:s.plan.alpha,power:s.plan.power};});
 const ninv=q=>{let lo=-8,hi=8;for(let i=0;i<80;i++){const m=(lo+hi)/2;(1-0.5*erfc(m/Math.SQRT2))<q?lo=m:hi=m;}return (lo+hi)/2;};
 const mde=(traf)=>{const c=(ninv(1-s2.alpha)+ninv(s2.power))*Math.sqrt(s2.IF),n=traf*s2.k/2,q=s2.pA;let d=c*Math.sqrt(2*q*(1-q)/n)/q;for(let i=0;i<200;i++){const q1=q*(1+d);d=c*Math.sqrt((q*(1-q)+q1*(1-q1))/n)/q;}return d;};
 const exp=30000*(s2.i+1),rt=s2.tot/exp,m0=mde(30000),m1=mde(30000*rt);
 ok('trafic sous le plan : part du plan et effet détectable recalculé', t.includes(fr(s2.tot,0)+' visiteurs sur '+fr(exp,0)+' prévus')&&t.includes('soit '+fr(rt*100,0)+' %')&&t.includes('passe d\'environ '+fr(m0*100,1)+' % à '+fr(m1*100,1)+' %'), {part:fr(rt*100,0),m0:fr(m0*100,2),m1:fr(m1*100,2),alpha:s2.alpha,puissance:s2.power,IF:+s2.IF.toFixed(4)});
 await b.close(); console.log(res.join('\n')); console.log(`\n${res.length-fails}/${res.length} OK`); process.exit(fails?1:0); })();

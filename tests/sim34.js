// Vérification indépendante par simulation : le plan « futilité à partir de la semaine 2 » tient-il alpha et la puissance ?
// La simulation ne reprend aucune fonction de l'outil : seules les bornes et la dérive sont lues, puis des marches aléatoires sont tirées.
const { chromium } = require('playwright');const path=require('path');
function rng(seed){let a=seed>>>0;return ()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return ((t^t>>>14)>>>0)/4294967296;};}
function sim(d,k,th,N,seed,off){const r=rng(seed);let win=0,fut=0,sumStop=0;const gauss=()=>{let u=0,v=0;while(u===0)u=r();v=r();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);};
 const K=k;for(let n=0;n<N;n++){let S=0,done=false;for(let i=0;i<K;i++){S+=gauss()+th/Math.sqrt(K);const z=S/Math.sqrt(i+1);const e=d.eff[i],f=d.fut[i];if(i<off)continue;if(e!=null&&z>=e){win++;sumStop+=i+1;done=true;break;}if(f!=null&&z<=f){fut++;sumStop+=i+1;done=true;break;}}if(!done)sumStop+=K;}
 return {win:win/N,fut:fut/N,stop:sumStop/N};}
(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.route('**/*',r=>r.request().url().startsWith('file://')?r.continue():r.fulfill({status:200,body:''}));
const out=[];
for(const file of ['repo/calculateur-sequentiel-v56-33.html','repo/calculateur-sequentiel-v56-34.html']){await p.goto('file://'+path.resolve(file));await p.waitForTimeout(300);
 for(const cfg of [{k:2},{k:3},{k:4},{k:8},{k:12},{k:4,alpha:0.1,power:0.9},{k:28,unit:'jour'},{k:10,unit:'jour'}]){
  const P=Object.assign({alpha:0.05,power:0.8,testType:3,sfu:'KimDeMets',sfl:'HSD',unit:'semaine'},cfg);P.beta=+(1-P.power).toFixed(4);
  const d=await p.evaluate(P=>window.GST.design(P),P);const N=2000000,off=d.skip||0;
  // marche en information : k lectures également espacées ; en quotidien, l'outil place les lectures aux jours 1..k
  const h0=sim(d,P.k,0,N,12345,off),h1=sim(d,P.k,d.th,N,54321,off);
  out.push({v:file.match(/v56-(\d+)/)[1],k:P.k,u:P.unit,a:P.alpha,pw:P.power,fut:d.fut.map(x=>x==null?null:+x.toFixed(3)).slice(0,P.unit==='jour'?16:4),eff1:+d.eff[0].toFixed(3),IF:+d.IF.toFixed(4),alpha:+h0.win.toFixed(4),puissance:+h1.win.toFixed(4),arretH0:+h0.stop.toFixed(2),arretH1:+h1.stop.toFixed(2)});}}
out.forEach(o=>console.log(JSON.stringify(o)));await b.close();})();

const fs=require('fs');
function normInv(p){let lo=-40,hi=40;const erfc=x=>{const z=Math.abs(x),t=1/(1+0.5*z),r=t*Math.exp(-z*z-1.26551223+t*(1.00002368+t*(0.37409196+t*(0.09678418+t*(-0.18628806+t*(0.27886807+t*(-1.13520398+t*(1.48851587+t*(-0.82215223+t*0.17087277)))))))));return x>=0?r:2-r;};const cdf=x=>0.5*erfc(-x/Math.SQRT2);for(let i=0;i<200;i++){const m=(lo+hi)/2;cdf(m)<p?lo=m:hi=m;}return (lo+hi)/2;}
global.normInv=normInv; eval(fs.readFileSync('gs.js','utf8')+';global.GS=GS');
const ref={T3:{eff:[3.725,3.1895,2.847,2.5754,2.3411,2.1284,1.9236,1.6737],fut:[-1.4542,-0.886,-0.4025,0.0339,0.4429,0.8366,1.2273,1.6737],IF:1.0856},
 G:[3.725,3.1895,2.8471,2.5756,2.3421,2.132,1.9374,1.7531],R:[3.8963,3.3861,3.0656,2.815,2.602,2.4127,2.2397,2.0784],S:[4.2201,3.7516,3.4658,3.2467,3.0638,2.9041,2.7606,2.6291]};
const d=(a,b)=>Math.max(...a.map((x,i)=>Math.abs(x-b[i])));
let t0=Date.now(); const base={k:8,alpha:0.05,beta:0.2,sfu:'KimDeMets',sfl:'HSD'};
const t3=GS.design({...base,testType:3}); console.log('T3 eff',d(t3.eff,ref.T3.eff).toFixed(5),'fut',d(t3.fut,ref.T3.fut).toFixed(5),'IF',t3.IF.toFixed(4),Date.now()-t0,'ms');
t0=Date.now();const g=GS.design({...base,testType:1}); console.log('T1 a',d(g.eff,ref.G).toFixed(5),'IF',g.IF.toFixed(4),Date.now()-t0,'ms');
console.log('T1 a/2',d(GS.design({...base,testType:1,alpha:0.025}).eff,ref.R).toFixed(5),'T1 a/8',d(GS.design({...base,testType:1,alpha:0.00625}).eff,ref.S).toFixed(5));
for(const k of [2,4,12,26,50]){t0=Date.now();const r=GS.design({...base,k,testType:3});console.log('k',k,'IF',r.IF.toFixed(4),'fin',r.eff[k-1].toFixed(4),Date.now()-t0,'ms');}
// trafic régulier : actual == design
const eq=[1,2,3,4,5,6,7,8].map(x=>x*20000); const a3=GS.actual({...base,testType:3},eq), a1=GS.actual({...base,testType:1},eq);
console.log('actual=design T3',d(a3.eff,t3.eff).toExponential(1),d(a3.fut,t3.fut).toExponential(1),'T1',d(a1.eff,g.eff).toExponential(1));
// frac = i/k explicite : identique
console.log('frac i/k',d(GS.actual({...base,testType:3},eq,[1,2,3,4,5,6,7,8].map(x=>x/8)).fut,t3.fut).toExponential(1));
const late=[2,4,7,11,17,26,40,60].map(x=>x*1000); let r=GS.actual({...base,testType:3},late); console.log('tardif sans plan eff',r.eff.map(x=>x.toFixed(3)).join(' '),'fut',r.fut.map(x=>x.toFixed(3)).join(' '));
r=GS.actual({...base,testType:3},late,late.map(x=>x/60000)); console.log('tardif avec plan  eff',r.eff.map(x=>x.toFixed(3)).join(' '),'fut',r.fut.map(x=>x.toFixed(3)).join(' '));
console.log('tardif T1',GS.actual({...base,testType:1},late).eff.map(x=>x.toFixed(3)).join(' '));
console.log('semaine vide',GS.actual({...base,testType:3},[10,20,20,40,50,60,70,80]).eff.map(x=>x.toFixed(3)).join(' '));
// stabilité : les bornes déjà appliquées ne bougent pas quand une semaine s'ajoute
const proj=(obs,k)=>{const N=obs.slice();const rate=N[N.length-1]/N.length;while(N.length<k)N.push(N[N.length-1]+rate);return N;};
const o3=[2000,4000,7000],o4=[2000,4000,7000,15000];
for(const tt of [1,3]){const b3=GS.actual({...base,testType:tt},proj(o3,8)),b4=GS.actual({...base,testType:tt},proj(o4,8));
 console.log('stabilité type',tt,'eff S1-S3',d(b3.eff.slice(0,3),b4.eff.slice(0,3)).toExponential(1),tt===3?'fut '+d(b3.fut.slice(0,3),b4.fut.slice(0,3)).toExponential(1):'');}
for(const p of [{k:16,alpha:0.2,beta:0.1,sfu:'KimDeMets',sfl:'OF',testType:3},{k:16,alpha:0.05,beta:0.2,sfu:'OF',sfl:'HSD',testType:1},{k:12,alpha:0.01,beta:0.2,sfu:'OF',sfl:'HSD',testType:1}]){const t0=Date.now();const r=GS.design(p);console.log(JSON.stringify(p),'eff',r.eff.slice(0,3).map(x=>x.toFixed(4)),'fut',r.fut.slice(0,3).map(x=>x==null?null:x.toFixed(4)),Date.now()-t0,'ms');}

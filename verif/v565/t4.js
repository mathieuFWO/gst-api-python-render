const {v5,spend,exact}=require('./lib.js');const GS=v5.GS;const f=x=>x==null?'—':(+x).toFixed(3);
const B=(tt,sfu,k,o)=>Object.assign({k,alpha:0.05,beta:0.2,power:0.8,testType:tt,sfu,sfl:'HSD',unit:'semaine'},o||{});
function show(lbl,p,info,frac,wk,K){let b;try{b=info?GS.actual(p,info,frac):GS.design(p);}catch(e){console.log(lbl,'EXCEPTION',e.message);return;}
  const nan=b.eff.concat(b.fut).some(x=>x!=null&&!isFinite(x));let s=`${lbl}: eff=[${b.eff.map(f)}] fut=[${b.fut.map(f)}] end=${b.end} IF=${f(b.IF)} NaN=${nan}`;
  if(wk){const I=wk,m0=wk.map(()=>0);const e=exact(I,m0,b.eff,b.fut,true),e2=exact(I,m0,b.eff,b.fut,false);s+=`\n     alpha cum reel (fut appl.)=[${e.cum.map(x=>x.toFixed(5))}] ; fut ignoree total=${e2.cum[wk.length-1].toFixed(5)} ; cible calendrier=[${wk.map(x=>spend(p.sfu,p.alpha,x/K).toFixed(5))}]`;}
  console.log(s);}
for(const tt of [3,1])for(const sfu of ['KimDeMets','OF']){console.log('--- tt',tt,sfu);
 show('k=1,_t=[1] (1re lecture semaine K) design',B(tt,sfu,1,{_t:[1]}),null,null,[4],4);
 show('k=1 actual info=[4000]',B(tt,sfu,1,{_t:[1]}),[4000],[1],[4],4);
 show('reste 1 lecture: {2,4} n=1 fait',B(tt,sfu,2,{_t:[.5,1]}),[2000,4000],[.5,1],[2,4],4);
 show('info non monotone {1,3,4}',B(tt,sfu,3,{_t:[.25,.75,1]}),[3000,1000,4000],null,[1,3,4],4);
 show('_t mauvaise longueur (4 pour k=3) {1,3,4}',B(tt,sfu,3,{_t:[.25,.5,.75,1]}),[1000,3000,4000],[.25,.75,1],[1,3,4],4);
 show('_t non croissant [.75,.25,1]',B(tt,sfu,3,{_t:[.75,.25,1]}),[1000,3000,4000],null,[1,3,4],4);
 show('lectures au-dela de K : K=4 {1,5,6} _t=[.25,1.25,1.5]',B(tt,sfu,3,{_t:[.25,1.25,1.5]}),[1000,5000,6000],[.25,1.25,1.5],[1,5,6],4);
 show('K=4 {1,2,5,6,7} _t>1 avant fin',B(tt,sfu,5,{_t:[.25,.5,1.25,1.5,1.75]}),[1,2,5,6,7].map(x=>x*1000),[1,2,5,6,7].map(x=>x/4),[1,2,5,6,7],4);
 show('trafic x3 (frac>1 tot) {1,3,4}',B(tt,sfu,3,{_t:[.25,.75,1]}),[3000,9000,12000],[.75,2.25,3],[1,3,4],4);
 show('trafic /10 {1,3,4}',B(tt,sfu,3,{_t:[.25,.75,1]}),[100,300,400],[.025,.075,.1],[1,3,4],4);
 show('info quasi egales {3,4}',B(tt,sfu,2,{_t:[.75,1]}),[4000,4001],[1,1.0002],null,4);
 // jour : K=14, lectures jours 1..7,10,11,12,13,14 (8,9 sautes) -> KL=12
 const dw=[1,2,3,4,5,6,7,10,11,12,13,14],pj=B(tt,sfu,12,{unit:'jour',_t:dw.map(x=>x/14)});
 let b=GS.actual(pj,dw.map(x=>x*500),dw.map(x=>x/14));const e=exact(dw.slice(6),dw.slice(6).map(()=>0),b.eff.slice(6),b.fut.slice(6),true),e2=exact(dw.slice(6),dw.slice(6).map(()=>0),b.eff.slice(6),b.fut.slice(6),false);
 console.log(`jour K=14 sauts j8,j9: eff=[${b.eff.map(f)}] fut=[${b.fut.map(f)}] skip=${b.skip}\n     alpha cum reel j7..=[${e.cum.map(x=>x.toFixed(5))}] fut ignoree=${e2.cum[5].toFixed(5)}\n     cible calendrier w/14=[${dw.slice(6).map(x=>spend(sfu,.05,x/14).toFixed(5))}] ; ce que fait le code (i+6)/12=[${[7,8,9,10,11,12].map(x=>spend(sfu,.05,x/12).toFixed(5))}]`);
 const b0=GS.actual(B(tt,sfu,14,{unit:'jour'}),Array.from({length:14},(_,i)=>(i+1)*500));console.log('     borne j7 sans saut:',f(b0.eff[6]),'-> avec saut (recalcul retroactif):',f(b.eff[6]));
}

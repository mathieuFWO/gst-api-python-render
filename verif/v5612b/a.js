const fs=require('fs');const L=require('../verif5612/lib.js');const R='/tmp/claude-0/-home-claude/f6658268-8fe7-580d-9107-6939e43c6edb/scratchpad/repo/';
function load(f){const s=fs.readFileSync(R+f,'utf8');const a=s.indexOf('var GS=(function(){');const b=s.indexOf('var bcache',a);let i=s.indexOf('function normInv(p){'),d=0,j=i;for(;;j++){if(s[j]==='{')d++;else if(s[j]==='}'){d--;if(d===0)break;}}
  return new Function(s.slice(i,j+1)+'\n'+s.slice(a,b)+'\nreturn {GS:GS,normInv:normInv};')();}
const v12=L.v5,v10=load('calculateur-sequentiel-v56-10.html'),exact=L.exact;
const CAL={4:[[1,2,3,4],[2,3,4],[1,3,4],[1,2,4],[1,4],[3,4],[4]],6:[[1,2,3,4,5,6],[2,3,4,5,6],[1,2,4,5,6],[1,3,5,6],[1,2,6],[4,6],[3,4,5,6]],8:[[1,2,3,4,5,6,7,8],[2,3,4,5,6,7,8],[1,2,3,5,6,7,8],[1,3,4,6,8],[1,2,3,4,8],[4,8],[1,2,3,4,5,6,8],[8]]};
const f=x=>x==null?'—':(x!==x?'NaN':x.toFixed(3));
function bnd(G,base,w,infoF){const K=base.k,p=w.length===K?base:Object.assign({},base,{k:w.length,_t:w.map(x=>x/K),_kd:K});return G.actual(p,w.map(infoF||(x=>x*1000)),w.map(x=>x/K));}
function view(w,j,K){const v=w.slice(0,j);for(let x=w[j-1]+1;x<=K;x++)v.push(x);return v;}
function drift(G,base,w){let mx=0;const K=base.k;let b;try{b=bnd(G,base,w);}catch(e){return NaN;}
  for(let j=1;j<w.length;j++){let bj;try{bj=bnd(G,base,view(w,j,K));}catch(e){return NaN;}for(let i=0;i<j;i++)for(const key of ['eff','fut']){const a=bj[key][i],c=b[key][i];if(a==null&&c==null)continue;if(a==null||c==null){mx=Infinity;continue;}mx=Math.max(mx,Math.abs(a-c));}}return mx;}
const W={a:0,p:1,d12:0,d10:0,nan:0,minFinal:9,n:0,bad:[]};
for(const sfu of ['KimDeMets','OF'])for(const tt of [3,1])for(const K of [4,6,8]){
  const base={k:K,alpha:0.05,beta:0.2,power:0.8,testType:tt,sfu,sfl:'HSD',unit:'semaine'};const d0=v12.GS.design(base);const th=tt===3?d0.th:(v12.normInv(0.95)+v12.normInv(0.8))*Math.sqrt(d0.IF);
  console.log(`== ${sfu} tt=${tt} K=${K} th=${th.toFixed(4)}`);
  for(const w of CAL[K]){let b;try{b=bnd(v12.GS,base,w);}catch(e){console.log(` {${w}} ERREUR ${e.message}`);W.bad.push([sfu,tt,K,w,'throw']);continue;}
    const all=b.eff.concat(b.fut).filter(x=>x!=null);const nan=all.some(x=>x!==x)||b.eff.every(x=>x==null);let m=b.eff.length;while(m>0&&b.eff[m-1]==null)m--;const fin=b.eff[m-1];
    const info=w.slice(),m0=w.map(()=>0),m1=w.map(x=>th*Math.sqrt(x/K));
    const eA=exact(info,m0,b.eff,b.fut,true),eP=exact(info,m1,b.eff,b.fut,true);const al=eA.cum[w.length-1],pw=eP.cum[w.length-1];
    const d12=w.length>1?drift(v12.GS,base,w):0,d10=w.length>1?drift(v10.GS,base,w):0;
    W.n++;if(nan)W.nan++;W.a=Math.max(W.a,al);W.p=Math.min(W.p,pw);W.d12=Math.max(W.d12,d12!==d12?Infinity:d12);W.d10=Math.max(W.d10,d10!==d10?Infinity:d10);W.minFinal=Math.min(W.minFinal,fin);
    const flag=(al>0.0501?' !ALPHA':'')+(pw<0.799?' !PUISS':'')+(nan?' !NaN':'')+(fin<1.6?' !FINALE':'')+(d12>1e-9||d12!==d12?' !BOUGE':'');if(flag)W.bad.push([sfu,tt,K,w.join(','),flag]);
    console.log(` {${w}} eff=[${b.eff.map(f).join(' ')}] fut=[${b.fut.map(f).join(' ')}] end=${b.end} alpha=${al.toFixed(5)} puiss=${pw.toFixed(4)} derive12=${d12.toExponential(1)} derive10=${d10.toExponential(1)}${flag}`);}
}
console.log('SYNTHESE',JSON.stringify(W));
// trafic irregulier : alpha seulement
{const irr=x=>[0,700,1900,2500,4300,5200,5600,7400,8100][x];let mx=0;for(const sfu of ['KimDeMets','OF'])for(const [K,w] of [[4,[1,3,4]],[6,[1,2,4,5,6]],[8,[1,3,4,6,8]],[8,[1,2,3,4,8]]]){const base={k:K,alpha:0.05,beta:0.2,power:0.8,testType:3,sfu,sfl:'HSD',unit:'semaine'};const b=bnd(v12.GS,base,w,irr);const e=exact(w.map(irr),w.map(()=>0),b.eff,b.fut,true);mx=Math.max(mx,e.cum[w.length-1]);console.log(` irregulier ${sfu} K=${K} {${w}} alpha=${e.cum[w.length-1].toFixed(5)} eff=[${b.eff.map(f)}] fut=[${b.fut.map(f)}]`);}console.log('IRREG alpha max',mx.toFixed(5));}
// (5) identite v56.10 / v56.12
{let n=0,diff=[];const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 for(const sfu of ['KimDeMets','OF'])for(const tt of [3,1]){
  for(const K of [4,6,8]){const base={k:K,alpha:0.05,beta:0.2,power:0.8,testType:tt,sfu,sfl:'HSD',unit:'semaine'};const info=[...Array(K)].map((_,i)=>(i+1)*1000+(i%2)*137),fr=info.map(x=>x/(K*1000));
    for(const [nm,fn] of [['design',G=>G.design(base)],['actual',G=>G.actual(base,info,fr)],['actualSansFrac',G=>G.actual(base,info)]]){n++;if(!eq(fn(v10.GS),fn(v12.GS)))diff.push(['sem',sfu,tt,K,nm]);}}
  for(const K of [7,10,14,21,28]){const base={k:K,alpha:0.05,beta:0.2,power:0.8,testType:tt,sfu,sfl:'HSD',unit:'jour'};const info=[...Array(K)].map((_,i)=>(i+1)*150+(i%3)*11),fr=info.map(x=>x/(K*150));
    for(const [nm,fn] of [['design',G=>G.design(base)],['actual',G=>G.actual(base,info,fr)],['actualSansFrac',G=>G.actual(base,info)]]){n++;let a,b;try{a=fn(v10.GS);}catch(e){a='ERR '+e.message;}try{b=fn(v12.GS);}catch(e){b='ERR '+e.message;}if(!eq(a,b))diff.push(['jour',sfu,tt,K,nm]);}}}
 console.log('IDENTITE v10/v12 sans saut :',n,'comparaisons,',diff.length,'differences',JSON.stringify(diff));
 // jour avec _t/_kd (information)
 for(const tt of [3,1]){const K=14,w=[1,2,3,4,5,6,7,8,9,11,12,13,14],base={k:13,alpha:0.05,beta:0.2,power:0.8,testType:tt,sfu:'KimDeMets',sfl:'HSD',unit:'jour',_t:w.map(x=>x/K),_kd:K};const info=w.map(x=>x*150);let a,b;try{a=v10.GS.actual(base,info,w.map(x=>x/K));}catch(e){a={err:e.message};}try{b=v12.GS.actual(base,info,w.map(x=>x/K));}catch(e){b={err:e.message};}
  console.log(' jour+saut tt='+tt+' identique v10/v12 ?',eq(a,b),'v10 eff',a.err||a.eff.map(f).join(' '),'| v12 eff',b.err||b.eff.map(f).join(' '),'| fut10',a.err||a.fut.map(f).join(' '),'| fut12',b.err||b.fut.map(f).join(' '));}}

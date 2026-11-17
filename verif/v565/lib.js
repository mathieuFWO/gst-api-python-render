const fs=require('fs');
const R='/tmp/claude-0/-home-claude/f6658268-8fe7-580d-9107-6939e43c6edb/scratchpad/repo/';
function load(f){const s=fs.readFileSync(R+f,'utf8');const a=s.indexOf('var GS=(function(){');const b=s.indexOf('var bcache',a);
  const ni=s.match(/function normInv\(p\)\{[\s\S]*?\n?\}(?=\s*(function|var|\/\*))/);
  let i=s.indexOf('function normInv(p){'),d=0,j=i;for(;;j++){if(s[j]==='{')d++;else if(s[j]==='}'){d--;if(d===0)break;}}
  return new Function(s.slice(i,j+1)+'\n'+s.slice(a,b)+'\nreturn {GS:GS,normInv:normInv};')();}
exports.v5=load('calculateur-sequentiel-v56-5.html');exports.v4=load('calculateur-sequentiel-v56-4.html');
function erfc(x){var z=Math.abs(x),t=1/(1+0.5*z),r=t*Math.exp(-z*z-1.26551223+t*(1.00002368+t*(0.37409196+t*(0.09678418+t*(-0.18628806+t*(0.27886807+t*(-1.13520398+t*(1.48851587+t*(-0.82215223+t*0.17087277)))))))));return x>=0?r:2-r;}
const sf=x=>0.5*erfc(x/Math.SQRT2);exports.sf=sf;
exports.spend=(name,tot,t)=>{t=Math.min(t,1);if(name==='OF')return 2*sf(exports.v5.normInv(1-tot/2)/Math.sqrt(t));if(name==='HSD')return tot*(1-Math.exp(2*t))/(1-Math.exp(2));return tot*t*t*t;};
/* intégration indépendante (trapèzes, pas 0.005) : proba cumulée de franchir eff à chaque lecture ; useFut : arrêt futilité */
exports.exact=(info,mean,eff,fut,useFut)=>{const h=0.004,lo=-9,n=Math.round(18/h)+1,C=1/Math.sqrt(2*Math.PI);let g=null,cum=0,out=[],futc=0;
  const xs=new Float64Array(n);for(let i=0;i<n;i++)xs[i]=lo+i*h;
  for(let j=0;j<info.length;j++){if(eff[j]==null){out.push(cum);continue;}
    let d=new Float64Array(n);
    if(j===0){for(let i=0;i<n;i++){const e=xs[i]-mean[0];d[i]=C*Math.exp(-0.5*e*e);}}
    else{const r=Math.sqrt(info[j-1]/info[j]),s=Math.sqrt(1-r*r),dd=mean[j]-r*mean[j-1];
      // conv: only where g>0
      let i0=0,i1=n-1;while(i0<n&&g[i0]===0)i0++;while(i1>=0&&g[i1]===0)i1--;
      for(let i=0;i<n;i++){let sum=0;const base=(xs[i]-dd)/s;for(let q=i0;q<=i1;q++){const v=base-r*xs[q]/s;if(v>-8.5&&v<8.5)sum+=g[q]*Math.exp(-0.5*v*v);}d[i]=sum*C/s*h;}}
    const u=eff[j],l=(useFut&&fut[j]!=null&&j<info.length)?fut[j]:-Infinity;
    // integrate tail above u, below l with partial-cell handling via linear interp
    let up=0,dn=0;for(let i=0;i<n-1;i++){const a=xs[i],b=xs[i+1];const f=(x)=>d[i]+(d[i+1]-d[i])*(x-a)/h;
      if(b>u){const s0=Math.max(a,u);up+=(f(s0)+d[i+1])/2*(b-s0);} if(a<l){const e0=Math.min(b,l);dn+=(d[i]+f(e0))/2*(e0-a);}
      }
    cum+=up;futc+=dn;out.push(cum);
    for(let i=0;i<n;i++){if(xs[i]>=u||xs[i]<=l)d[i]=0;}
    // boundary cells: keep approximate (error O(h*density)) -> refine by weighting edge nodes
    g=d;}
  return {cum:out,fut:futc};};

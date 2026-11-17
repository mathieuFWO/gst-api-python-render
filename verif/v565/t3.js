const {v5,spend,exact,sf}=require('./lib.js');const GS=v5.GS;
const NS=+process.argv[2]||400000;
function rng(seed){let a=seed>>>0;return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const scen={4:[[1,2,3,4],[1,3,4],[3,4],[2,4],[1,4]],6:[[1,2,3,4,5,6],[1,2,6],[4,6],[2,3,5,6]]};
const f=(x,d=3)=>x==null?'—':x.toFixed(d);
for(const sfu of ['KimDeMets','OF'])for(const tt of [3,1])for(const K of [4,6]){
  const base={k:K,alpha:0.05,beta:0.2,power:0.8,testType:tt,sfu,sfl:'HSD',unit:'semaine'};
  const d0=GS.design(base);const th=tt===3?d0.th:(v5.normInv(0.95)+v5.normInv(0.8))*Math.sqrt(d0.IF);
  const S=scen[K].map(w=>{const p=w.length===K?base:Object.assign({},base,{k:w.length,_t:w.map(x=>x/K)});const info=w.map(x=>x*1000),frac=w.map(x=>x/K);
    const b=GS.actual(p,info,frac);return {w,b,p,c:{fpNB:0,fpB:0,pw:0,pwNB:0,cum:w.map(()=>0)}};});
  const r=rng(777+K+tt*7+(sfu==='OF'?99:0));const Z=new Float64Array(K);
  for(let n=0;n<NS;n++){let s=0;for(let w=0;w<K;w+=2){const u1=r()||1e-12,u2=r(),m=Math.sqrt(-2*Math.log(u1));const g=[m*Math.cos(2*Math.PI*u2),m*Math.sin(2*Math.PI*u2)];for(let q=0;q<2&&w+q<K;q++){s+=g[q];Z[w+q]=s/Math.sqrt(w+q+1);}}
    for(const sc of S){const {w,b,c}=sc;let nb=0,bd=-1;
      // H0
      let alive=true;for(let j=0;j<w.length;j++){if(b.eff[j]==null)break;const z=Z[w[j]-1];if(z>=b.eff[j]){if(!nb)nb=1;if(alive){c.fpB++;for(let q=j;q<w.length;q++)c.cum[q]++;alive=false;}}else if(alive&&b.fut[j]!=null&&z<=b.fut[j])alive=false;if(nb&&!alive)break;}
      c.fpNB+=nb;
      alive=true;nb=0;for(let j=0;j<w.length;j++){if(b.eff[j]==null)break;const z=Z[w[j]-1]+th*Math.sqrt(w[j]/K);if(z>=b.eff[j]){nb=1;if(alive){c.pw++;alive=false;}}else if(alive&&b.fut[j]!=null&&z<=b.fut[j])alive=false;if(nb&&!alive)break;}
      c.pwNB+=nb;}}
  console.log(`\n== sfu=${sfu} testType=${tt} K=${K} th=${th.toFixed(4)} IF=${d0.IF.toFixed(4)} N=${NS}`);
  for(const sc of S){const {w,b,p,c}=sc;const info=w.map(x=>x),m0=w.map(()=>0),m1=w.map(x=>th*Math.sqrt(x/K));
    const eB=exact(info,m0,b.eff,b.fut,true),eN=exact(info,m0,b.eff,b.fut,false),eP=exact(info,m1,b.eff,b.fut,true);
    const tgt=w.map((x,j)=>j===w.length-1?0.05:spend(sfu,0.05,x/K));
    const se=x=>Math.sqrt(x*(1-x)/NS);
    console.log(`S{${w}} eff=[${b.eff.map(x=>f(x)).join(' ')}] fut=[${b.fut.map(x=>f(x)).join(' ')}] end=${b.end} thUsed=${f(b.th,4)} IFret=${f(b.IF,4)}`);
    console.log(`   alpha cum cible=[${tgt.map(x=>x.toFixed(5)).join(' ')}] exact=[${eB.cum.map(x=>x.toFixed(5)).join(' ')}] MC=[${c.cum.map(x=>(x/NS).toFixed(5)).join(' ')}]`);
    console.log(`   FPR fut.appliquee: exact ${eB.cum[w.length-1].toFixed(5)} MC ${(c.fpB/NS).toFixed(5)}±${se(c.fpB/NS).toFixed(5)} | fut.ignoree: exact ${eN.cum[w.length-1].toFixed(5)} MC ${(c.fpNB/NS).toFixed(5)}±${se(c.fpNB/NS).toFixed(5)} | puissance: exact ${eP.cum[w.length-1].toFixed(4)} MC ${(c.pw/NS).toFixed(4)}±${se(c.pw/NS).toFixed(4)} (fut ignoree MC ${(c.pwNB/NS).toFixed(4)}) | beta exact ${eP.fut.toFixed(4)}`);}
}

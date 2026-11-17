const {v4,v5}=require('./lib.js');
const plans=[];for(const k of [2,3,4,5,6,8,12])for(const sfu of ['KimDeMets','OF'])for(const tt of [1,3])for(const sfl of ['HSD','KimDeMets','OF'])for(const unit of ['semaine','jour'])for(const al of [0.05,0.025]){if(tt===1&&sfl!=='HSD')continue;plans.push({k,alpha:al,beta:0.2,power:0.8,testType:tt,sfu,sfl,unit});}
plans.push({k:14,alpha:0.05,beta:0.1,power:0.9,testType:3,sfu:'KimDeMets',sfl:'HSD',unit:'jour'},{k:1,alpha:0.05,beta:0.2,power:.8,testType:3,sfu:'OF',sfl:'HSD'});
let md=0,n=0,bad=0,md2=0;const eq=(a,b)=>{let m=0;if(a.length!==b.length)return Infinity;for(let i=0;i<a.length;i++){if(a[i]==null||b[i]==null){if(a[i]!==b[i])return Infinity;continue;}m=Math.max(m,Math.abs(a[i]-b[i]));}return m;};
for(const p of plans){const infos=[null,Array.from({length:p.k},(_,i)=>(i+1)*1000),Array.from({length:p.k},(_,i)=>1000*(i+1)+300*Math.sin(i*2)+(i>1?700:0))];
 for(const info of infos){for(const frac of [null,info?info.map(v=>v/(p.k*1100)):null]){let a,b,e1=null,e2=null;
  try{a=info?v4.GS.actual(p,info,frac):v4.GS.design(p);}catch(e){e1=e.message;}try{b=info?v5.GS.actual(p,info,frac):v5.GS.design(p);}catch(e){e2=e.message;}
  n++;if(e1||e2){if(e1!==e2){bad++;console.log('ERR diff',JSON.stringify(p),e1,e2);}continue;}
  const d=Math.max(eq(a.eff,b.eff),eq(a.fut,b.fut),Math.abs((a.IF||0)-(b.IF||0)),(a.end!==b.end)?Infinity:0);md=Math.max(md,d);if(d>0){bad++;console.log('DIFF',d,JSON.stringify(p));}
  // point 2 : _t = i/k
  const pt=Object.assign({},p,{_t:Array.from({length:p.k},(_,i)=>(i+1)/p.k)});let c;try{c=info?v5.GS.actual(pt,info,frac):v5.GS.design(pt);}catch(e){console.log('ERR _t',e.message);continue;}
  const d2=Math.max(eq(b.eff,c.eff),eq(b.fut,c.fut),Math.abs((b.IF||0)-(c.IF||0)));md2=Math.max(md2,d2);if(d2>1e-12)console.log('P2 DIFF',d2,JSON.stringify(p),!!info);
 }}}
console.log('plans',plans.length,'comparaisons',n,'ecart max v4/v5',md,'nb differents',bad,'| point2 ecart max',md2);

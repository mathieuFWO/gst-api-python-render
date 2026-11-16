/* ---------- bornes séquentielles calculées dans le navigateur (remplace l'API gsDesign) ----------
   Dépense d'erreur de Lan-DeMets, intégration numérique par récurrence (Armitage-McPherson-Rowe) sur noeuds de Gauss-Legendre.
   testType 1 : efficacité seule. testType 3 : efficacité + futilité contraignante (dépense de beta), dérive ajustée pour que les deux bornes se rejoignent à la fin. */
var GS=(function(){
  var NG=100,GX=[],GW=[];
  (function(){for(var i=0;i<NG;i++){var x=Math.cos(Math.PI*(i+0.75)/(NG+0.5)),pp,j,it;for(it=0;it<100;it++){var p1=1,p2=0;for(j=1;j<=NG;j++){var p3=p2;p2=p1;p1=((2*j-1)*x*p2-(j-1)*p3)/j;}pp=NG*(x*p1-p2)/(x*x-1);var dx=p1/pp;x-=dx;if(Math.abs(dx)<1e-15)break;}GX.push(x);GW.push(2/((1-x*x)*pp*pp));}})();
  function erfc(x){var z=Math.abs(x),t=1/(1+0.5*z),r=t*Math.exp(-z*z-1.26551223+t*(1.00002368+t*(0.37409196+t*(0.09678418+t*(-0.18628806+t*(0.27886807+t*(-1.13520398+t*(1.48851587+t*(-0.82215223+t*0.17087277)))))))));return x>=0?r:2-r;}
  function sf(x){return 0.5*erfc(x/Math.SQRT2);}
  function cdf(x){return 0.5*erfc(-x/Math.SQRT2);}
  var C=1/Math.sqrt(2*Math.PI);
  function qn(p){return normInv(p);}
  function root(f,lo,hi,tol){var flo=f(lo),fhi=f(hi);if(!(flo*fhi<=0))return NaN;if(flo===0)return lo;if(fhi===0)return hi;tol=tol||1e-9;
    for(var i=0;i<80;i++){var m=(lo*fhi-hi*flo)/(fhi-flo);if(!(m>Math.min(lo,hi)&&m<Math.max(lo,hi)))m=(lo+hi)/2;var fm=f(m);if(fm===0)return m;
      if(fm*fhi<0){lo=hi;flo=fhi;}else{flo*=0.5;}hi=m;fhi=fm;if(Math.abs(hi-lo)<tol)break;}
    return Math.abs(flo)<Math.abs(fhi)?lo:hi;}
  function Path(t,theta){this.t=t;this.th=theta;this.i=0;this.x=null;this.g=null;}
  Path.prototype.tail=function(z,up){
    var t=this.t,i=this.i;if(i===0){var m=this.th*Math.sqrt(t[0]);return up?sf(z-m):cdf(z-m);}
    var a=Math.sqrt(t[i-1]/t[i]),s=Math.sqrt(1-t[i-1]/t[i]),d=this.th*(t[i]-t[i-1])/Math.sqrt(t[i]),x=this.x,g=this.g,sum=0;
    for(var j=0;j<x.length;j++){var v=(z-a*x[j]-d)/s;sum+=g[j]*(up?sf(v):cdf(v));}return sum;};
  Path.prototype.advance=function(l,u){
    var t=this.t,i=this.i,m=this.th*Math.sqrt(t[i]),lo=Math.min(-9,m-9),hi=Math.max(9,m+9);if(isFinite(l))lo=Math.max(l,lo);if(isFinite(u))hi=Math.min(u,hi);if(hi<=lo)hi=lo+1e-9;
    var nx=new Float64Array(NG),ng=new Float64Array(NG),h=0.5*(hi-lo),c=0.5*(hi+lo),j,q;
    if(i===0){for(j=0;j<NG;j++){nx[j]=h*GX[j]+c;var e=nx[j]-m;ng[j]=C*Math.exp(-0.5*e*e)*h*GW[j];}}
    else{var a=Math.sqrt(t[i-1]/t[i]),s=Math.sqrt(1-t[i-1]/t[i]),d=this.th*(t[i]-t[i-1])/Math.sqrt(t[i]),x=this.x,g=this.g;
      for(j=0;j<NG;j++){nx[j]=h*GX[j]+c;var sum=0;for(q=0;q<NG;q++){var v=(nx[j]-a*x[q]-d)/s;sum+=g[q]*Math.exp(-0.5*v*v);}ng[j]=sum*C/s*h*GW[j];}}
    this.x=nx;this.g=ng;this.i++;};
  function spend(name,tot,t,par){
    if(name==='OF')return 2*sf(qn(1-tot/2)/Math.sqrt(t));
    if(name==='HSD'){var gm=par==null?-2:par;return gm===0?tot*t:tot*(1-Math.exp(-gm*t))/(1-Math.exp(-gm));}
    if(name==='Pocock')return tot*Math.log(1+(Math.E-1)*t);
    return tot*Math.pow(t,par==null?3:par);}
  function incs(name,tot,t,par){var o=[],prev=0;for(var i=0;i<t.length;i++){var c=i===t.length-1?tot:spend(name,tot,t[i],par);o.push(Math.max(c-prev,0));prev=c;}return o;}
  function type1(t,ia){var P=new Path(t,0),u=[];for(var i=0;i<t.length;i++){var ui=ia[i]>0?root(function(z){return P.tail(z,true)-ia[i];},-3,14):14;u.push(ui);if(i<t.length-1)P.advance(-Infinity,ui);}return u;}
  function type3(t,ia,ib,theta){var k=t.length,P0=new Path(t,0),P1=new Path(t,theta),u=[],l=[];
    for(var i=0;i<k;i++){var ui=root(function(z){return P0.tail(z,true)-ia[i];},-40,14);if(!isFinite(ui))ui=-40;
      var li=root(function(z){return P1.tail(z,false)-ib[i];},-40,40);if(!isFinite(li))li=P1.tail(40,false)<ib[i]?40:-40;
      if(i<k-1)li=Math.min(li,ui-1e-6);u.push(ui);l.push(li);if(i<k-1){P0.advance(li,ui);P1.advance(li,ui);}}
    return {u:u,l:l};}
  function design(p){
    var k=p.k,a=p.alpha,b=p.beta,i,t=p.timing||null;if(!t){t=[];for(i=1;i<=k;i++)t.push(i/k);}
    if(k===1){var z=qn(1-a);return {eff:[z],fut:[p.testType===1?null:z],IF:1};}
    var ia=incs(p.sfu,a,t,null);
    if(p.testType===1){var u1=type1(t,ia),z0=qn(1-a)+qn(1-b);
      /* inflation : dérive telle que la puissance vaut 1-beta */
      var pw=function(th){var P=new Path(t,th),s=0;for(var j=0;j<k;j++){s+=P.tail(u1[j],true);if(j<k-1)P.advance(-Infinity,u1[j]);}return s;};
      var th1=root(function(th){return pw(th)-(1-b);},0.8*z0,1.6*z0);
      return {eff:u1,fut:u1.map(function(){return null;}),IF:isFinite(th1)?Math.pow(th1/z0,2):NaN};}
    var ib=incs(p.sfl,b,t,p.sfl==='HSD'?-2:null),zz=qn(1-a)+qn(1-b),gap=function(th){var r=type3(t,ia,ib,th);return r.l[k-1]-r.u[k-1];};
    var th=root(gap,0.9*zz,1.6*zz);if(!isFinite(th))throw new Error('plan non calculable');
    var r=type3(t,ia,ib,th);r.l[k-1]=r.u[k-1];return {eff:r.u,fut:r.l,IF:Math.pow(th/zz,2)};}
  return {design:design};
})();

# v56-34 : pas d'arrêt pour futilité avant la semaine 2 (suivi quotidien : avant le jour 14). Le risque beta prévu pour ces lectures est reporté
# sur la première lecture où la futilité est permise, et le plan (dérive, bornes) est recalculé avec ce calendrier : alpha et puissance restent tenus.
# Les durées de l'onglet Plan sont préparées en tâche de fond après l'affichage des résultats.
s=open('repo/calculateur-sequentiel-v56-33.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(a[:80],s.count(a));s=s.replace(a,b)
# --- plan
rep("""  function skipOf(p){return p.unit==='jour'?Math.min(6,p.k-1):0;}""",
"""  function skipOf(p){return p.unit==='jour'?Math.min(6,p.k-1):0;}
  /* Futilité différée : aucune borne basse tant que la lecture n'est pas en semaine 2 (jour 14 en suivi quotidien) ; la dernière lecture garde toujours la sienne.
     noFut rend le masque des lecteurs sans futilité, carry reporte leur part de beta sur la première lecture qui en a une. */
  function noFut(p,t){var K=p._kd||(t.length+(p._off||0)),lim=p.unit==='jour'?13.5:1.5;return t.map(function(v,i){return i<t.length-1&&v*K<lim;});}
  function carry(ib,mask){var acc=0,o=[];for(var i=0;i<ib.length;i++){if(mask[i]){acc+=ib[i];o.push(0);}else{o.push(ib[i]+acc);acc=0;}}return o;}
  function unFut(r,mask){for(var i=0;i<mask.length;i++)if(mask[i]&&r.l[i]!=null&&(r.end==null||i<r.end))r.l[i]=null;return r;}""")
rep("""    var ib=incs(p.sfl,b,t,p.sfl==='HSD'?-2:null),zz=qn(1-a)+qn(1-b),gap=function(th){var r=type3(t,ia,ib,drift(th,t));return r.l[k-1]-r.u[k-1];};
    var th=root(gap,0.9*zz,1.6*zz);if(!isFinite(th))throw new Error('plan non calculable');
    var r=type3(t,ia,ib,drift(th,t));r.l[k-1]=r.u[k-1];return {eff:r.u,fut:r.l,IF:Math.pow(th/zz,2),th:th};}""",
"""    var nfm=noFut(p,t),ib=carry(incs(p.sfl,b,t,p.sfl==='HSD'?-2:null),nfm),zz=qn(1-a)+qn(1-b),gap=function(th){var r=type3(t,ia,ib,drift(th,t));return r.l[k-1]-r.u[k-1];};
    var th=root(gap,0.9*zz,1.6*zz);if(!isFinite(th))throw new Error('plan non calculable');
    var r=type3(t,ia,ib,drift(th,t));r.l[k-1]=r.u[k-1];unFut(r,nfm);return {eff:r.u,fut:r.l,IF:Math.pow(th/zz,2),th:th};}""")
rep("""    var d=d0,ib=incs(p.sfl,p.beta,t,p.sfl==='HSD'?-2:null),r=type3(info,ia,ib,drift(d.th,frac&&frac.length===k?frac:t),p.alpha);
    if(r.end===null)r.l[k-1]=r.u[k-1];return""","""    var d=d0,nfm=noFut(p,t),ib=carry(incs(p.sfl,p.beta,t,p.sfl==='HSD'?-2:null),nfm),r=type3(info,ia,ib,drift(d.th,frac&&frac.length===k?frac:t),p.alpha);
    if(r.end===null)r.l[k-1]=r.u[k-1];unFut(r,nfm);return""")
rep("""'v44|'""","""'v45|'""",2)
# --- graphique : la ligne de futilité peut commencer à la deuxième lecture
rep("""  if(k>1&&hasFut&&small)s+='<path class="futz" d="'+pf+' L'+xr+' '+yb+' L'+xl+' '+yb+' Z" fill="#EEF0F0"/>';""",
"""  var f0=0;while(f0<k-1&&fut[f0]==null)f0++;
  if(k>1&&hasFut&&small)s+='<path class="futz" d="'+pf+' L'+xr+' '+yb+' L'+x(f0)+' '+yb+' Z" fill="#EEF0F0"/>';""")
rep("""  if(small&&k>1&&hasFut){var jf=Math.min(k-2,Math.floor(k*0.6)),yf=y(fut[jf])+15;if(yf<y(-eff[jf])-4)""","""  if(small&&k>1&&hasFut){var jf=Math.max(f0,Math.min(k-2,Math.floor(k*0.6))),yf=fut[jf]==null?1e9:y(fut[jf])+15;if(yf<y(-eff[jf])-4)""")
rep("""(hasFut?(function(){var j=Math.min(k-2,Math.floor(k*0.6));return '<text x=""","""(hasFut&&fut[Math.max(f0,Math.min(k-2,Math.floor(k*0.6)))]!=null?(function(){var j=Math.max(f0,Math.min(k-2,Math.floor(k*0.6)));return '<text x=""")
# --- textes
rep("""<span class="hint">Le test s\\'arrête s\\'il gagne, ou s\\'il n\\'a plus de chances de gagner.</span>""","""<span class="hint">Le test s\\'arrête s\\'il gagne, ou, à partir de la semaine 2, s\\'il n\\'a plus de chances de gagner.</span>""")
rep("""(skp.length?'<p class="hint">'+T('Sans lecture : '""","""(state.plan.testType===3&&dw==null&&cur<k-1&&state.bounds&&state.bounds.fut&&state.bounds.fut[cur]==null&&!(UJ&&WK(cur)<7)?'<p class="hint nofut">Pas d\\'arrêt pour futilité avant '+(UJ?'le jour 14':'la semaine 2')+' : d\\'ici là, seul un gain démontré arrête le test.</p>':'')
    +(skp.length?'<p class="hint">'+T('Sans lecture : '""")
# --- onglet Plan préparé en tâche de fond
rep("""function softRender(){""","""/* Les durées affichées par l'onglet Plan sont calculées pendant la lecture des résultats, une à la fois, quand le navigateur est disponible. */
var warmT=0;
function warmPlan(){
  if(!state.weeks.length||!state.metrics.length)return;var p=state.plan,wkey=planKey(p);if(ui.warmKey===wkey)return;ui.warmKey=wkey;clearTimeout(warmT);var ks=(p.unit==='jour'?[7,14,21,28,35,42,p.k]:[2,4,6,8,10,12,p.k]).filter(function(v,i,a){return v>=1&&v<=50&&a.indexOf(v)===i;}),st=state;
  var idle=function(f){if(window.requestIdleCallback)window.requestIdleCallback(f,{timeout:1500});else warmT=setTimeout(f,300);};
  var next=function(){if(state!==st||ui.busy||!ks.length)return;var w=ks.shift(),r=needIF(st.plan,w);if(typeof r==='number')return next();warmT=setTimeout(function(){idle(next);},250);};
  warmT=setTimeout(function(){idle(next);},600);
}
function softRender(){""")
rep("""  drawCharts();
  clearTimeout(NTM);""","""  drawCharts();if(ui.tab==='resultats'&&state.bounds&&!ui.busy&&!ui.ro)warmPlan();
  clearTimeout(NTM);""")
assert s.count('v56.33')==1
s=s.replace('v56.33','v56.34')
open('repo/calculateur-sequentiel-v56-34.html','w',newline='').write(s);print(len(s))

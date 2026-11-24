# v56-35 : p-value de chaque métrique dans l'infobulle, avec le seuil à franchir à cette lecture et en fin de test ;
# p-value de chaque valeur d'une segmentation (colonne de droite et infobulle), signalée comme non corrigée.
s=open('repo/calculateur-sequentiel-v56-34.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(a[:80],s.count(a));s=s.replace(a,b)
rep("""function tipHTML(r,wk){""",
"""/* p-value unilatérale, dans le sens de l'écart observé : probabilité d'un écart au moins aussi marqué s'il n'y avait aucun effet. Elle se compare au seuil de la lecture, pas à 0,05. */
function sfN(x){var z=Math.abs(x)/Math.SQRT2,t=1/(1+0.5*z),e=t*Math.exp(-z*z-1.26551223+t*(1.00002368+t*(0.37409196+t*(0.09678418+t*(-0.18628806+t*(0.27886807+t*(-1.13520398+t*(1.48851587+t*(-0.82215223+t*0.17087277)))))))));return x>=0?e/2:1-e/2;}
function pOf(st){return st&&st.zAdj!=null&&isFinite(st.zAdj)?sfN(Math.abs(st.zAdj)):null;}
function fmtP(p){return p==null||!isFinite(p)?'—':p<0.001?'< 0,001':nf(p,p<0.1?3:2);}
function fmtT(p){return p==null||!isFinite(p)?'—':p<0.0001?'moins de 0,0001':nf(p,p<0.01?4:3);}
function pLine(r,seg){
  var m=r.metric,st=r.st,p=pOf(st);if(p==null)return '';
  var k=KL(),ef=effFor(m.role,k-1),h='<div class="tpv"><b>p-value '+fmtP(p)+'</b><span>écart '+(st.zAdj>=0?'favorable':'défavorable')+'</span></div>';
  if(seg)return h+'<div class="hint">Non corrigée pour le nombre de valeurs comparées : à lire comme un indice, pas comme une preuve.'+(isFinite(r.eff)?' Repère : la métrique entière doit passer sous '+fmtT(sfN(r.eff))+' à cette lecture.':'')+'</div>';
  if(isFinite(r.eff))h+='<div class="hint num">Seuil à franchir à cette lecture : '+fmtT(sfN(r.eff))+(isFinite(ef)&&Math.abs(ef-r.eff)>1e-9?' · en fin de test : '+fmtT(sfN(ef)):'')+'</div>';
  if(m.role==='garde-fou'&&st.zNi!=null&&isFinite(r.effNi))h+='<div class="hint num">Non-régression : p-value '+fmtP(sfN(st.zNi))+' · seuil '+fmtT(sfN(r.effNi))+'</div>';
  return h;
}
function tipHTML(r,wk,seg){""")
rep("""  return '<div class="tt"><b>'+esc(m.name)+'</b><span class="pill '+S[1]+'">'+S[0]+'</span></div>'
    +'<div class="td num"><b>'+pct(st.lift)+'</b>'+(st.lo!=null?' · intervalle à '+lvl(m.role)+' % : de '+pct(st.lo)+' à '+pct(st.hi):'')+'</div>'""",
"""  return '<div class="tt"><b>'+esc(seg||m.name)+'</b>'+(seg?'<span class="pill nc">Exploratoire</span>':'<span class="pill '+S[1]+'">'+S[0]+'</span>')+'</div>'
    +'<div class="td num"><b>'+pct(st.lift)+'</b>'+(st.lo!=null?' · intervalle à '+lvl(m.role)+' % : de '+pct(st.lo)+' à '+pct(st.hi):'')+'</div>'+pLine(r,seg)""")
rep("""    +'<div class="hint num">Z '+(st.zAdj!=null?nf(st.zAdj,2):'—')+' · borne '+nf(r.eff,2)+(m.role==='garde-fou'?""","""    +(seg?'':'<div class="hint num">Z '+(st.zAdj!=null?nf(st.zAdj,2):'—')+' · borne '+nf(r.eff,2)+(m.role==='garde-fou'?""")
rep("""+(m.sens==='baisse'?' · baisse favorable':'')+'</div>'
    +(m.role==='garde-fou'&&nRole('garde-fou')>1?""","""+(m.sens==='baisse'?' · baisse favorable':'')+'</div>')
    +(!seg&&m.role==='garde-fou'&&nRole('garde-fou')>1?""")
# lignes de segmentation : p-value à droite, infobulle
rep("""<span class="mob num">'+fv(st&&st.mA)+' → '+fv(st&&st.mB)+(tags.length?' · ':'')+'</span>'+tags.join(' · ')""","""<span class="mob num">'+fv(st&&st.mA)+' → '+fv(st&&st.mB)+(pOf(st)!=null?' · p '+fmtP(pOf(st)):'')+(tags.length?' · ':'')+'</span>'+tags.join(' · ')""")
rep("""#gst-app .mrw.sub .c-lift{grid-column:1/-1}""","""#gst-app .mrw.sub .c-lift{grid-column:1/3}#gst-app .mrw.sub .c-st{align-self:center}""")
rep("""<div class="c-ci">'+ciBar(st,ax,'')+'</div><div class="c-st"></div></div>';});""","""<div class="c-ci">'+ciBar(st,ax,'')+'</div><div class="c-st">'+(pOf(st)!=null?'<span class="pvs num">p '+fmtP(pOf(st))+'</span>':'')+'</div>'+(st?'<div class="tip" role="tooltip">'+tipHTML({metric:m,st:st,status:'NA',eff:r.eff,effNi:NaN},{A:x.A,B:x.B},x.l)+'</div>':'')+'</div>';});""")
rep("""  return h+'<p class="hint sgs-n">Intervalles à '+lvl(m.role)+' %, non corrigés pour le nombre de valeurs comparées.</p></div>';""","""  return h+'<p class="hint sgs-n">Intervalles à '+lvl(m.role)+' % et p-values non corrigés pour le nombre de valeurs comparées.</p></div>';""")
rep("""#gst-app .tt{display:flex;""","""#gst-app .tpv{display:flex;align-items:baseline;gap:8px;margin-top:8px;padding-top:8px;border-top:1px solid var(--line);font-size:14px}#gst-app .tpv span{font-size:12.5px;color:#6F7374}#gst-app .tpv+.hint{margin-top:2px}#gst-app .pvs{font-size:12.5px;color:#6F7374;white-space:nowrap}
#gst-app .tt{display:flex;""")
assert s.count('v56.34')==1
s=s.replace('v56.34','v56.35')
open('repo/calculateur-sequentiel-v56-35.html','w',newline='').write(s);print(len(s))

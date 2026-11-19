s=open('repo/calculateur-sequentiel-v56-19.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:70],s.count(a));s=s.replace(a,b)
PRE=r"""  var pA=tot>0?wk.A.n/tot*100:50,UQ=U(),ptw=state.plan.traffic>0?state.plan.traffic:0,pmQ=state.metrics.filter(function(m){return m.role==='principale';})[0],binQ=!!pmQ&&pmQ.type!=='continue';
  /* Périodes comparées : chaque lecture en suivi hebdomadaire, chaque semaine complète en suivi quotidien. */
  var per=[],pv=null;for(i=0;i<=cur;i++){if(UQ&&WK(i)%7!==0)continue;var w0=state.weeks[i],wp=pv!=null?state.weeks[pv]:null,o={lab:'S'+(UQ?WK(i)/7:WK(i)),span:((WK(i)-(pv!=null?WK(pv):0))/(UQ?7:1)),nA:w0.A.n-(wp?wp.A.n:0),nB:w0.B.n-(wp?wp.B.n:0)};
    if(binQ&&w0.A.m[pmQ.id]&&w0.B.m[pmQ.id]){o.cA=w0.A.m[pmQ.id].c-(wp&&wp.A.m[pmQ.id]?wp.A.m[pmQ.id].c:0);o.cB=w0.B.m[pmQ.id].c-(wp&&wp.B.m[pmQ.id]?wp.B.m[pmQ.id].c:0);}
    per.push(o);pv=i;}
  /* Trafic réel face au trafic prévu dans le plan : alerte sous 80 %. */
  var expQ=ptw*(UQ?WK(cur)/7:WK(cur)),rtQ=expQ>0?tot/expQ:null,lowQ=rtQ!=null&&rtQ<0.8,mdeTx='';
  if(lowQ&&binQ&&pr&&pr.st&&pr.st.mA>0&&pr.st.mA<1){var IFq=state.bounds&&state.bounds.IF>0?Math.sqrt(state.bounds.IF):1,m0=mdeAt(state.plan,{t:ptw,p:pr.st.mA},k,IFq),m1=mdeAt(state.plan,{t:ptw*rtQ,p:pr.st.mA},k,IFq);if(isFinite(m0)&&isFinite(m1))mdeTx=' À ce rythme, l\'effet détectable en '+k+(UQ?' jours':' semaines')+' passe d\'environ '+nf(m0*100,1)+' % à '+nf(m1*100,1)+' %.';}
  /* Période atypique : le taux de l'objectif d'une variation s'écarte des autres périodes de 3 écarts-types ou plus. */
  var zQ=null;if(binQ&&per.length>=3)['A','B'].forEach(function(sx){var Nn=0,Cc=0,okc=true;per.forEach(function(o){Nn+=o['n'+sx];if(typeof o['c'+sx]!=='number')okc=false;else Cc+=o['c'+sx];});if(!okc||!(Cc>0)||Cc>=Nn)return;
    per.forEach(function(o){var n1=o['n'+sx],c1=o['c'+sx],n2=Nn-n1,c2=Cc-c1;if(!(n1>0&&n2>0))return;var pp=Cc/Nn,se=Math.sqrt(pp*(1-pp)*(1/n1+1/n2)),z=se>0?(c1/n1-c2/n2)/se:0;o['z'+sx]=z;if(!zQ||Math.abs(z)>Math.abs(zQ.z))zQ={z:z,s:sx,lab:o.lab,r1:c1/n1,r2:c2/n2,o:o};});});
  var atyQ=!!zQ&&Math.abs(zQ.z)>=3,vName=function(sx){return sx==='A'?'du contrôle':'de la variante';},f2=function(v){return nf(v*100,2)+' %';};
  var nAl=(srm?1:0)+(lowQ||noinfo?1:0)+(irr||atyQ?1:0);
  var c2T=noinfo?'Volumes incohérents':lowQ?'Trafic sous le plan':rtQ!=null?'Trafic conforme au plan':'Trafic prévu non renseigné';
  var c2X=noinfo?'Un cumul de visiteurs est nul ou en baisse : les seuils sont calculés comme si chaque période apportait le même volume.':rtQ!=null?nf(tot)+' visiteurs sur '+nf(Math.round(expQ))+' prévus à fin '+(UQ?'J':'S')+WK(cur)+(lowQ?', soit '+nf(rtQ*100,0)+' %.'+mdeTx:'.'):'Indiquez le trafic prévu dans l\'onglet Plan pour comparer le trafic réel au plan.';
  var c3T=atyQ?'Semaine '+zQ.lab.slice(1)+' atypique':irr?'Trafic irrégulier':'Aucune semaine atypique détectée';
  var c3X=(atyQ?'Taux de l\'objectif '+vName(zQ.s)+' à '+nf(Math.abs(zQ.z),1)+' écarts-types des autres semaines ('+f2(zQ.r1)+' contre '+f2(zQ.r2)+'). Vérifiez qu\'aucun événement n\'a touché une seule variation.':'')
    +(irr?(atyQ?' ':'')+T('Les semaines n\'apportent pas le même volume (écart max '+nf(dev*100,0)+' points). Les seuils sont calculés sur le trafic réel de chaque semaine : le risque de faux positif est tenu.'+(late?(ptw>0?' Le trafic arrive tard : la futilité est réglée sur le trafic prévu, ce qui limite les arrêts à tort, mais la puissance reste inférieure à celle du plan.':' Le trafic arrive tard : la futilité peut arrêter à tort un test gagnant. Renseignez le trafic prévu dans l\'onglet Plan pour limiter ce risque.'):'')):'')
    +(!atyQ&&!irr?(binQ?(per.length>=3?'Volumes de visiteurs et taux de l\'objectif suivis.':'Volumes suivis. Le taux de l\'objectif est comparé à partir de 3 semaines.'):'Volumes de visiteurs suivis.'):'');
  var naI='<svg aria-hidden="true" width="20" height="20" viewBox="0 0 20 20"><circle cx="10" cy="10" r="10" fill="#E6EAEA"/><path d="M6 10h8" stroke="#5b5f60" stroke-width="2" stroke-linecap="round"/></svg>';
  var qdt='';if(ui.qd){var erfcQ=function(x){var z=Math.abs(x),t=1/(1+0.5*z),r=t*Math.exp(-z*z-1.26551223+t*(1.00002368+t*(0.37409196+t*(0.09678418+t*(-0.18628806+t*(0.27886807+t*(-1.13520398+t*(1.48851587+t*(-0.82215223+t*0.17087277)))))))));return x>=0?r:2-r;},pS=erfcQ(Math.sqrt(chi/2));
    qdt='<div class="tp-dt"><div class="tp-d1"><b>Répartition A/B</b><p class="hint num">Contrôle '+nf(wk.A.n)+' · Variante '+nf(wk.B.n)+', soit '+nf(Math.abs(wk.A.n-wk.B.n))+' visiteurs d\'écart. Test du khi-deux : p '+(pS<0.001?'< 0,001':'= '+nf(pS,pS<0.1?3:2))+'. Alerte sous p < 0,001.</p></div>'
      +'<div class="tp-d1"><b>Trafic réel face au plan</b><p class="hint">'+(ptw>0?'Plan : '+nf(ptw)+' visiteurs par semaine. Alerte si le cumul passe sous 80 % du plan.':'Aucun trafic prévu dans le plan : seuls les volumes réels sont affichés.')+'</p><table class="tp-tb"><thead><tr><th scope="col">Semaine</th><th scope="col">Visiteurs</th><th scope="col">Du plan</th></tr></thead><tbody>'+per.map(function(o){return '<tr><th scope="row">'+o.lab+'</th><td class="num">'+nf(o.nA+o.nB)+'</td><td class="num">'+(ptw>0&&o.span>0?nf((o.nA+o.nB)/(ptw*o.span)*100,0)+' %':'-')+'</td></tr>';}).join('')+'</tbody></table>'+(UQ?'<p class="hint">En suivi quotidien, les jours sont regroupés par semaine complète.</p>':'')+'</div>'
      +'<div class="tp-d1"><b>Taux de l\'objectif, semaine par semaine</b>'+(binQ?'<p class="hint">Chaque semaine est comparée aux autres, par variation. Alerte à partir de 3 écarts-types.</p><table class="tp-tb"><thead><tr><th scope="col">Semaine</th><th scope="col">Contrôle</th><th scope="col">Variante</th></tr></thead><tbody>'+per.map(function(o){var hi=zQ&&zQ.o===o;return '<tr><th scope="row">'+o.lab+'</th><td class="num'+(hi&&zQ.s==='A'?' hi':'')+'">'+(o.nA>0&&typeof o.cA==='number'?f2(o.cA/o.nA):'-')+'</td><td class="num'+(hi&&zQ.s==='B'?' hi':'')+'">'+(o.nB>0&&typeof o.cB==='number'?f2(o.cB/o.nB):'-')+'</td></tr>';}).join('')+'</tbody></table>'+(zQ?'<p class="hint">Écart le plus fort : taux '+vName(zQ.s)+' en '+zQ.lab+', à '+nf(Math.abs(zQ.z),1)+' écarts-types des autres semaines. '+(atyQ?'Au-dessus du seuil d\'alerte.':'Sous le seuil d\'alerte.')+'</p>':'<p class="hint">Comparaison disponible à partir de 3 semaines.</p>'):'<p class="hint">Ce contrôle porte sur un objectif en taux. Pour un objectif continu, seuls les volumes sont suivis.</p>')+'</div></div>';}
"""
rep("  var nAl=(srm?1:0)+(irr||noinfo?1:0),pA=tot>0?wk.A.n/tot*100:50;"+NL,PRE.replace('\n',NL))
i=s.index("    +'<aside class=\"tp-q v-side\">");j=s.index("</aside></div>';",i)+len("</aside></div>';")
ASIDE=r"""    +'<aside class="tp-q v-side"><h4>Qualité des données</h4><p class="hint">'+(nAl?nAl+' alerte'+(nAl>1?'s':''):'Aucune alerte')+' sur les trois contrôles '+inW(WK(cur))+'</p>'
    +'<div class="tp-k chk">'+(srm?koI:okI)+'<div><b>'+(srm?'Répartition A/B déséquilibrée (SRM)':'Répartition A/B équilibrée (SRM)')+'</b><span class="hint num">Contrôle '+nf(pA,2)+' % · Variante '+nf(100-pA,2)+' %'+(srm?'. p < 0,001 : vérifiez le tracking.':'')+'</span></div></div>'
    +'<div class="tp-k chk">'+(lowQ||noinfo?koI:rtQ!=null?okI:naI)+'<div><b>'+c2T+'</b><span class="hint num">'+c2X+'</span></div></div>'
    +'<div class="tp-k chk">'+(irr||atyQ?koI:okI)+'<div><b>'+c3T+'</b><span class="hint num">'+c3X+'</span></div></div>'
    +'<p class="hint tp-pd">Du '+frDate(state.plan.startDate)+' au '+frDate((state.weeks[n-1]&&state.weeks[n-1].end)||addDays(state.plan.startDate,(U()?1:7)*wl-1))+' · '+nf(tot)+' visiteurs</p>'
    +'<div class="tp-t"><button type="button" class="link tp-l" data-act="qdetail" aria-expanded="'+!!ui.qd+'">'+(ui.qd?'Masquer':'Voir')+' le détail des contrôles <span class="tp-ch'+(ui.qd?' up':'')+'" aria-hidden="true"></span></button></div></aside>'+qdt+'</div>';"""
s=s[:i]+ASIDE.replace('\n',NL)+s[j:]
rep("else if(name==='legend'){ui.legend=!ui.legend;}","else if(name==='legend'){ui.legend=!ui.legend;}"+NL+"  else if(name==='qdetail'){ui.qd=!ui.qd;}")
rep("legend:false,detail:false,","legend:false,qd:false,detail:false,")
css="""#gst-app .tp .tp-pd{margin-top:16px;padding-top:14px;border-top:1px solid var(--line);font-size:13px}#gst-app .tp .tp-t{border-top:0;margin-top:2px;padding-top:0}#gst-app .tp-tb td.hi{font-weight:700;color:#7a5410}#gst-app .tp-w .tp-o b.num{white-space:nowrap}#gst-app .tp-w .tp-o>span:not(.hint):not(.tx){align-items:baseline}#gst-app .tp .tp-l,#gst-app .tp .tp-l:hover,#gst-app .tp .tp-l:focus{color:var(--ink);font-weight:600;font-size:15px;text-decoration:underline;text-decoration-color:#0E7C5D;text-underline-offset:5px;min-height:44px;padding:0;margin:0}
"""
rep("</style>",css.replace('\n',NL)+"</style>")
rep("v56.19","v56.20")
open('repo/calculateur-sequentiel-v56-20.html','w',newline='').write(s);print(len(s))

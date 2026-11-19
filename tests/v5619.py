import json
s=open('repo/calculateur-sequentiel-v56-18.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:70],s.count(a));s=s.replace(a,b)
# --- décisions : un type lisible par l'affichage
rep("return {cls:'continue',stop:false,title:'En attente',","return {kind:'wait',cls:'continue',stop:false,title:'En attente',")
rep("if(i<SK())return {cls:'continue',stop:false,title:'Continuer',","if(i<SK())return {kind:'wait',cls:'continue',stop:false,title:'Continuer',")
rep("return {cls:'critical',stop:true,title:'Arrêter : ne pas déployer',","return {kind:'reg',cls:'critical',stop:true,title:'Arrêter : ne pas déployer',")
rep("return {cls:'win',stop:true,title:'Arrêter : déploiement recommandé',","return {kind:'win',cls:'win',stop:true,title:'Arrêter : déploiement recommandé',")
rep("return {cls:'discuss',stop:true,title:'Arrêter : discussion requise',","return {kind:'discuss',noSec:noSec,cls:'discuss',stop:true,title:'Arrêter : discussion requise',")
rep("if(ps==='NEGATIF')return {cls:'stop',stop:true,","if(ps==='NEGATIF')return {kind:'neg',cls:'stop',stop:true,")
rep("if(ps==='FUTILE')return {cls:'stop',stop:true,","if(ps==='FUTILE')return {kind:'fut',cls:'stop',stop:true,")
rep("if(stage<k)return {cls:'continue',stop:false,title:'Continuer',","if(stage<k)return {kind:'cont',cls:'continue',stop:false,title:'Continuer',")
rep("return {cls:'stop',stop:true,title:'Arrêter : test terminé, non concluant',","return {kind:'end',cls:'stop',stop:true,title:'Arrêter : test terminé, non concluant',")
# --- haut de page des résultats
i=s.index("  var h='<div class=\"verdict\"><div class=\"v-main t-'+tone+'\">'+dico+");j=s.index("  h+='<div class=\"tools hx1\">'",i)
old=s[i:j]
assert "var wks=WKS(),wl=WKL(),skp=[],seg='';" in old
NEW=r"""  var wks=WKS(),wl=WKL(),skp=[],seg='';for(i=0;i<k;i++){var jr=wks.indexOf(i+1);if(jr<0&&i+1<wl)skp.push(i+1);seg+='<span class="'+(jr>=0?(dw!=null&&jr>dw?'post':'done'):(i+1<wl?'skip':'todo'))+(jr>=0&&jr===dw?' dec':'')+'"'+(dw==null&&jr===cur?' style="background:#0B5E48"':'')+'></span>';}
  var lab='';if(k<=12)for(i=0;i<k;i++)lab+='<span'+(i+1===WK(dw!=null?dw:cur)?' class="k"':'')+'>S'+(i+1)+'</span>';
  var UJ=U(),inW=function(x){return (UJ?'au jour ':'en semaine ')+x;},kd=d.kind||'',wd=WK(dw!=null?dw:cur),stw=' '+inW(wd)+' sur les '+k+(UJ?' prévus.':' prévues.');
  var H3=d.stop?'Arrêter le test':kd==='wait'?'En attente':'Continuer le test';
  var SUB={win:'Seuil d\'arrêt atteint'+stw,discuss:'Seuil d\'arrêt atteint'+stw,neg:'Seuil d\'arrêt atteint'+stw,fut:'Seuil de futilité atteint'+stw,reg:'Régression démontrée sur un garde-fou'+stw,end:'Durée prévue atteinte : '+k+(UJ?' jours':' semaines')+' sur '+k+'.',cont:'Aucun seuil atteint'+stw}[kd]||'';
  var BT={win:'Déploiement recommandé',discuss:'Déploiement à discuter',neg:'Ne pas déployer',reg:'Ne pas déployer',fut:'Test non concluant',end:'Test non concluant',cont:'Rien à décider pour le moment'}[kd]||d.title;
  var BN={win:'g',discuss:'a',neg:'c',reg:'c'}[kd]||'n',btx=Tq(d.text);
  if(kd==='discuss'&&d.noSec&&d.noSec.length){var mg=d.noSec.map(function(r){return r.metric.marge>0?r.metric.marge:1;}),same=mg.every(function(x){return x===mg[0];});btx='Les données ne permettent pas d\'écarter une dégradation'+(same?' de plus de '+nf(mg[0],mg[0]%1?1:0)+' % en relatif':'')+' pour '+names(d.noSec)+'.';}
  var bic='<svg aria-hidden="true" width="36" height="36" viewBox="0 0 36 36"><rect width="36" height="36" rx="9" fill="'+{a:'#F6DFAE',g:'#BFE6D8',c:'#F6CFC8',n:'#DDE3E6'}[BN]+'"/>'+(BN==='a'?'<path d="M10 11.5h16a1.5 1.5 0 0 1 1.5 1.5v8a1.5 1.5 0 0 1-1.5 1.5h-9l-4.5 3.5v-3.5H10a1.5 1.5 0 0 1-1.5-1.5v-8a1.5 1.5 0 0 1 1.5-1.5z" fill="none" stroke="#7a5410" stroke-width="1.7" stroke-linejoin="round"/><path d="M13 15.5h10M13 18.5h6" stroke="#7a5410" stroke-width="1.7" stroke-linecap="round"/>':BN==='g'?'<path d="M10.5 18.5l5 5 10-11" fill="none" stroke="#0B5E48" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>':BN==='c'?'<rect x="11.5" y="11.5" width="13" height="13" rx="2.5" fill="#8f2c20"/>':d.stop?'<path d="M11 16.5h14v3H11z" fill="#3d4a52"/>':'<path d="M14 11.5l11 6.5-11 6.5z" fill="#3d4a52"/>')+'</svg>';
  var gr=(dw!=null?comp.weeks[dw]:W).rows.filter(function(r){return r.metric.role==='garde-fou'&&r.st;}),brow='';
  if(gr.length)brow+='<div class="tp-o"><span class="hint">Écart'+(gr.length>1?'s':'')+' observé'+(gr.length>1?'s':'')+'</span>'+gr.map(function(r){return '<span>'+esc(r.metric.name)+' <b class="num">'+pct(r.st.lift)+'</b></span>';}).join('')+'</div>';
  if(dw!=null&&d.stop&&WK(dw)<k){var gain=null,gtx='',IF0=state.bounds&&state.bounds.IF,pl=function(v){return nf(v,v%1?1:0)+(UJ?' jour':' semaine')+(v>=2?'s':'');};
    if(kd==='win'||kd==='discuss'||kd==='neg'){if(IF0>0){gain=Math.round((k/IF0-WK(dw))*10)/10;if(gain>=0.5)gtx='Un arrêt '+inW(WK(dw))+' économise environ <b>'+pl(gain)+'</b> par rapport à un test à horizon fixe équivalent.';}}
    else if(kd==='fut')gtx='L\'arrêt '+inW(WK(dw))+' libère <b>'+pl(k-WK(dw))+'</b> de trafic pour un autre test.';
    else if(kd==='reg')gtx='L\'arrêt '+inW(WK(dw))+' évite <b>'+pl(k-WK(dw))+'</b> d\'exposition à la variante.';
    if(gtx)brow+='<div class="tp-o"><span class="hint">Temps gagné</span><span class="tx">'+gtx+'</span></div>';}
  var obj='';if(pr&&pr.st){var pc2=pr.metric.type==='continue',pf2=function(v){return pc2?nf(v,2):nf(v*100,2)+' %';},pt2=TONE[pr.status]||'';
    obj='<div class="tp-b"><div class="kicker">Objectif principal</div><div class="tp-n vname">'+esc(pr.metric.name)+'<span class="pill '+STATUS[pr.status][1]+'">'+STATUS[pr.status][0]+'</span></div><div class="tp-v vlift num'+(pt2==='g'?'':pt2==='c'?' ng':' nt')+'">'+pct(pr.st.lift)+'</div><div class="tp-c">'+(pr.status==='POSITIF'&&pr.st.lift>0?'Gain relatif observé':'Écart relatif observé')+'</div><p class="num">Contrôle '+pf2(pr.st.mA)+' · Variante '+pf2(pr.st.mB)+'</p></div>';}
  var okI='<svg aria-hidden="true" width="20" height="20" viewBox="0 0 20 20"><circle cx="10" cy="10" r="10" fill="#DDF3EC"/><path d="M5.8 10.3l2.8 2.8 5.6-6" fill="none" stroke="#0E7C5D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',koI='<svg aria-hidden="true" width="20" height="20" viewBox="0 0 20 20"><circle cx="10" cy="10" r="10" fill="#FBE8C6"/><path d="M10 5.5v5.5" stroke="#7a5410" stroke-width="2" stroke-linecap="round"/><circle cx="10" cy="14.2" r="1.2" fill="#7a5410"/></svg>';
  var nAl=(srm?1:0)+(irr||noinfo?1:0),pA=tot>0?wk.A.n/tot*100:50;
  var h='<div class="verdict tp" data-kind="'+kd+'" data-title="'+esc(d.title)+'"><div class="tp-m v-main"><div class="tp-g"><div class="tp-a"><div class="kicker">Décision du test</div><h3>'+H3+'</h3>'+(SUB?'<p>'+SUB+'</p>':'')
    +(k<=16?'<div class="segs" style="grid-template-columns:repeat('+k+',minmax(0,1fr));max-width:'+(45*k)+'px">'+seg+'</div>'+(lab?'<div class="seglab" style="grid-template-columns:repeat('+k+',minmax(0,1fr));max-width:'+(45*k)+'px">'+lab+'</div>':''):'<div class="bar"><i style="width:'+Math.min(100,wl/k*100)+'%"></i></div>')
    +(dw!=null&&n>dw+1?'<p class="hint">'+(n-dw-1>1?(UJ?'Jours ':'Semaines ')+WK(dw+1)+(n-dw-1>2?' à ':' et ')+wl+(UJ?' importés':' importées')+' après la décision':(UJ?'Jour '+wl+' importé':'Semaine '+wl+' importée')+' après la décision')+'</p>':'')
    +(skp.length?'<p class="hint">'+T('Sans lecture : '+skp.map(function(x){return 'S'+x;}).join(', ')+' (en pointillé).')+'</p>':'')
    +(dw!=null&&cur!==dw?'<p class="hint">'+T('Vous relisez la semaine '+WK(cur)+' : elle ne modifie pas la décision.')+'</p>':'')+'</div>'+obj+'</div>'
    +'<div class="tp-w '+BN+'">'+bic+'<div><b>'+esc(BT)+'</b><span>'+esc(btx)+'</span>'+brow+'</div></div>'+warnV+'</div>'
    +'<aside class="tp-q v-side"><h4>Qualité des données</h4><p class="hint">'+(nAl?nAl+' alerte'+(nAl>1?'s':''):'Aucune alerte')+' sur les deux contrôles '+inW(WK(cur))+'</p>'
    +'<div class="tp-k chk">'+(srm?koI:okI)+'<div><b>'+(srm?'Répartition A/B déséquilibrée (SRM)':'Répartition A/B équilibrée (SRM)')+'</b><span class="hint num">Contrôle '+nf(pA,2)+' % · Variante '+nf(100-pA,2)+' %'+(srm?'. p < 0,001 : vérifiez le tracking.':'')+'</span></div></div>'
    +'<div class="tp-k chk">'+(irr||noinfo?koI:okI)+'<div><b>'+(noinfo?'Volumes incohérents':irr?'Trafic irrégulier':'Trafic régulier')+'</b><span class="hint num">'+T(noinfo?'Un cumul de visiteurs est nul ou en baisse : les seuils sont calculés comme si chaque semaine apportait le même volume.':irr?'Les semaines n\'apportent pas le même volume (écart max '+nf(dev*100,0)+' points). Les seuils sont calculés sur le trafic réel de chaque semaine : le risque de faux positif est tenu.'+(late?(state.plan.traffic>0?' Le trafic arrive tard : la futilité est réglée sur le trafic prévu, ce qui limite les arrêts à tort, mais la puissance reste inférieure à celle du plan.':' Le trafic arrive tard : la futilité peut arrêter à tort un test gagnant. Renseignez le trafic prévu dans l\'onglet Plan pour limiter ce risque.'):''):nf(tot)+' visiteurs, volume stable d\'une semaine à l\'autre.')+'</span></div></div>'
    +'<div class="tp-t"><span>Du '+frDate(state.plan.startDate)+' au '+frDate((state.weeks[n-1]&&state.weeks[n-1].end)||addDays(state.plan.startDate,(U()?1:7)*wl-1))+'</span><b class="num">'+nf(tot)+' visiteurs</b></div></aside></div>';
"""
s=s[:i]+NEW.replace('\n',NL)+s[j:]
# lien « Comment lire les statuts » au-dessus des tableaux
rep("  h+='<div class=\"tools hx1\">'"+NL+"    +'<label class=\"hist\">","  h+='<div class=\"tools hx1\"><button type=\"button\" class=\"link lgd\" data-act=\"legend\" aria-expanded=\"'+!!ui.legend+'\">Comment lire les statuts</button>'"+NL+"    +'<label class=\"hist\">")
k0="</select></label></div>';"+NL+"  if(ui.legend)h=h.replace('<!--lg-->',"
assert s.count(k0)==1,s.count(k0);s=s.replace(k0,"</select></label></div><!--lg-->';"+NL+"  if(ui.legend)h=h.replace('<!--lg-->',")
ST=json.load(open('states.json'))['css']
css=ST[:ST.index('#gst-app .st-h{')]
css=css.replace('#gst-app .tp-s,#gst-app .tp-sl{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:6px;max-width:360px}','')
css+="""#gst-app .verdict.tp{overflow:visible;margin-top:14px;flex-wrap:nowrap}#gst-app .verdict.tp .v-main{display:block;padding:0;background:none;flex:none;min-width:0}#gst-app .verdict.tp .v-main h3{font-size:38px;margin:8px 0 10px}#gst-app .verdict.tp .v-main p{font-size:14.5px;max-width:none}#gst-app .verdict.tp .v-side{display:block;flex:none;border:1px solid var(--line);padding:22px;gap:0}
#gst-app .tp .segs{gap:6px;margin-top:16px}#gst-app .tp .seglab{gap:6px;margin:5px 0 10px;color:#6F7273}#gst-app .tp .segs span{height:8px;border-radius:4px}#gst-app .tp .segs .done{background:#A9D5C5}#gst-app .tp .segs .todo{background:#ECEFEE;border:0}#gst-app .tp .segs span.dec{background:#0B5E48}#gst-app .tp .segs span.post{background:repeating-linear-gradient(135deg,#C9CECE 0 3px,#ECEFEE 3px 6px)}#gst-app .tp .seglab .k{font-weight:700;color:var(--ink)}
#gst-app .tp-v.ng{color:#c9402f}#gst-app .tp .tp-k.chk{margin-top:16px;align-items:start}#gst-app .tp .tp-t{font-size:13px}#gst-app .tp .tp-t b{font-size:15px}#gst-app .tp .v-main p.vw{margin-top:14px;display:flex;gap:10px}#gst-app .tp-a>p.hint{margin-top:4px}
#gst-app .tools.hx1{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}#gst-app .tools.hx1 button.link.lgd,#gst-app .tools.hx1 button.link.lgd:hover,#gst-app .tools.hx1 button.link.lgd:focus{margin:0;min-height:44px;padding:4px 2px;font-size:13px;font-weight:400}#gst-app .legend.lgin{margin-bottom:14px}
@media (max-width:700px){#gst-app .verdict.tp .v-main h3{font-size:30px}#gst-app .verdict.tp .v-side{padding:16px}#gst-app .verdict.tp{flex-wrap:wrap}}
"""
assert '`' not in css
rep("</style>",css.replace('\n',NL)+"</style>")
rep("v56.18","v56.19")
open('repo/calculateur-sequentiel-v56-19.html','w',newline='').write(s);print(len(s))

src='repo/calculateur-sequentiel-v56-4.html';dst='repo/calculateur-sequentiel-v56-5.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:110]); s=s.replace(a,b)
rep("VERSION='v56.4'","VERSION='v56.5'")
# ================= numérotation par le calendrier =================
rep("function SK(){return U()?Math.min(6,state.plan.k-1):0;}","""function SK(){return U()?Math.min(6,state.plan.k-1):0;}
/* Numérotation par le calendrier. Chaque lecture porte le numéro de la semaine où elle tombe (wk) ; une semaine sans lecture est « sautée ».
   WKS : semaine de chaque lecture. KL : nombre de lectures du plan, semaines sautées déduites. PL : le plan vu par le calcul des bornes. LW : semaine d'une lecture, faite ou à venir. */
function WKS(){var a=[],p=0;state.weeks.forEach(function(w,i){var x=Math.max(i+1,p+1,w&&w.wk>0?Math.round(w.wk):0);a.push(x);p=x;});return a;}
function WK(i){var a=WKS();return i<a.length?a[i]:i+1;}
function WKL(){var a=WKS();return a.length?a[a.length-1]:0;}
function KL(){var n=state.weeks.length;return Math.max(n||1,state.plan.k-(WKL()-n));}
function PL(){var k=KL();return k===state.plan.k?state.plan:Object.assign({},state.plan,{k:k});}
function LW(j){var n=state.weeks.length;return j<n?WK(j):WKL()+(j-n+1);}""")
# bornes : autant de lectures que de semaines restantes + lectures faites
rep("""  var n=Math.min(state.weeks.length,state.plan.k),k=state.plan.k,N=[],i;if(!n||k<2)return null;
  for(i=0;i<n;i++)N.push(state.weeks[i].A.n+state.weeks[i].B.n);
  var rate=state.plan.traffic>0?perLook(state.plan.traffic):N[n-1]/n;for(i=n;i<k;i++)N.push(N[i-1]+rate);""".replace('\n','\r\n' if '\r\n' in s else '\n'),
"""  var k=KL(),n=Math.min(state.weeks.length,k),N=[],i;if(!n||k<2)return null;
  for(i=0;i<n;i++)N.push(state.weeks[i].A.n+state.weeks[i].B.n);
  var rate=state.plan.traffic>0?perLook(state.plan.traffic):N[n-1]/WKL();for(i=n;i<k;i++)N.push(N[i-1]+rate);""".replace('\n','\r\n' if '\r\n' in s else '\n'))
rep("  var p=state.plan,key=planKey(p),ng=nRole('garde-fou')","  var p=PL(),key=planKey(p),ng=nRole('garde-fou')")
# décision
rep("  var k=state.plan.k,stage=i+1,prim=rows.filter(","  var k=KL(),stage=i+1,prim=rows.filter(")
rep("'Le volume prévu a été atteint en semaine '+(state.bounds.end+1)+' :","'Le volume prévu a été atteint en semaine '+WK(state.bounds.end)+' :")
rep("text:'Analyse pour la semaine '+(stage+1)+' nécessaire.","text:'Analyse pour la semaine '+(WK(i)+1)+' nécessaire.")
rep("text:'Aucun résultat démontré après '+k+' semaines.'","text:'Aucun résultat démontré après '+state.plan.k+' semaines.'")
# résumé (liste des tests enregistrés)
rep("return {t:w.dec.title,c:w.dec.cls,n:n,k:state.plan.k,dw:dw,","return {t:w.dec.title,c:w.dec.cls,n:WKL(),k:state.plan.k,dw:dw!=null?WK(dw)-1:null,")
# graphique : lectures placées sur l'axe du calendrier
rep("  var k=state.plan.k,mi=state.metrics.indexOf(m),prim=m.role==='principale'","  var kc=state.plan.k,k=KL(),mi=state.metrics.indexOf(m),prim=m.role==='principale'")
rep("sl.se/Math.abs(sl.mA)*100*Math.sqrt((last+1)/(i+1)):NaN","sl.se/Math.abs(sl.mA)*100*Math.sqrt(LW(last)/LW(i)):NaN")
rep("  var x=function(j){return k===1?L+(W-L-R)/2:L+j*(W-L-R)/(k-1);},y=function","  var xc=function(c){return kc===1?L+(W-L-R)/2:L+c*(W-L-R)/(kc-1);},x=function(j){return xc(LW(j)-1);},y=function")
rep("var stp=Math.ceil(k/(small?6:12));for(i=0;i<k;i++)if((i%stp===0&&k-1-i>=stp*0.6)||i===k-1)s+='<text x=\"'+x(i)+'\" y=\"'+(H-10)+'\" text-anchor=\"middle\" font-size=\"11\" fill=\"#464849\"'+(i===cur?' font-weight=\"700\"':'')+'>S'+(i+1)+'</text>';",
    "var stp=Math.ceil(kc/(small?6:12)),cw=WK(cur)-1;for(i=0;i<kc;i++)if((i%stp===0&&kc-1-i>=stp*0.6)||i===kc-1)s+='<text x=\"'+xc(i)+'\" y=\"'+(H-10)+'\" text-anchor=\"middle\" font-size=\"11\" fill=\"#464849\"'+(i===cw?' font-weight=\"700\"':'')+'>S'+(i+1)+'</text>';")
# bloc de décision et progression
rep("'acquise en semaine '+(dw+1)+' sur '+k:'semaine '+(cur+1)+' sur '+k)","'acquise en semaine '+WK(dw)+' sur '+k:'semaine '+WK(cur)+' sur '+k)")
rep("Vous relisez la semaine '+(cur+1)+' :","Vous relisez la semaine '+WK(cur)+' :")
rep("  var seg='';for(i=0;i<k;i++)seg+='<span class=\"'+(i<n?(dw!=null&&i>dw?'post':'done'):'todo')+(i===dw?' dec':'')+'\"></span>';",
    "  var wks=WKS(),wl=WKL(),skp=[],seg='';for(i=0;i<k;i++){var jr=wks.indexOf(i+1);if(jr<0&&i+1<wl)skp.push(i+1);seg+='<span class=\"'+(jr>=0?(dw!=null&&jr>dw?'post':'done'):(i+1<wl?'skip':'todo'))+(jr>=0&&jr===dw?' dec':'')+'\"></span>';}")
rep("lab+='<span'+(i===dw?' style=\"font-weight:700;color:#1A1D1F\"':'')+'>S'+(i+1)+'</span>';","lab+='<span'+(dw!=null&&i+1===WK(dw)?' style=\"font-weight:700;color:#1A1D1F\"':'')+'>S'+(i+1)+'</span>';")
rep("<b class=\"big\">'+n+' semaine'+(n>1?'s':'')+' sur '+k+'</b></div>'","<b class=\"big\">'+(skp.length?'Semaine '+wl+' sur '+k:n+' semaine'+(n>1?'s':'')+' sur '+k)+'</b></div>'")
rep("'<div class=\"bar\"><i style=\"width:'+Math.min(100,n/k*100)+'%\"></i></div>')","'<div class=\"bar\"><i style=\"width:'+Math.min(100,wl/k*100)+'%\"></i></div>')")
rep("'<b style=\"color:#1A1D1F\">Résultat acquis depuis la semaine '+(dw+1)+'.</b> '+(n>dw+1?'Le test devait s\\'arrêter là : '+(n-dw-1>1?'les semaines '+(dw+2)+(n-dw-1>2?' à ':' et ')+n+' ont été importées':'la semaine '+n+' a été importée')",
    "'<b style=\"color:#1A1D1F\">Résultat acquis depuis la semaine '+WK(dw)+'.</b> '+(n>dw+1?'Le test devait s\\'arrêter là : '+(n-dw-1>1?'les semaines '+WK(dw+1)+(n-dw-1>2?' à ':' et ')+wl+' ont été importées':'la semaine '+wl+' a été importée')")
rep("'Semaines importées en vert.')+' Du '","'Semaines importées en vert.')+(skp.length?' Sans lecture : '+skp.map(function(x){return 'S'+x;}).join(', ')+' (en pointillé) ; le test se termine toujours en semaine '+k+'.':'')+' Du '")
rep("addDays(state.plan.startDate,(U()?1:7)*n-1))+'.</span>'","addDays(state.plan.startDate,(U()?1:7)*wl-1))+'.</span>'")
rep("'>Semaine '+(j+1)+(j===dw?' : décision':'')+'</option>'","'>Semaine '+WK(j)+(j===dw?' : décision':'')+'</option>'")
# données
rep("'Ajouter la semaine '+(state.weeks.length+1)+' ou remplacer les données'","'Ajouter la semaine '+(WKL()+1)+' ou remplacer les données'")
rep("<th>Semaine '+(state.weeks.length+1)+' (cumul)</th>","<th>Semaine '+(WKL()+1)+' (cumul)</th>")
rep("'<tr><td>'+(v==='A'?'S'+(i+1):'')+'</td>","'<tr><td>'+(v==='A'?'S'+WK(i):'')+'</td>")
rep("data-act=\"delweek\">Supprimer la semaine '+state.weeks.length+'</button>'","data-act=\"delweek\">Supprimer la semaine '+WKL()+'</button>'")
rep("confirm(T('Supprimer les données de la semaine '+state.weeks.length+' ?'))","confirm(T('Supprimer les données de la semaine '+WKL()+' ?'))")
rep("  if(state.weeks.length>=state.plan.k)errs.push('Durée prévue atteinte ('+state.plan.k+' semaines).');","  if(WKL()>=state.plan.k)errs.push('Durée prévue atteinte ('+state.plan.k+' semaines).');")
rep("*st.seNi/Math.abs(st.mA)*Math.sqrt(Math.min(1,n/k))*","*st.seNi/Math.abs(st.mA)*Math.sqrt(Math.min(1,WKL()/k))*")
# CSS de la semaine sans lecture
rep("#gst-app .tools.hx1{justify-content:flex-end}","#gst-app .tools.hx1{justify-content:flex-end}\n#gst-app .segs span.skip{background:#fff;border:1px dashed #9FA1A1}")
# ================= import : semaine calendaire, durée, garde-fous =================
rep("map(function(w){var r={A:arm(w.A),B:arm(w.B)};if(/^\\d{4}-\\d{2}-\\d{2}$/.test(w.end))r.end=w.end;return r;});","map(function(w){var r={A:arm(w.A),B:arm(w.B)},wk=Math.round(Number(w.wk));if(/^\\d{4}-\\d{2}-\\d{2}$/.test(w.end))r.end=w.end;if(wk>=1&&wk<=60)r.wk=wk;return r;});")
a=s.index("function weekGate(d){");b=s.index("function lockErr(d){",a)
b=s.rindex("/* Les lectures d'un test viennent toutes du même test",a,b)
nl='\r\n' if '\r\n' in s else '\n'
s=s[:a]+("""function weekGate(d){
  if(d.mode!=='instantane'||state.plan.unit==='jour')return null;
  var n=state.weeks.length,start=n?state.plan.startDate:d.startDate,kk=n?state.plan.k:d.k,E=d.endDate,days=dayDiff(start,E)+1,last=n?state.weeks[n-1]:null,fix=n?' Si la date de début du test ('+frDate(start)+') est fausse, corrigez-la dans l\\'onglet Plan.':' Si le test a commencé plus tôt, corrigez la date de début.';
  if(!(days===days))return {ok:false,msg:'Indiquez la date de début du test et la date jusqu\\'à laquelle vont les données.'};
  if(E>todayISO())return {ok:false,msg:'La date « Données jusqu\\'au » est dans le futur.'};
  if(E===todayISO())return {ok:false,msg:'La journée d\\'aujourd\\'hui n\\'est pas terminée : indiquez hier au plus tard, avec un export arrêté à hier.'};
  if(days<1)return {ok:false,msg:'Les données s\\'arrêtent avant le début du test ('+frDate(start)+').'+fix};
  var w=Math.floor(days/7),wl=WKL(),next=addDays(start,7*(wl+1)-1);if(last&&last.end&&addDays(last.end,7)>next)next=addDays(last.end,7);
  if(w<=wl||(last&&last.end&&dayDiff(last.end,E)<7))return {ok:false,msg:(n?'Pas de nouvelle semaine complète depuis la dernière lecture (semaine '+wl+(last.end?', données jusqu\\'au '+frDate(last.end):'')+').'+(last.end?' Prochaine lecture avec des données allant au moins jusqu\\'au '+frDate(next)+'.':''):'La première semaine du test n\\'est pas terminée : '+days+' jour'+(days>1?'s':'')+' de données. Prochaine lecture avec des données allant au moins jusqu\\'au '+frDate(next)+'.')+fix};
  if(w>kk)return {ok:false,msg:'Ces données couvrent '+w+' semaines complètes, plus que la durée prévue ('+kk+'). '+(n?'Arrêtez l\\'export au '+frDate(addDays(start,7*kk-1))+', fin de la semaine '+kk+'.':'Indiquez la durée réellement prévue, ou arrêtez l\\'export au '+frDate(addDays(start,7*kk-1))+'.')};
  return {ok:true,w:w,skip:w-wl-1,msg:days+' jours de données depuis le '+frDate(start)+' : lecture de la semaine '+w+' sur '+kk+'.'+(w-wl-1>0?' '+(w-wl-1>1?'Les semaines '+(wl+1)+' à '+(w-1)+' restent':'La semaine '+(wl+1)+' reste')+' sans lecture : le test se termine toujours en semaine '+kk+'.':'')};
}
""").replace('\n',nl)+s[b:]
rep("    if(W.A&&W.B){if(d.mode==='instantane'&&/^\\d{4}-\\d{2}-\\d{2}$/.test(d.endDate||''))W.end=d.endDate;weeks.push(W);}","    if(W.A&&W.B){if(d.mode==='instantane'&&/^\\d{4}-\\d{2}-\\d{2}$/.test(d.endDate||''))W.end=d.endDate;if(d.mode==='instantane'&&gate&&gate.ok&&gate.w)W.wk=gate.w;weeks.push(W);}")
rep("  if(all.length>d.k)errs.push('Le fichier contient '+all.length+' semaines pour une durée prévue de '+d.k+'.');","  if(d.mode==='serie'&&all.length>d.k)errs.push('Le fichier contient '+all.length+' semaines pour une durée prévue de '+d.k+'.');")
# durée par défaut au premier import : au moins 4 semaines, et au moins le nombre de semaines déjà écoulées
rep("d.startGuess=!(keep&&keep.startDate)&&!isoD(sd)&&d.mode==='instantane'&&!state.weeks.length;","d.startGuess=!(keep&&keep.startDate)&&!isoD(sd)&&d.mode==='instantane'&&!state.weeks.length;\n  if(!(keep&&keep.k)&&d.mode==='instantane'&&!state.weeks.length){var w0=Math.floor((dayDiff(d.startDate,d.endDate)+1)/7);d.k=Math.min(50,Math.max(4,w0>0?w0:0));}")
rep("'Instantané cumulé : ajouté comme <b>semaine '+(state.weeks.length+1)+'</b>.'))","'Instantané cumulé : ajouté comme <b>semaine '+(gate&&gate.ok&&gate.w?gate.w:WKL()+1)+'</b>.'))")
# dates au format américain reconnues quand il n'y a pas de doute
rep("(/^(\\d{2})\\/(\\d{2})\\/(\\d{4})/.test(x)?x.replace(/^(\\d{2})\\/(\\d{2})\\/(\\d{4}).*/,'$3-$2-$1'):'');};","(/^(\\d{2})\\/(\\d{2})\\/(\\d{4})/.test(x)?(+x.slice(3,5)>12&&+x.slice(0,2)<=12?x.replace(/^(\\d{2})\\/(\\d{2})\\/(\\d{4}).*/,'$3-$1-$2'):x.replace(/^(\\d{2})\\/(\\d{2})\\/(\\d{4}).*/,'$3-$2-$1')):'');};")
# ================= onglet Plan : date de début et durée cohérentes avec les lectures =================
rep("    if(p.k<state.weeks.length){ui.error='La durée ('+p.k+') est inférieure au nombre de semaines déjà saisies ('+state.weeks.length+').';return render();}",
"""    if(p.k<WKL()){ui.error='La durée ('+p.k+') est inférieure à la semaine déjà atteinte ('+WKL()+').';return render();}
    if(!/^\\d{4}-\\d{2}-\\d{2}$/.test(p.startDate||'')||p.startDate<'2000-01-01'||p.startDate>todayISO()){ui.error='Date de début invalide.';return render();}
    if(p.unit!=='jour'&&p.startDate!==state.plan.startDate&&state.weeks.some(function(x){return x.end;})){var nw=[],bad=false,pv=0;state.weeks.forEach(function(x,i){var c=x.end?Math.floor((dayDiff(p.startDate,x.end)+1)/7):Math.max(pv+1,x.wk||i+1);if(c<=pv||c<i+1||c>p.k)bad=true;nw.push(c);pv=c;});
      if(bad){ui.error='Cette date de début ne correspond pas aux lectures déjà importées (données jusqu\\'au '+state.weeks.filter(function(x){return x.end;}).map(function(x){return frDate(x.end);}).join(', ')+') : chacune doit tomber sur une semaine complète différente, dans la durée prévue.';return render();}
      state.weeks.forEach(function(x,i){x.wk=nw[i];});}""")
# le risque reste dépensé selon le calendrier : une lecture en semaine w dépense le risque prévu pour w/k, qu'il y ait eu ou non des semaines sautées
rep("var k=p.k,off=p._off||0,a=p.alpha,b=p.beta,i,t=[];for(i=1;i<=k;i++)t.push((i+off)/(k+off));tune(t);","var k=p.k,off=p._off||0,a=p.alpha,b=p.beta,i,t=[];for(i=1;i<=k;i++)t.push((i+off)/(k+off));if(p._t&&p._t.length===k)t=p._t.slice();tune(t);")
rep("    var k=p.k,off=p._off||0,t=[],i;for(i=1;i<=k;i++)t.push((i+off)/(k+off));\n    if(k===1||!info","    var k=p.k,off=p._off||0,t=[],i;for(i=1;i<=k;i++)t.push((i+off)/(k+off));if(p._t&&p._t.length===k)t=p._t.slice();\n    if(k===1||!info") if "(k+off));\n    if(k===1||!info" in s else rep("    var k=p.k,off=p._off||0,t=[],i;for(i=1;i<=k;i++)t.push((i+off)/(k+off));\r\n    if(k===1||!info","    var k=p.k,off=p._off||0,t=[],i;for(i=1;i<=k;i++)t.push((i+off)/(k+off));if(p._t&&p._t.length===k)t=p._t.slice();\r\n    if(k===1||!info")
rep("function planKey(p){return [p.k,p.alpha,p.beta,p.testType,p.sfu,p.sfl].join('|')+(p.unit==='jour'?'|jour7':'');}","function planKey(p){return [p.k,p.alpha,p.beta,p.testType,p.sfu,p.sfl].join('|')+(p.unit==='jour'?'|jour7':'')+(p._t?'|t'+p._t.join(','):'');}")
rep("function PL(){var k=KL();return k===state.plan.k?state.plan:Object.assign({},state.plan,{k:k});}","function PL(){var k=KL(),kd=state.plan.k,t=[],j;if(k===kd)return state.plan;for(j=0;j<k;j++)t.push(LW(j)/kd);return Object.assign({},state.plan,{k:k,_t:t});}")
# relecture indépendante v56.5 : D1 (temps borné à 1), D2 (mode jour : pas de calendrier de semaines), D4 (clé de cache)
assert s.count("if(p._t&&p._t.length===k)t=p._t.slice();")==2
s=s.replace("if(p._t&&p._t.length===k)t=p._t.slice();","if(p._t&&p._t.length===k)t=p._t.map(function(v){return Math.min(1,v);});")
rep("for(j=0;j<k;j++)t.push(LW(j)/kd);return","for(j=0;j<k;j++)t.push(Math.min(1,LW(j)/kd));return")
rep("var x=Math.max(i+1,p+1,w&&w.wk>0?Math.round(w.wk):0);a.push(x);p=x;","var x=Math.max(i+1,p+1,!U()&&w&&w.wk>0?Math.round(w.wk):0);a.push(x);p=x;")
rep("IF=ui.ifc[planKey(state.plan)],out=[];","IF=ui.ifc[planKey(PL())],out=[];")
open(dst,'w',newline='').write(s);print(len(s))

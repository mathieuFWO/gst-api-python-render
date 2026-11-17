src='repo/calculateur-sequentiel-v55-4.html';dst='repo/calculateur-sequentiel-v55-5.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
rep("VERSION='v55.4'","VERSION='v55.5'")
rep("man:{name:'',k:4,ms:[{name:'',role:'principale'},{name:'',role:'garde-fou'}]}","man:{step:1,name:'',k:4,startDate:todayISO(),ms:[{name:'',role:'principale'},{name:'',role:'garde-fou'}]},manFlow:false")
a=s.index("function manualForm(){");b=s.index("function viewHome(){",a)
NEW=r"""function manSteps(n){return '<ol class="wz-steps">'+['Votre test','Durée','Chiffres de la semaine 1'].map(function(t,i){var k=i+1;return '<li class="'+(k===n?'on':k<n?'done':'')+'"'+(k===n?' aria-current="step"':'')+'><span class="nb">'+(k<n?'✓':k)+'</span><span class="t">'+t+'</span></li>';}).join('')+'</ol>';}
function manualForm(){
  var m=ui.man,h='<div class="man wz">'+manSteps(m.step===2?2:1);
  if(m.step!==2){
    h+='<h3>Quel test suivez-vous ?</h3><p class="lead2">Donnez-lui un nom et dites ce que vous mesurez. Pas de fichier à préparer : vous taperez vos chiffres chaque semaine.</p>'
      +'<div class="wz-g"><div class="w2"><label for="gst-mn">Nom du test</label><input id="gst-mn" data-man="name" value="'+esc(m.name)+'" placeholder="ex. Nouvelle fiche produit"></div>'
      +m.ms.map(function(x,i){return '<div><label for="gst-mm'+i+'">'+(i===0?'Objectif principal':i===1?'Garde-fou (facultatif)':'Métrique '+(i+1)+' (facultatif)')+'</label><input id="gst-mm'+i+'" data-man="m'+i+'name" value="'+esc(x.name)+'" placeholder="'+(i?'ex. Visiteurs avec rebond':'ex. Visiteurs avec achat')+'">'
        +(i===0?'<p class="fh">La métrique qui décide si la variante gagne.</p>':i===1?'<p class="fh">Une métrique qui ne doit pas se dégrader.</p>':'<select data-man="m'+i+'role" aria-label="Rôle de la métrique '+(i+1)+'" style="margin-top:8px"><option value="garde-fou"'+(x.role==='garde-fou'?' selected':'')+'>Garde-fou</option><option value="secondaire"'+(x.role==='secondaire'?' selected':'')+'>Secondaire</option></select>')+'</div>';}).join('')+'</div>'
      +(m.ms.length<5?'<p style="margin-top:14px"><button type="button" class="link" data-act="manadd">Ajouter une métrique</button></p>':'')
      +'<p class="row wz-act"><button type="button" class="pri big" data-act="manstep" data-v="2">Continuer</button></p>';
  }else{
    var p=JSON.parse(JSON.stringify(state.plan));p.k=m.k;var base=mdeBase(),ks=[2,4,6,8,10,12],rows=ks.map(function(w){var f=base?needIF(p,w):null,v=base?mdeAt(p,base,w,typeof f==='number'?Math.sqrt(f):1):null;return {w:w,ok:typeof f==='number',v:v};}),mxv=base?Math.max.apply(null,rows.map(function(r){return r.v;})):1,cur=rows.filter(function(r){return r.w===m.k;})[0];
    h+='<h3>Combien de temps doit durer le test ?</h3><p class="lead2">La durée se fixe avant de regarder les résultats, et ne change plus ensuite. Plus le test est long, plus il détecte de petits effets.</p>'
      +'<div class="wz2"><div class="wz2-l"><div class="kicker">Votre trafic</div>'
      +'<div><label for="gst-mt">Trafic par semaine (A + B)</label><input id="gst-mt" inputmode="numeric" data-mde="traffic" value="'+esc(ui.mde.traffic)+'" placeholder="ex. 20 000"><p class="fh">Les visiteurs exposés au test, les deux variations réunies.</p></div>'
      +'<div><label for="gst-mc">Conversions par semaine</label><input id="gst-mc" inputmode="numeric" data-mde="conv" value="'+esc(ui.mde.conv)+'" placeholder="ex. 1 000"><p class="fh">Les visiteurs qui réalisent l\'objectif principal'+(m.ms[0].name.trim()?' (« '+esc(m.ms[0].name.trim())+' »)':'')+'.</p></div>'
      +'<div><label for="gst-msd">Date de début du test</label><input id="gst-msd" type="date" data-man="startDate" value="'+esc(m.startDate)+'"></div></div>'
      +'<div class="wz2-r"><div class="kicker" style="color:#0E7C5D">Choisissez la durée</div>'
      +'<div class="mdetab"><div class="mh"><span>Durée</span><span>Plus petit effet détectable</span></div>'+rows.map(function(r){return '<button type="button" class="mr2'+(r.w===m.k?' on':'')+'" data-act="mank" data-v="'+r.w+'" role="radio" aria-checked="'+(r.w===m.k)+'"><span class="rd"></span><span>'+r.w+' semaines</span><span class="b">'+(base?'<i style="width:'+Math.max(4,r.v/mxv*100)+'%"></i>':'')+'</span><b class="num">'+(base?(r.ok?'':'≈ ')+nf(r.v*100,2)+' %':'—')+'</b></button>';}).join('')+'</div>'
      +(base&&cur?'<p class="wz-say">En <b>'+m.k+' semaines</b>, le test démontre un effet à partir de <b>'+(cur.ok?'':'≈ ')+nf(cur.v*100,2)+' %</b> : un taux qui passe de '+nf(base.p*100,2)+' % à '+nf(base.p*(1+cur.v)*100,2)+' % ou plus. Il peut s\'arrêter avant si le résultat est net.</p>':'<p class="wz-say">Renseignez le trafic et les conversions pour voir ce que chaque durée permet de démontrer. Sans ces chiffres, choisissez simplement une durée : 4 semaines convient à la plupart des tests.</p>')
      +'</div></div>'
      +'<p class="row wz-act"><button type="button" class="pri big" data-act="manstart">Continuer</button><button type="button" class="big" data-act="manstep" data-v="1">Retour</button></p>';
  }
  return h+'</div>';
}
function manWeek1(){
  return '<div class="card wz">'+manSteps(3)+'<h3>Vos chiffres après la semaine 1</h3><p class="lead2">Saisissez les <b>cumuls depuis le premier jour du test</b>, en visiteurs ayant fait l\'action. Vous reviendrez chaque semaine ajouter la suivante.</p>'
    +'<div class="wz-tab"><table><thead><tr><th class="l">Semaine 1 (cumul)</th><th>'+esc(state.labels.A)+'</th><th>'+esc(state.labels.B)+'</th></tr></thead><tbody><tr><td class="l">Visiteurs</td><td><input inputmode="numeric" data-mw="A|n" aria-label="Visiteurs, '+esc(state.labels.A)+'"></td><td><input inputmode="numeric" data-mw="B|n" aria-label="Visiteurs, '+esc(state.labels.B)+'"></td></tr>'
    +state.metrics.map(function(x){return '<tr><td class="l">'+esc(x.name)+'</td><td><input inputmode="numeric" data-mw="A|'+x.id+'|c" aria-label="'+esc(x.name)+', '+esc(state.labels.A)+'"></td><td><input inputmode="numeric" data-mw="B|'+x.id+'|c" aria-label="'+esc(x.name)+', '+esc(state.labels.B)+'"></td></tr>';}).join('')
    +'</tbody></table></div><p class="row wz-act"><button type="button" class="pri big" data-act="addweek">Voir la décision</button><button type="button" class="big" data-act="manback">Retour</button></p></div>';
}
"""
s=s[:a]+NEW+s[b:]
# accueil : en saisie manuelle, l'assistant prend toute la largeur (plus de colonne d'exemple)
a=s.index("    +'<div class=\"imp-r\">'+(tab==='manuel'");b=s.index("      :'<div class=\"kicker\">2 · Déposez le fichier</div>",a)
tail_a=s.index(")+'</div>'\n",b) if '\r\n' not in s else s.index(")+'</div>'\r\n",b)
s=s[:a]+"    +(tab==='manuel'?'':'<div class=\"imp-r\">'+("+s[b+len("      :"):tail_a]+")+'</div>')"+s[tail_a+len(")+'</div>'"):]
# données : étape 3 de l'assistant tant que la semaine 1 n'est pas saisie
rep("  h+='<div class=\"card\"><div class=\"kicker\">Import</div><h3>'+(state.weeks.length?","  if(ui.manFlow&&ui.manual&&!state.weeks.length&&state.metrics.length)return manWeek1();\n  h+='<div class=\"card\"><div class=\"kicker\">Import</div><h3>'+(state.weeks.length?")
# actions
rep("  else if(name==='manstart'){var mm=ui.man,kk=parseInt(mm.k,10),","  else if(name==='manstep'){if(v==='2'&&!ui.man.ms[0].name.trim()){ui.error='Donnez un nom à l\\'objectif principal.';return render();}ui.man.step=+v;ui.error='';}\n  else if(name==='mank'){ui.man.k=+v;}\n  else if(name==='manback'){state=freshState();ui.manFlow=false;ui.manual=false;ui.error='';ui.notice='';ui.tab='resultats';ui.howto='manuel';ui.man.step=2;}\n  else if(name==='manstart'){var mm=ui.man,kk=parseInt(mm.k,10),")
rep("state.plan.k=kk;state.plan.beta=parseFloat((1-state.plan.power).toFixed(4));","state.plan.k=kk;state.plan.beta=parseFloat((1-state.plan.power).toFixed(4));var mtv=toNum(ui.mde.traffic);if(mtv>0)state.plan.traffic=mtv;if(/^\\d{4}-\\d{2}-\\d{2}$/.test(mm.startDate||''))state.plan.startDate=mm.startDate;ui.manFlow=true;")
rep("ui.notice='Test créé. Saisissez les chiffres cumulés de la semaine 1.';ui.tab='donnees';ui.manual=true;","ui.notice='';ui.tab='donnees';ui.manual=true;")
rep("then(function(){if(ui.tab==='plan')softRender();});}","then(function(){if(ui.tab==='plan'||(ui.howto==='manuel'&&ui.man.step===2))softRender();});}")
rep("state.weeks.push(W);ui.manual=false;","state.weeks.push(W);ui.manual=false;ui.manFlow=false;ui.man.step=1;")
CSS="""#gst-app .wz-steps{display:flex;gap:8px;margin:0 0 22px;padding:0;list-style:none}
#gst-app .wz-steps li{flex:1;display:flex;align-items:center;gap:10px;padding:10px 12px;border:1px solid var(--border);border-radius:8px;background:#fff;font-size:13px;font-weight:600;color:var(--charcoal);min-width:0;margin:0}
#gst-app .wz-steps li .nb{flex:none;width:24px;height:24px;border-radius:50%;display:grid;place-items:center;background:#fff;border:1px solid var(--border);font-size:12px}
#gst-app .wz-steps li.on{border-color:var(--green);background:var(--wash);color:var(--ink)}#gst-app .wz-steps li.on .nb{background:var(--green);border-color:var(--green);color:#fff}
#gst-app .wz-steps li.done .nb{background:var(--tg);border-color:var(--green);color:#0E7C5D}
#gst-app .card.wz{padding:22px 24px 24px}#gst-app .man.wz{margin-top:22px}
#gst-app .wz h3{font-size:20px}#gst-app .wz .lead2{color:var(--charcoal);margin:6px 0 18px;max-width:66ch}
#gst-app .wz-g{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}#gst-app .wz-g .w2{grid-column:1/-1}
#gst-app .wz label{margin:0 0 6px}#gst-app .wz input,#gst-app .wz select{height:42px;min-height:42px}
#gst-app .wz .fh{font-size:12px;color:var(--charcoal);margin:6px 0 0}
#gst-app .wz2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.15fr);gap:20px 32px;align-items:start}
#gst-app .wz2-l{display:flex;flex-direction:column;gap:16px}
#gst-app .wz2-r{background:var(--wash);border-radius:12px;padding:18px 20px;display:flex;flex-direction:column;gap:12px}
#gst-app .wz2-r .mh{display:flex;justify-content:space-between;gap:12px}
#gst-app .wz-say{margin:0;font-size:13px;line-height:1.5}
#gst-app .wz-act{margin-top:24px;padding-top:20px;border-top:1px solid var(--line);gap:12px}
#gst-app .wz-tab table{table-layout:fixed;width:100%}#gst-app .wz-tab th:first-child{width:36%}#gst-app .wz-tab th,#gst-app .wz-tab td{white-space:normal;padding-left:6px;padding-right:6px}#gst-app .wz-tab input{text-align:right;min-width:0}
@media (max-width:760px){
  #gst-app .card.wz{padding:16px}
  #gst-app .wz-steps li{flex:0 0 auto}#gst-app .wz-steps li .t{display:none}#gst-app .wz-steps li.on{flex:1}#gst-app .wz-steps li.on .t{display:inline}
  #gst-app .wz-g,#gst-app .wz2{grid-template-columns:minmax(0,1fr)}
  #gst-app .wz2-r{padding:14px}
  #gst-app .wz-act button{flex:1 1 100%}
}
"""
i=s.index("h1.gst-h1+#gst-app{");j=s.index("\n",i)+1
s=s[:j]+CSS+s[j:]
rep("    +'<div class=\"imp-3\"><div><div class=\"kicker\">3 · Lisez la décision</div>","    +(tab==='manuel'?'':'<div class=\"imp-3\"><div><div class=\"kicker\">3 · Lisez la décision</div>")
rep("<span>Arrêter</span></div></div></div>'","<span>Arrêter</span></div></div>')+'</div>'")
open(dst,'w',newline='').write(s);print(len(s))

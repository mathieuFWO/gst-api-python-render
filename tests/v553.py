import sys,re
src='repo/calculateur-sequentiel-v55-2.html';dst='repo/calculateur-sequentiel-v55-3.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
rep("VERSION='v55.2'","VERSION='v55.3'")
# 1. survol : la règle de base ne répète plus :hover/:focus (elle écrasait les classes au survol : police des boutons .big)
rep("#gst-app button,#gst-app button:hover,#gst-app button:focus{font-family:var(--fb);","#gst-app button{font-family:var(--fb);")
# 2. air au-dessus du titre
rep("h1.gst-h1{margin:0!important;padding:16px 16px 0!important;","h1.gst-h1{margin:0!important;padding:44px 16px 0!important;")
# 3. plus de cumul automatique
rep("""  if(d.cumulate&&d.mode==='serie'){for(var i=1;i<weeks.length;i++)['A','B'].forEach(function(v){var c=weeks[i][v],p=weeks[i-1][v];c.n+=p.n;inc.forEach(function(m){var x=c.m[m.id],y=p.m[m.id];if(m.type==='continue'){x.s+=y.s;x.ss+=y.ss;}else x.c+=y.c;});});}\n""","")
rep("var d={file:fileName,H:H,data:data,errors:[],cumulate:false};","var d={file:fileName,H:H,data:data,errors:[]};")
rep("if(f==='cumulate')d.cumulate=t.checked;else if(f==='name')","if(f==='name')")
rep("old=d.metrics,cum=d.cumulate;","old=d.metrics;")
rep("ui.draft=analyze(ui.rawTable,d.file,keep);ui.draft.cumulate=cum;","ui.draft=analyze(ui.rawTable,d.file,keep);")
rep("Les données doivent être cumulées depuis le début du test.');","Le fichier donne sans doute les chiffres de chaque semaine séparément : refaites l\\'export sur une seule période, du premier jour du test à la fin de la semaine.');")
# 4. lecture des visiteurs du brouillon + alerte « export non cumulé »
rep("function buildWeeks(d){","""function draftVis(d){
  if(d.cVar<0||d.cVis<0||!d.control||!d.variant)return null;
  var rowsT=d.data.filter(function(r){return d.cTest<0||(r[d.cTest]||'').trim()===d.test;}),wk=d.cWeek>=0?d.cWeek:d.cEnd,keys=d.mode==='serie'?d.keys:[null],out=[];
  for(var i=0;i<keys.length;i++){var o={};
    [['A',d.control],['B',d.variant]].forEach(function(p){var rs=rowsT.filter(function(r){return (r[d.cVar]||'').trim()===p[1]&&(keys[i]===null||(r[wk]||'').trim()===keys[i]);});o[p[0]]=rs.length===1?toNum(rs[0][d.cVis]):NaN;});
    if(!(o.A>0)||!(o.B>0))return null;out.push(o);}
  return out;
}
function notCumul(v){
  if(!v||v.length<2)return null;var K=v.length,t=v.map(function(o){return o.A+o.B;}),down=0;
  for(var i=1;i<K;i++)if(t[i]<t[i-1])down++;
  return (down||t[K-1]<t[0]*(K>2?2:1.25))?{first:t[0],last:t[K-1],k:K}:null;
}
function buildWeeks(d){""")
# 5. écran de vérification
a=s.index("    h+='<div class=\"card\"><div class=\"kicker\">Import · '+esc(d.file||'')")
b=s.index("    return h;}",a)
NEW=r"""    var vis=draftVis(d),nc=d.mode==='serie'?notCumul(vis):null,last=vis&&vis[vis.length-1],nInc=d.metrics.filter(function(m){return m.include;}).length;
    h+='<div class="card dv"><div class="kicker">Import · '+esc(d.file||'')+'</div><h3>Vérifiez la lecture du fichier</h3>'
      +'<p class="muted" style="margin-top:4px">'+(d.mode==='serie'?d.keys.length+' semaine(s) détectée(s) : le fichier <b>remplace</b> les données du test.':'Instantané cumulé : ajouté comme <b>semaine '+(state.weeks.length+1)+'</b>.')+'</p>'
      +(d.errors.length?'<div class="err" role="alert">'+d.errors.map(esc).join('<br>')+'</div>':'')
      +(nc?'<div class="dv-warn" role="alert"><b>Ce fichier ressemble à un export semaine par semaine.</b> Les visiteurs n\'augmentent presque pas entre la semaine 1 ('+nf(nc.first)+') et la semaine '+nc.k+' ('+nf(nc.last)+'). L\'outil attend le <b>cumul depuis le premier jour du test</b> : refaites l\'export sur une seule période, du début du test à la fin de chaque semaine. Additionner les semaines ne convient pas : un visiteur revenu serait compté deux fois.</div>':'')
      +'<div class="dv-sec"><div class="kicker">1 · Votre test</div><div class="dv-g"><div class="w2"><label for="gst-dn">Nom du test</label><input id="gst-dn" data-d="name" value="'+esc(d.name)+'"></div>'
      +(locked?'':'<div><label for="gst-dk">Durée prévue (semaines)</label><input id="gst-dk" type="number" min="1" max="50" data-d="k" value="'+d.k+'"></div><div><label for="gst-ds">Date de début</label><input id="gst-ds" type="date" data-d="startDate" value="'+esc(d.startDate)+'"></div>')+'</div></div>'
      +'<div class="dv-sec"><div class="kicker">2 · Ce que l\'outil a lu</div><div class="dv-g">'
      +(d.tests.length>1?'<div class="w4"><label for="gst-dt">Test (colonne « '+esc(d.H[d.cTest])+' »)</label><select id="gst-dt" data-d="test">'+d.tests.map(function(t){return '<option'+(t===d.test?' selected':'')+'>'+esc(t)+'</option>';}).join('')+'</select></div>':'')
      +'<div><label for="gst-dv">Colonne des variations</label><select id="gst-dv" data-d="cVar">'+opt(d.cVar,true)+'</select></div><div><label for="gst-dc">Colonne des visiteurs</label><select id="gst-dc" data-d="cVis">'+opt(d.cVis,true)+'</select></div>'
      +'<div><label for="gst-da">Contrôle (A)</label><select id="gst-da" data-d="control">'+d.vars.map(function(t){return '<option'+(t===d.control?' selected':'')+'>'+esc(t)+'</option>';}).join('')+'</select></div>'
      +'<div><label for="gst-db">Variante (B)</label><select id="gst-db" data-d="variant">'+d.vars.filter(function(t){return t!==d.control;}).map(function(t){return '<option'+(t===d.variant?' selected':'')+'>'+esc(t)+'</option>';}).join('')+'</select></div></div>'
      +(last?'<p class="dv-read">'+ICON.ok+'<span>Dernier cumul lu : <b class="num">'+nf(last.A)+'</b> visiteurs pour '+esc(d.control)+', <b class="num">'+nf(last.B)+'</b> pour '+esc(d.variant)+'.</span></p>':'')+'</div>'
      +'<div class="dv-sec"><div class="kicker"><span>3 · Métriques à suivre</span><span class="num">'+nInc+' / '+MAX_METRICS+'</span></div>'
      +(d.metrics.length?'<div class="dv-mh" aria-hidden="true"><span></span><span>Métrique</span><span>Type</span><span>Rôle</span><span>Sens favorable</span></div>':'')
      +d.metrics.map(function(m,i){return '<div class="dv-m'+(m.include&&m.role==='principale'?' on':'')+(m.include?'':' off')+'"><input type="checkbox" data-dm="include" data-i="'+i+'"'+(m.include?' checked':'')+(locked?' disabled':'')+' aria-label="Inclure '+esc(m.name)+'"><input data-dm="name" data-i="'+i+'" value="'+esc(m.name)+'" aria-label="Nom de la métrique"'+(locked?' disabled':'')+'>'
        +'<span class="pill" title="'+(m.type==='continue'?'Valeur moyenne par visiteur (colonnes somme et somme des carrés)':'Part des visiteurs ayant fait l\'action')+'">'+(m.type==='continue'?'Moyenne':'Taux')+'</span>'
        +'<span class="dv-rs"><label><span>Rôle</span><select data-dm="role" data-i="'+i+'"'+(locked?' disabled':'')+'>'+[['principale','Principale'],['garde-fou','Garde-fou'],['secondaire','Secondaire']].map(function(o){return '<option value="'+o[0]+'"'+(m.role===o[0]?' selected':'')+'>'+o[1]+'</option>';}).join('')+'</select></label>'
        +'<label><span>Sens favorable</span><select data-dm="sens" data-i="'+i+'"'+(locked?' disabled':'')+'><option value="hausse"'+(m.sens==='hausse'?' selected':'')+'>Hausse</option><option value="baisse"'+(m.sens==='baisse'?' selected':'')+'>Baisse</option></select></label></span></div>';}).join('')
      +(d.metrics.length?'<p class="hint" style="margin-top:12px"><b>Taux</b> : part des visiteurs ayant fait l\'action. <b>Moyenne</b> : valeur moyenne par visiteur. Une seule métrique principale porte la décision ; les garde-fous vérifient que rien ne se dégrade.</p>':'<p class="err">Aucune colonne numérique de métrique détectée.</p>')+'</div>'
      +'<p class="row dv-act"><button type="button" class="pri big" data-act="apply">Importer et analyser</button><button type="button" class="big" data-act="cancel">Annuler</button></p></div>';
"""
s=s[:a]+NEW.replace('\n','\n' if '\r\n' not in s else '\r\n')+s[b:]
CSS="""#gst-app .card.dv{padding:22px 24px 24px}
#gst-app .dv-sec{margin-top:22px;padding-top:20px;border-top:1px solid var(--line)}
#gst-app .dv-sec>.kicker{display:flex;justify-content:space-between;gap:12px;margin-bottom:14px}
#gst-app .dv-g{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px 16px;align-items:end}
#gst-app .dv-g .w2{grid-column:span 2}#gst-app .dv-g .w4{grid-column:1/-1}
#gst-app .dv-g label{margin:0 0 6px}
#gst-app .dv input:not([type=checkbox]),#gst-app .dv select{height:42px;min-height:42px}
#gst-app .dv-read{display:flex;gap:8px;align-items:flex-start;margin:14px 0 0;font-size:13px;color:var(--charcoal)}#gst-app .dv-read svg{flex:none;margin-top:1px}
#gst-app .dv-mh,#gst-app .dv-m{display:grid;grid-template-columns:22px minmax(0,2.4fr) 92px minmax(0,1.2fr) minmax(0,1.3fr);gap:14px;align-items:center}
#gst-app .dv-mh{padding:0 12px 8px;font-size:12px;font-weight:600;color:var(--charcoal)}
#gst-app .dv-m{padding:9px 12px;border-top:1px solid var(--line)}
#gst-app .dv-m.on{background:var(--wash)}
#gst-app .dv-m.off input:not([type=checkbox]),#gst-app .dv-m.off select,#gst-app .dv-m.off .pill{opacity:.55}
#gst-app .dv-m .pill{justify-self:start}
#gst-app .dv-rs,#gst-app .dv-rs label{display:contents}#gst-app .dv-rs label>span{display:none}
#gst-app .dv-warn{background:#FBF1DC;border:1px solid var(--amber);color:#5f4209;border-radius:6px;padding:12px 14px;margin-top:14px;line-height:1.5}
#gst-app .dv-act{margin-top:22px;padding-top:20px;border-top:1px solid var(--line);gap:12px}
@media (max-width:760px){
  h1.gst-h1{padding-top:28px!important}
  #gst-app .card.dv{padding:16px}
  #gst-app .dv-g{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
  #gst-app .dv-g .w2{grid-column:1/-1}
  #gst-app .dv-mh{display:none}
  #gst-app .dv-m{grid-template-columns:22px minmax(0,1fr) auto;gap:8px 10px;padding:12px 8px}
  #gst-app .dv-rs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;grid-column:2/-1}
  #gst-app .dv-rs label{display:block;margin:0}#gst-app .dv-rs label>span{display:block;font-size:11px;margin-bottom:4px}
  #gst-app .dv-act button{flex:1 1 100%}
}
"""
i=s.index("h1.gst-h1+#gst-app{");j=s.index("\n",i)+1
s=s[:j]+CSS+s[j:]
if '--keepfaq' not in sys.argv:
    a=s.index("    +'<div class=\"sec\"><h3 class=\"sech\">Questions fréquentes</h3>");b=s.index("    +'</div></div>';",a)
    seg=s[a:b]; assert seg.count("faq(")==2
    # la ligne précédente se termine par +'...</div>' : on ferme l'expression
    s=s[:a]+"    ;"+s[b+len("    +'</div></div>';"):]
open(dst,'w',newline='').write(s)
print(len(s))

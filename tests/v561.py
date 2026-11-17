src='repo/calculateur-sequentiel-v56-0.html';dst='repo/calculateur-sequentiel-v56-1.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
rep("VERSION='v56.0'","VERSION='v56.1'")
# ---------- A. état : date de fin par lecture, choix de colonnes mémorisés
rep("map(function(w){return {A:arm(w.A),B:arm(w.B)};});","map(function(w){var r={A:arm(w.A),B:arm(w.B)};if(/^\\d{4}-\\d{2}-\\d{2}$/.test(w.end))r.end=w.end;return r;});\n  var M=o.map&&typeof o.map==='object'?o.map:null;if(M)st.map={test:str(M.test,160),vr:str(M.vr,160),vis:str(M.vis,160),tv:str(M.tv,300),c:str(M.c,160),v:str(M.v,160)};")
# ---------- B. analyse : colonnes retenues du test en cours, colonne du test au choix, dates
rep("  d.cTest=find(/^(test|mv_test|nom du test|experience|experiment)|^mvt?[^a-z0-9]*test/);","  var MP=!keep&&state.weeks.length&&state.map?state.map:null,byName=function(nm){if(!nm)return -1;for(var i=0;i<H.length;i++)if(H[i]===nm)return i;return -1;},isoD=function(x){x=String(x||'').trim();return /^\\d{4}-\\d{2}-\\d{2}/.test(x)?x.slice(0,10):(/^(\\d{2})\\/(\\d{2})\\/(\\d{4})/.test(x)?x.replace(/^(\\d{2})\\/(\\d{2})\\/(\\d{4}).*/,'$3-$2-$1'):'');};\n  d.cTest=keep&&keep.cTest!=null?keep.cTest:(MP&&MP.test===''&&byName(MP.vr)>=0?-1:(MP&&byName(MP.test)>=0?byName(MP.test):find(/^(test|mv_test|nom du test|experience|experiment)|^mvt?[^a-z0-9]*test/)));")
rep("  d.cVar=keep&&keep.cVar!=null?keep.cVar:find(","  d.cVar=keep&&keep.cVar!=null?keep.cVar:MP&&byName(MP.vr)>=0?byName(MP.vr):find(")
rep("  d.cVis=keep&&keep.cVis!=null?keep.cVis:find(","  d.cVis=keep&&keep.cVis!=null?keep.cVis:MP&&byName(MP.vis)>=0?byName(MP.vis):find(")
rep("d.test=keep&&d.tests.indexOf(keep.test)>=0?keep.test:(state.weeks.length&&","d.test=keep&&d.tests.indexOf(keep.test)>=0?keep.test:(MP&&d.tests.indexOf(MP.tv)>=0?MP.tv:state.weeks.length&&")
rep("  d.control=keep&&d.vars.indexOf(keep.control)>=0?keep.control:ctrl;","  d.control=keep&&d.vars.indexOf(keep.control)>=0?keep.control:(MP&&d.vars.indexOf(MP.c)>=0?MP.c:ctrl);")
rep("keep.variant!==d.control?keep.variant:(d.vars.filter(","keep.variant!==d.control?keep.variant:(MP&&d.vars.indexOf(MP.v)>=0&&MP.v!==d.control?MP.v:d.vars.filter(")
rep("  d.startDate=keep&&keep.startDate?keep.startDate:(/^\\d{4}-\\d{2}-\\d{2}/.test(sd)?sd.slice(0,10):(/^(\\d{2})\\/(\\d{2})\\/(\\d{4})/.test(sd)?sd.replace(/^(\\d{2})\\/(\\d{2})\\/(\\d{4}).*/,'$3-$2-$1'):state.plan.startDate));",
"  var ed=d.cEnd>=0&&rowsT[0]?isoD(rowsT[0][d.cEnd]):'';d.endFromFile=!!ed;d.endDate=keep&&keep.endDate?keep.endDate:(ed||addDays(todayISO(),-1));\n  d.startDate=keep&&keep.startDate?keep.startDate:(isoD(sd)||(d.mode==='instantane'&&!state.weeks.length?addDays(d.endDate,-6):state.plan.startDate));d.startGuess=!(keep&&keep.startDate)&&!isoD(sd)&&d.mode==='instantane'&&!state.weeks.length;")
# ---------- C. règle des semaines complètes
rep("function buildWeeks(d){","""function dayDiff(a,b){var x=/^(\\d{4})-(\\d{2})-(\\d{2})/.exec(a||''),y=/^(\\d{4})-(\\d{2})-(\\d{2})/.exec(b||'');return x&&y?Math.round((Date.UTC(+y[1],+y[2]-1,+y[3])-Date.UTC(+x[1],+x[2]-1,+x[3]))/864e5):NaN;}
/* Un import sans colonne « Semaine » n'ajoute une lecture que si une semaine complète de plus s'est écoulée depuis le début du test. */
function weekGate(d){
  if(d.mode!=='instantane'||state.plan.unit==='jour')return null;
  var n=state.weeks.length,start=n?state.plan.startDate:d.startDate,E=d.endDate,days=dayDiff(start,E)+1,fix=n?' Si la date de début du test ('+frDate(start)+') est fausse, corrigez-la dans l\\'onglet Plan.':' Si le test a commencé plus tôt, corrigez la date de début.';
  if(!(days===days))return {ok:false,msg:'Indiquez la date de début du test et la date jusqu\\'à laquelle vont les données.'};
  if(E>todayISO())return {ok:false,msg:'La date « Données jusqu\\'au » est dans le futur.'};
  if(days<1)return {ok:false,msg:'Les données s\\'arrêtent avant le début du test ('+frDate(start)+').'+fix};
  var w=Math.floor(days/7),last=n?state.weeks[n-1]:null,wl=last?(last.end?Math.floor((dayDiff(start,last.end)+1)/7):n):0,next=addDays(start,7*(wl+1)-1);
  if(w<=wl)return {ok:false,msg:(n?'Pas de nouvelle semaine complète depuis la dernière lecture'+(last.end?' (données jusqu\\'au '+frDate(last.end)+')':'')+'.':'La première semaine du test n\\'est pas terminée : '+days+' jour'+(days>1?'s':'')+' de données.')+' Prochaine lecture avec des données allant au moins jusqu\\'au '+frDate(next)+'.'+fix};
  return {ok:true,msg:days+' jours de données depuis le '+frDate(start)+', soit '+w+' semaine'+(w>1?'s':'')+' complète'+(w>1?'s':'')+'.'};
}
function buildWeeks(d){""")
rep("  if(state.weeks.length&&d.mode==='instantane'){state.metrics.forEach(","  var gate=weekGate(d);if(gate&&!gate.ok)errs.push(gate.msg);\n  if(state.weeks.length&&d.mode==='instantane'){state.metrics.forEach(")
rep("    if(W.A&&W.B)weeks.push(W);","    if(W.A&&W.B){if(d.mode==='instantane'&&/^\\d{4}-\\d{2}-\\d{2}$/.test(d.endDate||''))W.end=d.endDate;weeks.push(W);}")
# ---------- D. on retient les choix à l'import
rep("  var replace=d.mode==='serie'||!state.weeks.length;\n","  var replace=d.mode==='serie'||!state.weeks.length;\n  state.map={test:d.cTest>=0?d.H[d.cTest]:'',vr:d.H[d.cVar]||'',vis:d.H[d.cVis]||'',tv:d.test||'',c:d.control||'',v:d.variant||''};\n") if "  var replace=d.mode==='serie'||!state.weeks.length;\n" in s else rep("  var replace=d.mode==='serie'||!state.weeks.length;\r\n","  var replace=d.mode==='serie'||!state.weeks.length;\r\n  state.map={test:d.cTest>=0?d.H[d.cTest]:'',vr:d.H[d.cVar]||'',vis:d.H[d.cVis]||'',tv:d.test||'',c:d.control||'',v:d.variant||''};\r\n")
# ---------- E. écran de vérification
rep("""(locked?'':'<div><label for="gst-dk">Durée prévue (semaines)</label><input id="gst-dk" type="number" min="1" max="50" data-d="k" value="'+d.k+'"></div><div><label for="gst-ds">Date de début</label><input id="gst-ds" type="date" data-d="startDate" value="'+esc(d.startDate)+'"></div>')+'</div></div>'""",
"""(locked?'':'<div><label for="gst-dk">Durée prévue (semaines)</label><input id="gst-dk" type="number" min="1" max="50" data-d="k" value="'+d.k+'"></div><div><label for="gst-ds">Date de début du test</label><input id="gst-ds" type="date" data-d="startDate" value="'+esc(d.startDate)+'"></div>')
      +(d.mode==='instantane'?'<div><label for="gst-de">Données jusqu\\'au</label><input id="gst-de" type="date" data-d="endDate" value="'+esc(d.endDate)+'" max="'+todayISO()+'"></div><p class="dv-gate w3'+(gate&&!gate.ok?' ko':'')+'">'+(gate?(gate.ok?ICON.ok:'')+'<span>'+esc(gate.msg)+(gate.ok&&d.startGuess?' <b>Vérifiez la date de début</b> : elle est supposée une semaine avant la fin des données.':'')+'</span>':'<span>Dernier jour inclus dans l\\'export.</span>')+'</p>':'')+'</div></div>'""")
rep("    var vis=draftVis(d),","    var gate=weekGate(d),vis=draftVis(d),")
rep("""+(d.tests.length>1?'<div class="w4"><label for="gst-dt">Test (colonne « '+esc(d.H[d.cTest])+' »)</label><select id="gst-dt" data-d="test">'+d.tests.map(function(t){return '<option'+(t===d.test?' selected':'')+'>'+esc(t)+'</option>';}).join('')+'</select></div>':'')""",
"""+'<div><label for="gst-dct">Colonne du test</label><select id="gst-dct" data-d="cTest"><option value="-1">Aucune : un seul test</option>'+d.H.map(function(x,i){return '<option value="'+i+'"'+(i===d.cTest?' selected':'')+'>'+esc(x)+'</option>';}).join('')+'</select></div>'
      +(d.cTest>=0?'<div class="w3"><label for="gst-dt">Test à analyser</label><select id="gst-dt" data-d="test">'+d.tests.map(function(t){return '<option'+(t===d.test?' selected':'')+'>'+esc(t)+'</option>';}).join('')+'</select></div>':'<div class="w3 dv-fill" aria-hidden="true"></div>')""")
# ---------- F. saisie
rep("else if(f==='startDate')d.startDate=t.value;","else if(f==='startDate'){d.startDate=t.value;d.startGuess=false;}else if(f==='endDate')d.endDate=t.value;")
rep("var keep={name:d.name,k:d.k,startDate:d.startDate,cVar:d.cVar,cVis:d.cVis,test:d.test,control:d.control,variant:d.variant},old=d.metrics;","var keep={name:d.name,k:d.k,startDate:d.startDate,endDate:d.endDate,cTest:d.cTest,cVar:d.cVar,cVis:d.cVis,test:d.test,control:d.control,variant:d.variant},old=d.metrics,sg=d.startGuess;")
rep("if(f==='cVar'||f==='cVis'){keep[f]=parseInt(t.value,10);if(f==='cVar'){keep.control=null;keep.variant=null;}}else keep[f]=t.value;","if(f==='cVar'||f==='cVis'||f==='cTest'){keep[f]=parseInt(t.value,10);if(f!=='cVis'){keep.control=null;keep.variant=null;}if(f==='cTest')keep.test=null;}else keep[f]=t.value;")
rep("      ui.draft=analyze(ui.rawTable,d.file,keep);","      ui.draft=analyze(ui.rawTable,d.file,keep);if(keep.startDate)ui.draft.startGuess=sg;")
# dates réelles dans la progression
rep("' Du '+frDate(state.plan.startDate)+' au '+frDate(addDays(state.plan.startDate,(U()?1:7)*n-1))+'.</span>'","' Du '+frDate(state.plan.startDate)+' au '+frDate((state.weeks[n-1]&&state.weeks[n-1].end)||addDays(state.plan.startDate,(U()?1:7)*n-1))+'.</span>'")
CSS="""#gst-app .dv-g .w3{grid-column:span 3}
#gst-app .dv-gate{display:flex;gap:8px;align-items:flex-start;margin:0;font-size:13px;color:var(--charcoal);align-self:center;padding-top:18px}#gst-app .dv-gate svg{flex:none;width:18px;height:18px;margin-top:1px}
#gst-app .dv-gate.ko{color:#8f2c20;background:#FCF1EF;border:1px solid var(--coral);border-radius:6px;padding:10px 12px;align-self:end}
@media (max-width:760px){#gst-app .dv-g .w3{grid-column:1/-1}#gst-app .dv-g .dv-fill{display:none}#gst-app .dv-gate{padding-top:0}}
"""
i=s.index("h1.gst-h1+#gst-app{");j=s.index("\n",i)+1
s=s[:j]+CSS+s[j:]
rep("'Instantané cumulé : ajouté comme <b>semaine '+(state.weeks.length+1)+'</b>.')","(gate&&!gate.ok?'Instantané cumulé : une ligne par variation, sans colonne « Semaine ».':'Instantané cumulé : ajouté comme <b>semaine '+(state.weeks.length+1)+'</b>.'))")
rep("if(o){m.include=o.include;m.role=o.role;m.sens=o.sens;m.name=o.name;}});}","if(o){m.include=o.include;m.role=o.role;m.sens=o.sens;m.name=o.name;}});\n      if(!state.weeks.length&&!ui.draft.metrics.some(function(m){return m.include&&m.role==='principale';})){var fm=ui.draft.metrics.filter(function(m){return m.include&&m.type!=='continue';})[0];if(fm)fm.role='principale';}}")
open(dst,'w',newline='').write(s);print(len(s))

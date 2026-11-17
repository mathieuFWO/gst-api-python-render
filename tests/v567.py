src='repo/calculateur-sequentiel-v56-6.html';dst='repo/calculateur-sequentiel-v56-7.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:110]); s=s.replace(a,b)
rep("VERSION='v56.6'","VERSION='v56.7'")

# ===== A. confirmation de la date de fin quand elle n'est pas lue dans le fichier =====
rep("function srcNote(d){","""/* La date de fin n'est sûre que lue dans le fichier (colonne ou en-tête) ou saisie par l'utilisateur ; sinon il la confirme. */
function endNeed(d){return d.mode==='instantane'&&!d.endFromFile&&d.endSrc!=='entete'&&!d.endTyped;}
function legacy(d){return d.mode==='instantane'&&state.weeks.length>0&&state.plan.unit!=='jour'&&!state.weeks.some(function(w){return w.end;});}
function srcNote(d){""")
rep("else if(f==='endDate'){d.endDate=t.value;d.endSrc='';}","else if(f==='endDate'){d.endDate=t.value;d.endSrc='';d.endTyped=true;d.endOk=false;}else if(f==='endOk'){d.endOk=t.checked;d.errors=[];}else if(f==='cumOk'){d.cumOk=t.checked;d.errors=[];}")
rep("var keep={name:d.name,k:d.k,startDate:d.startDate,endDate:d.endDate,endSrc:d.endSrc,startSrc:d.startSrc,","var keep={name:d.name,k:d.k,startDate:d.startDate,endDate:d.endDate,endSrc:d.endSrc,startSrc:d.startSrc,endTyped:d.endTyped,endOk:d.endOk,")
rep("d.endExp=M.exp||'';","d.endExp=M.exp||'';d.endTyped=!!(keep&&keep.endTyped);d.endOk=!!(keep&&keep.endOk);d.cumOk=false;")
rep("+srcNote(d)+'</span>':'<span>Dernier jour inclus dans l\\'export.</span>')+'</p>':'')+'</div></div>'",
    "+srcNote(d)+'</span>':'<span>Dernier jour inclus dans l\\'export.</span>')+'</p>'+(endNeed(d)&&(!gate||gate.ok)?'<label class=\"dv-ck w3\"><input type=\"checkbox\" data-d=\"endOk\"'+(d.endOk?' checked':'')+'><span>Je confirme : cet export contient toutes les données du test <b>jusqu\\'au '+frDate(d.endDate)+' inclus</b>. Sinon, corrigez la date ci-dessus.</span></label>':''):'')+'</div></div>'")
rep("#gst-app .dv-gate.ko{","#gst-app .dv-ck{display:flex;gap:10px;align-items:flex-start;margin:0;font-size:14px;line-height:1.45;color:var(--ink);background:#F8FBFA;border:1px solid #D9D9D9;border-radius:6px;padding:10px 12px;cursor:pointer;font-weight:400}#gst-app .dv-ck input{flex:none;width:18px;height:18px;margin:2px 0 0;accent-color:#028D6A}#gst-app .dv-warn .dv-ck{margin-top:10px;background:#fff;border-color:var(--amber)}\n#gst-app .dv-gate.ko{")
# blocage à la validation
rep("function applyDraft(){\n  var d=ui.draft,","function applyDraft(){\n  var d0=ui.draft,g0=weekGate(d0),v0=draftVis(d0),lk0=lockErr(d0),LG0=legacy(d0),nc0=d0.mode==='serie'?notCumul(v0):(v0&&state.weeks.length&&!lk0.length?notCumul(state.weeks.map(function(x){return {A:x.A.n,B:x.B.n};}).concat(v0)):null);\n  if((!g0||g0.ok)&&!lk0.length){if(endNeed(d0)&&!d0.endOk){d0.errors=['Confirmez la date de fin des données (case à cocher sous « Données jusqu\\'au »), ou corrigez-la.'];return render();}if(nc0&&!d0.cumOk){d0.errors=['Confirmez que ces chiffres sont bien cumulés depuis le premier jour du test (case à cocher dans l\\'alerte), ou refaites l\\'export.'];return render();}}\n  var d=ui.draft,") if "function applyDraft(){\n  var d=ui.draft," in s else rep("function applyDraft(){\r\n  var d=ui.draft,","function applyDraft(){\r\n  var d0=ui.draft,g0=weekGate(d0),v0=draftVis(d0),lk0=lockErr(d0),LG0=legacy(d0),nc0=d0.mode==='serie'?notCumul(v0):(v0&&state.weeks.length&&!lk0.length?notCumul(state.weeks.map(function(x){return {A:x.A.n,B:x.B.n};}).concat(v0)):null);\r\n  if((!g0||g0.ok)&&!lk0.length){if(endNeed(d0)&&!d0.endOk){d0.errors=['Confirmez la date de fin des données (case à cocher sous « Données jusqu\\'au »), ou corrigez-la.'];return render();}if(nc0&&!d0.cumOk){d0.errors=['Confirmez que ces chiffres sont bien cumulés depuis le premier jour du test (case à cocher dans l\\'alerte), ou refaites l\\'export.'];return render();}}\r\n  var d=ui.draft,")
# la démonstration et l'exemple n'ont rien à confirmer
rep("if(ui.draft){ui.draft.k=8;ui.draft.name='Exemple : 7 métriques';if(!state.weeks.length){applyDraft();","if(state.weeks.length&&!ui.ro){autosave();state=freshState();ui.week=null;ui.sel=null;openDraft(EXEMPLE,'exemple-7-metriques.csv');}if(ui.draft){ui.draft.k=8;ui.draft.name='Exemple : 7 métriques';ui.draft.cumOk=true;ui.draft.endOk=true;if(!state.weeks.length){applyDraft();")

# ===== 8. alerte « non cumulé » : critère sur la progression moyenne, texte exact, confirmation =====
rep("  return (down||t[K-1]<t[0]*(K>2?2:1.25))?{first:t[0],last:t[K-1],k:K}:null;","  return (down||(t[K-1]-t[0])/(K-1)<0.5*t[0])?{first:t[0],last:t[K-1],k:K,down:down}:null;")
rep("(nc.last<nc.first?'ils baissent, ce qu\\'un cumul ne fait jamais':'c\\'est peu pour '+nc.k+' semaines de cumul')+'. L\\'outil attend",
    "(nc.down?'ils baissent d\\'une lecture à l\\'autre, ce qu\\'un cumul ne fait jamais':(nc.last>nc.first?'+'+Math.round((nc.last/nc.first-1)*100)+' %':'aucune hausse')+' en '+(nc.k-1)+' semaine'+(nc.k>2?'s':'')+', moins qu\\'attendu pour un cumul')+'. L\\'outil attend")
rep("un visiteur revenu serait compté deux fois.</div>':'')","un visiteur revenu serait compté deux fois.<label class=\"dv-ck\"><input type=\"checkbox\" data-d=\"cumOk\"'+(d.cumOk?' checked':'')+'><span>Je confirme : chaque ligne est bien le cumul depuis le premier jour du test.</span></label></div>':'')")

# ===== 6. test créé avant la v56.1 (aucune lecture datée) : la date de début se corrige dans l'écran d'import =====
rep("var n=state.weeks.length,start=n?state.plan.startDate:d.startDate,kk=n?state.plan.k:d.k,E=d.endDate,days=dayDiff(start,E)+1,last=n?state.weeks[n-1]:null,fix=n?' Si la date de début du test ('+frDate(start)+') est fausse, corrigez-la dans l\\'onglet Plan.':' Si le test a commencé plus tôt, corrigez la date de début.';",
    "var n=state.weeks.length,lg=legacy(d),start=n&&!lg?state.plan.startDate:d.startDate,kk=n?state.plan.k:d.k,E=d.endDate,days=dayDiff(start,E)+1,last=n?state.weeks[n-1]:null,fix=lg?' Vérifiez la date de début du test ci-dessus : ce test a été créé avant que les dates soient enregistrées.':(n?' Si la date de début du test ('+frDate(start)+') est fausse, corrigez-la dans l\\'onglet Plan.':' Si le test a commencé plus tôt, corrigez la date de début.');")
rep("+(locked?'':'<div><label for=\"gst-dk\">Durée prévue (semaines)</label>","+(locked?(legacy(d)?'<div><label for=\"gst-ds\">Date de début du test</label><input id=\"gst-ds\" type=\"date\" data-d=\"startDate\" value=\"'+esc(d.startDate)+'\" max=\"'+addDays(todayISO(),-1)+'\"></div>':''):'<div><label for=\"gst-dk\">Durée prévue (semaines)</label>")
rep("  if(replace){state.plan.k=d.k;state.plan.startDate=d.startDate;}","  if(replace){state.plan.k=d.k;state.plan.startDate=d.startDate;}else if(LG0&&/^\\d{4}-\\d{2}-\\d{2}$/.test(d.startDate||'')&&d.startDate>='2000-01-01')state.plan.startDate=d.startDate;")

# ===== 9. colonnes mémorisées : portées par le lien de partage et par les comptes =====
rep("w:state.weeks,d:todayISO()});}","w:state.weeks,x:state.map||null,d:todayISO()});}")
rep("var st=cleanState({name:o.n||'Test partagé',plan:o.p,metrics:o.m,labels:o.l,weeks:o.w});","var st=cleanState({name:o.n||'Test partagé',plan:o.p,metrics:o.m,labels:o.l,weeks:o.w,map:o.x});")
rep("labels:j.state.labels,weeks:j.state.weeks,sid:j.id});","labels:j.state.labels,weeks:j.state.weeks,map:j.state.map,sid:j.id});")
rep("state:{plan:state.plan,metrics:state.metrics,labels:state.labels,weeks:state.weeks},sum:","state:{plan:state.plan,metrics:state.metrics,labels:state.labels,weeks:state.weeks,map:state.map||null},sum:")

# ===== 17. l'assistant n'enregistre plus un test vide =====
rep("ui.tab='donnees';ui.manual=true;autosave();}","ui.tab='donnees';ui.manual=true;}")

# ===== 18. onglet Plan à 360 px : champs alignés quand un libellé passe sur deux lignes =====
rep("#gst-app .form2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}","#gst-app .form2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;align-items:end}")

# ===== 19. listes de l'écran d'import : identifiants Piano retirés de l'affichage =====
rep("function srcNote(d){","""function optLabs(a){var re=/^\\d{1,12}(?=[A-Za-zÀ-ÿ\\[])/,ids=a.map(function(x){return (re.exec(x)||[''])[0];});
  if(a.length<2||!ids.every(function(p){return p;})||!ids.some(function(p){return p==='0'||p.length>=4;}))return a.slice();
  var o=a.map(function(x){return x.replace(re,'').trim();});return o.every(function(x,i){return x&&o.indexOf(x)===i;})?o:a.slice();}
function srcNote(d){""")
rep("d.tests.map(function(t){return '<option'+(t===d.test?' selected':'')+'>'+esc(t)+'</option>';}).join('')","(function(){var L=optLabs(d.tests);return d.tests.map(function(t,i){return '<option value=\"'+esc(t)+'\"'+(t===d.test?' selected':'')+'>'+esc(L[i])+'</option>';}).join('');})()")
rep("d.vars.map(function(t){return '<option'+(t===d.control?' selected':'')+'>'+esc(t)+'</option>';}).join('')","(function(){var L=optLabs(d.vars);return d.vars.map(function(t,i){return '<option value=\"'+esc(t)+'\"'+(t===d.control?' selected':'')+'>'+esc(L[i])+'</option>';}).join('');})()")
rep("d.vars.filter(function(t){return t!==d.control;}).map(function(t){return '<option'+(t===d.variant?' selected':'')+'>'+esc(t)+'</option>';}).join('')","(function(){var L=optLabs(d.vars);return d.vars.map(function(t,i){return t===d.control?'':'<option value=\"'+esc(t)+'\"'+(t===d.variant?' selected':'')+'>'+esc(L[i])+'</option>';}).join('');})()")
open(dst,'w',newline='').write(s);print(len(s))

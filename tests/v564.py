import re
src='repo/calculateur-sequentiel-v56-3.html';dst='repo/calculateur-sequentiel-v56-4.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
rep("VERSION='v56.3'","VERSION='v56.4'")
# --- constats 1 et 2 : aux imports suivants, même test, même témoin, même variante
rep("function buildWeeks(d){","""/* Les lectures d'un test viennent toutes du même test, avec le même témoin et la même variante. */
function lockErr(d){
  var M=state.map,out=[];if(d.mode!=='instantane'||!state.weeks.length||!M)return out;
  if(M.tv&&d.cTest>=0&&d.test!==M.tv)out.push(d.tests.indexOf(M.tv)<0?'Ce fichier ne contient pas le test suivi jusqu\\'ici (« '+M.tv+' »). Vérifiez l\\'export, ou créez un nouveau test pour en analyser un autre.':'Les lectures précédentes portent sur « '+M.tv+' » : choisissez ce test, ou créez un nouveau test pour en analyser un autre.');
  else if(M.c&&M.v&&(d.control!==M.c||d.variant!==M.v))out.push(d.vars.indexOf(M.c)<0||d.vars.indexOf(M.v)<0?'Ce fichier ne contient pas les deux variations suivies jusqu\\'ici (« '+M.c+' » et « '+M.v+' »).':'Le contrôle et la variante doivent rester ceux des lectures précédentes : « '+M.c+' » en contrôle, « '+M.v+' » en variante.');
  return out;
}
function buildWeeks(d){""")
rep("  var gate=weekGate(d);if(gate&&!gate.ok)errs.push(gate.msg);","  var gate=weekGate(d);if(gate&&!gate.ok)errs.push(gate.msg);\n  lockErr(d).forEach(function(x){errs.push(x);});")
# affichés dès l'ouverture de l'écran
rep("      +(d.errors.length?'<div class=\"err\" role=\"alert\">'+d.errors.map(esc).join('<br>')+'</div>':'')\n      +(nc?","      +(d.errors.length?'<div class=\"err\" role=\"alert\">'+d.errors.map(esc).join('<br>')+'</div>':(lk.length?'<div class=\"err\" role=\"alert\">'+lk.map(esc).join('<br>')+'</div>':''))\n      +(nc?")
# --- constat 3 : alerte « non cumulé » aussi pour les instantanés successifs ; texte juste
rep("var gate=weekGate(d),vis=draftVis(d),nc=d.mode==='serie'?notCumul(vis):null,","var gate=weekGate(d),lk=lockErr(d),vis=draftVis(d),nc=d.mode==='serie'?notCumul(vis):(vis&&state.weeks.length&&!lk.length?notCumul(state.weeks.map(function(x){return {A:x.A.n,B:x.B.n};}).concat(vis)):null),")
a=s.index("'<div class=\"dv-warn\" role=\"alert\"><b>Ce fichier ressemble à un export semaine par semaine.</b>");e=s.index("</div>':'')",a)
s=s[:a]+"""'<div class="dv-warn" role="alert"><b>'+(d.mode==='serie'?'Ce fichier ressemble à un export semaine par semaine.':'Ces chiffres ne ressemblent pas à un cumul depuis le début du test.')+'</b> Les visiteurs passent de '+nf(nc.first)+' (semaine 1) à '+nf(nc.last)+' (semaine '+nc.k+') : '+(nc.last<nc.first?'ils baissent, ce qu\\'un cumul ne fait jamais':'c\\'est peu pour '+nc.k+' semaines de cumul')+'. L\\'outil attend le <b>cumul depuis le premier jour du test</b> : refaites l\\'export sur une seule période, du début du test à la fin de la semaine. Additionner les semaines ne convient pas : un visiteur revenu serait compté deux fois."""+s[e:]
# --- constat 7 : la journée en cours n'est pas terminée
rep("  if(E>todayISO())return {ok:false,msg:'La date « Données jusqu\\'au » est dans le futur.'};","  if(E>todayISO())return {ok:false,msg:'La date « Données jusqu\\'au » est dans le futur.'};\n  if(E===todayISO())return {ok:false,msg:'La journée d\\'aujourd\\'hui n\\'est pas terminée : indiquez hier au plus tard, avec un export arrêté à hier.'};")
rep("""data-d="endDate" value="'+esc(d.endDate)+'" max="'+todayISO()+'">""","""data-d="endDate" value="'+esc(d.endDate)+'" max="'+addDays(todayISO(),-1)+'">""")
# --- constats 10 et 12 : email
rep("""if(!/^[^\\s@<>,;"']+@[^\\s@<>,;"']+\\.[^\\s@<>,;"']+$/.test(to))to='';""","""if(!/^[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$/.test(to))to='';""")
rep("var nm=state.name||'test A/B',head='mailto:'+to+'?subject='","var nm=state.name||'test A/B',head='mailto:'+encodeURIComponent(to).replace(/%40/g,'@')+'?subject='")
a=s.index("    if(full.length>2000){");e=s.index("else ui.mailNote='ok';",a)
s=s[:a]+"""    if(full.length>2000){full=head+encodeURIComponent(intro+'[collez ici le lien copié : Ctrl+V]\\n');ui.mailNote='longko';var okc=function(){ui.mailNote='long';render();};try{if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(ui.shareUrl).then(okc,function(){});else{var i4=root.querySelector('[data-f=shareurl]');if(i4){i4.select();if(document.execCommand('copy'))ui.mailNote='long';}}}catch(e){}}"""+s[e:]
rep("""(ui.mailNote==='long'?'<b>Lien copié.</b> Il est trop long pour être inséré automatiquement : collez-le dans le message qui s\\'ouvre (Ctrl+V).':'Le message s\\'ouvre dans votre messagerie.')""","""(ui.mailNote==='long'?'<b>Lien copié.</b> Il est trop long pour être inséré automatiquement : collez-le dans le message qui s\\'ouvre (Ctrl+V).':ui.mailNote==='longko'?'Le lien est trop long pour être inséré automatiquement : cliquez sur « Copier le lien », puis collez-le dans le message qui s\\'ouvre.':'Le message s\\'ouvre dans votre messagerie.')""")
# --- constat 13 : libellés du type « 3D viewer » laissés intacts
rep("return re.test(a)&&re.test(b)&&a.replace(re,'').trim()!==b.replace(re,'').trim()?","var pa=(re.exec(a)||[''])[0],pb=(re.exec(b)||[''])[0];return pa&&pb&&(pa==='0'||pb==='0'||(pa.length>=4&&pb.length>=4))&&a.replace(re,'').trim()!==b.replace(re,'').trim()?")
# --- constat 15 : « 20.000 » est vingt mille dans les champs de trafic
rep("function toCSV(rows){","function toInt(s){s=String(s==null?'':s).trim();return /^\\d{1,3}(\\.\\d{3})+$/.test(s)?Number(s.replace(/\\./g,'')):toNum(s);}\nfunction toCSV(rows){")
rep("  var t=toNum(ui.mde.traffic),c=toNum(ui.mde.conv);","  var t=toInt(ui.mde.traffic),c=toInt(ui.mde.conv);")
rep("var mtv=toNum(ui.mde.traffic);","var mtv=toInt(ui.mde.traffic);")
rep("if(t.getAttribute('data-mde')==='traffic'&&ui.planDraft){var tv=toNum(t.value);","if(t.getAttribute('data-mde')==='traffic'&&ui.planDraft){var tv=toInt(t.value);")
# --- constat 11 : les chiffres saisis à l'étape 3 survivent à un nouvel affichage
rep("man:{step:1,","mw:{},man:{step:1,")
s=re.sub(r"""<input inputmode="numeric" data-mw="A\|n" aria-label""","""<input inputmode="numeric" data-mw="A|n" value="'+esc(ui.mw['A|n']||'')+'" aria-label""",s)
s=re.sub(r"""<input inputmode="numeric" data-mw="B\|n" aria-label""","""<input inputmode="numeric" data-mw="B|n" value="'+esc(ui.mw['B|n']||'')+'" aria-label""",s)
rep("""<input inputmode="numeric" data-mw="A|'+x.id+'|c" aria-label""","""<input inputmode="numeric" data-mw="A|'+x.id+'|c" value="'+esc(ui.mw['A|'+x.id+'|c']||'')+'" aria-label""")
rep("""<input inputmode="numeric" data-mw="B|'+x.id+'|c" aria-label""","""<input inputmode="numeric" data-mw="B|'+x.id+'|c" value="'+esc(ui.mw['B|'+x.id+'|c']||'')+'" aria-label""")
rep("root.addEventListener('change',function(e){","root.addEventListener('input',function(e){var t=e.target;if(t&&t.hasAttribute&&t.hasAttribute('data-mw')&&ui.manFlow)ui.mw[t.getAttribute('data-mw')]=t.value;});\nroot.addEventListener('change',function(e){")
rep("['data-f','data-d','data-dm','data-p','data-m','data-mde','data-i','data-act','data-v']","['data-f','data-d','data-dm','data-p','data-m','data-mde','data-mw','data-i','data-act','data-v']")
rep("state.weeks.push(W);ui.manual=false;ui.manFlow=false;","state.weeks.push(W);ui.manual=false;ui.manFlow=false;ui.mw={};")
rep("state.plan.startDate=mm.startDate;ui.manFlow=true;","state.plan.startDate=mm.startDate;ui.manFlow=true;ui.mw={};")
open(dst,'w',newline='').write(s);print(len(s))

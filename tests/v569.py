src='repo/calculateur-sequentiel-v56-8.html';dst='repo/calculateur-sequentiel-v56-9.html'
s=open(src,newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(s.count(a),a[:110]); s=s.replace(a,b)
rep("VERSION='v56.8'","VERSION='v56.9'")

# ================= barre de compte : bandeau discret à droite =================
rep("#gst-app .accbar{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:8px 16px;padding:10px 0 14px;margin-bottom:14px;border-bottom:1px solid var(--border)}#gst-app .accbar .row{gap:6px 16px}#gst-app .acc-me{max-width:22ch;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}",
    "#gst-app .accbar{display:flex;flex-wrap:wrap;justify-content:flex-end;align-items:center;gap:6px 14px;padding:0 0 12px;font-size:13px;color:var(--charcoal)}#gst-app .acc-me{max-width:26ch;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}"
    "#gst-app button.acc-d,#gst-app button.acc-d:focus{display:inline-flex;align-items:center;gap:7px;min-height:32px;padding:4px 14px 4px 12px;border-radius:999px;font-size:13px;font-weight:600;background:#fff;border:1px solid var(--border);color:var(--ink)}#gst-app button.acc-d svg{fill:#0E7C5D;flex:none}#gst-app button.acc-d:hover{border-color:#1D9E75;background:#fff;color:var(--ink)}#gst-app button.acc-d.on{background:#ECF7F4;border-color:#1D9E75;color:#0E7C5D}"
    "#gst-app .accbar button.link{font-size:13px;color:var(--charcoal);font-weight:400}#gst-app .accbar .acc-in{font-weight:600;color:#0E7C5D}@media (max-width:520px){#gst-app .acc-me{max-width:16ch}}")
rep("""  return '<div class="accbar"><span class="logo"><b>FWO</b>ptimisation <span class="hint">· Analyse séquentielle</span></span><span class="row">'
    +(ACC.user?'<button type="button" class="link" data-act="dash">Tableau de bord</button><span class="hint acc-me">'+esc(ACC.user.email)+'</span><button type="button" class="link" data-act="acclogout">Se déconnecter</button>'
      :'<button type="button" class="link" data-act="acclogin">Se connecter</button>')+'</span></div>';""",
"""  var gi='<svg aria-hidden="true" width="13" height="13" viewBox="0 0 13 13"><rect width="5.5" height="5.5" rx="1.2"/><rect x="7.5" width="5.5" height="5.5" rx="1.2"/><rect y="7.5" width="5.5" height="5.5" rx="1.2"/><rect x="7.5" y="7.5" width="5.5" height="5.5" rx="1.2"/></svg>',on=ui.tab==='dash';
  return '<div class="accbar">'+(ACC.user?'<button type="button" class="acc-d'+(on?' on':'')+'" data-act="dash"'+(on?' aria-current="page"':'')+'>'+gi+'Tableau de bord</button><span class="acc-me" title="'+esc(ACC.user.email)+'">'+esc(ACC.user.email)+'</span><button type="button" class="link" data-act="acclogout">Se déconnecter</button>'
      :'<span>Retrouvez vos tests sur tous vos postes</span><button type="button" class="link acc-in" data-act="acclogin">Se connecter</button>')+'</div>';""")

# ================= « Nouveau test » : écran de départ sans la page d'accueil =================
rep("manFlow:false,ro:false,roDate:'',api:","manFlow:false,ro:false,roDate:'',start:false,api:")
rep("  return '<div class=\"hero2\"><div class=\"h-txt\">","  return (ui.start?'<div class=\"start-h\">'+(ACC.user?'<button type=\"button\" class=\"link\" data-act=\"dash\">‹ Tableau de bord</button>':'')+'<h2>Nouveau test</h2><p class=\"lead\">Trois façons d\\'apporter vos chiffres : un export à déposer, une connexion directe à Piano, ou la saisie à la main. <button type=\"button\" class=\"link\" data-act=\"example\">Voir d\\'abord la démonstration</button></p></div>':'<div class=\"hero2\"><div class=\"h-txt\">")
rep("</p></div><div class=\"h-viz\">'+demoChart()+'</div></div>'\n    +'<div class=\"sec\" id=\"gst-import\"><h3 class=\"sech\">Importez vos données</h3><p class=\"secl\">Choisissez votre outil d\\'analyse : on vous montre l\\'export à préparer, puis vous déposez le fichier.</p>'",
    "</p></div><div class=\"h-viz\">'+demoChart()+'</div></div>')\n    +'<div class=\"sec'+(ui.start?' st':'')+'\" id=\"gst-import\">'+(ui.start?'':'<h3 class=\"sech\">Importez vos données</h3>')+'<p class=\"secl\">Choisissez votre outil d\\'analyse : on vous montre l\\'export à préparer, puis vous déposez le fichier. Avec Piano Analytics, l\\'outil peut aussi récupérer les chiffres lui-même, par l\\'API.</p>'")
rep("else if(name==='accnew'){state=freshState();ui.ro=false;","else if(name==='accnew'){state=freshState();ui.start=true;ui.howto=ui.howto==='manuel'?'piano':ui.howto;ui.api.open=false;ui.ro=false;")
rep("state=freshState();ui.week=null;ui.sel=null;ui.draft=null;ui.planDraft=null;ui.error='';ui.tab='resultats';}","state=freshState();ui.start=true;ui.api.open=false;ui.week=null;ui.sel=null;ui.draft=null;ui.planDraft=null;ui.error='';ui.tab='resultats';}")
rep("  else if(name==='dash'){if(!ACC.user){ui.tab='compte';}else{ui.tab='dash';","  else if(name==='dash'){ui.start=false;if(!ACC.user){ui.tab='compte';}else{ui.tab='dash';")
rep("  else if(name==='example'){","  else if(name==='example'){ui.start=false;")

# ================= accueil : l'API Piano est annoncée =================
rep("+(lg&&lg.word?lg.word:t[1])+'</button>';}).join('')+'</div>'\n    +(tab==='manuel'?manualForm()","+(lg&&lg.word?lg.word:t[1])+(t[0]==='piano'?'<span class=\"tbadge\">API</span>':'')+'</button>';}).join('')+'</div>'\n    +(tab==='manuel'?manualForm()")
rep("'<p class=\"api-go\">Sans fichier : <button type=\"button\" class=\"link\" data-act=\"apiopen\">récupérer les données directement dans Piano</button></p>'","'<div class=\"api-go\"><span><b>Sans fichier : connexion directe à Piano.</b> L\\'outil lit vos chiffres par l\\'API, puis les met à jour chaque semaine.</span><button type=\"button\" data-act=\"apiopen\">Connecter Piano</button></div>'")

# ================= onglet BigQuery =================
rep("['adobe','Adobe Analytics'],['autre','Autre outil'],['manuel','Saisie manuelle']].map(function(t){var lg=LOGOS[t[0]];","['adobe','Adobe Analytics'],['bigquery','BigQuery'],['autre','Autre outil'],['manuel','Saisie manuelle']].map(function(t){var lg=LOGOS[t[0]];")
rep("    :step(1,'<b>Créez un rapport par variation</b>","    :tab==='bigquery'?step(1,'<b>Copiez la requête modèle</b> dans l\\'éditeur BigQuery. Elle lit l\\'export Google Analytics 4 (tables <code>events_*</code>).')+step(2,'<b>Adaptez les lignes commentées</b> : les deux dates, la table, l\\'événement qui signale l\\'exposition au test et ses paramètres, vos objectifs.')+step(3,'<b>Exécutez</b> : le résultat tient en une ligne par variation, en cumul depuis le premier jour.')+step(4,'<b>Enregistrez le résultat en CSV</b> et déposez le fichier ici. Les deux dates sont dans le fichier : rien à saisir.')+step(5,'<b>Chaque semaine</b>, changez seulement la date de fin et relancez la requête.')\n    :step(1,'<b>Créez un rapport par variation</b>")
rep("+(tab==='manuel'?'':'<div class=\"imp-r\">'+(shots?","+(tab==='manuel'?'':'<div class=\"imp-r\">'+(tab==='bigquery'?'<div class=\"kicker\">La requête modèle</div><pre class=\"sql\" tabindex=\"0\">'+esc(BQ_SQL)+'</pre><p class=\"row\" style=\"margin-top:10px\"><button type=\"button\" data-act=\"sqlcopy\">'+(ui.copied==='sql'?'Requête copiée':'Copier la requête')+'</button></p><p class=\"cap\">Un visiteur vu dans deux variations est écarté ; un objectif ne compte qu\\'après la première exposition.</p>':shots?")
rep("function viewHome(){","""var BQ_SQL=[
"-- Test A/B : visiteurs cumulés depuis le premier jour, une ligne par variation.",
"DECLARE debut DATE DEFAULT DATE '2026-11-02';  -- premier jour du test",
"DECLARE fin   DATE DEFAULT DATE '2026-11-08';  -- dernier jour complet d'une semaine du test",
"",
"WITH expositions AS (",
"  SELECT",
"    user_pseudo_id,",
"    -- paramètre qui porte la variation",
"    (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'variation') AS variation,",
"    MIN(event_timestamp) AS premiere_exposition",
"  FROM `mon-projet.analytics_123456789.events_*`  -- votre table d'export GA4",
"  WHERE _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d', debut) AND FORMAT_DATE('%Y%m%d', fin)",
"    AND user_pseudo_id IS NOT NULL",
"    AND event_name = 'ab_test'  -- événement envoyé à l'exposition",
"    AND (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'test') = 'nom-du-test'",
"  GROUP BY user_pseudo_id, variation",
"),",
"visiteurs AS (  -- un visiteur vu dans deux variations est écarté",
"  SELECT",
"    user_pseudo_id,",
"    ANY_VALUE(variation) AS variation,",
"    MIN(premiere_exposition) AS premiere_exposition",
"  FROM expositions",
"  WHERE variation IS NOT NULL",
"  GROUP BY user_pseudo_id",
"  HAVING COUNT(DISTINCT variation) = 1",
"),",
"objectifs AS (  -- après la première exposition seulement",
"  SELECT",
"    v.user_pseudo_id,",
"    MAX(IF(e.event_name = 'purchase', 1, 0)) AS achat,          -- vos objectifs",
"    MAX(IF(e.event_name = 'add_to_cart', 1, 0)) AS ajout_panier",
"  FROM visiteurs AS v",
"  JOIN `mon-projet.analytics_123456789.events_*` AS e",
"    ON e.user_pseudo_id = v.user_pseudo_id",
"  WHERE e._TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d', debut) AND FORMAT_DATE('%Y%m%d', fin)",
"    AND e.event_timestamp >= v.premiere_exposition",
"  GROUP BY v.user_pseudo_id",
")",
"SELECT",
"  debut AS debut_test,",
"  fin AS fin_donnees,",
"  v.variation AS variation,",
"  COUNT(*) AS visiteurs,",
"  COUNTIF(o.achat = 1) AS visiteurs_avec_achat,",
"  COUNTIF(o.ajout_panier = 1) AS visiteurs_avec_ajout_panier",
"FROM visiteurs AS v",
"LEFT JOIN objectifs AS o USING (user_pseudo_id)",
"GROUP BY variation",
"ORDER BY variation;"].join('\\n');
function viewHome(){""")
rep("  else if(name==='shot'){ui.shot=+v;}","  else if(name==='sqlcopy'){var done=function(){ui.copied='sql';render();setTimeout(function(){if(ui.copied==='sql'){ui.copied=false;render();}},2500);};try{navigator.clipboard.writeText(BQ_SQL).then(done,function(){ui.error='Copie impossible : sélectionnez la requête et copiez-la à la main.';render();});}catch(e){ui.error='Copie impossible : sélectionnez la requête et copiez-la à la main.';}return;}\n  else if(name==='shot'){ui.shot=+v;}")

# ================= comptes : requête Piano gardée sur le poste, mise à jour à l'ouverture du tableau de bord =================
rep("function apiTok(){","""/* La requête Piano d'un test de compte reste sur ce poste (jamais sur le serveur) : table identifiant du test → requête. */
var REQ_STORE='fwoPianoReq_v1',SYN={};
function reqGet(){try{var o=JSON.parse(localStorage.getItem(REQ_STORE));return o&&typeof o==='object'&&!Array.isArray(o)?o:{};}catch(e){return {};}}
function reqSet(sid,q){sid=Math.round(Number(sid));if(!(sid>0))return;try{var m=reqGet(),k=Object.keys(m);if(q)m[sid]={q:q};else delete m[sid];if(k.length>300)return;localStorage.setItem(REQ_STORE,JSON.stringify(m));}catch(e){}}
function reqOf(sid){var r=reqGet()[sid];if(!r||!r.q)return null;try{return cleanParam(r.q);}catch(e){return null;}}
function dashPiano(){var m=reqGet();return (ACC.tests||[]).filter(function(t){return t.mine&&m[t.id]&&dashStatus(t)==='cours';});}
function dashPend(){var d=todayISO();return dashPiano().filter(function(t){return !SYN[t.id+'|'+d];});}
function syncStop(){var S=ACC.sync;if(S){ACC.sync=null;state=S.keep;ui.draft=null;ui.rawTable=null;ui.meta=null;ui.apiQ=null;}}
/* À l'ouverture du tableau de bord, chaque test en cours connecté à Piano est mis à jour s'il a une nouvelle semaine complète.
   Un test à la fois ; l'interface est verrouillée pendant ce temps ; mêmes contrôles qu'une collecte faite à la main, sinon le test est laissé tel quel. */
function dashSync(){
  if(ACC.sync||!ACC.user||!PKEY||ui.tab!=='dash')return;var list=dashPend();if(!list.length)return;
  var S={i:0,n:list.length,ok:0,ko:0,name:'',msg:'',keep:state},i=0,STOP={},alive=function(){return ACC.sync===S;};ACC.sync=S;
  var fin=function(){if(!alive())return;syncStop();ui.tab='dash';ui.error=S.msg;ui.notice=(S.ok?S.ok+' test'+(S.ok>1?'s mis':' mis')+' à jour depuis Piano.':'')+(S.ko?' '+S.ko+' test'+(S.ko>1?'s demandent':' demande')+' une vérification : ouvrez-le'+(S.ko>1?'s':'')+' pour récupérer la semaine.':'');if(S.ok)accList();else render();};
  var next=function(){if(!alive())return;if(i>=list.length||!PKEY)return fin();var t=list[i++],q=reqOf(t.id);S.i=i;S.name=t.name;SYN[t.id+'|'+todayISO()]=1;render();if(!q)return next();
    accFetch('tests/'+t.id).then(function(j){if(!alive())throw STOP;if(!j.state||!j.state.plan)throw new Error('test illisible');
        var st=cleanState({name:j.name,plan:j.state.plan,metrics:j.state.metrics,labels:j.state.labels,weeks:j.state.weeks,map:j.state.map,sid:j.id});st.api={q:q};state=st;ui.draft=null;ui.ro=false;
        var nx=apiDue();if(!nx||!st.map)return null;
        return pianoFetch(q,PKEY,nx.start,nx.end).then(function(res){if(!alive()||state!==st)throw STOP;
          ui.meta={start:nx.start,end:nx.end,src:'api',exp:''};ui.apiQ=q;ui.rawTable=res.table;var d=analyze(res.table,'Piano (API)',null);ui.draft=d;
          var g=weekGate(d),lk=lockErr(d),v=draftVis(d),nc=v&&!lk.length?notCumul(st.weeks.map(function(x){return {A:x.A.n,B:x.B.n};}).concat(v)):null,n0=st.weeks.length;
          if(res.full||d.errors.length||!g||!g.ok||lk.length||nc||!v){ui.draft=null;S.ko++;return null;}
          applyDraft();ui.tab='dash';ui.notice='';if(state!==st||st.weeks.length!==n0+1||ui.draft){ui.draft=null;S.ko++;return null;}
          return ensureBounds().then(function(){if(!alive()||state!==st)throw STOP;return accFetch('tests/'+st.sid,'PUT',accBody());}).then(function(){S.ok++;});});})
      .catch(function(e){if(e===STOP||!alive())return;if(!PKEY)S.msg=e.message;else S.ko++;})
      .then(function(){if(alive())next();});};
  next();}
function dashBar(){
  if(ACC.who!=='mes'||ACC.tests===null)return '';var S=ACC.sync;
  if(S)return '<div class="apibar due" role="status"><span><b>Mise à jour depuis Piano…</b> test '+S.i+' sur '+S.n+(S.name?' : '+esc(S.name):'')+'</span></div>';
  var pend=dashPend();if(!pend.length||PKEY)return '';
  return '<div class="apibar"><span><b>'+pend.length+' test'+(pend.length>1?'s connectés':' connecté')+' à Piano.</b> '+(pkHas()?'Saisissez votre code':'Saisissez votre clé Piano')+' pour récupérer les nouvelles semaines.</span>'
    +(pkHas()?'<div class="api-f"><div><label for="gst-pcode">Votre code</label><input id="gst-pcode" type="password" autocomplete="off" spellcheck="false"></div></div>':'<div class="api-f"><div><label for="gst-pak">Clé d\\'accès Piano</label><input id="gst-pak" type="password" autocomplete="off" spellcheck="false"></div><div><label for="gst-psk">Clé secrète</label><input id="gst-psk" type="password" autocomplete="off" spellcheck="false"></div></div>')
    +'<p class="api-err err" role="alert" hidden></p><span class="row"><button type="button" class="pri" data-act="dashkey">Mettre à jour mes tests</button></span></div>';}
function apiTok(){""")
rep("function autosave(){if(ui.ro)return;","function autosave(){if(ui.ro||ACC.sync)return;")
rep("function accSave(){\n  var body={name:state.name.trim(),state:{plan:state.plan,metrics:state.metrics,labels:state.labels,weeks:state.weeks,map:state.map||null},sum:Object.assign({u:state.plan.unit||'semaine'},summary()||{})};\n  return accFetch(state.sid?'tests/'+state.sid:'tests',state.sid?'PUT':'POST',body).then(function(j){var cs=cleanRow(j);state.sid=cs.id;",
    "function accBody(){return {name:state.name.trim(),state:{plan:state.plan,metrics:state.metrics,labels:state.labels,weeks:state.weeks,map:state.map||null},sum:Object.assign({u:state.plan.unit||'semaine'},summary()||{})};}\nfunction accSave(){\n  var body=accBody();\n  return accFetch(state.sid?'tests/'+state.sid:'tests',state.sid?'PUT':'POST',body).then(function(j){var cs=cleanRow(j);state.sid=cs.id;if(state.api)reqSet(cs.id,state.api.q);")
rep("labels:j.state.labels,weeks:j.state.weeks,map:j.state.map,sid:j.id});state=st;","labels:j.state.labels,weeks:j.state.weeks,map:j.state.map,sid:j.id});state=st;")
rep("function accOpen(id){\n  ACC.busy=true;render();","function accOpen(id){\n  syncStop();ACC.busy=true;render();")
rep("function accRoute(){\n    if(!ACC.on)return;","function accRoute(){\n    if(!ACC.on)return;syncStop();")
rep("function accList(){ACC.busy=true;return accFetch('tests').then(","function accList(){ACC.busy=true;return accFetch('tests').then(")
rep(".catch(function(e){ui.error='Liste des tests indisponible : '+e.message;}).then(function(){ACC.busy=false;render();});}",".catch(function(e){ui.error='Liste des tests indisponible : '+e.message;}).then(function(){ACC.busy=false;render();dashSync();});}")
rep("else if(name==='apioff'){delete state.api;autosave();","else if(name==='apioff'){delete state.api;if(state.sid)reqSet(state.sid,null);autosave();")
rep("function act(name,v,el){\n  ui.notice='';","function act(name,v,el){\n  if(ACC.sync)return;\n  ui.notice='';")
rep("  else if(name==='sqlcopy'){","""  else if(name==='dashkey'){var gk=function(id){var e=root.querySelector('#'+id);return e?e.value:'';},kb=el,kf=function(m){var e=root.querySelector('.api-err');if(e){e.textContent=m;e.hidden=false;}if(kb&&root.contains(kb)){kb.disabled=false;kb.textContent='Mettre à jour mes tests';}};
    if(kb){kb.disabled=true;kb.textContent='Vérification…';}
    (pkHas()?pkOpen(gk('gst-pcode')):new Promise(function(ok){ok(pkJoin(gk('gst-pak'),gk('gst-psk')));})).then(function(key){PKEY=key;render();dashSync();},function(e){kf(e.message);});return;}
  else if(name==='sqlcopy'){""")
# tableau de bord : bandeau de mise à jour et repère « Piano » sur les tests connectés
rep("  if(ACC.tests===null)return h+'<p class=\"hint\" style=\"margin-top:20px\">Chargement de vos tests…</p>';","  h+=dashBar();var rq=reqGet();\n  if(ACC.tests===null)return h+'<p class=\"hint\" style=\"margin-top:20px\">Chargement de vos tests…</p>';")
rep("<span class=\"d-n\"><b>'+esc(t.name)+'</b></span>","<span class=\"d-n\"><b>'+esc(t.name)+'</b>'+(t.mine&&rq[t.id]?'<span class=\"tbadge\" title=\"Mis à jour depuis Piano\">Piano</span>':'')+'</span>")

# test ouvert depuis le compte : sa requête Piano est retrouvée sur ce poste
rep("    var cr=cleanRow(j);ACC.mine=cr.mine;","    var cr=cleanRow(j);if(cr.mine){var rq0=reqOf(j.id);if(rq0)state.api={q:rq0};}ACC.mine=cr.mine;")

# ================= petits restes =================
# identifiant Piano retiré même quand le fichier ne contient qu'un test ; nom du test proposé sans identifiant
rep("if(a.length<2||!ids.every(function(p){return p;})||!ids.some(function(p){return p==='0'||p.length>=4;}))return a.slice();","if(!a.length||!ids.every(function(p){return p;})||!(a.length>1?ids.some(function(p){return p==='0'||p.length>=4;}):ids[0].length>=4))return a.slice();")
rep("d.name=keep?keep.name:(state.name||d.test||(fileName||'').replace(/\\.[a-z]+$/i,''));","d.name=keep?keep.name:(state.name||(d.test?optLabs([d.test])[0]:'')||(fileName||'').replace(/\\.[a-z]+$/i,''));")
# 360 px : listes de l'écran d'import
rep("#gst-app .dv-gate.ko{","@media (max-width:420px){#gst-app .dv-g select{padding-left:8px;padding-right:4px;font-size:13px}}\n#gst-app .dv-gate.ko{")
# clic pendant le chargement de la page : le bouton est rétabli au lieu de rester muet
rep("},function(e){if(apiSame(tg))fail(e.message);});\n      return;}","},function(e){if(apiSame(tg))fail(e.message);else{ui.error=e.message;render();}});\n      return;}")

# styles
rep("#gst-app .dv-gate.ko{","""#gst-app .tbadge{display:inline-block;margin-left:8px;padding:1px 7px;border-radius:999px;background:#ECF7F4;color:#0E7C5D;font-size:11px;font-weight:700;letter-spacing:.03em;vertical-align:middle;line-height:1.5}
#gst-app .start-h{margin-top:8px}#gst-app .start-h h2{font-size:26px;margin-top:6px}#gst-app .start-h .lead{margin-top:6px}#gst-app .sec.st{margin-top:8px}
#gst-app div.api-go{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 16px;margin-top:14px;padding:12px 14px;border:1px solid #1D9E75;border-radius:8px;background:#F8FBFA;font-size:14px}#gst-app div.api-go span{flex:1 1 220px;min-width:0}
#gst-app pre.sql{margin:10px 0 0;padding:12px 14px;max-height:360px;overflow:auto;background:#F8FBFA;border:1px solid var(--border);border-radius:8px;font:12px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:var(--ink);white-space:pre;tab-size:2}
#gst-app .dv-gate.ko{""",)
# alerte « non cumulé » : la dernière lecture est aussi comparée aux précédentes (un cumul ne s'arrête pas net)
rep("  return (down||(t[K-1]-t[0])/(K-1)<0.5*t[0])?{first:t[0],last:t[K-1],k:K,down:down}:null;","  var flat=K>2&&!down&&(t[K-1]-t[K-2])<0.25*(t[K-2]-t[0])/(K-2);\n  return (down||flat||(t[K-1]-t[0])/(K-1)<0.5*t[0])?{first:t[0],last:t[K-1],k:K,down:down,flat:flat?t[K-2]:0}:null;")
rep("(nc.down?'ils baissent d\\'une lecture à l\\'autre, ce qu\\'un cumul ne fait jamais':","(nc.down?'ils baissent d\\'une lecture à l\\'autre, ce qu\\'un cumul ne fait jamais':nc.flat?'dont seulement +'+nf((nc.last/nc.flat-1)*100,1)+' % depuis la lecture précédente, bien moins que les semaines d\\'avant':")
open(dst,'w',newline='').write(s);print(len(s))

src='repo/calculateur-sequentiel-v56-10.html';dst='repo/calculateur-sequentiel-v56-11.html'
s=open(src,newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(s.count(a),a[:110]); s=s.replace(a,b)
rep("VERSION='v56.10'","VERSION='v56.11'")
# H1 : le serveur de comptes ne peut plus figer l'interface (délai de 20 s) ; la mise à jour peut être arrêtée
rep("  return fetch(ACC_ROOT+path,{method:method||'GET',credentials:'same-origin',headers:h,body:body?JSON.stringify(body):undefined}).then(function(r){",
    "  var ctl=typeof AbortController==='function'?new AbortController():null,tm=ctl?setTimeout(function(){ctl.abort();},20000):0;\n  return fetch(ACC_ROOT+path,{method:method||'GET',credentials:'same-origin',headers:h,body:body?JSON.stringify(body):undefined,signal:ctl?ctl.signal:undefined}).then(function(r){clearTimeout(tm);return r;},function(e){clearTimeout(tm);throw new Error(e&&e.name==='AbortError'?'le serveur ne répond pas (20 secondes)':'connexion impossible');}).then(function(r){")
rep("function act(name,v,el){\n  if(ACC.sync)return;","function act(name,v,el){\n  if(ACC.sync){if(name==='syncstop'){syncStop();ui.tab='dash';ui.notice='Mise à jour arrêtée.';render();}return;}")
rep("+(S.name?' : '+esc(S.name):'')+'</span></div>';","+(S.name?' : '+esc(S.name):'')+'</span><span class=\"row\"><button type=\"button\" class=\"link\" data-act=\"syncstop\">Arrêter</button></span></div>';")
# M1 : l'interface de l'utilisateur est rendue telle qu'elle était (lecture seule, sélection, brouillon)
rep("function syncStop(){var S=ACC.sync;if(S){ACC.sync=null;state=S.keep;ui.draft=null;ui.rawTable=null;ui.meta=null;ui.apiQ=null;}}",
    "function syncStop(){var S=ACC.sync;if(S){ACC.sync=null;state=S.keep;var u=S.ui||{};ui.draft=u.draft||null;ui.rawTable=u.rawTable||null;ui.meta=u.meta||null;ui.apiQ=u.apiQ||null;ui.ro=!!u.ro;ui.week=u.week==null?null:u.week;ui.sel=u.sel==null?null:u.sel;}}")
rep("var S={i:0,n:list.length,ok:0,ko:0,name:'',msg:'',keep:state},","var S={i:0,n:list.length,ok:0,ko:0,net:0,name:'',msg:'',keep:state,ui:{draft:ui.draft,rawTable:ui.rawTable,meta:ui.meta,apiQ:ui.apiQ,ro:ui.ro,week:ui.week,sel:ui.sel}},")
# M4 : le test que l'utilisateur a ouvert n'est pas mis à jour dans son dos ; F4 : seules les requêtes lisibles comptent
rep("function dashPiano(){var m=reqGet();return (ACC.tests||[]).filter(function(t){return t.mine&&m[t.id]&&dashStatus(t)==='cours';});}",
    "function dashPiano(){var m=reqGet();return (ACC.tests||[]).filter(function(t){return t.mine&&m[t.id]&&dashStatus(t)==='cours'&&!!reqOf(t.id)&&!(state&&state.sid===t.id&&!ACC.sync);});}")
rep("(t.mine&&rq[t.id])sub.push('<span class=\"tbadge\"","(t.mine&&rq[t.id]&&reqOf(t.id))sub.push('<span class=\"tbadge\"")
# F3 : un test n'est marqué « vu aujourd'hui » qu'après une réponse ; panne et contrôle sont distingués. M3 : aucune exception ne laisse le verrou posé
rep("var t=list[i++],q=reqOf(t.id);S.i=i;S.name=t.name;SYN[t.id+'|'+todayISO()]=1;render();if(!q)return next();",
    "var t=list[i++],q=reqOf(t.id),mark=function(){SYN[t.id+'|'+todayISO()]=1;};S.i=i;S.name=t.name;S.seen[t.id]=1;try{render();}catch(e0){return fin();}if(!q){mark();return next();}")
rep("net:0,name:'',msg:'',keep:state,","net:0,seen:{},name:'',msg:'',keep:state,")
rep("var nx=apiDue();if(!nx||!st.map)return null;\n        return pianoFetch(q,PKEY,nx.start,nx.end).then(function(res){if(!alive()||state!==st)throw STOP;",
    "var nx=apiDue();if(!nx||!st.map){mark();return null;}\n        return pianoFetch(q,PKEY,nx.start,nx.end).then(function(res){if(!alive()||state!==st)throw STOP;mark();")
rep("      .catch(function(e){if(e===STOP||!alive())return;if(!PKEY)S.msg=e.message;else S.ko++;})","      .catch(function(e){if(e===STOP||!alive())return;if(!PKEY)S.msg=e.message;else{S.net++;S.msg='Mise à jour incomplète : '+e.message+'. Elle sera retentée à la prochaine ouverture du tableau de bord.';}})")
rep("function dashPend(){var d=todayISO();return dashPiano().filter(function(t){return !SYN[t.id+'|'+d];});}","function dashPend(){var d=todayISO(),S=ACC.sync;return dashPiano().filter(function(t){return !SYN[t.id+'|'+d]&&!(S&&S.seen[t.id]);});}")
# une panne ne relance pas la boucle dans la même visite : au plus un essai par test et par ouverture
rep("  if(ACC.sync||!ACC.user||!PKEY||ui.tab!=='dash')return;var list=dashPend();if(!list.length)return;","  if(ACC.sync||!ACC.user||!PKEY||ui.tab!=='dash')return;var now=Date.now();var list=dashPend().filter(function(t){return !(TRY[t.id]>now-60000);});if(!list.length)return;list.forEach(function(t){TRY[t.id]=now;});")
rep("var REQ_STORE='fwoPianoReq_v1',SYN={};","var REQ_STORE='fwoPianoReq_v1',SYN={},TRY={};")
# F1 : les bornes calculées ne sont écrites que dans l'état qui les a demandées
rep("  return Promise.all([fetchBounds(p,N,F),needG?fetchBounds(p1,N):null,ns>0?fetchBounds(Object.assign({},p1,{alpha:p.alpha/(2*ns)}),N):null,ng>1?fetchBounds(Object.assign({},p1,{alpha:p.alpha/ng}),N):null]).then(function(r){\n    state.bounds=r[0];","  var st0=state;\n  return Promise.all([fetchBounds(p,N,F),needG?fetchBounds(p1,N):null,ns>0?fetchBounds(Object.assign({},p1,{alpha:p.alpha/(2*ns)}),N):null,ng>1?fetchBounds(Object.assign({},p1,{alpha:p.alpha/ng}),N):null]).then(function(r){\n    if(state!==st0)return;state.bounds=r[0];")
rep("}).catch(function(e){state.bounds=state.boundsG=state.boundsS=state.boundsR=null;","}).catch(function(e){if(state!==st0)return;state.bounds=state.boundsG=state.boundsS=state.boundsR=null;")
# F2 : la table des requêtes ne se bloque plus quand elle est pleine (les plus anciennes sortent)
rep("if(q)m[sid]={q:q};else delete m[sid];if(k.length>300)return;localStorage.setItem(REQ_STORE,JSON.stringify(m));","if(q)m[sid]={q:q};else delete m[sid];k=Object.keys(m);while(k.length>300)delete m[k.shift()];localStorage.setItem(REQ_STORE,JSON.stringify(m));")
# M2 : une requête qui ne renvoie plus la colonne du test suivi est refusée
rep("  if(M.tv&&d.cTest>=0&&d.test!==M.tv)out.push(","  if(M.tv&&M.test&&d.cTest<0)out.push('Les lectures précédentes venaient d\\'une colonne de test (« '+M.test+' »), absente ici : impossible de vérifier qu\\'il s\\'agit du même test.');\n  else if(M.tv&&d.cTest>=0&&d.test!==M.tv)out.push(")
# un test du compte relié à Piano se met aussi à jour seul quand on l'ouvre (clé en mémoire)
rep("if(cr.mine){var rq0=reqOf(j.id);if(rq0)state.api={q:rq0};}","if(cr.mine){var rq0=reqOf(j.id);if(rq0){state.api={q:rq0};setTimeout(apiAuto,0);}}")
open(dst,'w',newline='').write(s);print(len(s))

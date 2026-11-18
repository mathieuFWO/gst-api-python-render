src='repo/calculateur-sequentiel-v56-11.html';dst='repo/calculateur-sequentiel-v56-12.html'
s=open(src,newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(s.count(a),a[:110]); s=s.replace(a,b)
rep("VERSION='v56.11'","VERSION='v56.12'")
# ===== semaines sautées : l'effet de référence et le volume restent ceux du plan complet, un seuil de futilité déjà affiché ne bouge plus =====
rep("for(j=0;j<k;j++)t.push(Math.min(1,LW(j)/kd));return Object.assign({},state.plan,{k:k,_t:t});}","for(j=0;j<k;j++)t.push(Math.min(1,LW(j)/kd));return Object.assign({},state.plan,{k:k,_t:t,_kd:kd});}")
rep("+(p._t?'|t'+p._t.join(','):'');}","+(p._t?'|t'+p._t.join(',')+'|'+(p._kd||''):'');}")
rep("    var ia=incs(p.sfu,p.alpha,t,null),d0=design(p);tune(info);","    /* avec des lectures sautées (_kd : durée du plan complet), l'effet attendu et l'inflation sont ceux du plan d'origine */\n    var ia=incs(p.sfu,p.alpha,t,null),d0=design(p._kd&&p._t?Object.assign({},p,{k:p._kd,_t:null,_kd:null}):p);tune(info);")
# ===== comptes : un test modifié ailleurs n'est pas écrasé =====
rep("function accSave(){\n  var body=accBody();\n  return accFetch(state.sid?'tests/'+state.sid:'tests',state.sid?'PUT':'POST',body).then(function(j){var cs=cleanRow(j);state.sid=cs.id;",
    "function accSave(){\n  var body=accBody(),st=state,chk=st.sid&&typeof st.srvN==='number'?accFetch('tests/'+st.sid).then(function(j){var n=j&&j.state&&Array.isArray(j.state.weeks)?j.state.weeks.length:-1;if(n!==st.srvN)throw new Error('ce test a été modifié ailleurs depuis son ouverture ('+(n<0?'introuvable':n+' lecture'+(n>1?'s':'')+' sur le serveur')+'). Rouvrez-le depuis le tableau de bord, puis refaites votre modification.');}):Promise.resolve();\n  return chk.then(function(){if(state!==st)throw new Error('enregistrement interrompu');return accFetch(st.sid?'tests/'+st.sid:'tests',st.sid?'PUT':'POST',body);}).then(function(j){var cs=cleanRow(j);state.sid=cs.id;state.srvN=state.weeks.length;")
rep("    var cr=cleanRow(j);if(cr.mine){var rq0=reqOf(j.id);","    var cr=cleanRow(j);state.srvN=state.weeks.length;if(cr.mine){var rq0=reqOf(j.id);")
# ===== mise à jour en cours : aucun champ ne peut modifier l'état =====
rep("root.addEventListener('change',function(e){\n  var t=e.target,d=ui.draft;","root.addEventListener('change',function(e){\n  if(ACC.sync)return;\n  var t=e.target,d=ui.draft;")
open(dst,'w',newline='').write(s);print(len(s))

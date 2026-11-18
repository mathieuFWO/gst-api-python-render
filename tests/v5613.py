src='repo/calculateur-sequentiel-v56-12.html';dst='repo/calculateur-sequentiel-v56-13.html'
s=open(src,newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(s.count(a),a[:110]); s=s.replace(a,b)
rep("VERSION='v56.12'","VERSION='v56.13'")
# A : le calendrier de semaines ne s'applique jamais au mode quotidien
rep("function PL(){var k=KL(),kd=state.plan.k,t=[],j;if(k===kd)return state.plan;","function PL(){var k=KL(),kd=state.plan.k,t=[],j;if(k===kd||U())return state.plan;")
# B : enregistrement d'un test du compte. Empreinte du contenu du serveur à l'ouverture ; tout écart refuse l'enregistrement ;
#     le résultat s'écrit sur le test enregistré, jamais sur celui qui est affiché entre-temps.
old_a=s.index("function accSave(){");old_b=s.index("function accBar(){")
s=s[:old_a]+"""function srvFp(j){var x=JSON.stringify([j&&j.name,j&&j.state]),h=5381,i;for(i=0;i<x.length;i++)h=((h<<5)+h+x.charCodeAt(i))|0;return x.length+':'+h;}
function accSave(){
  var body=accBody(),st=state,chk=Promise.resolve();
  if(st.sid)chk=accFetch('tests/'+st.sid).then(function(j){var n=j&&j.state&&Array.isArray(j.state.weeks)?j.state.weeks.length:0;
    if(typeof st.srvH==='string'){if(srvFp(j)!==st.srvH)throw new Error('ce test a été modifié ailleurs depuis son ouverture ('+n+' lecture'+(n>1?'s':'')+' sur le serveur). Rouvrez-le depuis le tableau de bord, puis refaites votre modification.');}
    else if(!confirm('Ce test existe déjà dans votre espace ('+n+' lecture'+(n>1?'s':'')+' sur le serveur). L\\'enregistrer remplacera cette version par celle de ce poste ('+st.weeks.length+' lecture'+(st.weeks.length>1?'s':'')+'). Continuer ?'))throw new Error('enregistrement annulé');});
  return chk.then(function(){if(state!==st)throw new Error('enregistrement interrompu : un autre test a été ouvert');return accFetch(st.sid?'tests/'+st.sid:'tests',st.sid?'PUT':'POST',body);})
    .then(function(j){var cs=cleanRow(j);st.sid=cs.id;st.srvH=null;if(st.api)reqSet(cs.id,st.api.q);
      return accFetch('tests/'+cs.id).then(function(j2){st.srvH=srvFp(j2);},function(){}).then(function(){if(state!==st)return;ACC.shared=cs.shared;ACC.mine=true;ACC.tests=null;ui.notice='Test « '+st.name+' » enregistré dans votre espace.';});})
    .catch(function(e){if(state===st)ui.error='Enregistrement impossible : '+e.message;}).then(render);
}
""".replace('\n',NL)+s[old_b:]
rep("    var cr=cleanRow(j);state.srvN=state.weeks.length;if(cr.mine){","    var cr=cleanRow(j);state.srvH=srvFp(j);if(cr.mine){")
# mise à jour du tableau de bord : même empreinte entre la lecture du test et son enregistrement
rep("labels:j.state.labels,weeks:j.state.weeks,map:j.state.map,sid:j.id});st.api={q:q};state=st;ui.draft=null;ui.ro=false;","labels:j.state.labels,weeks:j.state.weeks,map:j.state.map,sid:j.id});st.api={q:q};st.srvH=srvFp(j);state=st;ui.draft=null;ui.ro=false;")
rep("return ensureBounds().then(function(){if(!alive()||state!==st)throw STOP;return accFetch('tests/'+st.sid,'PUT',accBody());}).then(function(){S.ok++;});});})",
    "return ensureBounds().then(function(){if(!alive()||state!==st)throw STOP;var bd=accBody();return accFetch('tests/'+st.sid).then(function(j2){if(!alive()||state!==st)throw STOP;if(srvFp(j2)!==st.srvH){S.ko++;return;}return accFetch('tests/'+st.sid,'PUT',bd).then(function(){S.ok++;});});});});})")
# C1 : seule une panne retient un test une minute ; une clé refusée puis corrigée repart aussitôt
rep("if(!list.length)return;list.forEach(function(t){TRY[t.id]=now;});","if(!list.length)return;")
rep("else{S.net++;S.msg=","else{S.net++;TRY[t.id]=Date.now();S.msg=")
# C2 : dans un test du compte, la semaine collectée est enregistrée aussitôt
rep("{ui.notice='Semaine '+WKL()+' récupérée automatiquement depuis Piano (données jusqu\\'au '+frDate(end)+').';}}}",
    "{var nt='Semaine '+WKL()+' récupérée automatiquement depuis Piano (données jusqu\\'au '+frDate(end)+').';ui.notice=nt;if(state.sid&&ACC.user&&!ui.ro){var sv=state;ensureBounds().then(function(){return state===sv?accSave():null;}).then(function(){if(state===sv&&!ui.error){ui.notice=nt+' Enregistrée dans votre espace.';render();}});}}}}")
# C3 : fichier sans la colonne du test : refus pour une collecte automatique, confirmation explicite pour un fichier déposé
rep("  if(M.tv&&M.test&&d.cTest<0)out.push('Les lectures précédentes venaient d\\'une colonne de test (« '+M.test+' »), absente ici : impossible de vérifier qu\\'il s\\'agit du même test.');",
    "  if(M.tv&&M.test&&d.cTest<0&&!(d.sameOk&&!d.api))out.push('Les lectures précédentes venaient d\\'une colonne de test (« '+M.test+' »), absente ici : impossible de vérifier qu\\'il s\\'agit du même test.');")
rep("(lk.length?'<div class=\"err\" role=\"alert\">'+lk.map(esc).join('<br>')+'</div>':'')","(lk.length?'<div class=\"err\" role=\"alert\">'+lk.map(esc).join('<br>')+'</div>':'')+(!d.api&&state.weeks.length&&state.map&&state.map.tv&&state.map.test&&d.cTest<0&&d.mode==='instantane'?'<label class=\"dv-ck\" style=\"margin-top:10px\"><input type=\"checkbox\" data-d=\"sameOk\"'+(d.sameOk?' checked':'')+'><span>Je confirme : ce fichier ne contient que le test <b>'+esc(optLabs([state.map.tv])[0])+'</b>, celui des lectures précédentes.</span></label>':'')")
rep("else if(f==='cumOk'){","else if(f==='sameOk'){d.sameOk=t.checked;d.errors=[];}else if(f==='cumOk'){")
open(dst,'w',newline='').write(s);print(len(s))

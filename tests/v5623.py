# v56.23 : présentation du test (comptes, extension 0.4.0), organisation du compte, visuels dans le lien de partage.
s=open('repo/calculateur-sequentiel-v56-22.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(a[:70],s.count(a));s=s.replace(a,b)
# --- état
rep("function freshState(){return {v:40,name:'',","function freshState(){return {v:40,name:'',pres:{problem:'',page:'',hyp:''},")
rep("  if(o.sid!=null&&isFinite(Number(o.sid)))st.sid=Number(o.sid);\n  return st;",
    "  var PR=o.pres&&typeof o.pres==='object'?o.pres:{};st.pres={problem:str(PR.problem,2000),page:str(PR.page,160),hyp:str(PR.hyp,2000)};\n  if(o.sid!=null&&isFinite(Number(o.sid)))st.sid=Number(o.sid);\n  return st;")
# --- partage
rep("w:state.weeks,x:state.map||null,d:todayISO()});}","w:state.weeks,x:state.map||null,d:todayISO(),r:presHas()?state.pres:undefined});}")
rep("function openShared(t){","function openShared(t,pub){")
rep("weeks:o.w,map:o.x});if(!st.metrics.length||!st.weeks.length)throw new Error('lien incomplet');state=st;",
    "weeks:o.w,map:o.x,pres:o.r});if(!st.metrics.length||!st.weeks.length)throw new Error('lien incomplet');state=st;if(pub)pubLoad(st,pub);")
rep("var hm=/[#&]t=([zj][A-Za-z0-9_-]+)/.exec(location.hash||'');","var hm=/[#&]t=([zj][A-Za-z0-9_-]+)/.exec(location.hash||''),hp=/[#&]p=(\\d{1,12})\\.([a-f0-9]{48})(?:&|$)/.exec(location.hash||'');")
rep("if(hm)openShared(hm[1]);else accBoot();","if(hm)openShared(hm[1],hp?{id:+hp[1],k:hp[2]}:null);else accBoot();")
rep("encodeShare().then(function(t){ui.shareUrl=shareBase()+'#t='+t;render();})",
    "encodeShare().then(function(t){var st=state,u=shareBase()+'#t='+t;if(ACC.user&&ACC.pres&&st.sid&&ACC.mine&&st.vis&&st.vis.length)return accFetch('tests/'+st.sid+'/publink','POST').then(function(j){return /^[a-f0-9]{48}$/.test(j&&j.key)?u+'&p='+st.sid+'.'+j.key:u;},function(){return u;}).then(function(x){if(state===st){ui.shareUrl=x;render();}});ui.shareUrl=u;render();})")
rep("La personne voit la décision, les métriques et le graphique, sans pouvoir modifier.</p>'",
    "La personne voit la décision, les métriques et le graphique, sans pouvoir modifier.'+(/&p=/.test(u)?' Les visuels de la présentation, eux, sont lus sur le site tant que ce test existe dans votre espace.':'')+'</p>'")
# --- comptes
rep("var ACC={on:false,user:null,","var ACC={pres:false,org:'',orgSkip:false,on:false,user:null,")
rep("    if(!j||!j.enabled)return;ACC.on=true;","    if(!j||!j.enabled)return;ACC.on=true;ACC.pres=typeof j.v==='string'&&/^\\d+\\.\\d+\\.\\d+$/.test(j.v);try{ACC.orgSkip=localStorage.getItem('fwoOrgSkip')==='1';}catch(e){}")
rep("labels:j.state.labels,weeks:j.state.weeks,map:j.state.map,sid:j.id});state=st;\n    var cr=cleanRow(j);",
    "labels:j.state.labels,weeks:j.state.weeks,map:j.state.map,sid:j.id,pres:j.pres});state=st;st.vis=cleanVis(j.visuals);\n    var cr=cleanRow(j);")
rep("function accBody(){return {name:state.name.trim(),state:{","function accBody(){return {name:state.name.trim(),pres:state.pres,state:{")
MOD=r"""
/* v56.23 : présentation du test. Réservée aux comptes (extension 0.4.0) ; lue en lecture seule par un invité ou par le lien de partage. */
var VIS={};
function cleanVis(a){return (Array.isArray(a)?a:[]).slice(0,8).filter(function(x){return x&&typeof x==='object'&&/^[a-f0-9]{12}$/.test(x.id)&&(x.arm==='A'||x.arm==='B');}).map(function(x){return {id:x.id,arm:x.arm,w:Math.max(0,Math.round(Number(x.w))||0),h:Math.max(0,Math.round(Number(x.h))||0)};});}
function presHas(){var p=state.pres||{};return !!(p.problem||p.page||p.hyp||(state.vis&&state.vis.length));}
function pubLoad(st,pub){
  fetch(ACC_ROOT+'public/'+pub.id,{credentials:'omit',headers:{'X-FWO-Key':pub.k}}).then(function(r){if(!r.ok)throw 0;return r.json();}).then(function(j){if(state!==st)return;st.pub=pub;st.vis=cleanVis(j&&j.visuals);render();}).catch(function(){});
}
function visLoad(){
  var st=state;(st.vis||[]).forEach(function(v){if(VIS[v.id])return;VIS[v.id]='w';var h={},path,cred='same-origin';
    if(st.pub){h['X-FWO-Key']=st.pub.k;path='public/'+st.pub.id+'/visuals/'+v.id;cred='omit';}else{if(ACC.nonce)h['X-WP-Nonce']=ACC.nonce;path='tests/'+st.sid+'/visuals/'+v.id;}
    fetch(ACC_ROOT+path,{credentials:cred,headers:h}).then(function(r){if(!r.ok)throw 0;return r.blob();}).then(function(b){if(b.type!=='image/jpeg')throw 0;VIS[v.id]=URL.createObjectURL(b);}).catch(function(){VIS[v.id]='x';}).then(function(){if(state===st)render();});});
}
function visDrop(id){var u=VIS[id];if(u&&u.length>1){try{URL.revokeObjectURL(u);}catch(e){}}delete VIS[id];}
function visUpload(arm,file){
  var st=state;if(!file||ui.ro||!ACC.user)return;
  if(!/^image\/(png|jpeg)$/.test(file.type)){ui.error='Format non accepté : choisissez une image PNG ou JPG.';return render();}
  if(file.size>2097152){ui.error='Image trop lourde : 2 Mo au plus ('+(file.size/1048576).toFixed(1).replace('.',',')+' Mo ici).';return render();}
  ui.error='';ui.visBusy=arm;render();
  var go=function(){if(state!==st||!st.sid)throw new Error('enregistrez d\'abord le test dans votre espace');
    return new Promise(function(ok,ko){var fr=new FileReader();fr.onload=function(){ok(String(fr.result));};fr.onerror=function(){ko(new Error('lecture du fichier impossible'));};fr.readAsDataURL(file);})
      .then(function(d){return accFetch('tests/'+st.sid+'/visuals','POST',{arm:arm,data:d});}).then(function(j){st.vis=cleanVis(j.visuals);});};
  (st.sid?Promise.resolve():accSave()).then(go).catch(function(e){if(state===st)ui.error='Visuel non ajouté : '+e.message;}).then(function(){ui.visBusy=null;render();});
}
function presVis(arm,ro){
  var L=(state.vis||[]).filter(function(v){return v.arm===arm;}),h='<div class="pv-c"><div class="pv-h"><b>'+esc(state.labels[arm].indexOf(arm)===0?state.labels[arm]:arm+' · '+state.labels[arm])+'</b><span class="hint">'+L.length+' visuel'+(L.length>1?'s':'')+'</span></div>';
  L.forEach(function(v,i){var u=VIS[v.id];h+='<figure class="pv-f">'+(u&&u.length>1?'<img src="'+esc(u)+'" alt="Visuel '+(i+1)+' de la variation '+arm+'"'+(v.w&&v.h?' width="'+v.w+'" height="'+v.h+'"':'')+'>':'<div class="pv-w">'+(u==='x'?'Visuel indisponible':'Chargement…')+'</div>')+(ro?'':'<figcaption><button type="button" class="link" data-act="visdel" data-v="'+v.id+'">Retirer ce visuel</button></figcaption>')+'</figure>';});
  if(!ro&&L.length<4)h+='<button type="button" class="pv-add" data-act="vispick" data-v="'+arm+'"'+(ui.visBusy?' disabled':'')+'>'+(ui.visBusy===arm?'Envoi en cours…':'+ Ajouter un visuel')+'</button>';
  if(ro&&!L.length)h+='<p class="hint">Aucun visuel.</p>';
  return h+'</div>';
}
function viewPres(){
  var p=state.pres;if(state.sid&&state.vis&&state.vis.length)visLoad();
  return '<div class="card pres"><div class="kicker">Présentation du test</div><h3>Ce que vous testez, et pourquoi</h3>'
    +'<label for="gst-pp">Le problème constaté</label><textarea id="gst-pp" rows="3" maxlength="2000" data-f="pres" data-v="problem">'+esc(p.problem)+'</textarea>'
    +'<label for="gst-pg">Page ou parcours concerné</label><input id="gst-pg" maxlength="160" data-f="pres" data-v="page" value="'+esc(p.page)+'">'
    +'<label for="gst-ph">L\'hypothèse</label><textarea id="gst-ph" rows="4" maxlength="2000" data-f="pres" data-v="hyp">'+esc(p.hyp)+'</textarea>'
    +'<p class="hint">Structure conseillée : Si [le changement], alors [l\'effet attendu], parce que [la raison]. Vous pouvez coller votre hypothèse telle quelle.</p>'
    +'<h4>Visuels des variations</h4>'+(state.sid?'<div class="pv">'+presVis('A',false)+presVis('B',false)+'</div><p class="hint">PNG ou JPG, 2 Mo par image, 4 visuels par variation. Ils sont enregistrés dans votre espace.</p>':'<p class="hint">Enregistrez d\'abord la présentation : vous pourrez ensuite ajouter les visuels de chaque variation.</p>')
    +'<p class="row" style="margin-top:20px"><button type="button" class="pri" data-act="pressave">Enregistrer la présentation</button></p></div>';
}
function presRO(){
  if(!presHas())return '';var p=state.pres,any=state.vis&&state.vis.length;if(any&&(state.sid||state.pub))visLoad();
  var blk=function(t,v){return v?'<div class="pr-b"><span class="kicker">'+t+'</span><p>'+esc(v)+'</p></div>':'';};
  return '<details class="card pres ro"'+(ui.presOpen===false?'':' open')+'><summary><span class="kicker">Présentation du test</span><span class="pr-s">Ce que l\'on teste, et pourquoi</span></summary>'
    +blk('Le problème constaté',p.problem)+blk('Page ou parcours concerné',p.page)+blk('L\'hypothèse',p.hyp)+(any?'<div class="pv">'+presVis('A',true)+presVis('B',true)+'</div>':'')+'</details>';
}
function orgCard(inAccount){
  if(!ACC.user||!ACC.pres)return '';var has=!!ACC.user.org;
  if(!inAccount&&(has||ACC.orgSkip))return '';
  return '<div class="card org"'+(inAccount?' style="margin-top:16px"':'')+'><h3>'+(inAccount?'Votre organisation':'Pour quelle organisation travaillez-vous\u00a0?')+'</h3><p class="hint" style="margin-top:6px">Son nom apparaîtra sur vos rapports. Facultatif.</p>'
    +'<div class="row" style="margin-top:12px;align-items:flex-end"><div class="grow"><label for="gst-org">Nom de l\'organisation</label><input id="gst-org" maxlength="120" data-f="org" value="'+esc(ACC.org||ACC.user.org||'')+'" autocomplete="organization"></div><button type="button" class="pri" data-act="orgsave">Enregistrer</button>'+(inAccount?'':'<button type="button" class="link" data-act="orgskip">Plus tard</button>')+'</div></div>';
}
"""
rep("\nfunction accBody(){",MOD+"\nfunction accBody(){")
# --- tableau de bord et compte
rep("<p class=\"row\" style=\"margin-top:16px\"><button type=\"button\" data-act=\"acclogout\">Se déconnecter</button><button type=\"button\" class=\"danger\" data-act=\"accdelete\">Supprimer mon compte et mes tests</button></p></div>';",
    "<p class=\"row\" style=\"margin-top:16px\"><button type=\"button\" data-act=\"acclogout\">Se déconnecter</button><button type=\"button\" class=\"danger\" data-act=\"accdelete\">Supprimer mon compte et mes tests</button></p></div>'+orgCard(true);")
rep("  h+='<div class=\"dash-h\"><div><h2>'+(ACC.who==='mes'?'Mes tests':'Partagés avec moi')+'</h2>","  h+=orgCard(false)+'<div class=\"dash-h\"><div><h2>'+(ACC.who==='mes'?'Mes tests':'Partagés avec moi')+'</h2>")
# --- onglets et rendu
rep("+[['resultats','Résultats'],['donnees','Données et métriques'],['plan','Plan']].map(function(t){return '<button type=\"button\" role=\"tab\" aria-selected=\"'+(ui.tab===t[0])+'\" class=\"'+(ui.tab===t[0]?'on':'')+'\" data-act=\"tab\" data-v=\"'+t[0]+'\">'+t[1]+'</button>';}).join('')",
    "+(ACC.user&&ACC.pres?[['pres','Présentation<span class=\"nw\">Nouveau</span>']]:[]).concat([['resultats','Résultats'],['donnees','Données et métriques'],['plan','Plan']]).map(function(t){return '<button type=\"button\" role=\"tab\" aria-selected=\"'+(ui.tab===t[0])+'\" class=\"'+(ui.tab===t[0]?'on':'')+'\" data-act=\"tab\" data-v=\"'+t[0]+'\">'+t[1]+'</button>';}).join('')")
rep("ui.tab==='compte'?viewLogin():ui.ro?viewResults():ui.tab==='donnees'?viewData():","ui.tab==='compte'?viewLogin():ui.ro?presRO()+viewResults():ui.tab==='pres'&&ACC.user&&ACC.pres?viewPres():ui.tab==='donnees'?viewData():")
# --- actions
rep("  else if(name==='dash'){ui.start=false;",
"""  else if(name==='pressave'){if(!state.name.trim()){ui.error='Donnez un nom au test avant de l\\'enregistrer.';}else{ui.error='';autosave();accSave();return;}}
  else if(name==='vispick'){var vi=document.createElement('input');vi.type='file';vi.accept='image/png,image/jpeg';vi.onchange=function(){visUpload(v,vi.files&&vi.files[0]);};vi.click();return;}
  else if(name==='visdel'){var vst=state;if(!vst.sid||ui.ro)return;accFetch('tests/'+vst.sid+'/visuals/'+v,'DELETE').then(function(j){visDrop(v);vst.vis=cleanVis(j.visuals);},function(e){if(state===vst)ui.error='Retrait impossible : '+e.message;}).then(render);return;}
  else if(name==='orgsave'){var og=String(ACC.org||(ACC.user&&ACC.user.org)||'').trim().slice(0,120);accFetch('me','POST',{org:og}).then(function(j){if(j&&j.user&&ACC.user){ACC.user.org=String(j.user.org||'');ACC.org='';ui.notice=ACC.user.org?'Organisation enregistrée.':'';}},function(e){ui.error='Enregistrement impossible : '+e.message;}).then(render);return;}
  else if(name==='orgskip'){ACC.orgSkip=true;try{localStorage.setItem('fwoOrgSkip','1');}catch(e){}}
  else if(name==='dash'){ui.start=false;""")
rep("root.addEventListener('input',function(e){var t=e.target;",
    "root.addEventListener('input',function(e){var t=e.target;if(t&&t.getAttribute){var pf=t.getAttribute('data-f');if(pf==='pres'&&!ui.ro&&state.pres&&/^(problem|page|hyp)$/.test(t.getAttribute('data-v'))){state.pres[t.getAttribute('data-v')]=String(t.value).slice(0,t.getAttribute('data-v')==='page'?160:2000);return;}if(pf==='org'){ACC.org=String(t.value).slice(0,120);return;}}")
rep("  if(t.getAttribute('data-f')==='accemail'){ACC.email=t.value;return;}","  if(t.getAttribute('data-f')==='pres'){autosave();return;}\n  if(t.getAttribute('data-f')==='org')return;\n  if(t.getAttribute('data-f')==='accemail'){ACC.email=t.value;return;}")
# --- styles
CSS="""#gst-app .tabs .nw{margin-left:8px;padding:1px 7px;border-radius:999px;background:#E6F2F9;color:#005a88;font-size:10.5px;font-weight:700;letter-spacing:.04em;vertical-align:1px}
#gst-app .pres label{margin-top:16px;font-size:13px}#gst-app .pres textarea,#gst-app .pres input{width:100%;font:inherit;font-size:15px;line-height:1.5;color:var(--ink);background:#fff;border:1px solid var(--line);border-radius:8px;padding:10px 12px;box-sizing:border-box}#gst-app .pres textarea{resize:vertical;min-height:84px}#gst-app .pres h4{margin:24px 0 10px;font-size:15px}#gst-app .pres>.hint{margin-top:8px}#gst-app .pres .row button,#gst-app .card.org .row button{min-height:44px}
#gst-app .pv{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}#gst-app .pv-h{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin-bottom:8px}#gst-app .pv-f{margin:0 0 10px;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:#fff}#gst-app .pv-f img{display:block;width:100%;height:auto;max-height:440px;object-fit:contain;background:#F4F6F6}#gst-app .pv-f figcaption{padding:6px 10px;border-top:1px solid var(--line);text-align:right}#gst-app .pv-f figcaption .link{min-height:44px}#gst-app .pv-w{display:grid;place-items:center;min-height:120px;color:#5b5f60;font-size:13px;background:#F4F6F6}
#gst-app button.pv-add{display:block;width:100%;min-height:52px;border:1px dashed #1D9E75;border-radius:10px;background:#F2FAF7;color:#0E7C5D;font-weight:700}#gst-app button.pv-add:disabled{opacity:.6}
#gst-app details.pres.ro{margin-bottom:16px}#gst-app details.pres.ro summary{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 12px;cursor:pointer;min-height:44px;align-content:center}#gst-app .pr-s{font-family:var(--ft);font-weight:600;font-size:18px;color:var(--ink)}#gst-app .pr-b{margin-top:14px}#gst-app .pr-b p{margin:4px 0 0;white-space:pre-wrap;color:var(--ink)}#gst-app details.pres.ro .pv{margin-top:16px}
#gst-app .card.org{margin-top:20px;border-color:#BFE6D8;background:#F2FAF7}#gst-app .card.org input{width:100%;box-sizing:border-box}
@media (max-width:700px){#gst-app .pv{grid-template-columns:minmax(0,1fr)}}
#gst-app .dash-h{"""
rep("#gst-app .dash-h{",CSS)
rep("v56.22","v56.23")
open('repo/calculateur-sequentiel-v56-23.html','w',newline='').write(s);print(len(s))

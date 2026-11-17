src='repo/calculateur-sequentiel-v56-7.html';dst='repo/calculateur-sequentiel-v56-8.html'
s=open(src,newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(s.count(a),a[:110]); s=s.replace(a,b)
rep("VERSION='v56.7'","VERSION='v56.8'")

# ================= API Piano : cœur =================
rep("function readFile(f){","""/* ---------- API Piano ----------
   Règles de sécurité : la clé ne va qu'à PIANO_URL (adresse fixe, jamais celle collée), dans un en-tête, jamais dans une adresse ;
   elle n'est ni dans state, ni dans un lien de partage, ni dans un compte, ni réécrite dans la page. En mémoire le temps de la visite (PKEY) ;
   sur l'appareil seulement chiffrée (AES-GCM, clé dérivée du code par PBKDF2). La réponse de Piano est une donnée non fiable : elle passe par le même contrôle qu'un CSV. */
var PIANO_URL='https://api.atinternet.io/v3/data/getData',PKEY='',PK_STORE='fwoPianoCle_v1',PTRY={};
function cleanParam(o){
  if(!o||typeof o!=='object'||Array.isArray(o))throw new Error('Requête Piano illisible.');
  var id=/^-?[A-Za-z0-9_.:~-]{1,80}$/,cols=(Array.isArray(o.columns)?o.columns:[]).filter(function(c){return typeof c==='string'&&id.test(c)&&c[0]!=='-';}).slice(0,25);
  if(cols.length<3)throw new Error('La requête doit contenir au moins trois colonnes : la variation, les visiteurs et une métrique.');
  var sp=o.space&&typeof o.space==='object'?o.space:{},pos=function(x){return typeof x==='number'&&x>0&&x<1e12&&x===Math.round(x);},S=(Array.isArray(sp.s)?sp.s:[]).filter(pos).slice(0,20),L=(Array.isArray(sp.l2s)?sp.l2s:[]).filter(function(x){return x&&pos(x.s)&&typeof x.l2==='number'&&x.l2>=0&&x.l2<1e9&&x.l2===Math.round(x.l2);}).slice(0,20).map(function(x){return {s:x.s,l2:x.l2};});
  if(!S.length&&!L.length)throw new Error('La requête ne dit pas sur quel site lire les données (« space »).');
  var r={columns:cols,space:S.length?{s:S}:{l2s:L},'max-results':1000,'page-num':1,options:{}};
  var so=(Array.isArray(o.sort)?o.sort:[]).filter(function(c){return typeof c==='string'&&id.test(c);}).slice(0,5);if(so.length)r.sort=so;
  if(o.filter&&typeof o.filter==='object'){var fs=JSON.stringify(o.filter);if(fs.length>4000)throw new Error('Le filtre de la requête est trop long.');r.filter=JSON.parse(fs);}
  if(o.options&&typeof o.options==='object')Object.keys(o.options).slice(0,10).forEach(function(k){if(/^[a-z_]{1,40}$/.test(k)&&typeof o.options[k]==='boolean')r.options[k]=o.options[k];});
  return r;}
function pianoParam(raw){
  raw=String(raw||'').trim();if(!raw)throw new Error('Collez l\\'adresse copiée dans Piano (« Copier l\\'URL API (GET) »).');if(raw.length>12000)throw new Error('Adresse trop longue.');
  var js=raw;
  if(raw[0]!=='{'){var u;try{u=new URL(raw);}catch(e){throw new Error('Adresse illisible : collez l\\'adresse complète copiée dans Piano.');}
    if(u.protocol!=='https:'||u.hostname!=='api.atinternet.io'||u.port||u.username||u.password||u.pathname!=='/v3/data/getData')throw new Error('Cette adresse n\\'est pas celle de l\\'API Piano (https://api.atinternet.io/v3/data/getData). Par sécurité, la clé n\\'est envoyée nulle part ailleurs.');
    js=u.searchParams.get('param')||'';}
  var o;try{o=JSON.parse(js);}catch(e){throw new Error('Requête illisible : collez l\\'adresse complète copiée dans Piano.');}
  return cleanParam(o);}
function pianoTable(j){
  var df=j&&(j.DataFeed||j.dataFeed);if(Array.isArray(df))df=df[0];if(!df||typeof df!=='object')throw new Error('Réponse de Piano inattendue.');
  var rows=df.Rows||df.rows,cols=df.Columns||df.columns;if(!Array.isArray(rows))throw new Error('Réponse de Piano inattendue.');
  if(!rows.length)throw new Error('Piano ne renvoie aucune ligne sur cette période : vérifiez la date de début du test et le filtre de la requête.');
  var names=Array.isArray(cols)&&cols.length?cols.slice(0,40).map(function(c){return String((c&&(c.Name||c.name))||'');}):(Array.isArray(rows[0])?rows[0].map(function(x,i){return String(i);}):Object.keys(rows[0]||{}).slice(0,40));
  var seen={},head=names.map(function(nm,i){var c=Array.isArray(cols)?cols[i]:null,l=String((c&&(c.Label||c.label))||nm||('Colonne '+(i+1))).replace(/[\\r\\n\\t]+/g,' ').trim().slice(0,120)||('Colonne '+(i+1));while(seen[l])l+=' ('+(i+1)+')';seen[l]=1;return l;});
  if(head.length<3)throw new Error('La requête doit renvoyer au moins trois colonnes.');
  var cell=function(v){return v==null?'':(typeof v==='number'?(isFinite(v)?String(v):''):(typeof v==='string'||typeof v==='boolean'?String(v).slice(0,300):''));};
  var t=[head];rows.slice(0,1000).forEach(function(r){if(Array.isArray(r))t.push(names.map(function(n,i){return cell(r[i]);}));else if(r&&typeof r==='object')t.push(names.map(function(n){return cell(r[n]);}));});
  if(t.length<3)throw new Error('Piano renvoie moins de deux lignes : il en faut une par variation.');
  return {table:t,full:rows.length>=1000};}
function pianoFetch(q,key,start,end){
  var p=JSON.parse(JSON.stringify(q));p.period={p1:[{type:'D',start:start,end:end}]};
  var ctl=new AbortController(),tm=setTimeout(function(){ctl.abort();},20000);
  return fetch(PIANO_URL+'?param='+encodeURIComponent(JSON.stringify(p)),{method:'GET',headers:{'x-api-key':key},mode:'cors',credentials:'omit',cache:'no-store',redirect:'error',referrerPolicy:'no-referrer',signal:ctl.signal})
    .then(function(r){return r.text().then(function(t){clearTimeout(tm);
      if(r.status===401||r.status===403)throw new Error('Piano refuse cette clé (erreur '+r.status+') : vérifiez la clé d\\'accès, la clé secrète, et que la clé donne bien accès à ce site.');
      if(r.status===429)throw new Error('Piano limite le nombre d\\'appels : réessayez dans quelques minutes.');
      if(t.length>3e6)throw new Error('Réponse de Piano trop volumineuse : filtrez la requête sur votre test.');
      var j=null;try{j=JSON.parse(t);}catch(e){}
      if(!r.ok){var m=j&&(j.ErrorMessage||j.errorMessage||j.message);throw new Error('Piano a répondu par une erreur ('+r.status+')'+(typeof m==='string'?' : '+m.replace(/[\\r\\n\\t]+/g,' ').slice(0,200):'.'));}
      if(!j)throw new Error('Réponse de Piano illisible.');return pianoTable(j);});},
      function(e){clearTimeout(tm);throw new Error(e&&e.name==='AbortError'?'Piano ne répond pas (20 secondes) : réessayez.':'Connexion à Piano impossible : vérifiez votre connexion, ou un bloqueur de requêtes.');});}
function pkJoin(a,b){a=String(a||'').trim();b=String(b||'').trim();var re=/^[\\x21-\\x7E]{6,200}$/;if(!re.test(a)||!re.test(b))throw new Error('Saisissez la clé d\\'accès et la clé secrète de Piano.');return a+'_'+b;}
function pkB64(buf){var x='';new Uint8Array(buf).forEach(function(c){x+=String.fromCharCode(c);});return btoa(x);}
function pkBin(x){var b=atob(String(x||'')),u=new Uint8Array(b.length);for(var i=0;i<b.length;i++)u[i]=b.charCodeAt(i);return u;}
function pkDerive(code,salt){return crypto.subtle.importKey('raw',new TextEncoder().encode(code),'PBKDF2',false,['deriveKey']).then(function(k){return crypto.subtle.deriveKey({name:'PBKDF2',salt:salt,iterations:600000,hash:'SHA-256'},k,{name:'AES-GCM',length:256},false,['encrypt','decrypt']);});}
function pkSeal(key,code){if(!(window.crypto&&crypto.subtle))return Promise.reject(new Error('Ce navigateur ne permet pas de chiffrer la clé : elle n\\'a pas été mémorisée.'));
  var salt=crypto.getRandomValues(new Uint8Array(16)),iv=crypto.getRandomValues(new Uint8Array(12));
  return pkDerive(code,salt).then(function(k){return crypto.subtle.encrypt({name:'AES-GCM',iv:iv},k,new TextEncoder().encode(key));}).then(function(c){localStorage.setItem(PK_STORE,JSON.stringify({v:1,s:pkB64(salt),i:pkB64(iv),c:pkB64(c)}));});}
function pkOpen(code){var o=null;try{o=JSON.parse(localStorage.getItem(PK_STORE));}catch(e){}
  if(!o||o.v!==1||!(window.crypto&&crypto.subtle))return Promise.reject(new Error('Aucune clé mémorisée sur cet appareil.'));
  var bad=function(){throw new Error('Code incorrect.');};
  try{return pkDerive(String(code||''),pkBin(o.s)).then(function(k){return crypto.subtle.decrypt({name:'AES-GCM',iv:pkBin(o.i)},k,pkBin(o.c));}).then(function(p){return new TextDecoder().decode(p);},bad);}catch(e){return Promise.reject(new Error('Code incorrect.'));}}
function pkHas(){try{return !!localStorage.getItem(PK_STORE);}catch(e){return false;}}
function pkForget(){PKEY='';try{localStorage.removeItem(PK_STORE);}catch(e){}}
/* Prochaine lecture possible : la dernière semaine complète écoulée, sans dépasser la durée prévue. */
function apiNext(start){
  var n=state.weeks.length,st=n?state.plan.startDate:start,y=addDays(todayISO(),-1),days=dayDiff(st,y)+1;if(!(days>=7))return null;
  var w=Math.floor(days/7);if(n)w=Math.min(w,state.plan.k);return {start:st,end:addDays(st,7*w-1),w:w};}
function apiDue(){
  if(!state.api||!state.weeks.length||ui.ro||state.plan.unit==='jour'||ui.draft)return null;var nx=apiNext(),last=state.weeks[state.weeks.length-1];
  if(!nx||nx.w<=WKL()||(last.end&&dayDiff(last.end,nx.end)<7))return null;return nx;}
function apiShow(res,q,start,end,auto){
  ui.error='';ui.notice='';ui.meta={start:start,end:end,src:'api',exp:''};ui.apiQ=q;ui.rawTable=res.table;ui.draft=analyze(res.table,'Piano (API)',null);ui.tab='donnees';ui.api.open=false;
  var d=ui.draft;if(res.full)d.errors.push('Piano a renvoyé 1 000 lignes, le maximum demandé : des lignes peuvent manquer. Filtrez la requête sur votre test dans Piano, puis recollez l\\'adresse.');
  if(auto&&state.map&&!d.errors.length){var g=weekGate(d),lk=lockErr(d),v=draftVis(d),nc=v&&!lk.length?notCumul(state.weeks.map(function(x){return {A:x.A.n,B:x.B.n};}).concat(v)):null;
    if(g&&g.ok&&!lk.length&&!nc&&v){var n0=state.weeks.length;applyDraft();if(state.weeks.length===n0+1&&!ui.draft){ui.notice='Semaine '+WKL()+' récupérée automatiquement depuis Piano (données jusqu\\'au '+frDate(end)+').';}}}
  render();}
function apiAuto(){var nx=apiDue();if(!nx||!PKEY)return;var tk=state.name+'|'+nx.end;if(PTRY[tk])return;PTRY[tk]=1;
  pianoFetch(state.api.q,PKEY,nx.start,nx.end).then(function(res){if(apiDue())apiShow(res,state.api.q,nx.start,nx.end,true);},function(e){ui.error='Collecte automatique depuis Piano impossible. '+e.message;render();});}
function apiBar(){
  if(!state.api||!state.weeks.length||ui.ro||ui.draft||(ui.tab!=='resultats'&&ui.tab!=='donnees'))return '';
  var nx=apiDue(),lk='<svg aria-hidden="true" width="16" height="16" viewBox="0 0 22 22" style="flex:none"><rect x="4" y="10" width="14" height="9" rx="2" fill="none" stroke="#0E7C5D" stroke-width="2"/><path d="M7.5 10V7a3.5 3.5 0 017 0v3" fill="none" stroke="#0E7C5D" stroke-width="2" stroke-linecap="round"/></svg>',off='<button type="button" class="link" data-act="apioff">Déconnecter Piano de ce test</button>'+(pkHas()?'<button type="button" class="link" data-act="apiforget">Oublier la clé mémorisée</button>':'');
  if(!nx){var n1=apiNext(),done=WKL()>=state.plan.k;return '<div class="apibar">'+lk+'<span><b>Piano connecté.</b> '+(done?'Toutes les lectures prévues sont faites.':'Prochaine collecte automatique à partir du '+frDate(addDays(state.plan.startDate,7*(Math.max(WKL(),n1?n1.w:0)+1)))+'.')+'</span><span class="row">'+off+'</span></div>';}
  var ask=PKEY?'':(pkHas()?'<div class="api-f"><div><label for="gst-pcode">Votre code</label><input id="gst-pcode" type="password" autocomplete="off" spellcheck="false"></div></div>'
    :'<div class="api-f"><div><label for="gst-pak">Clé d\\'accès Piano</label><input id="gst-pak" type="password" autocomplete="off" spellcheck="false"></div><div><label for="gst-psk">Clé secrète</label><input id="gst-psk" type="password" autocomplete="off" spellcheck="false"></div></div>');
  return '<div class="apibar due">'+lk+'<span><b>Nouvelle semaine complète disponible dans Piano</b> : semaine '+nx.w+', données jusqu\\'au '+frDate(nx.end)+'.</span>'+ask+'<p class="api-err err" role="alert" hidden></p><span class="row"><button type="button" class="pri" data-act="apiupd">Récupérer la semaine '+nx.w+'</button>'+off+'</span></div>';}
function apiForm(){
  var a=ui.api,n=state.weeks.length;
  return '<div class="kicker">2 · Connectez Piano</div><div class="apif">'
    +'<div><label for="gst-purl">Adresse de la requête</label><textarea id="gst-purl" data-api="url" rows="3" spellcheck="false" placeholder="https://api.atinternet.io/v3/data/getData?param=…">'+esc(a.url)+'</textarea><p class="hint">Dans Piano, Data Query : même tableau que pour l\\'export (une ligne par variation), puis Partager, « Copier l\\'URL API (GET) ». La période de la requête est remplacée par celle du test.</p></div>'
    +(n?'':'<div><label for="gst-pstart">Date de début du test</label><input id="gst-pstart" type="date" data-api="start" value="'+esc(a.start)+'" max="'+addDays(todayISO(),-7)+'"></div>')
    +'<div class="api-f"><div><label for="gst-pak">Clé d\\'accès Piano</label><input id="gst-pak" type="password" autocomplete="off" spellcheck="false"></div><div><label for="gst-psk">Clé secrète</label><input id="gst-psk" type="password" autocomplete="off" spellcheck="false"></div></div>'
    +'<fieldset class="api-mem"><legend>Mémoriser la clé ?</legend><label><input type="radio" name="gst-pmem" data-api="mem" value="non"'+(a.mem!=='code'?' checked':'')+'><span><b>Non</b> : gardée le temps de cette visite, à ressaisir ensuite.</span></label><label><input type="radio" name="gst-pmem" data-api="mem" value="code"'+(a.mem==='code'?' checked':'')+'><span><b>Sur cet appareil, chiffrée par un code</b> que vous choisissez : la collecte se fait ensuite en saisissant ce code.</span></label>'
    +'<div class="api-code"'+(a.mem==='code'?'':' hidden')+'><label for="gst-pcode">Code (8 caractères au moins)</label><input id="gst-pcode" type="password" autocomplete="new-password" spellcheck="false"></div></fieldset>'
    +'<p class="api-err err" role="alert" hidden></p>'
    +'<p class="row"><button type="button" class="pri" data-act="apigo">Récupérer les données</button><button type="button" data-act="apiclose">Annuler</button></p>'
    +'<ul class="api-sec"><li>La clé va directement de votre navigateur à Piano. Elle ne passe par aucun serveur FWOptimisation et n\\'entre ni dans un lien de partage, ni dans votre compte.</li><li>Utilisez une clé créée pour cet usage, limitée au site du test et avec une date d\\'expiration.</li><li>Sur un poste partagé, ne mémorisez pas la clé.</li></ul></div>';}
function readFile(f){""")

# état de l'interface, nettoyage de l'état
rep("manFlow:false,ro:false,roDate:''};","manFlow:false,ro:false,roDate:'',api:{open:false,url:'',start:'',mem:'non'},apiQ:null};")
rep("var M=o.map&&typeof o.map==='object'?o.map:null;if(M)st.map=","if(o.api&&typeof o.api==='object'&&o.api.q){try{st.api={q:cleanParam(o.api.q)};}catch(e){}}\n  var M=o.map&&typeof o.map==='object'?o.map:null;if(M)st.map=")

# un fichier déposé n'est plus un import par API
rep("ui.error='';ui.notice='';ui.meta=fileMeta(text,name,lm);","ui.error='';ui.notice='';ui.apiQ=null;ui.meta=fileMeta(text,name,lm);")
# brouillon venu de l'API : période sûre, dates non modifiables
rep("d.endTyped=!!(keep&&keep.endTyped);","d.api=M.src==='api';d.endTyped=!!(keep&&keep.endTyped);")
rep("function endNeed(d){return d.mode==='instantane'&&!d.endFromFile&&d.endSrc!=='entete'&&!d.endTyped;}","function endNeed(d){return d.mode==='instantane'&&!d.endFromFile&&d.endSrc!=='entete'&&d.endSrc!=='api'&&!d.endTyped;}")
rep("function srcNote(d){var e=d.endSrc,s=d.startSrc;","function srcNote(d){var e=d.endSrc,s=d.startSrc;\n  if(e==='api')return ' Période demandée à Piano : pour la changer, relancez la collecte.';")
rep("data-d=\"startDate\" value=\"'+esc(d.startDate)+'\"></div>')","data-d=\"startDate\" value=\"'+esc(d.startDate)+'\"'+(d.api?' disabled':'')+'></div>')")
rep("data-d=\"endDate\" value=\"'+esc(d.endDate)+'\" max=\"'+addDays(todayISO(),-1)+'\">","data-d=\"endDate\" value=\"'+esc(d.endDate)+'\" max=\"'+addDays(todayISO(),-1)+'\"'+(d.api?' disabled':'')+'>")
# après import : la requête (sans la clé) est gardée avec le test, sur ce poste seulement
rep("  if(replace){state.plan.k=d.k;state.plan.startDate=d.startDate;}else if(LG0","  if(d.api&&ui.apiQ)state.api={q:ui.apiQ};\n  if(replace){state.plan.k=d.k;state.plan.startDate=d.startDate;}else if(LG0")
rep("ui.draft=null;ui.rawTable=null;ui.week=null;ui.sel=null;ui.tab='resultats';ui.notice=res.weeks.length+' semaine(s) de données chargée(s).';","ui.draft=null;ui.rawTable=null;ui.apiQ=null;ui.week=null;ui.sel=null;ui.tab='resultats';ui.notice=res.weeks.length+' semaine(s) de données chargée(s).';")

# rendu : bandeau de collecte, formulaire dans le bloc d'import (onglet Piano)
rep("root.innerHTML=finalize(accBar()+head()+(","root.innerHTML=finalize(accBar()+head()+apiBar()+(")
rep("+'<div class=\"imp-d\"><div class=\"kicker\">2 · Déposez le fichier</div>","+'<div class=\"imp-d\">'+(tab==='piano'&&ui.api.open?apiForm()+'</div>':'<div class=\"kicker\">2 · Déposez le fichier</div>")
rep("Vos chiffres ne quittent pas votre poste.</p></div>')","Vos chiffres ne quittent pas votre poste.</p>'+(tab==='piano'?'<p class=\"api-go\">Sans fichier : <button type=\"button\" class=\"link\" data-act=\"apiopen\">récupérer les données directement dans Piano</button></p>':'')+'</div>'))")
# chargement d'un test : collecte automatique si la clé est déjà en mémoire
rep("  if(state.metrics.length)ensureBounds();render();\n}\n\n/* ---------- rendu ---------- */","  if(state.metrics.length)ensureBounds();render();apiAuto();\n}\n\n/* ---------- rendu ---------- */")

# actions
rep("  else if(name==='shot'){ui.shot=+v;}","""  else if(name==='apiopen'){ui.api.open=true;}
  else if(name==='apiclose'){ui.api.open=false;}
  else if(name==='apioff'){delete state.api;autosave();ui.notice='Piano est déconnecté de ce test. La clé n\\'a pas été modifiée.';}
  else if(name==='apiforget'){pkForget();ui.notice='La clé Piano mémorisée sur cet appareil est effacée.';}
  else if(name==='apigo'||name==='apiupd'){
    var gv=function(id){var e=root.querySelector('#'+id);return e?e.value:'';},btn=el,lab=btn?btn.textContent:'',fail=function(m){var e=root.querySelector('.api-err');if(e){e.textContent=m;e.hidden=false;}else{ui.error=m;render();}if(btn&&root.contains(btn)){btn.disabled=false;btn.textContent=lab;}},busy=function(){var e=root.querySelector('.api-err');if(e)e.hidden=true;if(btn){btn.disabled=true;btn.textContent='Connexion à Piano…';}};
    if(name==='apigo'){var q,key,nx,code=gv('gst-pcode'),mem=ui.api.mem;
      try{q=pianoParam(gv('gst-purl'));}catch(e1){return fail(e1.message);}
      nx=apiNext(gv('gst-pstart'));if(!nx)return fail(state.weeks.length?'Aucune semaine complète n\\'est encore écoulée depuis le début du test.':'Indiquez la date de début du test : il faut au moins une semaine complète de données.');
      if(state.weeks.length&&!apiDueFor(nx))return fail('Pas de nouvelle semaine complète depuis la dernière lecture.');
      try{key=pkJoin(gv('gst-pak'),gv('gst-psk'));}catch(e2){return fail(e2.message);}
      if(mem==='code'&&code.length<8)return fail('Choisissez un code d\\'au moins 8 caractères, ou ne mémorisez pas la clé.');
      busy();pianoFetch(q,key,nx.start,nx.end).then(function(res){PKEY=key;return (mem==='code'?pkSeal(key,code):Promise.resolve()).then(function(){apiShow(res,q,nx.start,nx.end,false);},function(e){apiShow(res,q,nx.start,nx.end,false);ui.error=e.message;render();});},function(e){fail(e.message);});
      return;}
    var nu=apiDue();if(!nu)return render();
    var pk=PKEY?Promise.resolve(PKEY):(pkHas()?pkOpen(gv('gst-pcode')):new Promise(function(ok){ok(pkJoin(gv('gst-pak'),gv('gst-psk')));}));
    busy();pk.then(function(key){return pianoFetch(state.api.q,key,nu.start,nu.end).then(function(res){PKEY=key;PTRY[state.name+'|'+nu.end]=1;apiShow(res,state.api.q,nu.start,nu.end,true);});}).catch(function(e){fail(e.message);});
    return;}
  else if(name==='shot'){ui.shot=+v;}""")
rep("function apiShow(res,q,start,end,auto){","function apiDueFor(nx){var last=state.weeks[state.weeks.length-1];return nx.w>WKL()&&!(last&&last.end&&dayDiff(last.end,nx.end)<7);}\nfunction apiShow(res,q,start,end,auto){")
rep("root.addEventListener('input',function(e){var t=e.target;","root.addEventListener('input',function(e){var t=e.target;if(t&&t.hasAttribute&&t.hasAttribute('data-api')){var ak=t.getAttribute('data-api');if(ak==='url')ui.api.url=String(t.value).slice(0,12000);else if(ak==='start')ui.api.start=t.value;else if(ak==='mem'&&t.checked){ui.api.mem=t.value;var cz=root.querySelector('.api-code');if(cz)cz.hidden=t.value!=='code';}return;}")
rep("window.GST={acc:ACC,","window.GST={piano:{param:pianoParam,table:pianoTable,has:pkHas},acc:ACC,")

# styles
rep("#gst-app .dv-gate.ko{","""#gst-app .apibar{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;background:#F8FBFA;border:1px solid #D9D9D9;border-radius:6px;padding:10px 12px;margin-top:12px;font-size:14px;color:var(--ink)}#gst-app .apibar.due{border-color:var(--green);background:var(--wash)}#gst-app .apibar>span:first-of-type{flex:1 1 240px;min-width:0}#gst-app .apibar .row{gap:8px 16px;margin:0}#gst-app .apibar .api-f,#gst-app .apibar .api-err{flex:1 1 100%}
#gst-app .api-f{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;align-items:end}#gst-app .apif{display:grid;gap:14px;margin-top:10px}#gst-app .apif textarea{font-family:var(--fb);font-size:13px;color:var(--ink);background:#fff;border:1px solid var(--border);border-radius:6px;padding:8px 10px;width:100%;max-width:100%;margin:0;resize:vertical;word-break:break-all}#gst-app .apif .hint{margin-top:6px}
#gst-app .api-mem{border:1px solid var(--border);border-radius:6px;padding:10px 12px;margin:0;display:grid;gap:8px}#gst-app .api-mem legend{font-size:13px;font-weight:600;padding:0 4px;color:var(--ink)}#gst-app .api-mem label{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:14px;line-height:1.45;margin:0;cursor:pointer}#gst-app .api-mem input[type=radio]{flex:none;width:18px;height:18px;min-height:0;margin:2px 0 0;padding:0;accent-color:#028D6A}
#gst-app .api-sec{margin:0;padding-left:18px;font-size:13px;color:var(--charcoal);display:grid;gap:4px}#gst-app .api-go{margin:12px 0 0;font-size:14px}#gst-app .api-err{margin-top:0}#gst-app .api-err[hidden],#gst-app .api-code[hidden]{display:none}
@media (max-width:520px){#gst-app .api-f{grid-template-columns:minmax(0,1fr)}}
#gst-app .dv-gate.ko{""")
# ===== relecture de sécurité v56.8 =====
# F1 : une réponse n'est appliquée qu'au test qui l'a demandée, dans l'état où il était
rep("function apiDueFor(nx){","function apiTok(){return {s:state,n:state.weeks.length,q:state.api?state.api.q:null,d:ui.draft};}\nfunction apiSame(t){return state===t.s&&state.weeks.length===t.n&&(state.api?state.api.q:null)===t.q&&ui.draft===t.d&&!ui.ro;}\nfunction apiDueFor(nx){")
rep("PTRY[tk]=1;\n  pianoFetch(state.api.q,PKEY,nx.start,nx.end).then(function(res){if(apiDue())apiShow(res,state.api.q,nx.start,nx.end,true);},function(e){ui.error='Collecte automatique depuis Piano impossible. '+e.message;render();});}",
    "PTRY[tk]=1;var q0=state.api.q,tk0=apiTok();\n  pianoFetch(q0,PKEY,nx.start,nx.end).then(function(res){if(apiSame(tk0))apiShow(res,q0,nx.start,nx.end,true);else delete PTRY[tk];},function(e){if(!apiSame(tk0)){delete PTRY[tk];return;}ui.error='Collecte automatique depuis Piano impossible. '+e.message;render();});}")
rep("busy();pianoFetch(q,key,nx.start,nx.end).then(function(res){PKEY=key;return (mem==='code'","var tg=apiTok();busy();pianoFetch(q,key,nx.start,nx.end).then(function(res){PKEY=key;if(!apiSame(tg))return;return (mem==='code'")
rep("},function(e){fail(e.message);});\n      return;}","},function(e){if(apiSame(tg))fail(e.message);});\n      return;}")
rep("busy();pk.then(function(key){return pianoFetch(state.api.q,key,nu.start,nu.end).then(function(res){PKEY=key;PTRY[state.name+'|'+nu.end]=1;apiShow(res,state.api.q,nu.start,nu.end,true);});}).catch(function(e){fail(e.message);});",
    "var qu=state.api.q,tu=apiTok(),nmu=state.name;busy();pk.then(function(key){return pianoFetch(qu,key,nu.start,nu.end).then(function(res){PKEY=key;if(!apiSame(tu))return;PTRY[nmu+'|'+nu.end]=1;apiShow(res,qu,nu.start,nu.end,true);});}).catch(function(e){if(apiSame(tu))fail(e.message);});")
# F2 : une clé refusée par Piano est oubliée ; la clé de la visite peut être oubliée à la main
rep("if(r.status===401||r.status===403)throw new Error(","if(r.status===401||r.status===403){PKEY='';throw new Error(")
rep("et que la clé donne bien accès à ce site.');","et que la clé donne bien accès à ce site.');}")
rep("+(pkHas()?'<button type=\"button\" class=\"link\" data-act=\"apiforget\">Oublier la clé mémorisée</button>':'');","+(pkHas()?'<button type=\"button\" class=\"link\" data-act=\"apiforget\">Oublier la clé mémorisée</button>':(PKEY?'<button type=\"button\" class=\"link\" data-act=\"apiforget\">Oublier la clé de cette visite</button>':''));")
rep("else if(name==='apiforget'){pkForget();ui.notice='La clé Piano mémorisée sur cet appareil est effacée.';}","else if(name==='apiforget'){pkForget();ui.notice='La clé Piano est oubliée : elle sera redemandée à la prochaine collecte.';}")
# F3 : réponse lue avec un plafond, colonnes bornées dans tous les cas
rep("(Array.isArray(rows[0])?rows[0].map(function(x,i){return String(i);})","(Array.isArray(rows[0])?rows[0].slice(0,40).map(function(x,i){return String(i);})")
rep("function pianoFetch(q,key,start,end){","function capText(r){if(!r.body||!r.body.getReader)return r.text();var rd=r.body.getReader(),dec=new TextDecoder(),out='',n=0;\n  return (function step(){return rd.read().then(function(x){if(x.done)return out+dec.decode();n+=x.value.length;if(n>3e6){try{rd.cancel();}catch(e){}throw new Error('Réponse de Piano trop volumineuse : filtrez la requête sur votre test.');}out+=dec.decode(x.value,{stream:true});return step();});})();}\nfunction pianoFetch(q,key,start,end){")
rep(".then(function(r){return r.text().then(function(t){clearTimeout(tm);",".then(function(r){return capText(r).then(function(t){clearTimeout(tm);")
rep("if(!j)throw new Error('Réponse de Piano illisible.');return pianoTable(j);});},","if(!j)throw new Error('Réponse de Piano illisible.');return pianoTable(j);},function(e){clearTimeout(tm);if(e&&e.name==='AbortError')throw new Error('Piano ne répond pas (20 secondes) : réessayez.');throw e;});},")
# F4 : code de 12 caractères au moins
rep("Code (8 caractères au moins)","Code ou phrase (12 caractères au moins)")
rep("if(mem==='code'&&code.length<8)return fail('Choisissez un code d\\'au moins 8 caractères, ou ne mémorisez pas la clé.');","if(mem==='code'&&code.length<12)return fail('Choisissez un code d\\'au moins 12 caractères, ou ne mémorisez pas la clé.');")
# F6 : le site interrogé est affiché dans le bandeau
rep("function apiBar(){\n  if(","function apiSite(){var sp=state.api&&state.api.q&&state.api.q.space||{},a=(sp.s||[]).concat((sp.l2s||[]).map(function(x){return x.s;}));return a.length?' Site Piano '+a.slice(0,3).join(', ')+(a.length>3?'…':'')+'.':'';}\nfunction apiBar(){\n  if(")
rep("'<span><b>Piano connecté.</b> '+(done?","'<span><b>Piano connecté.</b>'+apiSite()+' '+(done?")
rep("données jusqu\\'au '+frDate(nx.end)+'.</span>'+ask","données jusqu\\'au '+frDate(nx.end)+'.'+apiSite()+'</span>'+ask")
# F7 : ne pas inviter le gestionnaire de mots de passe à retenir le code
rep("type=\"password\" autocomplete=\"new-password\" spellcheck=\"false\"","type=\"password\" autocomplete=\"off\" spellcheck=\"false\"")
# F5 : dit dans l'interface
rep("<li>Sur un poste partagé, ne mémorisez pas la clé.</li>","<li>Sur un poste partagé, ne mémorisez pas la clé.</li><li>La requête (identifiant du site et filtre, sans la clé) est gardée avec le test sur ce poste.</li>")
open(dst,'w',newline='').write(s);print(len(s))

import re
src='repo/calculateur-sequentiel-v56-14.html';dst='repo/calculateur-sequentiel-v56-15.html'
s=open(src,newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(s.count(a),a[:110]); s=s.replace(a,b)
rep("VERSION='v56.14'","VERSION='v56.15'")

# ================= Piano : la requête est reprise en entier (segment compris), et une variation peut être un segment =================
rep("function cleanParam(o){\n  if(!o||typeof o!=='object'||Array.isArray(o))throw new Error('Requête Piano illisible.');",
"""/* Une requête simple (variations en lignes) ou deux requêtes, une par variation (variations définies par des segments) : {seg:[contrôle,variante],labs:[…]}. */
function cleanParam(o){
  if(o&&typeof o==='object'&&Array.isArray(o.seg)){if(o.seg.length!==2)throw new Error('Il faut deux requêtes : une pour le contrôle, une pour la variante.');
    var lb=Array.isArray(o.labs)?o.labs:[],L1=String(lb[0]||'Contrôle').replace(/[\\r\\n\\t<>]+/g,' ').trim().slice(0,60)||'Contrôle',L2=String(lb[1]||'Variante').replace(/[\\r\\n\\t<>]+/g,' ').trim().slice(0,60)||'Variante';if(L1===L2)L2+=' (B)';
    return {seg:[cleanOne(o.seg[0],2),cleanOne(o.seg[1],2)],labs:[L1,L2]};}
  return cleanOne(o,3);}
function cleanOne(o,min){
  if(!o||typeof o!=='object'||Array.isArray(o))throw new Error('Requête Piano illisible.');""")
rep("  if(cols.length<3)throw new Error('La requête doit contenir au moins trois colonnes : la variation, les visiteurs et une métrique.');","  if(cols.length<(min||3))throw new Error(min===2?'Chaque requête doit contenir au moins deux colonnes : les visiteurs et une métrique.':'La requête doit contenir au moins trois colonnes : la variation, les visiteurs et une métrique.');")
rep("  if(o.options&&typeof o.options==='object')Object.keys(o.options).slice(0,10).forEach(function(k){if(/^[a-z_]{1,40}$/.test(k)&&typeof o.options[k]==='boolean')r.options[k]=o.options[k];});\n  return r;}",
"""  if(o.options&&typeof o.options==='object')Object.keys(o.options).slice(0,10).forEach(function(k){if(/^[a-z_]{1,40}$/.test(k)&&typeof o.options[k]==='boolean')r.options[k]=o.options[k];});
  /* Tout autre paramètre (segment…) change la population lue : il est repris tel quel plutôt qu'ignoré. Seuls la période, la pagination et l'évolution sont les nôtres. */
  var own={columns:1,space:1,sort:1,filter:1,options:1,period:1,evo:1,'max-results':1,'page-num':1,seg:1,labs:1,__proto__:1,constructor:1,prototype:1};
  Object.keys(o).slice(0,30).forEach(function(k){if(Object.prototype.hasOwnProperty.call(own,k)||k==='__proto__'||!/^[A-Za-z0-9_-]{1,40}$/.test(k))return;var v=o[k];if(v==null)return;var js=JSON.stringify(v);if(js===undefined)return;if(js.length>4000)throw new Error('Le paramètre « '+k+' » de la requête est trop long.');r[k]=JSON.parse(js);});
  return r;}
function apiKept(q){var one=function(x){var a=[];Object.keys(x||{}).forEach(function(k){if(['columns','space','sort','max-results','page-num'].indexOf(k)>=0)return;if(k==='options'){var ok=Object.keys(x.options||{}).filter(function(z){return x.options[z];});if(ok.length)a.push('options ('+ok.join(', ')+')');return;}a.push(k==='filter'?'filtre':k);});return a;};
  if(!q)return '';if(q.seg){var u=one(q.seg[0]).concat(one(q.seg[1])).filter(function(v,i,a){return a.indexOf(v)===i;});return ' Deux requêtes, une par variation'+(u.length?' ; repris de vos requêtes : '+u.join(', '):'')+'.';}
  var k=one(q);return k.length?' Repris de votre requête : '+k.join(', ')+'.':' Votre requête ne porte ni filtre ni segment.';}""")
rep("function pianoParam(raw){","function pianoParam(raw,min){")
s2=s[s.index("function pianoParam(raw,min){"):s.index("function pianoTable(j){")]
assert s2.count("return cleanParam(o);}")==1
s=s.replace(s2,s2.replace("return cleanParam(o);}","return cleanOne(o,min||3);}"))
rep("function pianoTable(j){","function pianoTable(j,seg){")
rep("  if(head.length<3)throw new Error('La requête doit renvoyer au moins trois colonnes.');","  if(head.length<(seg?2:3))throw new Error(seg?'Chaque requête doit renvoyer au moins deux colonnes.':'La requête doit renvoyer au moins trois colonnes.');\n  if(seg&&rows.length!==1)throw new Error('La requête d\\'une variation doit renvoyer une seule ligne ('+rows.length+' reçues) : retirez les dimensions en lignes, la variation est définie par le segment.');")
rep("  if(t.length<3)throw new Error('Piano renvoie moins de deux lignes : il en faut une par variation.');","  if(!seg&&t.length<3)throw new Error('Piano renvoie moins de deux lignes : il en faut une par variation.');")
rep("function pianoFetch(q,key,start,end){\n  var p=JSON.parse(JSON.stringify(q));",
"""function pianoFetch(q,key,start,end){
  if(!q||!q.seg)return pianoOne(q,key,start,end,false);
  return pianoOne(q.seg[0],key,start,end,true).then(function(a){return pianoOne(q.seg[1],key,start,end,true).then(function(b){
    var ha=a.table[0],hb=b.table[0];if(ha.join('\\u0001')!==hb.join('\\u0001'))throw new Error('Les deux requêtes ne renvoient pas les mêmes colonnes ('+ha.join(', ')+' / '+hb.join(', ')+') : elles doivent être identiques, au segment près.');
    var num=function(v){return String(v).trim()!==''&&isFinite(Number(v));},ix=[];ha.forEach(function(h,i){if(num(a.table[1][i])&&num(b.table[1][i]))ix.push(i);});
    if(ix.length<2)throw new Error('Les requêtes doivent renvoyer au moins deux colonnes chiffrées : les visiteurs et une métrique.');
    var pick=function(r){return ix.map(function(i){return r[i];});};
    return {table:[['Variation'].concat(pick(ha)),[q.labs[0]].concat(pick(a.table[1])),[q.labs[1]].concat(pick(b.table[1]))],full:false};});});}
function pianoOne(q,key,start,end,seg){
  var p=JSON.parse(JSON.stringify(q));""")
rep("if(!j)throw new Error('Réponse de Piano illisible.');return pianoTable(j);}","if(!j)throw new Error('Réponse de Piano illisible.');return pianoTable(j,seg);}")
rep("function apiSite(){var sp=state.api&&state.api.q&&state.api.q.space||{},","function apiSite(){var q0=state.api&&state.api.q,sp=(q0&&q0.seg?q0.seg[0].space:q0&&q0.space)||{},")
rep("  if(e==='api')return ' Période demandée à Piano : pour la changer, relancez la collecte.';","  if(e==='api')return ' Période demandée à Piano : pour la changer, relancez la collecte.'+esc(apiKept(ui.apiQ));")
# formulaire : choix du mode
rep("api:{open:false,url:'',start:'',mem:'non'}","api:{open:false,url:'',url2:'',mode:'lignes',start:'',mem:'non'}")
rep("    +'<div><label for=\"gst-purl\">Adresse de la requête</label><textarea id=\"gst-purl\" data-api=\"url\" rows=\"3\" spellcheck=\"false\" placeholder=\"https://api.atinternet.io/v3/data/getData?param=…\">'+esc(a.url)+'</textarea><p class=\"hint\">Dans Piano, Data Query : même tableau que pour l\\'export (une ligne par variation), puis Partager, « Copier l\\'URL API (GET) ». La période de la requête est remplacée par celle du test.</p></div>'",
"""    +'<fieldset class="api-mem"><legend>Comment vos variations sont-elles définies ?</legend><label><input type="radio" name="gst-pmode" data-api="mode" value="lignes"'+(a.mode!=='segments'?' checked':'')+'><span><b>En lignes de la requête</b> : une ligne par variation (propriété <code>mv_creation</code>).</span></label><label><input type="radio" name="gst-pmode" data-api="mode" value="segments"'+(a.mode==='segments'?' checked':'')+'><span><b>Par deux segments</b> : une requête par variation, chacune restreinte au segment de ses visiteurs.</span></label></fieldset>'
    +'<div><label for="gst-purl"><span class="api-m1"'+(a.mode==='segments'?' hidden':'')+'>Adresse de la requête</span><span class="api-m2"'+(a.mode==='segments'?'':' hidden')+'>Requête du contrôle</span></label><textarea id="gst-purl" data-api="url" rows="3" spellcheck="false" placeholder="https://api.atinternet.io/v3/data/getData?param=…">'+esc(a.url)+'</textarea>'
    +'<div class="api-m2"'+(a.mode==='segments'?'':' hidden')+' style="margin-top:12px"><label for="gst-purl2">Requête de la variante</label><textarea id="gst-purl2" data-api="url2" rows="3" spellcheck="false" placeholder="https://api.atinternet.io/v3/data/getData?param=…">'+esc(a.url2)+'</textarea></div>'
    +'<p class="hint"><span class="api-m1"'+(a.mode==='segments'?' hidden':'')+'>Dans Piano, Data Query : même tableau que pour l\\'export (une ligne par variation), puis Partager, « Copier l\\'URL API (GET) ».</span><span class="api-m2"'+(a.mode==='segments'?'':' hidden')+'>Dans Piano, Data Query : les mêmes métriques dans les deux requêtes (visiteurs, puis visiteurs par objectif), sans dimension en lignes, avec le segment de la variation. Puis Partager, « Copier l\\'URL API (GET) » pour chacune.</span> La période est remplacée par celle du test ; le filtre et le segment sont repris tels quels. Si Piano propose un mode éco, désactivez-le : il estime les visiteurs.</p></div>'""")
rep("if(ak==='url')ui.api.url=String(t.value).slice(0,12000);","if(ak==='url')ui.api.url=String(t.value).slice(0,12000);else if(ak==='url2')ui.api.url2=String(t.value).slice(0,12000);else if(ak==='mode'&&t.checked){ui.api.mode=t.value==='segments'?'segments':'lignes';root.querySelectorAll('.api-m1').forEach(function(x){x.hidden=ui.api.mode==='segments';});root.querySelectorAll('.api-m2').forEach(function(x){x.hidden=ui.api.mode!=='segments';});}")
rep("      try{q=pianoParam(gv('gst-purl'));}catch(e1){return fail(e1.message);}","      try{q=ui.api.mode==='segments'?cleanParam({seg:[pianoParam(gv('gst-purl'),2),pianoParam(gv('gst-purl2'),2)],labs:['Contrôle','Variante']}):pianoParam(gv('gst-purl'));}catch(e1){return fail((ui.api.mode==='segments'?'Requêtes par segment : ':'')+e1.message);}")
rep("#gst-app .api-err[hidden],#gst-app .api-code[hidden]{display:none}","#gst-app .api-err[hidden],#gst-app .api-code[hidden],#gst-app .api-m1[hidden],#gst-app .api-m2[hidden]{display:none}#gst-app .api-mem code{font-size:12px}")
rep("window.GST={piano:{param:pianoParam,table:pianoTable,has:pkHas},","window.GST={piano:{param:pianoParam,clean:cleanParam,table:pianoTable,has:pkHas},")

# ================= BigQuery : visiteurs écartés comptés, lus et affichés =================
rep("  var used=[d.cTest,d.cWeek,d.cEnd,d.cStart,d.cVar,d.cVis];","  d.cExcl=find(/^exclu|vus dans (les )?deux/);\n  var used=[d.cTest,d.cWeek,d.cEnd,d.cStart,d.cVar,d.cVis,d.cExcl];")
rep("  var sd=d.cStart>=0&&rowsT[0]?","  d.excl=d.cExcl>=0&&rowsT[0]?toInt(rowsT[0][d.cExcl]):NaN;\n  var sd=d.cStart>=0&&rowsT[0]?")
rep("      +(last?'<p class=\"dv-read\">'+ICON.ok+'<span>","      +(last&&d.excl>=0?'<p class=\"dv-read\"><span>'+(d.excl>0?'<b class=\"num\">'+nf(d.excl)+'</b> visiteur'+(d.excl>1?'s vus':' vu')+' dans les deux variations '+(d.excl>1?'ont été écartés':'a été écarté')+' par la requête, soit '+nf(d.excl/(last.A+last.B+d.excl)*100,2)+' % des visiteurs. Au-delà de 1 %, vérifiez l\\'affectation des variations avant de lire le résultat.':'Aucun visiteur vu dans les deux variations.')+'</span></p>':'')\n      +(last?'<p class=\"dv-read\">'+ICON.ok+'<span>")
a=s.index('"),\\n"visiteurs AS (')  if False else None
rep('"visiteurs AS (  -- un visiteur vu dans deux variations est écarté",','"exclus AS (  -- visiteurs vus dans les deux variations : écartés, mais comptés",\n"  SELECT COUNT(*) AS n FROM (",\n"    SELECT user_pseudo_id FROM expositions WHERE variation IS NOT NULL",\n"    GROUP BY user_pseudo_id HAVING COUNT(DISTINCT variation) > 1)",\n"),",\n"visiteurs AS (  -- un visiteur vu dans deux variations est écarté",')
rep('"  COUNTIF(o.ajout_panier = 1) AS visiteurs_avec_ajout_panier",','"  COUNTIF(o.ajout_panier = 1) AS visiteurs_avec_ajout_panier,",\n"  (SELECT n FROM exclus) AS exclus_deux_variations",')
rep("<p class=\"cap\">Un visiteur vu dans deux variations est écarté ; un objectif ne compte qu\\'après la première exposition.</p>","<p class=\"cap\">Un visiteur vu dans deux variations est écarté et compté à part ; un objectif ne compte qu\\'après la première exposition. Un « visiteur » est un identifiant GA4 : une personne sur deux appareils compte deux fois. Google peut compléter une table jusqu\\'à trois jours après la date : attendez ce délai avant de lire une semaine.</p>")

# ================= tutoriels =================
rep("step(2,'<b>En lignes</b> : la dimension qui porte la variation du test (celle que votre outil de test envoie à Analytics).')+step(3,'<b>En colonnes</b> : « Nom de l\\'événement », limité aux événements que vous suivez.')+step(4,'<b>En valeurs</b> : « Nombre total d\\'utilisateurs ». Chaque colonne donne les visiteurs ayant déclenché l\\'événement ; <code>session_start</code> donne les visiteurs exposés.')+step(5,'<b>Période</b> : du premier jour du test à hier, puis exportez en CSV.')",
    "step(2,'<b>En lignes</b> : la dimension qui porte la variation du test. Elle doit être de portée utilisateur ; sinon un achat fait plus tard n\\'est pas rattaché à la variation.')+step(3,'<b>En colonnes</b> : « Nom de l\\'événement », limité à l\\'événement d\\'exposition de votre outil de test et à vos objectifs.')+step(4,'<b>En valeurs</b> : « Nombre total d\\'utilisateurs ». La colonne de l\\'événement d\\'exposition donne les visiteurs exposés. N\\'utilisez pas <code>session_start</code> : la session commence souvent avant l\\'exposition.')+step(5,'<b>Période</b> : du premier jour du test à hier, puis exportez en CSV.')+'<p class=\"hint tnote\">L\\'exploration ne vérifie pas qu\\'un objectif est atteint après la première exposition. Si la variation n\\'est pas une propriété utilisateur, ou si cet ordre compte pour vous, passez par l\\'onglet BigQuery.</p>'")
rep("+step(5,'<b>Exportez en CSV</b> et déposez le fichier ici. Refaites le même export chaque semaine.')","+step(5,'<b>Exportez en CSV</b> et déposez le fichier ici. Refaites le même export chaque semaine.')+'<p class=\"hint tnote\">À vérifier une fois : un achat fait lors d\\'une visite suivante doit rester compté pour sa variation. Si ce n\\'est pas le cas, définissez chaque variation par un segment de visiteurs et utilisez la connexion directe « par deux segments ». Si Piano propose un mode éco, désactivez-le : il estime les visiteurs.</p>'")
rep("#gst-app .dv-gate.ko{","#gst-app .tnote{margin-top:12px;padding:10px 12px;border-left:3px solid var(--amber);background:#FDF8EC;border-radius:0 6px 6px 0;color:var(--ink)}\n#gst-app .dv-gate.ko{")

# ================= confidentialité : la promesse suit le comportement =================
rep("<span>Vos chiffres restent dans votre navigateur</span>","<span>Sans compte, vos chiffres restent dans votre navigateur</span>")
rep("<b>Vos chiffres ne quittent pas votre poste.</b> Rien n\\'est enregistré sur le site : le calcul se fait dans votre navigateur, et vous pouvez sauvegarder le test en local.","<b>Votre fichier n\\'est envoyé nulle part.</b> Il est lu et calculé dans votre navigateur, et le test se sauvegarde sur ce poste. Seul un test que vous enregistrez dans votre espace envoie ses chiffres agrégés (visiteurs et conversions par variation) au serveur FWOptimisation.")
n0=s.count("Vos chiffres ne quittent pas votre poste.");assert n0==1,n0
rep("Vos chiffres ne quittent pas votre poste.","Fichier lu dans votre navigateur, jamais envoyé.")
rep("Sans compte, l\\'outil reste utilisable : vos tests sont alors gardés sur ce poste uniquement.","Sans compte, l\\'outil reste utilisable : vos tests sont alors gardés sur ce poste uniquement. Avec un compte, les chiffres agrégés des tests que vous enregistrez sont conservés sur le serveur FWOptimisation.")
rep("Elle ne passe par aucun serveur FWOptimisation et n\\'entre ni dans un lien de partage, ni dans votre compte.</li>","Elle ne passe par aucun serveur FWOptimisation et n\\'entre ni dans un lien de partage, ni dans votre compte.</li><li>La mise à jour se fait à l\\'ouverture de l\\'outil, clé disponible, jusqu\\'à la dernière semaine complète du test. Rien ne tourne quand l\\'outil est fermé.</li>")
open(dst,'w',newline='').write(s);print(len(s))

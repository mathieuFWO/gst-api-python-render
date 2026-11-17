import base64,re
src='repo/calculateur-sequentiel-v55-8.html';dst='repo/calculateur-sequentiel-v55-9.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
rep("VERSION='v55.8'","VERSION='v55.9'")
b64=lambda n:'data:image/png;base64,'+base64.b64encode(open('tuto/logos/'+n+'.png','rb').read()).decode()
rep("howto:'piano',","howto:'piano',shot:0,")
# onglets avec logos
a=s.index("[['piano','Piano Analytics'],['ga4','Google Analytics 4'],['adobe','Adobe Analytics'],['autre','Autre outil'],['manuel','Saisie manuelle']].map(function(t){return '<button type=\"button\" role=\"tab\"")
e=s.index(".join('')+'</div>'",a)
s=s[:a]+"""[['piano','Piano Analytics'],['ga4','Google Analytics 4'],['adobe','Adobe Analytics'],['autre','Autre outil'],['manuel','Saisie manuelle']].map(function(t){var lg=LOGOS[t[0]];return '<button type="button" role="tab" aria-selected="'+(tab===t[0])+'" class="'+(tab===t[0]?'on':'')+'" data-act="howto" data-v="'+t[0]+'"'+(lg&&lg.word?' aria-label="'+t[1]+'"':'')+'>'+(lg?'<img class="tlg'+(lg.word?' w':'')+'" src="'+lg.src+'" alt="" width="'+lg.w+'" height="'+lg.h+'">':'')+(lg&&lg.word?lg.word:t[1])+'</button>';})"""+s[e:]
# bloc d'import : dépôt sous les étapes, visuels (ou fichier attendu) à droite
a=s.index("    +(tab==='manuel'?manualForm():'<div class=\"tuto\">'+tuto+'</div>')+'</div>'")
b=s.index("    +(tab==='manuel'?'':'<div class=\"imp-3\">",a)
old=s[a:b]
FILE=re.search(r"'(<div class=\"file\" aria-label=\"Exemple de fichier attendu\">.*?</table></div>)'",old,re.S).group(1)
LOCK=re.search(r"(<p class=\"lock\">.*?</p>)'\)\+'</div>'\)",old,re.S).group(1)
nl='\r\n' if '\r\n' in s else '\n'
NEW=("""    +(tab==='manuel'?manualForm():'<div class="tuto">'+tuto+'</div>')+'</div>'
    +(tab==='manuel'?'':'<div class="imp-r">'+(shots?'<div class="kicker">L\\'export en images</div><div class="shots" role="tablist" aria-label="Étapes illustrées">'+shots.map(function(x,i){return '<button type="button" role="tab" aria-selected="'+(i===si)+'" class="'+(i===si?'on':'')+'" data-act="shot" data-v="'+i+'">'+x[1]+'</button>';}).join('')+'</div><figure class="shot"><img src="'+TUTO_BASE+shots[si][0]+'.webp" alt="'+shots[si][2]+'" width="1200" height="'+shots[si][4]+'" loading="lazy" decoding="async"><figcaption>'+shots[si][3]+'</figcaption></figure>'
      :'<div class="kicker">Le fichier attendu</div>"""+FILE.replace('class="file"','class="file solo"')+"""<p class="cap">Une ligne par variation, une colonne par métrique, en cumul depuis le premier jour du test.</p>')+'</div>'
      +'<div class="imp-d"><div class="kicker">2 · Déposez le fichier</div><div class="drop dz2 dzc" data-act="pick" tabindex="0" role="button"><h3>Déposez votre export CSV ici</h3><p class="row"><button type="button" class="pri" data-act="pick">Choisir un fichier</button><button type="button" data-act="template">Télécharger le modèle CSV</button></p></div><input type="file" accept=".csv,.txt,.tsv,text/csv" data-f="file" style="display:none">"""+LOCK+"""</div>')
""").replace('\n',nl)
s=s[:a]+NEW+s[b:]
rep("  var tab=ui.howto||'piano',step=function(n,t)","  var tab=ui.howto||'piano',shots=SHOTS[tab]||null,si=shots?Math.min(shots.length-1,Math.max(0,ui.shot|0)):0,step=function(n,t)")
rep("function viewHome(){","""var TUTO_BASE='https://fwoptimisation.com/wp-content/uploads/2026/11/';
var SHOTS={ga4:[['google-analytics-4-export-test-ab-choisir-periode','Période','Google Analytics 4 : choisir la période d\\'une exploration pour exporter un test A/B','<b>Période.</b> Une seule période, du premier jour du test à hier.',611],['google-analytics-4-export-test-ab-filtrer-experience','Filtre','Google Analytics 4 : filtrer l\\'exploration sur l\\'expérience du test A/B','<b>Filtre.</b> Ne gardez que votre test, pour n\\'avoir que ses variations en lignes.',585],['google-analytics-4-export-test-ab-exporter-csv','Export CSV','Google Analytics 4 : exporter l\\'exploration du test A/B en CSV','<b>Export.</b> Téléchargez le tableau en CSV, puis déposez le fichier ici.',583]],
  piano:[['piano-analytics-export-test-ab-choisir-periode','Période','Piano Analytics : choisir la période dans Data Query pour exporter un test A/B','<b>Période.</b> Une seule période, du premier jour du test à hier.',595],['piano-analytics-export-test-ab-filtrer-experience','Filtre','Piano Analytics : filtrer Data Query sur l\\'expérience du test A/B','<b>Filtre.</b> Ne gardez que votre test, pour n\\'avoir que ses variations en lignes.',568],['piano-analytics-export-test-ab-exporter-csv','Export CSV','Piano Analytics : exporter la requête Data Query du test A/B en CSV','<b>Export.</b> Exportez la requête en CSV, puis déposez le fichier ici.',589]]};
var LOGOS={piano:{src:'"""+b64('piano')+"""',w:44,h:14,word:'Analytics'},ga4:{src:'"""+b64('ga')+"""',w:18,h:18},adobe:{src:'"""+b64('adobe')+"""',w:20,h:20}};
function viewHome(){""")
s=s.replace("    +'<div class=\"imp\"><div class=\"imp-l\">","    +'<div class=\"imp'+(tab==='manuel'?'':' g')+'\"><div class=\"imp-l\">");assert "(tab==='manuel'?'':' g')" in s
rep("  else if(name==='faq'){","  else if(name==='shot'){ui.shot=+v;}\n  else if(name==='faq'){")
# changer d'outil : on repart sur le premier visuel
m=re.search(r"else if\(name==='howto'\)\{([^}]*)\}",s);assert m,(1)
s=s[:m.start()]+"else if(name==='howto'){ui.shot=0;"+m.group(1)+"}"+s[m.end():]
CSS="""#gst-app .tools2 button{display:inline-flex;align-items:center;gap:8px}#gst-app .tools2 img.tlg{display:block;flex:none;width:auto;height:18px;max-width:none;border-radius:0;box-shadow:none}#gst-app .tools2 img.tlg.w{height:14px;margin-top:-3px}
#gst-app .imp.g{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:24px 40px;align-items:start}
#gst-app .imp.g .imp-l{grid-column:1;grid-row:1}#gst-app .imp.g .imp-r{grid-column:2;grid-row:1/3}#gst-app .imp.g .imp-d{grid-column:1;grid-row:2;min-width:0}#gst-app .imp.g .imp-3{grid-column:1/-1}
@media (max-width:760px){#gst-app .imp.g{grid-template-columns:minmax(0,1fr);gap:24px}#gst-app .imp.g .imp-l,#gst-app .imp.g .imp-r,#gst-app .imp.g .imp-d,#gst-app .imp.g .imp-3{grid-column:1;grid-row:auto}}
#gst-app .imp .drop.dz2.dzc{margin-top:12px;padding:18px 16px}#gst-app .imp .drop.dz2.dzc p.row{justify-content:center;margin-top:12px}
#gst-app .shots{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}
#gst-app .shots button,#gst-app .shots button:focus{min-height:34px;padding:0 12px;border-radius:999px;font-size:13px}
#gst-app .shots button.on{background:#ECF7F4;border-color:#1D9E75;color:#0E7C5D}
#gst-app figure.shot{margin:12px 0 0;padding:0}
#gst-app figure.shot img{display:block;width:100%;height:auto;max-width:none;border:1px solid var(--border);border-radius:10px;background:#fff;box-shadow:none}
#gst-app figure.shot figcaption{margin-top:10px;font-size:13px;color:var(--charcoal);text-align:left;font-style:normal}
"""
i=s.index("h1.gst-h1+#gst-app{");j=s.index("\n",i)+1
s=s[:j]+CSS+s[j:]
open(dst,'w',newline='').write(s);print(len(s))

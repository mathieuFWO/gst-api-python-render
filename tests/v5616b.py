f='repo/calculateur-sequentiel-v56-16.html'
s=open(f,newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(s.count(a),a[:110]); s=s.replace(a,b)
# 5. structure : outil, puis fichier ou API ; le tutoriel ne s'affiche que pour un fichier
a=s.index("""      +'<div class="imp-d">'+(HAS_API[tab]?'<div class="kicker">2 · Apportez vos chiffres</div>""")
b=s.index("""'<div class="drop dz2 dzc\"""",a)
old=s[a:b]
t0=old.index('<div class="toggle way"');t1=old.index("</div>':'')+(tab==='piano'")
way="'"+old[t0:t1]+"</div>'"
pre="""</p>')+'</div>'"""+NL
assert s[a-len(pre):a]==pre
s=s[:a-len(pre)]+"""</p>')+'</div>')"""+NL+"""      +'<div class="imp-d'+(VIA?' wide':'')+'">'+(VIA?apiForm()+'</div>':'<div class="kicker">3 · Déposez le fichier</div>"""+s[b+1:]
rep("""  var faq=function(id,q,body){""","""  var VIA=!!(HAS_API[tab]&&ui.api.open),WAY=HAS_API[tab]?"""+way+""":'';\n  var faq=function(id,q,body){""")
rep(r"""    +(tab==='manuel'?manualForm():'<div class="tuto">'+tuto.replace(""",r"""    +(tab==='manuel'?manualForm()+'</div>':WAY+'</div>'+(VIA?'':'<div class="imp-t"><div class="kicker">2 · Préparez l\'export</div><div class="tuto">'+tuto.replace(""")
rep(r"""'+m;})+'</div>')+'</div>'""",r"""'+m;})+'</div></div>'))""")
rep(r"""    +(tab==='manuel'?'':'<div class="imp-r">'+(tab==='bigquery'""",r"""    +(tab==='manuel'?'':(VIA?'':'<div class="imp-r">'+(tab==='bigquery'""")
rep("#gst-app .imp.g .imp-l{grid-column:1;grid-row:1}#gst-app .imp.g .imp-r{grid-column:2;grid-row:1/3}#gst-app .imp.g .imp-d{grid-column:1;grid-row:2;min-width:0}","#gst-app .imp.g .imp-l{grid-column:1/-1;grid-row:1}#gst-app .imp.g .imp-t{grid-column:1;grid-row:2;min-width:0}#gst-app .imp.g .imp-r{grid-column:2;grid-row:2}#gst-app .imp.g .imp-d{grid-column:1/-1;grid-row:3;min-width:0}")
rep("#gst-app .imp.g .imp-l,#gst-app .imp.g .imp-r,","#gst-app .imp.g .imp-l,#gst-app .imp.g .imp-t,#gst-app .imp.g .imp-r,")
rep("#gst-app .toggle.way{margin-top:10px;display:flex}","#gst-app .toggle.way{margin-top:14px;display:flex;max-width:520px}#gst-app .imp-t .tuto{margin-top:12px}")
# 6. Piano : formulaire à gauche, encadré bleu « Votre confidentialité » à droite
rep(r"""'<p class="way-l">L\'outil lit vos chiffres dans Piano, puis les met à jour chaque semaine.</p><div class="apif">'""",r"""'<div class="kicker">2 · Connectez Piano</div><p class="way-l">L\'outil lit vos chiffres dans Piano, puis les met à jour chaque semaine.</p><div class="apiw"><div class="apif">'""")
rep("""    +'<ul class="api-sec"><li>La clé va""","""    +'</div><aside class="api-conf"><p class="api-ct">Votre confidentialité</p><ul class="api-sec"><li>La clé va""")
rep("""sur ce poste.</li></ul></div>';}""","""sur ce poste.</li></ul></aside></div>';}""")
rep("#gst-app .dec3{","#gst-app .api-conf{margin-top:14px;background:#E6F2F9;border:1px solid #BFDDF0;border-radius:10px;padding:14px 16px}#gst-app .api-ct{margin:0 0 8px;font-family:var(--ft);font-weight:700;font-size:15px;color:#006A9E}#gst-app .api-conf .api-sec{color:var(--ink);gap:6px}@media (min-width:761px){#gst-app .imp-d.wide .apiw{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);gap:24px 40px;align-items:start}#gst-app .imp-d.wide .api-conf{margin-top:10px}}\n#gst-app .dec3{")
# 7. tableau de bord : le gain en pastille pleine
rep("#gst-app .dec3{","#gst-app .dst.g{background:#0E7C5D;color:#fff;padding:3px 11px 3px 9px;border-radius:999px;align-items:center}#gst-app .dst.g i{background:#fff;transform:none}#gst-app .dash .d-e.g{font-weight:700}\n#gst-app .dec3{")
# 8. règle d'arrêt : « Recommandé » en pastille, avantages et inconvénients plus lisibles
rep(r"""<b>Dès que le résultat est joué</b> · recommandé<br>""",r"""<b>Dès que le résultat est joué</b> <span class="reco">Recommandé</span><br>""")
rep("#gst-app .dec3{","#gst-app .reco{display:inline-block;margin-left:6px;padding:1px 9px;border-radius:999px;background:#E6F4F0;border:1px solid #1D9E75;color:#0E7C5D;font-size:12px;font-weight:600;line-height:1.6;vertical-align:1px}#gst-app label.opt .pc{gap:6px;margin-top:10px;font-size:14px;line-height:1.45;color:var(--ink)}#gst-app label.opt .pc span{padding-left:26px}#gst-app label.opt .pro::before,#gst-app label.opt .con::before{left:0;top:2px;width:17px;height:17px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;line-height:1}#gst-app label.opt .pro::before{background:#E6F4F0;color:#0E7C5D}#gst-app label.opt .con::before{background:#F2D4D0;color:#8f2c20}#gst-app label.opt .hint{display:inline-block;margin-top:2px;font-size:13px}\n#gst-app .dec3{")
# 9. message de chargement : il s'efface seul au bout de 8 secondes (les erreurs restent)
rep("""  drawCharts();\n  if(fsel){""","""  drawCharts();\n  clearTimeout(NTM);if(ui.notice&&/^(Exemple chargé|Test « |\\d+ semaine\\(s\\) |Plan appliqué)/.test(ui.notice)){var nt0=ui.notice;NTM=setTimeout(function(){if(ui.notice!==nt0)return;ui.notice='';var o=root.querySelector('.ok');if(o&&o.parentNode)o.parentNode.removeChild(o);},8000);}\n  if(fsel){""")
rep("function render(){","var NTM=0;\nfunction render(){")
# 10. plus de pastilles dans l'étape 6 ; la note devient « Conseils supplémentaires », en infobulle sous la galerie
rep(r"""<b>Lisez la décision</b> : <span class="dec3" aria-hidden="true"><span>Continuer</span><span class="on">Déployer</span><span>Arrêter</span></span> Vous revenez chaque semaine tant que l\'outil dit de continuer.""",r"""<b>Lisez la décision</b> : continuer, déployer ou arrêter. Vous revenez chaque semaine tant que l\'outil dit de continuer.""")
rep(r"""<div class="tuto">'+tuto.replace(/(<p class="hint tnote">|$)/,""",r"""<div class="tuto">'+tuto.replace(/<p class="hint tnote">[\s\S]*$/,'').replace(/$/,""")
rep("""ou remplissez le modèle à la main.');""","""ou remplissez le modèle à la main.');\n  var TN=(/<p class="hint tnote">([\\s\\S]*)<\\/p>$/.exec(tuto)||[])[1]||'';""")
rep("""'</figcaption></figure>'""","""'</figcaption></figure>'+(TN?'<details class="tips"><summary>Conseils supplémentaires</summary><div class="tips-b">'+TN+'</div></details>':'')""")
rep("#gst-app .dec3{","#gst-app details.tips{position:relative;margin-top:10px;font-size:13px}#gst-app details.tips summary{display:inline-flex;align-items:center;min-height:44px;cursor:pointer;color:#0E7C5D;font-weight:600;text-decoration:underline;text-underline-offset:3px;list-style:none}#gst-app details.tips summary::-webkit-details-marker{display:none}#gst-app details.tips summary::before{content:'i';flex:none;display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;margin-right:8px;border-radius:50%;border:1.5px solid #0E7C5D;font-size:11px;font-weight:700;text-decoration:none}#gst-app .tips-b{position:absolute;z-index:5;left:0;top:calc(100% - 2px);width:min(100%,440px);background:#fff;border:1px solid var(--border);border-left:3px solid var(--amber);border-radius:8px;padding:12px 14px;color:var(--ink);line-height:1.5;box-shadow:0 6px 18px rgba(26,29,31,.10)}\n#gst-app .dec3{")
# 11. le thème du site impose line-height:1 aux libellés : on le fixe, pour que la production suive la maquette
rep("#gst-app label{font-size:12px;","#gst-app label{line-height:1.45;font-size:12px;")
# 12. dépôt allégé : deux boutons sous la liste, sans le cadre vert ; tout le bloc accepte un fichier glissé
rep("""<div class="drop dz2 dzc" data-act="pick" tabindex="0" role="button"><h3>Déposez votre export CSV ici</h3><p class="row">""","""<div class="drop lite"><p class="row">""")
rep("""<p class="dz-o">Un autre outil ? Le modèle""","""<p class="dz-o">Vous pouvez aussi glisser le fichier dans ce cadre. Un autre outil ? Le modèle""")
rep("""root.addEventListener('dragover',function(e){var z=e.target.closest('.drop');""","""root.addEventListener('dragover',function(e){var z=e.target.closest('.drop,.imp');""")
rep("""root.addEventListener('dragleave',function(e){var z=e.target.closest('.drop');""","""root.addEventListener('dragleave',function(e){var z=e.target.closest('.drop,.imp');""")
rep("""root.addEventListener('drop',function(e){var z=e.target.closest('.drop');""","""root.addEventListener('drop',function(e){var z=e.target.closest('.drop,.imp');""")
rep("#gst-app .imp.g .imp-r{grid-column:2;grid-row:2}#gst-app .imp.g .imp-d{grid-column:1/-1;grid-row:3;min-width:0}","#gst-app .imp.g .imp-r{grid-column:2;grid-row:2/4}#gst-app .imp.g .imp-d{grid-column:1;grid-row:3;min-width:0}#gst-app .imp.g .imp-d.wide{grid-column:1/-1;grid-row:2}")
rep("#gst-app .dec3{","#gst-app .imp .drop.lite{margin-top:10px;padding:0;border:0;background:none;text-align:left;cursor:default}#gst-app .imp .drop.lite p.row{margin:0;justify-content:flex-start}#gst-app .imp .drop.lite button{font-size:14px;padding:0 14px}#gst-app .imp .drop.lite .dz-o{margin-top:10px;font-size:13px;line-height:1.5}@media (max-width:760px){#gst-app .imp .drop.lite button{min-height:44px}}#gst-app .imp.over{outline:2px dashed #1D9E75;outline-offset:-3px;background:#F7FCFA}\n#gst-app .dec3{")
open(f,'w',newline='').write(s);print(len(s))

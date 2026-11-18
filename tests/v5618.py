s=open('repo/calculateur-sequentiel-v56-16.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
L=s.split(NL)
n=[i for i,l in enumerate(L) if """<div class="imp'+(tab==='manuel'""" in l];assert len(n)==1;n=n[0]
assert L[n+5].strip()=="+'</div>'"
L[n]=r"""    +(!ui.pick?chooser():'<div class="imp'+(tab==='manuel'?'':' g')+'"><div class="imp-l">'+backHead(tab)"""
L[n+5]="    +'</div>')"
s=NL.join(L)
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(s.count(a),a[:110]); s=s.replace(a,b)
rep("var HAS_API={piano:1};",r"""var HAS_API={piano:1};
var TOOLN={piano:'Piano Analytics',ga4:'Google Analytics 4',adobe:'Adobe Analytics',bigquery:'BigQuery',manuel:'Saisie manuelle'};
function toolLab(k){var lg=LOGOS[k];return (lg?'<img class="tlg'+(lg.word?' w':'')+'" src="'+lg.src+'" alt="" width="'+lg.w+'" height="'+lg.h+'">':'')+(lg&&lg.word?lg.word:TOOLN[k]);}
function chooser(){
  var sub={piano:'Export CSV ou connexion directe',ga4:'Export CSV d\'une exploration',adobe:'Export CSV d\'Analysis Workspace',bigquery:'Requête modèle fournie'};
  return '<div class="imp ch"><div class="ch-l"><div class="kicker">Vos chiffres viennent d\'un outil d\'analyse</div><div class="ch-t">'+['piano','ga4','adobe','bigquery'].map(function(k){var lg=LOGOS[k];return '<button type="button" class="tc" data-act="howto" data-v="'+k+'"'+(lg&&lg.word?' aria-label="'+TOOLN[k]+'"':'')+'><span class="tn">'+toolLab(k)+(HAS_API[k]?'<span class="tbadge">API</span>':'')+'</span><small>'+sub[k]+'</small></button>';}).join('')+'</div></div>'
    +'<div class="ch-r"><div class="kicker">Sans fichier à préparer</div><button type="button" class="tc" data-act="howto" data-v="manuel"><span class="tn">Saisie manuelle</span><small>Vous tapez les chiffres de chaque semaine</small></button><p class="hint">Même analyse, mêmes décisions. Avec un outil, l\'import reprend toutes vos métriques d\'un coup ; à la main, c\'est plus rapide pour un test avec un ou deux objectifs.</p></div></div>';
}
function backHead(tab){return '<div class="bh"><button type="button" class="link" data-act="unpick">‹ Tous les outils</button><span class="bh-t">'+toolLab(tab)+'</span></div>';}""")
rep("  else if(name==='howto'){ui.shot=0;ui.howto=v;}","  else if(name==='howto'){ui.shot=0;ui.howto=v;ui.pick=true;}\n  else if(name==='unpick'){ui.pick=false;ui.api.open=false;}")
rep("else if(name==='accnew'){state=freshState();ui.start=true;","else if(name==='accnew'){state=freshState();ui.start=true;ui.pick=false;")
rep(r"""<div class="kicker">2 · Préparez l\'export</div>""",r"""<div class="kicker">1 · Préparez l\'export</div>""")
rep("""<div class="kicker">3 · Déposez le fichier</div>""","""<div class="kicker">2 · Déposez le fichier</div>""")
rep("""<div class="kicker">2 · Connectez Piano</div>""","""<div class="kicker">Connectez Piano</div>""")
rep("#gst-app .dec3{","#gst-app .imp.ch{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(0,1fr);gap:0;align-items:start}#gst-app .ch-l{padding-right:32px}#gst-app .ch-r{padding-left:32px;border-left:1px solid var(--border);align-self:stretch}#gst-app .ch-t{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}#gst-app .ch .kicker{margin-bottom:12px}#gst-app button.tc,#gst-app button.tc:focus{display:flex;flex-direction:column;align-items:flex-start;justify-content:center;gap:4px;width:100%;min-height:68px;padding:12px 16px;border-radius:10px;text-align:left;background:#fff}#gst-app button.tc:hover{border-color:#1D9E75;background:#F7FCFA}#gst-app .tc .tn{display:inline-flex;align-items:center;gap:8px;font-size:15px;font-weight:600;color:var(--ink)}#gst-app .tc small{font-size:12px;font-weight:400;color:var(--charcoal)}#gst-app .ch-r .hint{margin-top:12px}#gst-app .bh{display:flex;flex-wrap:wrap;align-items:center;gap:6px 16px}#gst-app .bh-t{display:inline-flex;align-items:center;gap:8px;font-family:var(--ft);font-weight:600;font-size:18px;color:var(--ink)}#gst-app .bh+.toggle.way{margin-top:16px}#gst-app .bh .link{min-height:44px}#gst-app .tuto .nb{background:#fff;border:1.5px solid #1D9E75;color:#0E7C5D}@media (max-width:760px){#gst-app .imp.ch{grid-template-columns:minmax(0,1fr)}#gst-app .ch-l{padding-right:0}#gst-app .ch-r{padding-left:0;border-left:0;border-top:1px solid var(--border);margin-top:20px;padding-top:20px}#gst-app .ch-t{grid-template-columns:minmax(0,1fr)}}\n#gst-app .dec3{")
open('proto/choix.html','w',newline='').write(s);print(len(s))

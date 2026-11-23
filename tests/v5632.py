# v56-32 : puce de sélection noire (plus de puce devant le titre du graphique), « Non conclusif » en gris,
# segmentation discrète : lien gris « Segmenter » à côté du nom, dimensions en onglets de texte dans le détail, note sur une ligne.
s=open('repo/calculateur-sequentiel-v56-31.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(a[:80],s.count(a));s=s.replace(a,b)
def cut(a,b,new):
    global s
    assert s.count(a)==1,(a[:60],s.count(a));i=s.index(a);j=s.index(b,i);s=s[:i]+new+s[j:]
rep("""NEUTRE:['Non conclusif','']""","""NEUTRE:['Non conclusif','nc']""")
rep("""AUCUN_SIGNAL:['Non conclusif','']""","""AUCUN_SIGNAL:['Non conclusif','nc']""")
rep("""<span class="pill">Non conclusif</span>""","""<span class="pill nc">Non conclusif</span>""")
rep("""<h3><span class="rsel on" aria-hidden="true"></span>Trajectoire : '""","""<h3>Trajectoire : '""")
rep("""La puce bleue marque la métrique affichée dans le graphique : cliquez une autre ligne pour la changer.""","""La puce noire marque la métrique affichée dans le graphique : cliquez une autre ligne pour la changer.""")
# bouton de segmentation : lien discret à côté du nom
cut("""
      +(wk.dims&&wk.dims.length&&st?(function(){var on=!!(ui.segX&&ui.segX[m.id]),lab=""","""+'</div>'
    +'<div class="c-a num">'+fv(st&&st.mA)+'</div><div class="c-b num">'+fv(st&&st.mB)+'</div>'
    +'<div class="c-lift"><span class="lift num">'+pct(st&&st.lift)+'</span></div>'
    +'<div class="c-ci">'+ciBar(st,ax,tone)+'</div>'""","")
rep("""    +'<div class="c-name"><div class="mn">'+esc(m.name)+'</div>""",
"""    +'<div class="c-name"><div class="mn">'+esc(m.name)+(wk.dims&&wk.dims.length&&st?'<button type="button" class="sgl" data-act="segx" data-v="'+m.id+'" aria-expanded="'+!!(ui.segX&&ui.segX[m.id])+'" aria-label="'+(ui.segX&&ui.segX[m.id]?'Masquer la segmentation de ':'Segmenter ')+esc(m.name)+'">'+(ui.segX&&ui.segX[m.id]?'Masquer':'Segmenter')+'<span class="sgl-c" aria-hidden="true"></span></button>':'')+'</div>""")
# détail : dimensions en onglets de texte, note sur une ligne
cut("""  var h='<div class="sgs" data-m="'+m.id+'"><div class="sgs-h">""","""  dm.v.forEach(function(x){""",
"""  var h='<div class="sgs" data-m="'+m.id+'"><div class="sgs-h"><span>Par</span>'+wk.dims.map(function(x,i){return wk.dims.length>1?'<button type="button" class="sgt'+(x===dm?' on':'')+'" data-act="segdim" data-v="'+i+'" aria-pressed="'+(x===dm)+'">'+esc(x.n)+'</button>':'<b>'+esc(x.n)+'</b>';}).join('')+'<span class="sgs-x">exploratoire, sans effet sur la décision</span></div>';
""")
cut("""  return h+'<p class="hint sgs-n">La décision reste celle de la ligne globale.""","""}
function boundsStale(){""","""  return h+'<p class="hint sgs-n">Intervalles à '+lvl(m.role)+' %, non corrigés pour le nombre de valeurs comparées.</p></div>';
""")
rep("""  else if(name==='segx'){""","""  else if(name==='segdim'){ui.segD=+v;}
  else if(name==='segx'){""")
i=s.index("#gst-app .rsel{display:block");j=s.index("#gst-app .sgs{border-top");k=s.index("#gst-app .mrw.sub{cursor:default")
s=s[:i]+"""#gst-app .rsel{display:block;width:14px;height:14px;box-sizing:border-box;border-radius:50%;border:1.5px solid #B9C4C4;background:#fff;justify-self:center;grid-row:1;grid-column:1}#gst-app .mrw:not(.sub):hover .rsel{border-color:#464849}#gst-app .mrw.sel .rsel{border:4px solid #1A1D1F;background:#fff}
#gst-app .pill.nc{color:#6F7374;font-weight:500;border-color:#E3E7E7;background:#fff}
#gst-app .sgl{position:relative;display:inline-flex;align-items:center;gap:4px;min-height:0;margin:0 0 0 10px;padding:0;border:0;background:none;color:#6F7374;font-family:var(--fb,inherit);font-size:12px;font-weight:400;line-height:1.2;vertical-align:middle;cursor:pointer;white-space:nowrap}#gst-app .sgl::after{content:'';position:absolute;inset:-14px -8px}#gst-app .sgl:hover,#gst-app .sgl[aria-expanded=true]{color:#1A1D1F;text-decoration:underline;background:none}#gst-app .sgl-c{width:6px;height:6px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:rotate(45deg) translateY(-2px)}#gst-app .sgl[aria-expanded=true] .sgl-c{transform:rotate(-135deg) translateY(-2px)}
#gst-app .sgs{border-top:1px solid var(--line);background:#FAFBFB}#gst-app .sgs-h{display:flex;flex-wrap:wrap;align-items:center;gap:4px 12px;padding:8px 18px 4px 58px;font-size:12px;color:#6F7374}#gst-app .sgs-h b{color:var(--ink);font-weight:600}#gst-app .sgt{position:relative;min-height:0;margin:0;padding:0;border:0;background:none;color:#6F7374;font-size:12px;font-weight:400;cursor:pointer}#gst-app .sgt::after{content:'';position:absolute;inset:-14px -6px}#gst-app .sgt:hover{color:#1A1D1F;text-decoration:underline;background:none}#gst-app .sgt.on{color:var(--ink);font-weight:600;text-decoration:underline;text-underline-offset:4px}#gst-app .sgs-x{margin-left:auto}
"""+s[k:]
rep("""#gst-app .sgs-n{margin:0;padding:8px 18px 12px 58px;font-size:12px;line-height:1.5}""","""#gst-app .sgs-n{margin:0;padding:6px 18px 10px 58px;font-size:11.5px;line-height:1.4;color:#6F7374}""")
rep("""@media (max-width:760px){#gst-app .sgs-h{padding:10px 14px 4px}#gst-app .sgs-n{padding:8px 14px 12px}#gst-app .sgs-h select{min-height:44px}""","""@media (max-width:760px){#gst-app .sgs-h{padding:10px 14px 4px;gap:10px 14px}#gst-app .sgs-x{margin-left:0;flex-basis:100%}#gst-app .sgs-n{padding:8px 14px 12px}#gst-app .sgl{font-size:13px}""")
assert s.count('v56.31')==1
s=s.replace('v56.31','v56.32')
open('repo/calculateur-sequentiel-v56-32.html','w',newline='').write(s);print(len(s))

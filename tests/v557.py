src='repo/calculateur-sequentiel-v55-6.html';dst='repo/calculateur-sequentiel-v55-7.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
rep("VERSION='v55.6'","VERSION='v55.7'")
# « Nouveau test » : un vrai bouton
rep("""<button type="button" class="link" data-act="new">Nouveau test</button></div>'""","""<button type="button" data-act="new">Nouveau test</button></div>'""")
# « Comment lire les statuts » : lien gris dans le bloc de décision, à la suite des pastilles
rep("""(nN?'<span class="pill">'+nN+' non conclusive'+(nN>1?'s':'')+'</span>':'')+'</div></div></div>';""","""(nN?'<span class="pill">'+nN+' non conclusive'+(nN>1?'s':'')+'</span>':'')+'<button type="button" class="link lgd" data-act="legend" aria-expanded="'+!!ui.legend+'">Comment lire les statuts</button></div></div></div>';""")
a=s.index("""  h+='<div class="tools"><button type="button" data-act="legend" """);b=s.index("""    +'<label class="hist">Historique""",a)
s=s[:a]+"""  h+='<div class="tools hx1">'\n"""+s[b:]
rep("#gst-app button.link.danger{color:#8f2c20}","#gst-app button.link.danger{color:#8f2c20}\n#gst-app button.link.lgd,#gst-app button.link.lgd:hover,#gst-app button.link.lgd:focus{color:var(--charcoal);font-weight:400;font-size:13px;padding:4px 2px;margin-left:4px;align-self:center}#gst-app button.link.lgd:hover{color:var(--ink)}\n#gst-app .tools.hx1{justify-content:flex-end}")
open(dst,'w',newline='').write(s);print(len(s))

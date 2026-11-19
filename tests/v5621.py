s=open('repo/calculateur-sequentiel-v56-20.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:70],s.count(a));s=s.replace(a,b)
# 1. objectif : le chiffre sous le sur-titre, puis le nom de l'indicateur
rep("""<div class="kicker">Objectif principal</div><div class="tp-n vname">'+esc(pr.metric.name)+'<span class="pill '+STATUS[pr.status][1]+'">'+STATUS[pr.status][0]+'</span></div><div class="tp-v vlift num'+(pt2==='g'?'':pt2==='c'?' ng':' nt')+'">'+pct(pr.st.lift)+'</div><div class="tp-c">'+(pr.status==='POSITIF'&&pr.st.lift>0?'Gain relatif observé':'Écart relatif observé')+'</div>""",
    """<div class="kicker">Objectif principal</div><div class="tp-v vlift num'+(pt2==='g'?'':pt2==='c'?' ng':' nt')+'">'+pct(pr.st.lift)+'</div><div class="tp-n vname">'+esc(pr.metric.name)+'<span class="pill '+STATUS[pr.status][1]+'">'+STATUS[pr.status][0]+'</span></div>""")
# 2. bloc de droite : le nombre d'alertes en titre
rep("""<h4>Qualité des données</h4><p class="hint">'+(nAl?nAl+' alerte'+(nAl>1?'s':''):'Aucune alerte')+' sur les trois contrôles '+inW(WK(cur))+'</p>'""",
    """<div class="kicker">Qualité des données</div><h4>'+(nAl?nAl+' alerte'+(nAl>1?'s':''):'Aucune alerte')+'</h4><p class="hint">Trois contrôles lus '+inW(WK(cur))+'</p>'""")
# 3. bandeau de décision sans pictogramme
rep("""'<div class="tp-w '+BN+'">'+bic+'<div><b>'""","""'<div class="tp-w '+BN+'"><div><b>'""")
css="""#gst-app .tp-g{padding-top:22px}#gst-app .verdict.tp .v-main h3{font-size:38px;line-height:42px;margin:8px 0 10px}#gst-app .tp .tp-v{font-size:46px;line-height:42px;margin:8px 0 10px}#gst-app .tp .tp-n{font-size:16px;margin-top:0}#gst-app .tp .tp-b p.num{margin-top:6px}#gst-app .verdict.tp .v-side h4{font-family:var(--ft);font-size:30px;line-height:42px;margin:8px 0 10px;color:var(--ink)}#gst-app .verdict.tp .v-side>.hint{margin:0}
@media (max-width:700px){#gst-app .tp-g{padding-top:0}#gst-app .verdict.tp .v-main h3{font-size:30px;line-height:36px}#gst-app .tp .tp-v{font-size:40px;line-height:40px}#gst-app .verdict.tp .v-side h4{font-size:26px;line-height:34px;margin:6px 0 8px}}
"""
rep("</style>",css.replace('\n',NL)+"</style>")
rep("v56.20","v56.21")
open('repo/calculateur-sequentiel-v56-21.html','w',newline='').write(s);print(len(s))

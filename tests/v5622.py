s=open('repo/calculateur-sequentiel-v56-21.html',newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:70],s.count(a));s=s.replace(a,b)
# le filet au-dessus de la période collait au troisième contrôle : la remise à zéro des marges ne vise plus que la ligne sous le titre
rep("#gst-app .verdict.tp .v-side>.hint{margin:0}","#gst-app .verdict.tp .v-side>h4+.hint{margin:0}#gst-app .verdict.tp .v-side>.tp-pd{margin:16px 0 0;padding-top:14px}")
rep("v56.21","v56.22")
open('repo/calculateur-sequentiel-v56-22.html','w',newline='').write(s);print(len(s))

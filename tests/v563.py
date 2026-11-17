import re
src='repo/calculateur-sequentiel-v56-2.html';dst='repo/calculateur-sequentiel-v56-3.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
rep("VERSION='v56.2'","VERSION='v56.3'")
from PIL import Image
hh=lambda n:Image.open('tuto/out/'+n+'.webp').height
A=['adobe-analytics-export-test-ab-filtrer-experience','adobe-analytics-export-test-ab-choisir-periode','adobe-analytics-export-test-ab-exporter-csv']
a=s.index("  piano:[['piano-analytics-export-test-ab-variations-en-lignes'");e=s.index("]};",a)
s=s[:e]+"],\n  adobe:[['%s','Filtre','Adobe Analytics : filtrer le panneau Analysis Workspace sur l\\'expérience du test A/B','<b>Filtre.</b> Déposez le segment de votre test en haut du panneau, pour n\\'avoir que ses variations.',%d],['%s','Période','Adobe Analytics : choisir la plage de dates du panneau pour exporter un test A/B','<b>Période.</b> Une seule période, du premier jour du test à hier.',%d],['%s','Export CSV','Adobe Analytics : télécharger le tableau à structure libre du test A/B au format CSV','<b>Export.</b> Téléchargez le tableau en CSV, puis déposez le fichier ici.',%d]"%(A[0],hh(A[0]),A[1],hh(A[1]),A[2],hh(A[2]))+s[e:]
open(dst,'w',newline='').write(s);print(len(s))

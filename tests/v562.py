src='repo/calculateur-sequentiel-v56-1.html';dst='repo/calculateur-sequentiel-v56-2.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
rep("VERSION='v56.1'","VERSION='v56.2'")
H=600
# ordre des visuels calé sur les étapes écrites : lignes, colonnes, filtre, période, export
a=s.index("var SHOTS={ga4:[");b=s.index("var LOGOS=",a)
old=s[a:b]
import re
items=re.findall(r"\[('[^\]]*?),(\d+)\]",old)
def get(key):
    m=[x for x in items if key in x[0]];assert len(m)==1,key;return '['+m[0][0]+','+m[0][1]+']'
ga=["['google-analytics-4-export-test-ab-variations-en-lignes','Lignes','Google Analytics 4 : la variation du test A/B en lignes d\\'une exploration libre','<b>Lignes.</b> La variation du test en lignes : une ligne par variation, sans dimension « Semaine ».',%d]"%H,
    "['google-analytics-4-export-test-ab-visiteurs-en-colonnes','Colonnes','Google Analytics 4 : nom de l\\'événement en colonnes et nombre total d\\'utilisateurs en valeurs pour un test A/B','<b>Colonnes.</b> « Nom de l\\'événement » en colonnes, « Nombre total d\\'utilisateurs » en valeurs.',%d]"%H,
    get('google-analytics-4-export-test-ab-filtrer-experience'),get('google-analytics-4-export-test-ab-choisir-periode'),get('google-analytics-4-export-test-ab-exporter-csv')]
pi=["['piano-analytics-export-test-ab-variations-en-lignes','Lignes','Piano Analytics : la propriété mv_creation en lignes dans Data Query pour un test A/B','<b>Lignes.</b> La variation du test en lignes : une ligne par variation, sans dimension « Semaine ».',%d]"%H,
    "['piano-analytics-export-test-ab-visiteurs-en-colonnes','Colonnes','Piano Analytics : visiteurs et visiteurs par objectif en colonnes dans Data Query pour un test A/B','<b>Colonnes.</b> Visiteurs, puis une colonne « visiteurs ayant… » par objectif suivi.',%d]"%H,
    get('piano-analytics-export-test-ab-filtrer-experience'),get('piano-analytics-export-test-ab-choisir-periode'),get('piano-analytics-export-test-ab-exporter-csv')]
nl='\r\n' if '\r\n' in s else '\n'
s=s[:a]+"var SHOTS={ga4:["+','.join(ga)+"],"+nl+"  piano:["+','.join(pi)+"]};"+nl+s[b:]
open(dst,'w',newline='').write(s);print(len(s))

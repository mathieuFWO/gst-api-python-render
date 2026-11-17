src='repo/calculateur-sequentiel-v55-9.html';dst='repo/calculateur-sequentiel-v56-0.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
rep("VERSION='v55.9'","VERSION='v56.0'")
# export Piano réel : colonne « MVT - Test », lignes « N/A », identifiants collés aux libellés
rep("d.cTest=find(/^(test|mv_test|nom du test|experience|experiment)/);","d.cTest=find(/^(test|mv_test|nom du test|experience|experiment)|^mvt?[^a-z0-9]*test/);")
rep("var uniq=function(c){var s=[];data.forEach(function(r){var v=(r[c]||'').trim();if(v&&s.indexOf(v)<0)s.push(v);});return s;};","var uniq=function(c){var s=[];data.forEach(function(r){var v=(r[c]||'').trim();if(v&&!NA_RE.test(v)&&s.indexOf(v)<0)s.push(v);});return s;};")
rep("function analyze(table,fileName,keep){","var NA_RE=/^(n\\/a|na|\\(not set\\)|\\(non défini\\)|null|-)$/i;\n/* Piano colle l'identifiant au libellé (« 0Original », « 2098765Variation 1 ») : on l'ôte à l'affichage si les deux libellés en portent un. */\nfunction cleanLabs(a,b){var re=/^\\d{1,12}(?=[A-Za-zÀ-ÿ\\[])/;return re.test(a)&&re.test(b)&&a.replace(re,'').trim()!==b.replace(re,'').trim()?[a.replace(re,'').trim(),b.replace(re,'').trim()]:[a,b];}\nfunction analyze(table,fileName,keep){")
rep("state.labels={A:d.control,B:d.variant};","var cl=cleanLabs(d.control,d.variant);state.labels={A:cl[0],B:cl[1]};")
# par défaut : le premier test du fichier qui a exactement deux variations
rep("d.tests=d.cTest>=0?uniq(d.cTest):[];d.test=keep&&d.tests.indexOf(keep.test)>=0?keep.test:(d.tests[0]||'');","d.tests=d.cTest>=0?uniq(d.cTest):[];var two=d.tests.filter(function(t){var vs=[];data.forEach(function(r){var v=(r[d.cVar]||'').trim();if((r[d.cTest]||'').trim()===t&&v&&!NA_RE.test(v)&&vs.indexOf(v)<0&&toNum(r[d.cVis])>0)vs.push(v);});return vs.length===2;})[0];d.test=keep&&d.tests.indexOf(keep.test)>=0?keep.test:(state.weeks.length&&d.tests.indexOf(state.name)>=0?state.name:(two||d.tests[0]||''));")
rep("  d.vars=d.cVar>=0?uniq(d.cVar):[];","  d.vars=[];if(d.cVar>=0)data.forEach(function(r){var v=(r[d.cVar]||'').trim();if(v&&!NA_RE.test(v)&&d.vars.indexOf(v)<0&&(d.cTest<0||(r[d.cTest]||'').trim()===d.test))d.vars.push(v);});")
rep("visiteurs pour '+esc(d.control)+', <b class=\"num\">'+nf(last.B)+'</b> pour '+esc(d.variant)+'.","visiteurs pour '+esc(cleanLabs(d.control,d.variant)[0])+', <b class=\"num\">'+nf(last.B)+'</b> pour '+esc(cleanLabs(d.control,d.variant)[1])+'.")
open(dst,'w',newline='').write(s);print(len(s))

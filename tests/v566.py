src='repo/calculateur-sequentiel-v56-5.html';dst='repo/calculateur-sequentiel-v56-6.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:110]); s=s.replace(a,b)
rep("VERSION='v56.5'","VERSION='v56.6'")
# ===== période de l'export cherchée hors du tableau : en-tête commenté, nom du fichier, date du fichier =====
rep("function readFile(f){","""/* Période de l'export quand le tableau n'en porte pas : lignes de commentaire en tête du fichier (« # … »), puis nom du fichier, puis date du fichier.
   Rien n'est tenu pour sûr hors de l'en-tête : la source est affichée et l'utilisateur confirme. */
function metaDates(str){var o=[],re=/(?:^|[^\\d])(?:(\\d{4})[-\\/._]?(\\d{2})[-\\/._]?(\\d{2})|(\\d{2})[-\\/._](\\d{2})[-\\/._](\\d{4}))(?!\\d)/g,x;
  while((x=re.exec(String(str||'')))){var y=+(x[1]||x[6]),mo=+(x[2]||x[5]),d=+(x[3]||x[4]);if(y>=2000&&y<=2100&&mo>=1&&mo<=12&&d>=1&&d<=31){var iso=y+'-'+String(mo).padStart(2,'0')+'-'+String(d).padStart(2,'0');if(addDays(iso,0)===iso)o.push(iso);}}
  return o.sort();}
function headLines(text){var L=String(text||'').replace(/^\\uFEFF/,'').split(/\\r?\\n/),n=0;while(n<L.length&&n<40&&(!L[n].trim()||(/^\\s*"?#/.test(L[n])&&L[n].split(/[;,\\t]/).length<3)))n++;return /#/.test(L.slice(0,n).join(''))?n:0;}
function fileMeta(text,name,lm){
  var m={start:'',end:'',src:'',exp:''},y=addDays(todayISO(),-1),n=headLines(text),a=n?metaDates(String(text).split(/\\r?\\n/).slice(0,n).join('\\n')):[];
  if(a.length){m.end=a[a.length-1];if(a.length>1&&a[0]<m.end)m.start=a[0];m.src='entete';}
  else{a=metaDates(String(name||'').replace(/\\.[a-z0-9]+$/i,''));
    if(a.length){m.end=a[a.length-1];if(a.length>1&&a[0]<m.end)m.start=a[0];m.src='nom';}
    else if(lm>0){var d=new Date(lm),iso=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');if(iso<todayISO()&&iso>='2000-01-01'){m.end=addDays(iso,-1);m.exp=iso;m.src='fichier';}}}
  if(m.end>y){if(m.src==='nom'&&!m.start&&addDays(m.end,-1)<=y){m.end=addDays(m.end,-1);}else m={start:'',end:'',src:'',exp:''};}
  return m;}
function readFile(f){""")
rep("r2.onload=function(){openDraft(r2.result,f.name);};r2.readAsText(f,'windows-1252');}else openDraft(t,f.name);};","r2.onload=function(){openDraft(r2.result,f.name,f.lastModified);};r2.readAsText(f,'windows-1252');}else openDraft(t,f.name,f.lastModified);};")
rep("function openDraft(text,name){\n  ui.error='';ui.notice='';var t=parseCSV(text);","function openDraft(text,name,lm){\n  ui.error='';ui.notice='';ui.meta=fileMeta(text,name,lm);var hn=headLines(text);if(hn)text=String(text).replace(/^\\uFEFF/,'').split(/\\r?\\n/).slice(hn).join('\\n');var t=parseCSV(text);") if "function openDraft(text,name){\n  ui.error" in s else rep("function openDraft(text,name){\r\n  ui.error='';ui.notice='';var t=parseCSV(text);","function openDraft(text,name,lm){\r\n  ui.error='';ui.notice='';ui.meta=fileMeta(text,name,lm);var hn=headLines(text);if(hn)text=String(text).replace(/^\\uFEFF/,'').split(/\\r?\\n/).slice(hn).join('\\n');var t=parseCSV(text);")
rep("d.endFromFile=!!ed;d.endDate=keep&&keep.endDate?keep.endDate:(ed||addDays(todayISO(),-1));",
    "var M=ui.meta||{};d.endFromFile=!!ed;d.endDate=keep&&keep.endDate?keep.endDate:(ed||M.end||addDays(todayISO(),-1));d.endSrc=keep?(keep.endSrc||''):(ed?'':(M.end?M.src:''));d.endExp=M.exp||'';")
rep("d.startDate=keep&&keep.startDate?keep.startDate:(isoD(sd)||(d.mode==='instantane'&&!state.weeks.length?addDays(d.endDate,-6):state.plan.startDate));d.startGuess=!(keep&&keep.startDate)&&!isoD(sd)&&d.mode==='instantane'&&!state.weeks.length;",
    "var ms=!isoD(sd)&&d.mode==='instantane'&&!state.weeks.length&&M.start&&M.start<d.endDate?M.start:'';d.startDate=keep&&keep.startDate?keep.startDate:(isoD(sd)||ms||(d.mode==='instantane'&&!state.weeks.length?addDays(d.endDate,-6):state.plan.startDate));d.startGuess=!(keep&&keep.startDate)&&!isoD(sd)&&!ms&&d.mode==='instantane'&&!state.weeks.length;d.startSrc=keep?(keep.startSrc||''):(ms?M.src:'');")
rep("else if(f==='startDate'){d.startDate=t.value;d.startGuess=false;}else if(f==='endDate')d.endDate=t.value;","else if(f==='startDate'){d.startDate=t.value;d.startGuess=false;d.startSrc='';}else if(f==='endDate'){d.endDate=t.value;d.endSrc='';}")
rep("var keep={name:d.name,k:d.k,startDate:d.startDate,endDate:d.endDate,","var keep={name:d.name,k:d.k,startDate:d.startDate,endDate:d.endDate,endSrc:d.endSrc,startSrc:d.startSrc,")
rep("(gate.ok&&d.startGuess?' <b>Vérifiez la date de début</b> : elle est supposée une semaine avant la fin des données.':'')+'</span>'",
    "(gate.ok&&d.startGuess?' <b>Vérifiez la date de début</b> : elle est supposée une semaine avant la fin des données.':'')+srcNote(d)+'</span>'")
rep("function readFile(f){","""function srcNote(d){var e=d.endSrc,s=d.startSrc;
  if(e==='entete')return ' '+(s==='entete'?'Période':'Date de fin')+' lue dans l\\'en-tête du fichier.';
  if(e==='nom')return ' <b>'+(s==='nom'?'Période lue':'Date de fin lue')+' dans le nom du fichier</b> : vérifiez-la.';
  if(e==='fichier')return ' <b>Date de fin déduite de la date du fichier</b> (exporté le '+frDate(d.endExp)+', donc données jusqu\\'à la veille) : vérifiez-la.';
  return '';}
function readFile(f){""")
rep("openCSV:openDraft,","openCSV:openDraft,meta:fileMeta,")
open(dst,'w',newline='').write(s);print(len(s))

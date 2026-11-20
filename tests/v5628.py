# v56-28 : un export qui détaille chaque variation par une autre dimension (appareil, source...) est lu.
# La décision se lit au global (lignes additionnées) ; le détail par valeur est gardé et s'ouvre au clic dans les résultats, en lecture exploratoire.
# Les colonnes de montant ou de volume ne sont plus proposées comme des taux.
s=open('repo/calculateur-sequentiel-v56-27.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(a[:80],s.count(a));s=s.replace(a,b)
# 1. analyse : montants / volumes
rep("""    else mets.push({src:h,name:h,type:'binaire',col:i});});""",
"""    else{var na='';data.forEach(function(r){var x=toNum(r[i]),nv=d.cVis>=0?toNum(r[d.cVis]):NaN;if(!isFinite(x))return;if(x!==Math.round(x)||x<0)na='montant';else if(!na&&isFinite(nv)&&nv>0&&x>nv&&d.cVar>=0&&(r[d.cVar]||'').trim()&&!NA_RE.test((r[d.cVar]||'').trim()))na='volume';});
      mets.push({src:h,name:h,type:'binaire',col:i,na:na});}});""")
rep("""    var role=ex?ex.role:(guard?'garde-fou':(firstPrim&&m.type==='binaire'?'principale':'secondaire'));if(!ex&&role==='principale')firstPrim=false;
    return {src:m.src,name:ex?ex.name:m.name,type:m.type,col:m.col,col2:m.col2,include:ex?true:(state.metrics.length?false:idx<MAX_METRICS),""",
"""    var na=ex?'':(m.na||''),role=ex?ex.role:(na?'secondaire':guard?'garde-fou':(firstPrim&&m.type==='binaire'?'principale':'secondaire'));if(!ex&&role==='principale')firstPrim=false;
    return {src:m.src,name:ex?ex.name:m.name,type:m.type,col:m.col,col2:m.col2,na:na,include:ex?true:(na?false:state.metrics.length?false:idx<MAX_METRICS),""")
rep("""  if(!state.metrics.length&&!d.metrics.some(function(m){return m.role==='principale';})&&d.metrics[0])d.metrics[0].role='principale';""",
"""  if(!state.metrics.length&&!d.metrics.some(function(m){return m.role==='principale';})){var m0=d.metrics.filter(function(m){return !m.na;})[0];if(m0)m0.role='principale';}""")
# 2. analyse : colonne de détail
rep("""  var wk=d.cWeek>=0?d.cWeek:d.cEnd;d.keys=[];
  if(wk>=0)rowsT.forEach(""",
"""  var wk=d.cWeek>=0?d.cWeek:d.cEnd;d.keys=[];
  /* Colonne de détail : une colonne de texte qui découpe chaque variation en plusieurs lignes (appareil, source...), chaque valeur une seule fois. */
  d.cSeg=-1;d.segs=[];
  if(d.cVar>=0&&d.control){var grp={},multi=false;rowsT.forEach(function(r){var v=(r[d.cVar]||'').trim();if(v!==d.control&&v!==d.variant)return;var kk=v+'\\u0001'+(wk>=0?(r[wk]||'').trim():'');(grp[kk]=grp[kk]||[]).push(r);});
    Object.keys(grp).forEach(function(kk){if(grp[kk].length>1)multi=true;});
    if(multi){var cand=[];H.forEach(function(h,i){if(used.indexOf(i)>=0||isNum(i))return;var okc=Object.keys(grp).every(function(kk){var seen=[];return grp[kk].every(function(r){var v=(r[i]||'').trim();if(!v||seen.indexOf(v)>=0)return false;seen.push(v);return true;});});if(okc)cand.push(i);});
      var SM=state.weeks.length&&state.map?state.map:null,pc=SM&&SM.sc?byName(SM.sc):-1;d.cSeg=cand.indexOf(pc)>=0?pc:(cand.length?cand[0]:-1);
      if(d.cSeg>=0)rowsT.forEach(function(r){var v=(r[d.cVar]||'').trim(),x=(r[d.cSeg]||'').trim();if((v===d.control||v===d.variant)&&x&&d.segs.indexOf(x)<0)d.segs.push(x);});}}
  if(wk>=0)rowsT.forEach(""")
rep("""function draftVis(d){""",
"""/* Lignes d'une variation pour une lecture : une seule en temps normal, plusieurs si le fichier détaille par une autre colonne (sv : une seule valeur de cette colonne). */
function segRows(d,rowsT,val,key,wk,sv){return rowsT.filter(function(r){return (r[d.cVar]||'').trim()===val&&(key===null||(r[wk]||'').trim()===key)&&(!sv||(r[d.cSeg]||'').trim()===sv);});}
function segSum(rs,c){return rs.length===1?toNum(rs[0][c]):rs.reduce(function(a,r){return a+toNum(r[c]);},0);}
function draftVis(d){""")
rep("""var rs=rowsT.filter(function(r){return (r[d.cVar]||'').trim()===p[1]&&(keys[i]===null||(r[wk]||'').trim()===keys[i]);});o[p[0]]=rs.length===1?toNum(rs[0][d.cVis]):NaN;});""",
"""var rs=segRows(d,rowsT,p[1],keys[i],wk);o[p[0]]=rs.length===1||(rs.length>1&&d.cSeg>=0)?segSum(rs,d.cVis):NaN;});""")
rep("""      var rs=rowsT.filter(function(r){return (r[d.cVar]||'').trim()===p[1]&&(key===null||(r[wk]||'').trim()===key);});
      if(rs.length!==1){errs.push(lab+' : '+rs.length+' ligne(s) pour « '+p[1]+' » (1 attendue).');return;}
      var r=rs[0],n=toNum(r[d.cVis]),o={n:n,m:{}};""",
"""      var rs=segRows(d,rowsT,p[1],key,wk);
      if(!rs.length||(rs.length>1&&d.cSeg<0)){errs.push(lab+' : '+rs.length+' ligne(s) pour « '+p[1]+' » (1 attendue).'+(rs.length>1?' Le fichier détaille sans doute chaque variation par une autre colonne (date, page...) : refaites l\\'export avec la variation seule en ligne.':''));return;}
      var r={};d.H.forEach(function(h,c){r[c]=rs.length===1?rs[0][c]:String(segSum(rs,c));});var n=toNum(r[d.cVis]),o={n:n,m:{}};""")
rep("""    if(W.A&&W.B){if(d.mode==='instantane'&&/^\\d{4}-\\d{2}-\\d{2}$/.test(d.endDate||''))W.end=d.endDate;""",
"""    if(W.A&&W.B&&d.cSeg>=0&&!errs.length){var sg=d.segs.map(function(l){var o={l:l.slice(0,60)};[['A',d.control],['B',d.variant]].forEach(function(p){var rs=segRows(d,rowsT,p[1],key,wk,l),a={n:rs.length?segSum(rs,d.cVis):0,m:{}};inc.forEach(function(m){a.m[m.id]=m.type==='continue'?{s:rs.length?segSum(rs,m.col):0,ss:rs.length?segSum(rs,m.col2):0}:{c:rs.length?segSum(rs,m.col):0};});o[p[0]]=a;});return o;})
      .filter(function(o){return isFinite(o.A.n+o.B.n)&&o.A.n+o.B.n>0;}).sort(function(a,b){return (b.A.n+b.B.n)-(a.A.n+a.B.n);}).slice(0,MAX_SEG);if(sg.length>1)W.seg=sg;}
    if(W.A&&W.B){if(d.mode==='instantane'&&/^\\d{4}-\\d{2}-\\d{2}$/.test(d.endDate||''))W.end=d.endDate;""")
rep("""MAX_METRICS=15,VERSION=""","""MAX_METRICS=15,MAX_SEG=12,VERSION=""")
# 3. nom de la colonne de détail et détail gardés avec le test
rep("""tv:d.test||'',c:d.control||'',v:d.variant||''};
  if(replace)""","""tv:d.test||'',c:d.control||'',v:d.variant||'',sc:d.cSeg>=0?d.H[d.cSeg]:((state.map&&state.map.sc)||'')};
  if(replace)""")
rep("""c:str(M.c,160),v:str(M.v,160)};""","""c:str(M.c,160),v:str(M.v,160),sc:str(M.sc,160)};""")
rep("""var r={A:arm(w.A),B:arm(w.B)},wk=Math.round(Number(w.wk));""","""var r={A:arm(w.A),B:arm(w.B)},wk=Math.round(Number(w.wk));if(Array.isArray(w.seg)){var sg=w.seg.slice(0,MAX_SEG).filter(function(x){return x&&typeof x==='object'&&str(x.l,60);}).map(function(x){return {l:str(x.l,60),A:arm(x.A),B:arm(x.B)};});if(sg.length>1)r.seg=sg;}""")
# 4. interface de l'import
rep("""      +(last&&d.excl>=0?'<p class="dv-read"><span>'""",
"""      +(d.cSeg>=0?'<div class="dv-seg"><p><b>Ce fichier détaille chaque variation par « '+esc(d.H[d.cSeg])+' »</b> ('+esc(d.segs.slice(0,4).join(', '))+(d.segs.length>4?'…':'')+'). La décision se lit au global : l\\'outil additionne ces lignes, et garde le détail pour le bouton « Segmenter » des résultats. Un visiteur présent dans plusieurs lignes est compté plusieurs fois : c\\'est marginal pour un type d\\'appareil, faux pour une page ou une date.</p></div>':'')
      +(last&&d.excl>=0?'<p class="dv-read"><span>'""")
rep("""return '<div class="dv-m'+(m.include&&m.role==='principale'?' on':'')+(m.include?'':' off')+'"><input type="checkbox" data-dm="include" data-i="'+i+'"'+(m.include?' checked':'')+(locked?' disabled':'')+""",
"""if(m.na)return '<div class="dv-m off na"><input type="checkbox" disabled aria-label="'+esc(m.name)+' : non analysable"><span class="dv-nn">'+esc(m.name)+'</span><span class="pill">'+(m.na==='montant'?'Montant':'Volume')+'</span><span class="dv-na">'+(m.na==='montant'?'Non analysable depuis cet export : un montant demande aussi la somme des carrés par visiteur (colonnes « somme » et « somme des carrés », voir BigQuery).':'Non analysable : la valeur dépasse le nombre de visiteurs, ce n\\'est donc pas un nombre de visiteurs ayant fait l\\'action.')+'</span></div>';
        return '<div class="dv-m'+(m.include&&m.role==='principale'?' on':'')+(m.include?'':' off')+'"><input type="checkbox" data-dm="include" data-i="'+i+'"'+(m.include?' checked':'')+(locked?' disabled':'')+""")
rep("""#gst-app .dv-warn{background:#FBF1DC;""","""#gst-app .dv-seg{margin-top:16px;padding:12px 16px;background:#F8FBFA;border:1px solid #D9D9D9;border-radius:6px}#gst-app .dv-seg p{margin:0;font-size:13px;line-height:1.5;color:var(--charcoal)}#gst-app .dv-m.na .dv-na{grid-column:4/-1;font-size:13px;line-height:1.45;color:var(--charcoal)}#gst-app .dv-m.na .dv-nn{font-size:15px;color:var(--charcoal);overflow-wrap:anywhere}@media (max-width:760px){#gst-app .dv-m.na .dv-na{grid-column:1/-1}}
#gst-app .sgx{margin-top:22px;border-top:1px solid var(--line);padding-top:14px}#gst-app .sgx-b{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:8px 14px;font-size:14px;font-weight:600}#gst-app .sgx-h{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 16px}#gst-app .sgx-h label{display:flex;align-items:center;gap:8px;margin:0;font-size:13px;color:var(--charcoal)}#gst-app .sgx-h select{min-height:44px;max-width:260px}
#gst-app .sgx-t{margin-top:12px;border:1px solid var(--line);border-radius:8px;background:#fff;overflow:hidden}#gst-app .sgx-r{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1.2fr) minmax(0,1.3fr);gap:6px 16px;align-items:center;padding:10px 16px;border-top:1px solid var(--line);font-size:14px}#gst-app .sgx-r:first-child{border-top:0}#gst-app .sgx-r.hd{font-size:12px;color:var(--charcoal);padding:8px 16px;background:#F8FBFA}#gst-app .sgx-r.tot{background:#F8FBFA}#gst-app .sgx-r>div{min-width:0;overflow-wrap:anywhere}#gst-app .sgx-r>div:nth-child(n+2){text-align:right}#gst-app .sgx-r .hint{display:block;margin:0;font-size:12px}#gst-app .sgx>p.hint{margin:10px 0 0;line-height:1.5}
@media (max-width:760px){#gst-app .sgx-b{width:100%;justify-content:center}#gst-app .sgx-h label,#gst-app .sgx-h select{width:100%;max-width:none}#gst-app .sgx-h label{flex-direction:column;align-items:flex-start}#gst-app .sgx-r{grid-template-columns:minmax(0,1fr) auto;padding:10px 12px}#gst-app .sgx-r.hd{display:none}#gst-app .sgx-r>div:first-child{grid-column:1/-1}#gst-app .sgx-r>div:nth-child(2){text-align:left;font-size:13px;color:var(--charcoal)}}
#gst-app .dv-warn{background:#FBF1DC;""")
# 5. résultats : détail au clic
rep("""  var m=state.metrics.filter(function(x){return x.id===sel;})[0],mi=state.metrics.indexOf(m);""",
"""  if(wk.seg&&wk.seg.length>1){var sn=(state.map&&state.map.sc)||'segment',sm=state.metrics.filter(function(x){return x.id===ui.segM;})[0]||state.metrics.filter(function(x){return x.role==='principale';})[0]||state.metrics[0],scn=sm.type==='continue',sf=function(v){return v==null||!isFinite(v)?'—':scn?nf(v,2):nf(v*100,2)+' %';},crit=ciFor(sm.role,cur);
    var sline=function(l,a,b,cl){var s=stat(sm,a,b,crit),va=a.m[sm.id],vb=b.m[sm.id],lowv=!scn&&va&&vb&&Math.min(va.c,vb.c)<LOWC;return '<div class="sgx-r'+(cl?' '+cl:'')+'"><div><b>'+esc(l)+'</b><span class="hint num">'+nf(a.n+b.n)+' visiteurs'+(cl?'':' · '+nf((a.n+b.n)/tot*100,1)+' %')+'</span></div><div class="num">'+sf(s&&s.mA)+' → '+sf(s&&s.mB)+'</div><div class="num"><b>'+(s?pct(s.lift):'—')+'</b><span class="hint">'+(s&&s.lo!=null?'de '+pct(s.lo)+' à '+pct(s.hi):'')+(lowv?(s&&s.lo!=null?' · ':'')+'volume très faible':'')+'</span></div></div>';};
    h+='<div class="sgx"><div class="sgx-h"><button type="button" class="sgx-b" data-act="segtog" aria-expanded="'+!!ui.segOn+'"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16"><path d="M2 3.500h12M4.500 8h7M7 12.500h2" fill="none" stroke="currentColor" stroke-width="1.600" stroke-linecap="round"/></svg>'+(ui.segOn?'Masquer le détail par « ':'Segmenter par « ')+esc(sn)+' »</button>'
      +(ui.segOn&&state.metrics.length>1?'<label>Métrique <select data-act="segmet" aria-label="Métrique détaillée">'+state.metrics.map(function(x){return '<option value="'+x.id+'"'+(x===sm?' selected':'')+'>'+esc(x.name)+'</option>';}).join('')+'</select></label>':'')+'</div>';
    if(ui.segOn)h+='<div class="sgx-t"><div class="sgx-r hd"><div>'+esc(sn)+'</div><div>Contrôle → Variante</div><div>Écart sur '+esc(sm.name)+'</div></div>'+sline('Global',wk.A,wk.B,'tot')+wk.seg.map(function(x){return sline(x.l,x.A,x.B,'');}).join('')+'</div>'
      +'<p class="hint"><b>Lecture exploratoire.</b> La décision reste celle du résultat global. Les intervalles sont ceux de la lecture '+inW(WK(cur))+' (à '+lvl(sm.role)+' %), sans correction pour le nombre de valeurs comparées : plus on découpe, plus un écart peut apparaître par hasard. Un écart net sur une valeur est une piste à confirmer par un test dédié.'+'</p>';
    h+='</div>';}
  var m=state.metrics.filter(function(x){return x.id===sel;})[0],mi=state.metrics.indexOf(m);""")
rep("""  else if(name==='qdetail'){ui.qd=!ui.qd;}""","""  else if(name==='qdetail'){ui.qd=!ui.qd;}
  else if(name==='segtog'){ui.segOn=!ui.segOn;}""")
rep("""  if(t.matches('[data-act=weeksel]')){ui.week=+t.value;return later();}""","""  if(t.matches('[data-act=weeksel]')){ui.week=+t.value;return later();}
  if(t.matches('[data-act=segmet]')){ui.segM=t.value;return later();}""")
# 6. gestionnaire de l'import
rep("""if(o){m.include=o.include;m.role=o.role;m.sens=o.sens;m.name=o.name;}});""","""if(o&&!m.na&&!o.na){m.include=o.include;m.role=o.role;m.sens=o.sens;m.name=o.name;}});""")
rep("""    if(g==='include')m.include=t.checked;else m[g]=t.value;""","""    if(m.na)return;if(g==='include')m.include=t.checked;else m[g]=t.value;""")
assert s.count('v56.27')==1
s=s.replace('v56.27','v56.28')
open('repo/calculateur-sequentiel-v56-28.html','w',newline='').write(s);print(len(s))

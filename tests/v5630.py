# v56-30 : date de fin proposée à J+7, import replié quand la structure n'a pas changé, liste des dimensions à l'import,
# segmentation à la manière de Statsig (un « + » sur chaque métrique, lignes par valeur sous la métrique), plusieurs dimensions, message sur les montants.
s=open('repo/calculateur-sequentiel-v56-29.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(a[:80],s.count(a));s=s.replace(a,b)
def cut(a,b,new):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==1,(a[:60],s.count(a));i=s.index(a);j=s.index(b,i);s=s[:i]+new.replace('\n',NL)+s[j:]
# ---- A. dimensions : plusieurs colonnes de texte, unicité sur leur combinaison
cut("""  d.cSeg=-1;d.segs=[];""","""  if(wk>=0)rowsT.forEach(""",
"""  d.cSeg=-1;d.segs=[];d.dimCols=[];
  if(d.cVar>=0&&d.control){var grp={},multi=false;rowsT.forEach(function(r){var v=(r[d.cVar]||'').trim();if(v!==d.control&&v!==d.variant)return;var kk=v+'\\u0001'+(wk>=0?(r[wk]||'').trim():'');(grp[kk]=grp[kk]||[]).push(r);});
    Object.keys(grp).forEach(function(kk){if(grp[kk].length>1)multi=true;});
    if(multi){var tc=[];H.forEach(function(h,i){if(used.indexOf(i)<0&&!isNum(i)&&Object.keys(grp).every(function(kk){return grp[kk].every(function(r){return (r[i]||'').trim()!=='';});}))tc.push(i);});
      var okc=tc.length>0&&Object.keys(grp).every(function(kk){var seen={};return grp[kk].every(function(r){var t=tc.map(function(i){return (r[i]||'').trim();}).join('\\u0001');if(seen[t])return false;seen[t]=1;return true;});});
      if(okc){tc.forEach(function(i){var vs=[];rowsT.forEach(function(r){var v=(r[d.cVar]||'').trim(),x=(r[i]||'').trim();if((v===d.control||v===d.variant)&&vs.indexOf(x)<0)vs.push(x);});if(vs.length>1&&d.dimCols.length<MAX_DIM)d.dimCols.push({c:i,vals:vs});});
        if(d.dimCols.length){d.cSeg=d.dimCols[0].c;d.segs=d.dimCols[0].vals;}}}}
""")
rep("""function segRows(d,rowsT,val,key,wk,sv){return rowsT.filter(function(r){return (r[d.cVar]||'').trim()===val&&(key===null||(r[wk]||'').trim()===key)&&(!sv||(r[d.cSeg]||'').trim()===sv);});}""",
"""function segRows(d,rowsT,val,key,wk,sv,col){return rowsT.filter(function(r){return (r[d.cVar]||'').trim()===val&&(key===null||(r[wk]||'').trim()===key)&&(sv==null||(r[col]||'').trim()===sv);});}""")
cut("""    if(W.A&&W.B&&d.cSeg>=0&&!errs.length){var sg=""","""    if(W.A&&W.B){if(d.mode==='instantane'""",
"""    if(W.A&&W.B&&d.cSeg>=0&&!errs.length){var dm=d.dimCols.map(function(dc){var sg=dc.vals.map(function(l){var o={l:l.slice(0,60)};[['A',d.control],['B',d.variant]].forEach(function(p){var rs=segRows(d,rowsT,p[1],key,wk,l,dc.c),a={n:rs.length?segSum(rs,d.cVis):0,m:{}};inc.forEach(function(m){a.m[m.id]=m.type==='continue'?{s:rs.length?segSum(rs,m.col):0,ss:rs.length?segSum(rs,m.col2):0}:{c:rs.length?segSum(rs,m.col):0};});o[p[0]]=a;});return o;})
        .filter(function(o){return isFinite(o.A.n+o.B.n)&&o.A.n+o.B.n>0;}).sort(function(a,b){return (b.A.n+b.B.n)-(a.A.n+a.B.n);}).slice(0,MAX_SEG);return {n:d.H[dc.c].slice(0,160),v:sg};}).filter(function(x){return x.v.length>1;});if(dm.length)W.dims=dm;}
""")
rep("""MAX_METRICS=15,MAX_SEG=12,VERSION=""","""MAX_METRICS=15,MAX_SEG=12,MAX_DIM=3,VERSION=""")
rep("""if(Array.isArray(w.seg)){var sg=w.seg.slice(0,MAX_SEG).filter(function(x){return x&&typeof x==='object'&&str(x.l,60);}).map(function(x){return {l:str(x.l,60),A:arm(x.A),B:arm(x.B)};});if(sg.length>1)r.seg=sg;}""",
"""var segL=function(a){return (Array.isArray(a)?a:[]).slice(0,MAX_SEG).filter(function(x){return x&&typeof x==='object'&&str(x.l,60);}).map(function(x){return {l:str(x.l,60),A:arm(x.A),B:arm(x.B)};});},dm=[];
    if(Array.isArray(w.dims))w.dims.slice(0,MAX_DIM).forEach(function(x){if(!x||typeof x!=='object')return;var v=segL(x.v);if(v.length>1)dm.push({n:str(x.n,160)||'Dimension',v:v});});
    else if(Array.isArray(w.seg)){var v0=segL(w.seg);if(v0.length>1)dm.push({n:str(o.map&&typeof o.map==='object'?o.map.sc:'',160)||'Dimension',v:v0});}
    if(dm.length)r.dims=dm;""")
# ---- B. résultats : « + » sur chaque métrique, lignes par valeur
cut("""  if(wk.seg&&wk.seg.length>1){var sn=""","""  var m=state.metrics.filter(function(x){return x.id===sel;})[0],mi=state.metrics.indexOf(m);""","")
rep("""rowHead(ax)+rows.map(function(r){return metricRow(r,wk,ax,sel,g[0]==='principale');}).join('')+'</div>';""",
"""rowHead(ax)+rows.map(function(r){return metricRow(r,wk,ax,sel,g[0]==='principale')+segSub(r,wk,ax,cur);}).join('')+'</div>';""")
rep("""    +'<div class="c-name"><div class="mn">'+esc(m.name)+'</div>""",
"""    +'<div class="c-name"><div class="mn">'+esc(m.name)+(wk.dims&&wk.dims.length&&st?'<button type="button" class="sgp" data-act="segx" data-v="'+m.id+'" aria-expanded="'+!!(ui.segX&&ui.segX[m.id])+'" aria-label="'+(ui.segX&&ui.segX[m.id]?'Masquer':'Afficher')+' le détail de '+esc(m.name)+' par '+esc(segDim(wk).n)+'" title="Détailler par '+esc(segDim(wk).n)+'">'+(ui.segX&&ui.segX[m.id]?'−':'+')+'</button>':'')+'</div>""")
rep("""function boundsStale(){""",
"""/* Détail d'une métrique par valeur d'une dimension, sous sa ligne : lecture exploratoire, mêmes intervalles que la lecture globale. */
function segDim(wk){return wk.dims[ui.segD>=0&&ui.segD<wk.dims.length?ui.segD:0];}
function segSub(r,wk,ax,cur){
  var m=r.metric;if(!wk.dims||!wk.dims.length||!ui.segX||!ui.segX[m.id]||!r.st)return '';
  var dm=segDim(wk),cont=m.type==='continue',crit=ciFor(m.role,cur),tot=wk.A.n+wk.B.n,fv=function(v){return v==null||!isFinite(v)?'—':cont?nf(v,2):nf(v*100,2)+' %';};
  var h='<div class="sgs" data-m="'+m.id+'"><div class="sgs-h"><span>'+esc(m.name)+' par</span>'+(wk.dims.length>1?'<select data-act="segdim" aria-label="Dimension du détail">'+wk.dims.map(function(x,i){return '<option value="'+i+'"'+(x===dm?' selected':'')+'>'+esc(x.n)+'</option>';}).join('')+'</select>':'<b>'+esc(dm.n)+'</b>')+'<span class="pill">Exploratoire</span></div>';
  dm.v.forEach(function(x){var st=stat(m,x.A,x.B,crit),va=x.A.m[m.id],vb=x.B.m[m.id],low=!cont&&va&&vb&&Math.min(va.c,vb.c)<LOWC;
    h+='<div class="mrw sub"><span></span><div class="c-name"><div class="mn">'+esc(x.l)+'</div><div class="hint"><span class="mob num">'+fv(st&&st.mA)+' → '+fv(st&&st.mB)+' · </span><span class="num">'+nf(x.A.n+x.B.n)+' visiteurs · '+nf((x.A.n+x.B.n)/tot*100,1)+' %</span>'+(low?' · moins de '+LOWC+' conversions':'')+'</div></div>'
      +'<div class="c-a num">'+fv(st&&st.mA)+'</div><div class="c-b num">'+fv(st&&st.mB)+'</div><div class="c-lift"><span class="lift num">'+pct(st&&st.lift)+'</span></div><div class="c-ci">'+ciBar(st,ax,'')+'</div><div class="c-st"></div></div>';});
  return h+'<p class="hint sgs-n">La décision reste celle de la ligne globale. Intervalles de la lecture '+(U()?'au jour ':'en semaine ')+WK(cur)+' (à '+lvl(m.role)+' %), sans correction pour le nombre de valeurs comparées : plus on découpe, plus un écart peut apparaître par hasard.</p></div>';
}
function boundsStale(){""")
rep("""  else if(name==='segtog'){ui.segOn=!ui.segOn;}""","""  else if(name==='segx'){ui.segX=ui.segX||{};ui.segX[v]=!ui.segX[v];}
  else if(name==='dvfull'){ui.dvFull=true;}""")
rep("""  if(t.matches('[data-act=segmet]')){ui.segM=t.value;return later();}""","""  if(t.matches('[data-act=segdim]')){ui.segD=+t.value;return later();}""")
# ---- C. import : dimensions listées, structure inchangée repliée
cut("""      +(d.cSeg>=0?'<div class="dv-seg"><p><b>Ce fichier détaille""","""      +(last&&d.excl>=0?'<p class="dv-read"><span>'""",
"""      +'<div class="dv-dims"><span class="dv-dl">Dimensions du fichier</span>'+(d.cTest>=0?'<span class="dv-dc"><b>'+esc(d.H[d.cTest])+'</b> test</span>':'')+(d.cVar>=0?'<span class="dv-dc"><b>'+esc(d.H[d.cVar])+'</b> variations</span>':'')+((d.cWeek>=0?d.cWeek:d.cEnd)>=0?'<span class="dv-dc"><b>'+esc(d.H[d.cWeek>=0?d.cWeek:d.cEnd])+'</b> période</span>':'')+d.dimCols.map(function(dc){return '<span class="dv-dc seg"><b>'+esc(d.H[dc.c])+'</b> segmentation · '+dc.vals.length+' valeurs</span>';}).join('')+'</div>'
      +(d.cSeg>=0?'<p class="dv-seg">La décision se lit au global : l\\'outil additionne les lignes de chaque variation. Dans les résultats, le « + » d\\'une métrique la détaille par '+esc(d.dimCols.map(function(dc){return '« '+d.H[dc.c]+' »';}).join(' ou '))+'. Un visiteur présent dans plusieurs lignes est compté plusieurs fois : marginal pour un type d\\'appareil, faux pour une page ou une date.</p>':'')
""")
rep("""+'</div>')+'<div class="dv-sec"><div class="kicker">2 · Ce que l\\'outil a lu</div><div class="dv-g">'""",
"""+'</div>')+(same?'<div class="dv-same">'+ICON.ok+'<span><b>Même structure que la lecture précédente.</b> Variations, visiteurs et '+state.metrics.length+' métrique'+(state.metrics.length>1?'s':'')+' retrouvés'+(d.dimCols.length?', détail par '+esc(d.dimCols.map(function(dc){return '« '+d.H[dc.c]+' »';}).join(' et '))+' conservé':'')+'.'+(last?' Dernier cumul lu : <b class="num">'+nf(last.A)+'</b> visiteurs pour '+esc(cleanLabs(d.control,d.variant)[0])+', <b class="num">'+nf(last.B)+'</b> pour '+esc(cleanLabs(d.control,d.variant)[1])+'.':'')+'</span><button type="button" class="link" data-act="dvfull">Voir le détail</button></div>':'<div class="dv-sec"><div class="kicker">2 · Ce que l\\'outil a lu</div><div class="dv-g">'""")
rep("""'<p class="err">Aucune colonne numérique de métrique détectée.</p>')+'</div>'
      +'<p class="row dv-act">""","""'<p class="err">Aucune colonne numérique de métrique détectée.</p>')+'</div>')
      +'<p class="row dv-act">""")
rep("""last=vis&&vis[vis.length-1],nInc=d.metrics.filter(function(m){return m.include;}).length;""",
"""last=vis&&vis[vis.length-1],nInc=d.metrics.filter(function(m){return m.include;}).length,SM=state.map,pw=state.weeks[state.weeks.length-1];
    var same=!!(locked&&!ui.dvFull&&SM&&!lk.length&&!d.errors.length&&last&&d.cVar>=0&&d.cVis>=0&&d.H[d.cVar]===SM.vr&&d.H[d.cVis]===SM.vis&&(d.cTest>=0?d.H[d.cTest]:'')===(SM.test||'')&&(d.test||'')===(SM.tv||'')&&d.control===SM.c&&d.variant===SM.v&&state.metrics.every(function(m){return d.metrics.some(function(x){return x.src===m.src&&x.include;});})&&d.dimCols.map(function(dc){return d.H[dc.c];}).join('\\u0001')===((pw&&pw.dims)||[]).map(function(x){return x.n;}).join('\\u0001'));""")
rep("""  ui.rawTable=t;ui.draft=analyze(t,name,null);ui.tab='donnees';render();""","""  ui.rawTable=t;ui.dvFull=false;ui.draft=analyze(t,name,null);ui.tab='donnees';render();""")
# ---- D. dates : J+7 après la lecture précédente, ou fin de la première semaine quand la date de début est saisie
rep("""d.endDate=keep&&keep.endDate?keep.endDate:(ed||M.end||addDays(todayISO(),-1));d.endSrc=keep?(keep.endSrc||''):(ed?'':(M.end?M.src:''));""",
"""var pwk=state.weeks.length?state.weeks[state.weeks.length-1]:null,pEnd=d.mode==='instantane'&&pwk&&pwk.end&&state.plan.unit!=='jour'?pwk.end:'',aEnd=autoEnd(pEnd?addDays(pEnd,7):'');d.endDate=keep&&keep.endDate?keep.endDate:(ed||M.end||aEnd);d.endSrc=keep?(keep.endSrc||''):(ed?'':(M.end?M.src:(pEnd&&aEnd!==addDays(todayISO(),-1)?'j7':'')));d.prevEnd=pEnd;""")
rep("""function endNeed(d){""","""/* Date de fin proposée : la date attendue (J+7) si elle est passée depuis plus d'une semaine, sinon hier (test suivi en direct). */
function autoEnd(base){var y=addDays(todayISO(),-1);if(!base||base>y)return y;return dayDiff(base,y)<7?y:base;}
function endNeed(d){""")
rep("""  if(e==='nom')return ' <b>'+(s==='nom'""","""  if(e==='j7')return ' <b>Date proposée : 7 jours après la lecture précédente</b> ('+frDate(d.prevEnd)+'). Corrigez-la si l\\'export va plus loin.';
  if(e==='j7s')return ' <b>Date proposée : fin de la première semaine du test.</b> Corrigez-la si l\\'export va plus loin.';
  if(e==='nom')return ' <b>'+(s==='nom'""")
rep("""else if(f==='startDate'){d.startDate=t.value;d.startGuess=false;d.startSrc='';}""",
"""else if(f==='startDate'){d.startDate=t.value;d.startGuess=false;d.startSrc='';if(!state.weeks.length&&d.mode==='instantane'&&state.plan.unit!=='jour'&&!d.endTyped&&!d.endFromFile&&(!d.endSrc||d.endSrc==='j7s')&&/^\\d{4}-\\d{2}-\\d{2}$/.test(t.value)){var ne=autoEnd(addDays(t.value,6));if(ne!==d.endDate){d.endDate=ne;d.endOk=false;}d.endSrc=ne===addDays(todayISO(),-1)?'':'j7s';}}""")
# ---- E. message sur les montants
rep("""'Non analysable depuis cet export : un montant demande aussi la somme des carrés par visiteur (colonnes « somme » et « somme des carrés », voir BigQuery).'""",
"""'Non analysable depuis un export agrégé : pour un montant, le calcul a besoin de la dispersion des valeurs d\\'un visiteur à l\\'autre, et cet export ne donne que le total. Il faut des données par visiteur (entrepôt de données).'""")
# ---- styles
rep("""#gst-app .dv-seg{margin-top:16px;padding:12px 16px;background:#F8FBFA;border:1px solid #D9D9D9;border-radius:6px}#gst-app .dv-seg p{margin:0;font-size:13px;line-height:1.5;color:var(--charcoal)}""",
"""#gst-app .dv-dims{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:16px}#gst-app .dv-dl{font-size:13px;color:var(--charcoal);margin-right:4px}#gst-app .dv-dc{display:inline-flex;gap:6px;align-items:baseline;padding:5px 10px;border:1px solid #D9D9D9;border-radius:999px;background:#fff;font-size:13px;color:var(--charcoal);max-width:100%;overflow-wrap:anywhere}#gst-app .dv-dc b{color:var(--ink);font-weight:600}#gst-app .dv-dc.seg{border-color:#A6CFEA;background:#F2F8FC}
#gst-app p.dv-seg{margin:10px 0 0;font-size:13px;line-height:1.5;color:var(--charcoal)}
#gst-app .dv-same{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:flex-start;margin-top:18px;padding:12px 16px;background:#F8FBFA;border:1px solid #D9D9D9;border-radius:6px;font-size:14px;line-height:1.5}#gst-app .dv-same svg{flex:none;margin-top:2px}#gst-app .dv-same>span{flex:1 1 0;min-width:180px}#gst-app .dv-same .link{min-height:44px;margin:0;padding:0 2px;font-size:13px}
#gst-app .sgp{position:relative;display:inline-grid;place-items:center;width:22px;height:22px;min-height:0;margin:0 0 0 8px;padding:0;border:1px solid #B9C4C4;border-radius:50%;background:#fff;color:var(--charcoal);font-size:15px;font-weight:600;line-height:1;vertical-align:middle;cursor:pointer}#gst-app .sgp::after{content:'';position:absolute;inset:-11px}#gst-app .sgp:hover,#gst-app .sgp[aria-expanded=true]{border-color:#0082C3;color:#0082C3}
#gst-app .sgs{border-top:1px solid var(--line);background:#FAFBFB}#gst-app .sgs-h{display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px;padding:10px 18px 6px 58px;font-size:13px;color:var(--charcoal)}#gst-app .sgs-h b{color:var(--ink)}#gst-app .sgs-h select{min-height:36px;width:auto;max-width:240px;padding:4px 28px 4px 10px;font-size:13px}#gst-app .sgs-h .pill{font-size:11px}
#gst-app .mrw.sub{cursor:default;min-height:44px;border-top:1px dashed var(--line)}#gst-app .mrw.sub:hover{background:none}#gst-app .mrw.sub .mn{font-weight:600;font-size:14px}#gst-app .mrw.sub .lift{font-size:15px;color:var(--ink)}#gst-app .sgs-n{margin:0;padding:8px 18px 12px 58px;font-size:12px;line-height:1.5}
@media (max-width:760px){#gst-app .sgs-h{padding:10px 14px 4px}#gst-app .sgs-n{padding:8px 14px 12px}#gst-app .sgs-h select{min-height:44px}#gst-app .mrw.sub{padding-bottom:4px}#gst-app .mrw.sub .c-lift{grid-column:1/-1}}""")
assert s.count('v56.29')==1
s=s.replace('v56.29','v56.30')
open('repo/calculateur-sequentiel-v56-30.html','w',newline='').write(s);print(len(s))

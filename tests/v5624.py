# v56.24 : rapport PowerPoint (le test, le résultat). La bibliothèque d'export n'est chargée qu'au clic, avec contrôle d'intégrité.
s=open('repo/calculateur-sequentiel-v56-23.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(a[:70],s.count(a));s=s.replace(a,b)
MOD=r"""
/* v56-24 : rapport .pptx à la charte FWO. Les chiffres sont ceux de l'écran de résultats (semaine de décision, sinon dernière lecture). */
var PPTX_LIB={url:'https://cdn.jsdelivr.net/npm/pptxgenjs@4.0.1/dist/pptxgen.bundle.js',sri:'sha384-qb0Xhi7LLYpvW1HCK6oMrmDLSY9sy7vwm6ZlV6KjtrlL9yg30+YN4neTwnmX+Kp8'};
function pptxLib(){
  if(window.PptxGenJS)return Promise.resolve();
  return new Promise(function(ok,ko){var sc=document.createElement('script');sc.src=window.FWO_GST_PPTX||PPTX_LIB.url;sc.integrity=PPTX_LIB.sri;sc.crossOrigin='anonymous';
    sc.onload=function(){window.PptxGenJS?ok():ko(new Error('bibliothèque d\'export illisible'));};sc.onerror=function(){ko(new Error('bibliothèque d\'export indisponible (connexion ou filtrage réseau)'));};document.head.appendChild(sc);});
}
function blobData(u){return fetch(u).then(function(r){return r.blob();}).then(function(b){return new Promise(function(ok,ko){var fr=new FileReader();fr.onload=function(){ok(String(fr.result));};fr.onerror=function(){ko(new Error('visuel illisible'));};fr.readAsDataURL(b);});});}
function reportData(){
  var c=compute(),ix=c.decisionWeek!=null?c.decisionWeek:c.weeks.length-1,w=c.weeks[ix],unit=U()?'jour':'semaine',un=U()?'jours':'semaines',k=state.plan.k;
  var rows=w.rows.map(function(r){var S=STATUS[r.status]||STATUS.NA;return {name:r.metric.name,role:r.metric.role==='principale'?'Objectif':r.metric.role==='garde-fou'?'Garde-fou':'Secondaire',main:r.metric.role==='principale',lift:r.st?pct(r.st.lift):'—',status:S[0],tone:TONE[r.status]||'',lo:r.st?pct(r.st.lo):'—',hi:r.st?pct(r.st.hi):'—',ci:Math.round(ciLevel(r.metric.role)*1000)/10,rk:r.metric.role==='principale'?0:r.metric.role==='garde-fou'?1:2};}).map(function(r,i){r.i=i;return r;}).sort(function(a,b){return a.rk-b.rk||a.i-b.i;});
  var v=root.querySelector('.verdict'),tx=function(q){var e=v&&v.querySelector(q);return e?e.textContent.replace(/\s+/g,' ').trim():'';},bw=v&&v.querySelector('.tp-w');
  var gf=state.metrics.filter(function(m){return m.role==='garde-fou';}).map(function(m){return m.name;}),pr=rows.filter(function(r){return r.main;})[0]||rows[0],wk=state.weeks[ix]||{};
  return {rows:rows,pr:pr,ix:ix,stop:c.decisionWeek!=null,k:k,un:un,unit:unit,wkn:WK(ix),head:tx('.tp-a h3'),sub:tx('.tp-a p'),big:tx('.tp-v'),rates:tx('.tp-b p.num'),band:bw?bw.querySelector('b').textContent.trim():'',bandTx:bw&&bw.querySelector('div>span')?bw.querySelector('div>span').textContent.trim():'',tone:bw?(bw.className.match(/\b([agcn])\b/)||[])[1]||'n':'n',
    vis:(wk.A&&wk.B&&isFinite(wk.A.n+wk.B.n))?wk.A.n+wk.B.n:null,goal:pr.name+', lu chaque '+unit+' pendant '+k+' '+un+' au plus.'+(gf.length?' Garde-fou'+(gf.length>1?'s':'')+' : '+gf.join(', ')+'.':'')};
}
function reportBuild(){
  var st=state,D=reportData(),P=new window.PptxGenJS(),G='028D6A',INK='1A1D1F',CH='464849',MU='5B5F60',FT='Raleway',FB='Open Sans';
  P.layout='LAYOUT_WIDE';P.title=st.name;P.author='FWOptimisation';P.company=(ACC.user&&ACC.user.org)||'';
  var foot=function(sl,txt){sl.addShape(P.ShapeType.line,{x:0.6,y:6.85,w:12.13,h:0,line:{color:'D9D9D9',width:0.75}});sl.addText(txt,{x:0.6,y:6.92,w:9.4,h:0.36,fontFace:FB,fontSize:10,color:MU,margin:0,valign:'middle'});
    sl.addText([{text:'FWO',options:{bold:true,color:G}},{text:'ptimisation',options:{color:'019875'}}],{x:10.3,y:6.92,w:2.43,h:0.36,fontFace:FT,fontSize:13,align:'right',margin:0,valign:'middle'});};
  var org=(ACC.user&&ACC.user.org)?ACC.user.org+' · ':'',per=org+(D.vis!=null?nf(D.vis)+' visiteurs · ':'')+'début le '+frDate(st.plan.startDate)+' · '+D.k+' '+D.un+' prévu'+(U()?'s':'es');
  var p=st.pres||{},vA=(st.vis||[]).filter(function(x){return x.arm==='A'&&VIS[x.id]&&VIS[x.id].length>1;})[0],vB=(st.vis||[]).filter(function(x){return x.arm==='B'&&VIS[x.id]&&VIS[x.id].length>1;})[0];
  var imgs=Promise.all([vA,vB].map(function(x){return x?blobData(VIS[x.id]).then(function(d){return {d:d,w:x.w||4,h:x.h||3};},function(){return null;}):null;}));
  return imgs.then(function(I){
    if(p.problem||p.hyp||I[0]||I[1]){
      var s1=P.addSlide(),hasI=!!(I[0]||I[1]),tw=hasI?5.7:12.13,y=1.95;s1.background={color:'FFFFFF'};
      s1.addText(('Test A/B'+(p.page?' · '+p.page:'')).toUpperCase(),{x:0.6,y:0.5,w:12.13,h:0.3,fontFace:FT,fontSize:11,bold:true,color:G,charSpacing:1.5,margin:0});
      s1.addText(st.name,{x:0.6,y:0.82,w:12.13,h:0.9,fontFace:FT,fontSize:28,bold:true,color:INK,margin:0,valign:'top',fit:'shrink'});
      [['Le problème',p.problem,1.35],['L\'hypothèse',p.hyp,1.55],['L\'objectif',D.goal,0.9]].forEach(function(b){if(!b[1])return;
        s1.addText(b[0].toUpperCase(),{x:0.6,y:y,w:tw,h:0.26,fontFace:FT,fontSize:10,bold:true,color:G,charSpacing:1.2,margin:0});
        s1.addText(b[1],{x:0.6,y:y+0.28,w:tw,h:b[2],fontFace:FB,fontSize:13,color:INK,margin:0,valign:'top',fit:'shrink',paraSpaceAfter:4});y+=b[2]+0.42;});
      if(hasI){var bx=6.75,bw=2.9,bh=4.3;[0,1].forEach(function(i){var x=bx+i*(bw+0.2),im=I[i],arm=i?'B':'A';
        s1.addText(st.labels[arm].indexOf(arm)===0?st.labels[arm]:arm+' · '+st.labels[arm],{x:x,y:1.95,w:bw,h:0.3,fontFace:FT,fontSize:11,bold:true,color:i?G:CH,margin:0});
        s1.addShape(P.ShapeType.rect,{x:x,y:2.3,w:bw,h:bh,fill:{color:'F8FBFA'},line:{color:i?G:'D9D9D9',width:1}});
        if(im){var r=Math.min((bw-0.1)/im.w,(bh-0.1)/im.h),iw=im.w*r,ih=im.h*r;s1.addImage({data:im.d.replace(/^data:/,''),x:x+(bw-iw)/2,y:2.3+(bh-ih)/2,w:iw,h:ih});}
        else s1.addText('Pas de visuel',{x:x,y:2.3,w:bw,h:bh,fontFace:FB,fontSize:11,color:MU,align:'center',valign:'middle',margin:0});});}
      foot(s1,per);
    }
    var s2=P.addSlide(),TC={a:['FBF1DC','D79A2A','5C3D06'],g:['EAF6F1','9AD3BE','0B5E48'],c:['FCEDEA','F2A99F','8F2C20'],n:['F1F4F5','CBD3D7','1A1D1F']}[D.tone]||['F1F4F5','CBD3D7','1A1D1F'];s2.background={color:'FFFFFF'};
    s2.addText(('Le résultat · '+(D.stop?'acquis':'lecture')+' en '+D.unit+' '+D.wkn+' sur '+D.k).toUpperCase(),{x:0.6,y:0.5,w:12.13,h:0.3,fontFace:FT,fontSize:11,bold:true,color:G,charSpacing:1.5,margin:0});
    s2.addText(D.head+(D.band?' : '+D.band.charAt(0).toLowerCase()+D.band.slice(1):''),{x:0.6,y:0.82,w:12.13,h:0.9,fontFace:FT,fontSize:28,bold:true,color:INK,margin:0,valign:'top',fit:'shrink'});
    s2.addText(D.big||D.pr.lift,{x:0.6,y:1.95,w:5.2,h:1.25,fontFace:FT,fontSize:66,bold:true,color:D.pr.tone==='g'?'0E7C5D':D.pr.tone==='c'?'C9402F':CH,margin:0,valign:'middle'});
    s2.addText([{text:D.pr.name,options:{bold:true,color:INK,breakLine:true}},{text:D.rates,options:{color:CH,breakLine:true}},{text:'Intervalle à '+nf(D.pr.ci,D.pr.ci%1?1:0)+' % : de '+D.pr.lo+' à '+D.pr.hi,options:{color:MU}}],{x:0.6,y:3.25,w:5.2,h:1.05,fontFace:FB,fontSize:13,margin:0,valign:'top',paraSpaceAfter:3});
    if(D.band){s2.addShape(P.ShapeType.roundRect,{x:0.6,y:4.5,w:5.2,h:1.7,rectRadius:0.08,fill:{color:TC[0]},line:{color:TC[1],width:1}});
      s2.addText([{text:D.band,options:{bold:true,fontFace:FT,fontSize:16,color:TC[2],breakLine:true}},{text:D.bandTx,options:{fontFace:FB,fontSize:12,color:INK}}],{x:0.8,y:4.62,w:4.8,h:1.46,margin:0,valign:'top',fit:'shrink',paraSpaceAfter:5});}
    var R=D.rows.slice(0,10),more=D.rows.length-R.length,hd=function(t,a){return {text:t,options:{bold:true,fontFace:FT,fontSize:10,color:MU,align:a||'left',border:[{type:'none'},{type:'none'},{type:'solid',color:'D9D9D9',pt:1},{type:'none'}]}};};
    var cell=function(t,o){return {text:t,options:Object.assign({fontFace:FB,fontSize:11.5,color:INK,valign:'middle',border:[{type:'none'},{type:'none'},{type:'solid',color:'E3E6E6',pt:0.75},{type:'none'}]},o||{})};};
    var tb=[[hd('MÉTRIQUE'),hd('RÔLE'),hd('ÉCART','right'),hd('STATUT','right')]].concat(R.map(function(r){var col=r.tone==='g'?'0E7C5D':r.tone==='c'?'C9402F':r.tone==='w'?'7A5410':CH;return [cell(r.name,{bold:r.main}),cell(r.role,{color:MU}),cell(r.lift,{align:'right',bold:true}),cell(r.status,{align:'right',color:col,bold:r.tone!==''})];}));
    if(more>0)tb.push([cell('+ '+more+' autre'+(more>1?'s':'')+' métrique'+(more>1?'s':''),{color:MU,colspan:4})]);
    s2.addTable(tb,{x:6.3,y:1.95,w:6.43,colW:[2.85,1.08,1.05,1.45],rowH:0.4,margin:[0.04,0.06,0.04,0.02]});
    foot(s2,per);
    var slug=String(st.name||'test').normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^A-Za-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,60).toLowerCase()||'test';
    return P.writeFile({fileName:'rapport-'+slug+'.pptx'});
  });
}
function reportGo(){
  var st=state;ui.week=null;ui.tab='resultats';ui.error='';ui.repBusy=true;render();
  if((st.vis||[]).length&&(st.sid||st.pub))visLoad();
  var wait=function(n){return (st.vis||[]).some(function(x){return VIS[x.id]==='w';})&&n>0?new Promise(function(ok){setTimeout(ok,300);}).then(function(){return wait(n-1);}):Promise.resolve();};
  pptxLib().then(function(){return wait(30);}).then(function(){if(state!==st)throw new Error('un autre test a été ouvert');return reportBuild();}).then(function(){if(state===st)ui.notice='Rapport téléchargé. Il s\'ouvre dans PowerPoint, et dans Google Slides par Fichier, puis Importer des diapositives.';},function(e){if(state===st)ui.error='Rapport impossible : '+(e&&e.message||e);}).then(function(){ui.repBusy=false;render();});
}
"""
rep("\nfunction accBody(){",MOD+"\nfunction accBody(){")
rep("""<div class="tools hx1"><button type="button" class="link lgd" data-act="legend" aria-expanded="'+!!ui.legend+'">Comment lire les statuts</button>'""",
    """<div class="tools hx1"><button type="button" class="link lgd" data-act="legend" aria-expanded="'+!!ui.legend+'">Comment lire les statuts</button><button type="button" class="rep" data-act="report"'+(ui.repBusy?' disabled':'')+'><svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16"><path d="M3 2.500h7l3 3v8H3zM10 2.500v3h3M5.500 9h5M5.500 11.500h3" fill="none" stroke="currentColor" stroke-width="1.500" stroke-linejoin="round" stroke-linecap="round"/></svg>'+(ui.repBusy?'Préparation du rapport…':'Exporter le rapport (.pptx)')+'</button>'""")
rep("  else if(name==='legend'){ui.legend=!ui.legend;}","  else if(name==='legend'){ui.legend=!ui.legend;}\n  else if(name==='report'){if(!ui.repBusy)reportGo();return;}")
rep("#gst-app .dash-h{","#gst-app .tools.hx1 button.rep{display:inline-flex;align-items:center;gap:8px;min-height:44px;margin:0;padding:0 14px;font-size:14px;font-weight:600}#gst-app .tools.hx1 button.rep svg{flex:none;color:#0E7C5D}\n#gst-app .dash-h{")
rep("/^(Exemple chargé|Test « |\\d+ semaine\\(s\\) |Plan appliqué)/","/^(Exemple chargé|Test « |\\d+ semaine\\(s\\) |Plan appliqué|Rapport téléchargé)/")
rep("/* v56.23 : présentation","/* v56-23 : présentation")
rep("v56.23","v56.24")
open('repo/calculateur-sequentiel-v56-24.html','w',newline='').write(s);print(len(s))

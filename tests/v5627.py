# v56.27 : rapport, deuxième passe d'après les retours de Mat.
# Diapositive 1 : rôle puis métrique, plus de MDE, bloc « Décision » à ajuster, visuels larges sans cadre fixe et disposés selon leur format.
# Diapositive 2 : le résultat face à l'hypothèse, données techniques en petit, garde-fous sur leurs lignes, synthèse par règles.
# Diapositive 3 : le détail de toutes les métriques.
s=open('repo/calculateur-sequentiel-v56-26.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
i=s.index("function reportData(){");j=s.index("function reportLogo(){");k=s.index("function reportBuild(){");l=s.index("function reportGo(){")
DATA=r"""function reportData(){
  var c=compute(),ix=c.decisionWeek!=null?c.decisionWeek:c.weeks.length-1,w=c.weeks[ix],unit=U()?'jour':'semaine',un=U()?'jours':'semaines',k=state.plan.k;
  var val=function(m,x){return x==null||!isFinite(x)?'—':m.type==='continue'?nf(x,2):nf(x*100,2)+' %';};
  var rows=w.rows.map(function(r,i){var S=STATUS[r.status]||STATUS.NA,K=r.status;return {i:i,key:K,name:r.metric.name,role:r.metric.role==='principale'?'Objectif':r.metric.role==='garde-fou'?'Garde-fou':'Secondaire',main:r.metric.role==='principale',a:r.st?val(r.metric,r.st.mA):'—',b:r.st?val(r.metric,r.st.mB):'—',lift:r.st?pct(r.st.lift):'—',status:S[0],
    grp:['POSITIF','SECURITE','SIGNAL_POS'].indexOf(K)>=0?'g':['NEGATIF','REGRESSION','SIGNAL_NEG','WATCH'].indexOf(K)>=0?'c':'n',soft:K==='SIGNAL_POS'||K==='SIGNAL_NEG'||K==='WATCH',lo:r.st?pct(r.st.lo):'—',hi:r.st?pct(r.st.hi):'—',ci:Math.round(ciLevel(r.metric.role)*1000)/10,rk:r.metric.role==='principale'?0:r.metric.role==='garde-fou'?1:2};}).sort(function(a,b){return a.rk-b.rk||a.i-b.i;});
  var v=root.querySelector('.verdict'),tx=function(q){var e=v&&v.querySelector(q);return e?e.textContent.replace(/\s+/g,' ').trim():'';};
  var pr=rows.filter(function(r){return r.main;})[0]||rows[0],wk=state.weeks[ix]||{},vis=(wk.A&&wk.B&&isFinite(wk.A.n+wk.B.n))?wk.A.n+wk.B.n:null,d=w.dec||{};
  return {rows:rows,pr:pr,gf:rows.filter(function(r){return r.rk===1;}),stop:c.decisionWeek!=null,k:k,un:un,unit:unit,wkn:WK(ix),big:tx('.tp-v'),vis:vis,
    choice:d.kind==='win'?'Déployer':d.kind==='discuss'?'Déployer / Abandonner':d.stop?'Abandonner / Itérer':'Test en cours'};
}
"""
BUILD=r"""function reportBuild(){
  var st=state,D=reportData(),P=new window.PptxGenJS(),G='028D6A',INK='1A1D1F',CH='464849',MU='5B5F60',RED='C9402F',GRN='0E7C5D',FT='Raleway',FB='Open Sans';
  P.layout='LAYOUT_WIDE';P.title=st.name;P.author='FWOptimisation';P.company=(ACC.user&&ACC.user.org)||'';
  var lines=function(t,w,fs){var cpl=Math.max(8,Math.floor(w*72/(fs*0.52)));return String(t).split('\n').reduce(function(a,l){return a+Math.max(1,Math.ceil(l.length/cpl));},0);},hOf=function(n,fs){return n*fs*1.34/72;};
  var tfs=function(t){return t.length<=44?28:t.length<=70?23:t.length<=100?19:16;},low=function(t){return t.charAt(0).toLowerCase()+t.slice(1);};
  var org=(ACC.user&&ACC.user.org)?ACC.user.org+' · ':'',per=org+(D.vis!=null?nf(D.vis)+' visiteurs · ':'')+'début le '+frDate(st.plan.startDate)+' · '+D.k+' '+D.un+' prévu'+(U()?'s':'es');
  var p=st.pres||{},pick=function(arm){return (st.vis||[]).filter(function(x){return x.arm===arm&&VIS[x.id]&&VIS[x.id].length>1;})[0];},vA=pick('A'),vB=pick('B');
  var imgs=Promise.all([vA,vB].map(function(x){return x?blobData(VIS[x.id]).then(function(d){return {d:d,w:x.w||4,h:x.h||3};},function(){return null;}):null;}));
  return Promise.all([imgs,reportLogo()]).then(function(R){var I=R[0],LG=R[1];
    var kick=function(sl,t){sl.addText(t.toUpperCase(),{x:0.6,y:0.5,w:12.13,h:0.3,fontFace:FT,fontSize:11,bold:true,color:G,charSpacing:1.5,margin:0});},head=function(sl,t){sl.addText(t,{x:0.6,y:0.82,w:12.13,h:0.9,fontFace:FT,fontSize:tfs(t),bold:true,color:INK,margin:0,valign:'top'});};
    var foot=function(sl){sl.addShape(P.ShapeType.line,{x:0.6,y:6.85,w:12.13,h:0,line:{color:'D9D9D9',width:0.75}});sl.addText(per,{x:0.6,y:6.92,w:9.4,h:0.36,fontFace:FB,fontSize:10,color:MU,margin:0,valign:'middle'});
      if(LG){var lh=0.3,lw=lh*LG.w/LG.h;sl.addImage({data:LG.d.replace(/^data:/,''),x:12.73-lw,y:6.95,w:lw,h:lh});}
      else sl.addText([{text:'FWO',options:{bold:true,color:G,fontFace:FT}},{text:'ptimisation',options:{color:'019875',fontFace:FT}}],{x:10.3,y:6.92,w:2.43,h:0.36,fontFace:FT,fontSize:13,align:'right',margin:0,valign:'middle'});};
    var lab=function(arm){return st.labels[arm].indexOf(arm)===0?st.labels[arm]:arm+' · '+st.labels[arm];};
    /* ---- 1 : le test ---- */
    if(p.problem||p.hyp||I[0]||I[1]){
      var s1=P.addSlide(),hasI=!!(I[0]||I[1]),rr=[I[0],I[1]].filter(Boolean).map(function(m){return m.w/m.h;}),rmax=rr.length?Math.max.apply(null,rr):1,wide=hasI&&rmax>1.15;s1.background={color:'FFFFFF'};
      var tl=(p.problem||'').length+(p.hyp||'').length,side=!wide||(tl<=900&&Math.min(3.67,4.3*rmax)>=Math.min(6.33,2.0*rmax)),tw=hasI?(!wide?5.7:side?4.2:5.4):12.13,Y0=1.95,AV=4.62;
      kick(s1,'Test A/B'+(p.page?' · '+p.page:''));head(s1,st.name);
      var ob=[['Objectif principal',D.pr.name]].concat(D.gf.map(function(g){return ['Garde-fou',g.name];})),last='Lecture chaque '+D.unit+', '+D.k+' '+D.un+' au plus';
      var T=[p.problem||'',p.hyp||''],GAP=0.2,LB=0.25,fs,obl=function(f){return ob.reduce(function(a,o){return a+lines(o[0]+' : '+o[1],tw,f);},0)+lines(last,tw,f);},need=function(f){var h=0;T.forEach(function(t){if(t)h+=LB+hOf(lines(t,tw,f),f)+GAP;});return h+LB+hOf(obl(f),f)+GAP+LB+hOf(1,f+1);};
      for(fs=13;fs>9&&need(fs)>AV;fs-=0.5);
      var guard=0;while(need(fs)>AV&&guard++<60){var li=T[0].length>=T[1].length?0:1;if(T[li].length<160)break;T[li]=T[li].slice(0,Math.floor(T[li].length*0.9)).replace(/\s+\S*$/,'')+'…';}
      var y=Y0,blk=function(title,h,body,o){s1.addText(title.toUpperCase(),{x:0.6,y:y,w:tw,h:LB,fontFace:FT,fontSize:10,bold:true,color:G,charSpacing:1.2,margin:0,valign:'top'});s1.addText(body,Object.assign({x:0.6,y:y+LB,w:tw,h:h,fontFace:FB,fontSize:fs,color:INK,margin:0,valign:'top',lineSpacingMultiple:1.08},o||{}));y+=LB+h+GAP;};
      if(T[0])blk('Le problème',hOf(lines(T[0],tw,fs),fs),T[0]);
      if(T[1])blk('L\'hypothèse',hOf(lines(T[1],tw,fs),fs),T[1]);
      var runs=[];ob.forEach(function(o){runs.push({text:o[0]+' : ',options:{color:CH}});runs.push({text:o[1],options:{bold:true,breakLine:true}});});runs.push({text:last,options:{color:CH}});
      blk('L\'objectif',hOf(obl(fs),fs),runs);
      blk('Décision',hOf(1,fs+1),D.choice,{bold:true,fontSize:fs+1});
      if(hasI){var lbl=function(i,x,yy,bw){s1.addText(lab(i?'B':'A'),{x:x,y:yy,w:bw,h:0.27,fontFace:FT,fontSize:11,bold:true,color:i?G:CH,margin:0,valign:'top'});};
        if(!wide){[0,1].forEach(function(i){var x=6.75+i*3.1,bw=2.9,bh=4.3,im=I[i];lbl(i,x,1.95,bw);s1.addShape(P.ShapeType.rect,{x:x,y:2.25,w:bw,h:bh,fill:{color:'F8FBFA'},line:{color:i?G:'D9D9D9',width:1}});
            if(im){var r=Math.min((bw-0.1)/im.w,(bh-0.1)/im.h),iw=im.w*r,ih=im.h*r;s1.addImage({data:im.d.replace(/^data:/,''),x:x+(bw-iw)/2,y:2.25+(bh-ih)/2,w:iw,h:ih});}
            else s1.addText('Pas de visuel',{x:x,y:2.25,w:bw,h:bh,fontFace:FB,fontSize:11,color:MU,align:'center',valign:'middle',margin:0});});}
        else{var put=function(i,x,yy,mw,mh){var im=I[i];lbl(i,x,yy,mw);if(!im){s1.addText('Pas de visuel',{x:x,y:yy+0.3,w:mw,h:0.4,fontFace:FB,fontSize:11,color:MU,margin:0});return 0.4;}
            var r=Math.min(mw/im.w,mh/im.h),iw=im.w*r,ih=im.h*r;s1.addImage({data:im.d.replace(/^data:/,''),x:x,y:yy+0.3,w:iw,h:ih});s1.addShape(P.ShapeType.rect,{x:x,y:yy+0.3,w:iw,h:ih,fill:{type:'none'},line:{color:i?G:'D9D9D9',width:0.75}});return ih;};
          if(side){put(0,5.2,1.95,3.67,4.3);put(1,9.06,1.95,3.67,4.3);}else{var h0=put(0,6.4,1.95,6.33,2.0);put(1,6.4,1.95+0.3+h0+0.22,6.33,2.0);}}}
      foot(s1);
    }
    /* ---- 2 : le résultat face à l'hypothèse ---- */
    var s2=P.addSlide(),K=D.pr.key,tone=K==='POSITIF'?'g':K==='NEGATIF'?'c':'n',TC={g:['EAF6F1','9AD3BE','0B5E48'],c:['FCEDEA','F2A99F','8F2C20'],n:['F1F4F5','CBD3D7','1A1D1F']}[tone];s2.background={color:'FFFFFF'};
    var verdict=K==='POSITIF'?'l\'effet attendu est démontré':K==='NEGATIF'?'l\'effet inverse est démontré':D.stop?'l\'effet attendu n\'est pas démontré':'rien n\'est démontré à ce stade';
    kick(s2,'Le résultat'+(D.stop?' · acquis en '+D.wkn+' '+(D.wkn>1?D.un:D.unit):' · lecture en '+D.unit+' '+D.wkn+' sur '+D.k));head(s2,st.name+' : '+verdict);
    s2.addText(D.big||D.pr.lift,{x:0.6,y:1.9,w:5.2,h:1.2,fontFace:FT,fontSize:66,bold:true,color:tone==='g'?GRN:tone==='c'?RED:CH,margin:0,valign:'middle'});
    s2.addText('de '+low(D.pr.name),{x:0.6,y:3.12,w:5.2,h:0.36,fontFace:FB,fontSize:15,bold:true,color:INK,margin:0,valign:'top'});
    s2.addText('Contrôle '+D.pr.a+' · Variante '+D.pr.b+' · intervalle à '+nf(D.pr.ci,D.pr.ci%1?1:0)+' % : de '+D.pr.lo+' à '+D.pr.hi,{x:0.6,y:3.5,w:5.2,h:0.3,fontFace:FB,fontSize:9,color:MU,margin:0,valign:'top'});
    var hy=(p.hyp||'').replace(/\s+/g,' ').trim();if(hy.length>330)hy=hy.slice(0,330).replace(/\s+\S*$/,'')+'…';
    var bx=[{text:'Par rapport à l\'hypothèse'.toUpperCase(),options:{bold:true,fontFace:FT,fontSize:10,color:TC[2],charSpacing:1.2,breakLine:true}},{text:verdict.charAt(0).toUpperCase()+verdict.slice(1),options:{bold:true,fontFace:FT,fontSize:16,color:TC[2],breakLine:!!hy}}];
    if(hy)bx.push({text:'« '+hy+' »',options:{italic:true,fontFace:FB,fontSize:11,color:CH}});
    var bh=0.92+(hy?hOf(lines(hy,6.03,11),11)+0.1:0);s2.addShape(P.ShapeType.roundRect,{x:6.3,y:1.95,w:6.43,h:bh,rectRadius:0.06,fill:{color:TC[0]},line:{color:TC[1],width:1}});s2.addText(bx,{x:6.5,y:2.07,w:6.03,h:bh-0.24,margin:0,valign:'top',paraSpaceAfter:5});
    var Y2=Math.max(4.15,1.95+bh+0.3),lbl2=function(t,x,w2){s2.addText(t.toUpperCase(),{x:x,y:Y2,w:w2,h:0.26,fontFace:FT,fontSize:10,bold:true,color:G,charSpacing:1.2,margin:0,valign:'top'});};
    lbl2('Garde-fous',0.6,5.2);
    var col=function(g){return g==='g'?GRN:g==='c'?RED:CH;},gr=[];D.gf.slice(0,5).forEach(function(g,n,a){gr.push({text:g.name,options:{bold:true,color:INK}});gr.push({text:'  '+g.lift+'  ',options:{color:CH}});gr.push({text:g.status,options:{bold:g.grp!=='n',color:col(g.grp),breakLine:n<a.length-1}});});
    if(!gr.length)gr.push({text:'Aucun garde-fou défini pour ce test.',options:{color:MU}});
    s2.addText(gr,{x:0.6,y:Y2+0.3,w:5.2,h:Math.max(0.3,hOf(Math.max(1,Math.min(5,D.gf.length)),12)+0.1),fontFace:FB,fontSize:12,margin:0,valign:'top',lineSpacingMultiple:1.12});
    var gRed=D.gf.filter(function(g){return g.key==='REGRESSION';}),gOk=D.gf.length&&D.gf.every(function(g){return g.key==='SECURITE';});
    var syn=(tone==='g'?'L\'objectif progresse':tone==='c'?'L\'objectif recule':'Rien n\'est démontré sur l\'objectif')+(!D.gf.length?'.':gRed.length?(tone==='g'?', mais ':' et ')+(gRed.length>1?'des garde-fous se dégradent':'un garde-fou se dégrade')+' : c\'est ce qui retient le déploiement.':gOk?' et les garde-fous sont respectés.':' ; aucun garde-fou ne se dégrade, sans que leur maintien soit démontré.');
    lbl2('Synthèse',6.3,6.43);
    var grp=function(k2){return D.rows.filter(function(r){return r.grp===k2;});},item=function(r){return r.name+' '+r.lift+(r.soft?' (signal)':'');},sy=[{text:syn,options:{bold:true,color:INK,breakLine:true}}];
    [['g','Ce qui progresse'],['c','Ce qui recule ou inquiète']].forEach(function(q){var L=grp(q[0]);if(!L.length)return;sy.push({text:q[1]+' : ',options:{bold:true,color:col(q[0])}});sy.push({text:L.slice(0,5).map(item).join(' · ')+(L.length>5?' · + '+(L.length-5):''),options:{color:INK,breakLine:true}});});
    var N0=grp('n');if(N0.length)sy.push({text:'Sans conclusion : ',options:{bold:true,color:CH}},{text:N0.length+' métrique'+(N0.length>1?'s':'')+(N0.length<=3?' ('+N0.map(function(r){return r.name;}).join(', ')+')':''),options:{color:CH}});
    s2.addText(sy,{x:6.3,y:Y2+0.3,w:6.43,h:6.7-(Y2+0.3),fontFace:FB,fontSize:12,margin:0,valign:'top',paraSpaceAfter:6,fit:'shrink'});
    foot(s2);
    /* ---- 3 : le détail ---- */
    var s3=P.addSlide(),RW=D.rows.slice(0,15),more=D.rows.length-RW.length,tf=RW.length>11?9.5:11,rh=RW.length>11?0.29:0.36;s3.background={color:'FFFFFF'};kick(s3,'Les données');head(s3,'Le détail des métriques');
    var hd=function(t,a){return {text:t,options:{bold:true,fontFace:FT,fontSize:9.5,color:MU,align:a||'left',border:[{type:'none'},{type:'none'},{type:'solid',color:'D9D9D9',pt:1},{type:'none'}]}};};
    var cell=function(t,o){return {text:t,options:Object.assign({fontFace:FB,fontSize:tf,color:INK,valign:'middle',border:[{type:'none'},{type:'none'},{type:'solid',color:'E3E6E6',pt:0.75},{type:'none'}]},o||{})};};
    var tb=[[hd('MÉTRIQUE'),hd('RÔLE'),hd('CONTRÔLE','right'),hd('VARIANTE','right'),hd('ÉCART','right'),hd('INTERVALLE','right'),hd('STATUT','right')]].concat(RW.map(function(r){return [cell(r.name,{bold:r.main}),cell(r.role,{color:MU}),cell(r.a,{align:'right'}),cell(r.b,{align:'right'}),cell(r.lift,{align:'right',bold:true}),cell(r.lo+' à '+r.hi,{align:'right',color:MU}),cell(r.status,{align:'right',color:col(r.grp),bold:r.grp!=='n'})];}));
    if(more>0)tb.push([cell('+ '+more+' autre'+(more>1?'s':'')+' métrique'+(more>1?'s':''),{color:MU,colspan:7})]);
    s3.addTable(tb,{x:0.6,y:1.9,w:12.13,colW:[3.6,1.2,1.3,1.3,1.2,2.03,1.5],rowH:rh,margin:[0.03,0.06,0.03,0.02]});
    s3.addText('Intervalles à '+nf(D.pr.ci,D.pr.ci%1?1:0)+' % pour l\'objectif et les garde-fous'+(D.rows.some(function(r){return r.rk===2;})?', corrigés pour les métriques secondaires':'')+'.',{x:0.6,y:6.45,w:12.13,h:0.3,fontFace:FB,fontSize:9,color:MU,margin:0,valign:'middle'});
    foot(s3);
    var slug=String(st.name||'test').normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^A-Za-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,60).toLowerCase()||'test';
    return P.writeFile({fileName:'rapport-'+slug+'.pptx'});
  });
}
"""
s=s[:i]+DATA.replace('\n',NL)+s[j:k]+BUILD.replace('\n',NL)+s[l:]
assert s.count('v56.26')==1
s=s.replace('v56.26','v56.27')
open('repo/calculateur-sequentiel-v56-27.html','w',newline='').write(s);print(len(s))

# v56.26 : rapport revu (objectifs en gras et à la ligne, MDE, tailles ajustées à la longueur, visuels empilés ou côte à côte selon leur format,
# titre de la diapositive 2 sur le résultat face à l'hypothèse, logo en image quand la police de marque est chargée).
s=open('repo/calculateur-sequentiel-v56-25.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
i=s.index("function reportData(){");j=s.index("function reportGo(){")
NEW=r"""function reportData(){
  var c=compute(),ix=c.decisionWeek!=null?c.decisionWeek:c.weeks.length-1,w=c.weeks[ix],unit=U()?'jour':'semaine',un=U()?'jours':'semaines',k=state.plan.k;
  var rows=w.rows.map(function(r,i){var S=STATUS[r.status]||STATUS.NA;return {i:i,key:r.status,name:r.metric.name,role:r.metric.role==='principale'?'Objectif':r.metric.role==='garde-fou'?'Garde-fou':'Secondaire',main:r.metric.role==='principale',bin:r.metric.type!=='continue',mA:r.st?r.st.mA:null,lift:r.st?pct(r.st.lift):'—',status:S[0],tone:TONE[r.status]||'',lo:r.st?pct(r.st.lo):'—',hi:r.st?pct(r.st.hi):'—',ci:Math.round(ciLevel(r.metric.role)*1000)/10,rk:r.metric.role==='principale'?0:r.metric.role==='garde-fou'?1:2};}).sort(function(a,b){return a.rk-b.rk||a.i-b.i;});
  var v=root.querySelector('.verdict'),tx=function(q){var e=v&&v.querySelector(q);return e?e.textContent.replace(/\s+/g,' ').trim():'';};
  var pr=rows.filter(function(r){return r.main;})[0]||rows[0],wk=state.weeks[ix]||{},vis=(wk.A&&wk.B&&isFinite(wk.A.n+wk.B.n))?wk.A.n+wk.B.n:null,mde=null;
  try{var tw=state.plan.traffic>0?state.plan.traffic:(vis!=null?vis/(U()?WK(ix)/7:WK(ix)):0),IFq=state.bounds&&state.bounds.IF?Math.sqrt(state.bounds.IF):1;if(pr.bin&&pr.mA>0&&pr.mA<1&&tw>0){var m=mdeAt(state.plan,{t:tw,p:pr.mA},k,IFq);if(isFinite(m)&&m>0)mde=m;}}catch(e){}
  return {rows:rows,pr:pr,gf:rows.filter(function(r){return r.rk===1;}),ix:ix,stop:c.decisionWeek!=null,k:k,un:un,unit:unit,wkn:WK(ix),big:tx('.tp-v'),rates:tx('.tp-b p.num'),vis:vis,mde:mde};
}
function reportLogo(){
  try{var ok=false;if(document.fonts&&document.fonts.forEach)document.fonts.forEach(function(f){if(/Raleway/i.test(f.family))ok=true;});if(!ok)return Promise.resolve(null);
    return Promise.all([document.fonts.load('700 64px Raleway'),document.fonts.load('400 64px Raleway')]).then(function(L){if(!L[0].length)return null;
      var cv=document.createElement('canvas'),x=cv.getContext('2d'),a='FWO',b='ptimisation';x.font='700 64px Raleway';var wa=x.measureText(a).width;x.font='400 64px Raleway';var wb=x.measureText(b).width;
      cv.width=Math.ceil(wa+wb+8);cv.height=92;x=cv.getContext('2d');x.textBaseline='alphabetic';x.font='700 64px Raleway';x.fillStyle='#028D6A';x.fillText(a,2,68);x.font='400 64px Raleway';x.fillStyle='#019875';x.fillText(b,2+wa,68);
      return {d:cv.toDataURL('image/png'),w:cv.width,h:cv.height};},function(){return null;});}catch(e){return Promise.resolve(null);}
}
function reportBuild(){
  var st=state,D=reportData(),P=new window.PptxGenJS(),G='028D6A',INK='1A1D1F',CH='464849',MU='5B5F60',FT='Raleway',FB='Open Sans';
  P.layout='LAYOUT_WIDE';P.title=st.name;P.author='FWOptimisation';P.company=(ACC.user&&ACC.user.org)||'';
  var lines=function(t,w,fs){var cpl=Math.max(8,Math.floor(w*72/(fs*0.52)));return String(t).split('\n').reduce(function(a,l){return a+Math.max(1,Math.ceil(l.length/cpl));},0);},hOf=function(n,fs){return n*fs*1.34/72;};
  var tfs=function(t){return t.length<=44?28:t.length<=70?23:t.length<=100?19:16;};
  var org=(ACC.user&&ACC.user.org)?ACC.user.org+' · ':'',per=org+(D.vis!=null?nf(D.vis)+' visiteurs · ':'')+'début le '+frDate(st.plan.startDate)+' · '+D.k+' '+D.un+' prévu'+(U()?'s':'es');
  var p=st.pres||{},pick=function(arm){return (st.vis||[]).filter(function(x){return x.arm===arm&&VIS[x.id]&&VIS[x.id].length>1;})[0];},vA=pick('A'),vB=pick('B');
  var imgs=Promise.all([vA,vB].map(function(x){return x?blobData(VIS[x.id]).then(function(d){return {d:d,w:x.w||4,h:x.h||3};},function(){return null;}):null;}));
  return Promise.all([imgs,reportLogo()]).then(function(R){var I=R[0],LG=R[1];
    var foot=function(sl){sl.addShape(P.ShapeType.line,{x:0.6,y:6.85,w:12.13,h:0,line:{color:'D9D9D9',width:0.75}});sl.addText(per,{x:0.6,y:6.92,w:9.4,h:0.36,fontFace:FB,fontSize:10,color:MU,margin:0,valign:'middle'});
      if(LG){var lh=0.3,lw=lh*LG.w/LG.h;sl.addImage({data:LG.d.replace(/^data:/,''),x:12.73-lw,y:6.95,w:lw,h:lh});}
      else sl.addText([{text:'FWO',options:{bold:true,color:G,fontFace:FT}},{text:'ptimisation',options:{color:'019875',fontFace:FT}}],{x:10.3,y:6.92,w:2.43,h:0.36,fontFace:FT,fontSize:13,align:'right',margin:0,valign:'middle'});};
    var lab=function(arm){return st.labels[arm].indexOf(arm)===0?st.labels[arm]:arm+' · '+st.labels[arm];};
    if(p.problem||p.hyp||I[0]||I[1]){
      var s1=P.addSlide(),hasI=!!(I[0]||I[1]),wide=hasI&&[I[0],I[1]].some(function(m){return m&&m.w/m.h>1.15;}),tw=hasI?(wide?5.4:5.7):12.13,Y0=1.95,AV=4.62;s1.background={color:'FFFFFF'};
      s1.addText(('Test A/B'+(p.page?' · '+p.page:'')).toUpperCase(),{x:0.6,y:0.5,w:12.13,h:0.3,fontFace:FT,fontSize:11,bold:true,color:G,charSpacing:1.5,margin:0});
      s1.addText(st.name,{x:0.6,y:0.82,w:12.13,h:0.9,fontFace:FT,fontSize:tfs(st.name),bold:true,color:INK,margin:0,valign:'top'});
      var ob=[[D.pr.name,'objectif principal']].concat(D.gf.map(function(g){return [g.name,'garde-fou'];})),last='Lecture chaque '+D.unit+', '+D.k+' '+D.un+' au plus',mdl=D.mde!=null?'Effet minimal détectable : '+nf(D.mde*100,1)+' % sur '+D.k+' '+D.un:'';
      var T=[p.problem||'',p.hyp||''],GAP=0.2,LB=0.25,fs,need=function(f){var h=0;T.forEach(function(t){if(t)h+=LB+hOf(lines(t,tw,f),f)+GAP;});var ol=ob.reduce(function(a,o){return a+lines(o[0]+' · '+o[1],tw,f);},0)+lines(last,tw,f)+(mdl?lines(mdl,tw,f):0);return h+LB+hOf(ol,f);};
      for(fs=13;fs>9&&need(fs)>AV;fs-=0.5);
      var guard=0;while(need(fs)>AV&&guard++<60){var li=T[0].length>=T[1].length?0:1;if(T[li].length<160)break;T[li]=T[li].slice(0,Math.floor(T[li].length*0.9)).replace(/\s+\S*$/,'')+'…';}
      var y=Y0,blk=function(title,h,body){s1.addText(title.toUpperCase(),{x:0.6,y:y,w:tw,h:LB,fontFace:FT,fontSize:10,bold:true,color:G,charSpacing:1.2,margin:0,valign:'top'});s1.addText(body,{x:0.6,y:y+LB,w:tw,h:h,fontFace:FB,fontSize:fs,color:INK,margin:0,valign:'top',lineSpacingMultiple:1.08});y+=LB+h+GAP;};
      if(T[0])blk('Le problème',hOf(lines(T[0],tw,fs),fs),T[0]);
      if(T[1])blk('L\'hypothèse',hOf(lines(T[1],tw,fs),fs),T[1]);
      var runs=[];ob.forEach(function(o){runs.push({text:o[0],options:{bold:true}});runs.push({text:' · '+o[1],options:{color:CH,breakLine:true}});});if(mdl){runs.push({text:'Effet minimal détectable : ',options:{}});runs.push({text:nf(D.mde*100,1)+' %',options:{bold:true}});runs.push({text:' sur '+D.k+' '+D.un,options:{breakLine:true}});}runs.push({text:last,options:{color:CH}});
      blk('L\'objectif',hOf(ob.reduce(function(a,o){return a+lines(o[0]+' · '+o[1],tw,fs);},0)+lines(last,tw,fs)+(mdl?lines(mdl,tw,fs):0),fs),runs);
      if(hasI){var box=function(i,x,yy,bw,bh){var im=I[i],arm=i?'B':'A';s1.addText(lab(arm),{x:x,y:yy,w:bw,h:0.27,fontFace:FT,fontSize:11,bold:true,color:i?G:CH,margin:0,valign:'top'});
          s1.addShape(P.ShapeType.rect,{x:x,y:yy+0.3,w:bw,h:bh,fill:{color:'F8FBFA'},line:{color:i?G:'D9D9D9',width:1}});
          if(im){var r=Math.min((bw-0.1)/im.w,(bh-0.1)/im.h),iw=im.w*r,ih=im.h*r;s1.addImage({data:im.d.replace(/^data:/,''),x:x+(bw-iw)/2,y:yy+0.3+(bh-ih)/2,w:iw,h:ih});}
          else s1.addText('Pas de visuel',{x:x,y:yy+0.3,w:bw,h:bh,fontFace:FB,fontSize:11,color:MU,align:'center',valign:'middle',margin:0});};
        if(wide){box(0,6.4,1.95,6.33,1.95);box(1,6.4,4.4,6.33,1.95);}else{box(0,6.75,1.95,2.9,4.3);box(1,9.85,1.95,2.9,4.3);}}
      foot(s1);
    }
    var s2=P.addSlide(),K=D.pr.key,tone=K==='POSITIF'?'g':K==='NEGATIF'?'c':'n',TC={g:['EAF6F1','9AD3BE','0B5E48'],c:['FCEDEA','F2A99F','8F2C20'],n:['F1F4F5','CBD3D7','1A1D1F']}[tone];s2.background={color:'FFFFFF'};
    var verdict=K==='POSITIF'?'L\'effet attendu par l\'hypothèse est démontré':K==='NEGATIF'?'L\'effet inverse de l\'hypothèse est démontré':D.stop?'L\'effet attendu par l\'hypothèse n\'est pas démontré':'Rien n\'est démontré à ce stade : le test continue';
    var ttl=D.pr.name+' : '+(D.big||D.pr.lift)+', '+D.pr.status.charAt(0).toLowerCase()+D.pr.status.slice(1);
    s2.addText(('Le résultat · '+(D.stop?'acquis':'lecture')+' en '+D.unit+' '+D.wkn+' sur '+D.k).toUpperCase(),{x:0.6,y:0.5,w:12.13,h:0.3,fontFace:FT,fontSize:11,bold:true,color:G,charSpacing:1.5,margin:0});
    s2.addText(ttl,{x:0.6,y:0.82,w:12.13,h:0.9,fontFace:FT,fontSize:tfs(ttl),bold:true,color:INK,margin:0,valign:'top'});
    s2.addText(D.big||D.pr.lift,{x:0.6,y:1.9,w:5.2,h:1.2,fontFace:FT,fontSize:66,bold:true,color:tone==='g'?'0E7C5D':tone==='c'?'C9402F':CH,margin:0,valign:'middle'});
    s2.addText([{text:D.pr.name,options:{bold:true,color:INK,breakLine:true}},{text:D.rates,options:{color:CH,breakLine:true}},{text:'Intervalle à '+nf(D.pr.ci,D.pr.ci%1?1:0)+' % : de '+D.pr.lo+' à '+D.pr.hi,options:{color:MU}}],{x:0.6,y:3.15,w:5.2,h:1.0,fontFace:FB,fontSize:13,margin:0,valign:'top',paraSpaceAfter:3});
    var hy=(p.hyp||'').replace(/\s+/g,' ').trim();if(hy.length>230)hy=hy.slice(0,230).replace(/\s+\S*$/,'')+'…';
    var gfc={},gft=[];D.gf.forEach(function(g){gfc[g.status]=(gfc[g.status]||0)+1;});Object.keys(gfc).forEach(function(kk){gft.push(gfc[kk]+' × '+kk.charAt(0).toLowerCase()+kk.slice(1));});
    var bx=[{text:'Par rapport à l\'hypothèse'.toUpperCase(),options:{bold:true,fontFace:FT,fontSize:10,color:TC[2],charSpacing:1.2,breakLine:true}},{text:verdict,options:{bold:true,fontFace:FT,fontSize:15,color:TC[2],breakLine:true}}];
    if(hy)bx.push({text:'« '+hy+' »',options:{italic:true,fontFace:FB,fontSize:11,color:CH,breakLine:true}});
    if(gft.length)bx.push({text:'Garde-fous : '+gft.join(', '),options:{fontFace:FB,fontSize:11.5,color:INK}});
    var bh=0.95+(hy?hOf(lines(hy,4.8,11),11)+0.12:0)+(gft.length?0.3:0);
    s2.addShape(P.ShapeType.roundRect,{x:0.6,y:4.3,w:5.2,h:bh,rectRadius:0.08,fill:{color:TC[0]},line:{color:TC[1],width:1}});
    s2.addText(bx,{x:0.8,y:4.42,w:4.8,h:bh-0.24,margin:0,valign:'top',paraSpaceAfter:5});
    var RW=D.rows.slice(0,10),more=D.rows.length-RW.length,hd=function(t,a){return {text:t,options:{bold:true,fontFace:FT,fontSize:10,color:MU,align:a||'left',border:[{type:'none'},{type:'none'},{type:'solid',color:'D9D9D9',pt:1},{type:'none'}]}};};
    var cell=function(t,o){return {text:t,options:Object.assign({fontFace:FB,fontSize:11.5,color:INK,valign:'middle',border:[{type:'none'},{type:'none'},{type:'solid',color:'E3E6E6',pt:0.75},{type:'none'}]},o||{})};};
    var tb=[[hd('MÉTRIQUE'),hd('RÔLE'),hd('ÉCART','right'),hd('STATUT','right')]].concat(RW.map(function(r){var col=r.tone==='g'?'0E7C5D':r.tone==='c'?'C9402F':r.tone==='w'?'7A5410':CH;return [cell(r.name,{bold:r.main}),cell(r.role,{color:MU}),cell(r.lift,{align:'right',bold:true}),cell(r.status,{align:'right',color:col,bold:r.tone!==''})];}));
    if(more>0)tb.push([cell('+ '+more+' autre'+(more>1?'s':'')+' métrique'+(more>1?'s':''),{color:MU,colspan:4})]);
    s2.addTable(tb,{x:6.3,y:1.95,w:6.43,colW:[2.85,1.08,1.05,1.45],rowH:0.4,margin:[0.04,0.06,0.04,0.02]});
    foot(s2);
    var slug=String(st.name||'test').normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^A-Za-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,60).toLowerCase()||'test';
    return P.writeFile({fileName:'rapport-'+slug+'.pptx'});
  });
}
""".replace('\n',NL)
s=s[:i]+NEW+s[j:]
assert s.count('v56.25')==1
s=s.replace('v56.25','v56.26')
open('repo/calculateur-sequentiel-v56-26.html','w',newline='').write(s);print(len(s))

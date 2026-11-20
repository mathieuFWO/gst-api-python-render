# v56-29 : les visuels des variations se placent sans enregistrer d'abord la présentation (l'enregistrement se fait à l'ajout),
# et un emplacement vide montre un squelette d'interface grisé.
s=open('repo/calculateur-sequentiel-v56-28.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(a[:80],s.count(a));s=s.replace(a,b)
rep("""'<h4>Visuels des variations</h4>'+(state.sid?'<div class="pv">'+presVis('A',false)+presVis('B',false)+'</div><p class="hint">PNG ou JPG, 2 Mo par image, 4 visuels par variation. Ils sont enregistrés dans votre espace.</p>':'<p class="hint">Enregistrez d\\'abord la présentation : vous pourrez ensuite ajouter les visuels de chaque variation.</p>')""",
"""'<h4>Visuels des variations</h4><div class="pv">'+presVis('A',false)+presVis('B',false)+'</div><p class="hint">PNG ou JPG, 2 Mo par image, 4 visuels par variation. '+(state.sid?'Ils sont enregistrés dans votre espace.':'Le test est enregistré dans votre espace à l\\'ajout du premier visuel.')+'</p>'""")
rep("""  if(!ro&&L.length<4)h+='<button type="button" class="pv-add" data-act="vispick" data-v="'+arm+'"'+(ui.visBusy?' disabled':'')+'>'+(ui.visBusy===arm?'Envoi en cours…':'+ Ajouter un visuel')+'</button>';""",
"""  if(!ro&&!L.length)h+='<button type="button" class="pv-sk" data-act="vispick" data-v="'+arm+'"'+(ui.visBusy?' disabled':'')+' aria-label="Ajouter un visuel pour '+esc(state.labels[arm])+'"><span class="sk" aria-hidden="true"><span class="sk-top"><i></i><i></i><i></i><i></i></span><span class="sk-hero"></span><span class="sk-row"><span class="sk-img"></span><span class="sk-tx"><i class="w8"></i><i class="w6"></i>'+(arm==='B'?'<span class="sk-st"><i></i><i></i><i></i><i></i><i></i></span>':'<i class="w4"></i>')+'<i class="sk-cta"></i></span></span><span class="sk-row3"><i></i><i></i><i></i></span></span><span class="pv-skl">'+(ui.visBusy===arm?'Envoi en cours…':'+ Ajouter un visuel')+'</span></button>';
  else if(!ro&&L.length<4)h+='<button type="button" class="pv-add" data-act="vispick" data-v="'+arm+'"'+(ui.visBusy?' disabled':'')+'>'+(ui.visBusy===arm?'Envoi en cours…':'+ Ajouter un visuel')+'</button>';""")
rep("""  else if(name==='vispick'){var vi=""","""  else if(name==='vispick'){if(!state.sid&&!state.name.trim()){ui.error='Donnez un nom au test (en haut de l\\'écran) avant d\\'ajouter un visuel : il est enregistré dans votre espace à ce moment-là.';return render();}var vi=""")
rep("""  var go=function(){if(state!==st||!st.sid)throw new Error('enregistrez d\\'abord le test dans votre espace');""",
"""  var go=function(){if(state===st&&!st.sid&&ui.error)throw new Error('\\u0001');if(state!==st||!st.sid)throw new Error('enregistrez d\\'abord le test dans votre espace');""")
rep("""catch(function(e){if(state===st)ui.error='Visuel non ajouté : '+e.message;})""","""catch(function(e){if(state===st&&e.message!=='\\u0001')ui.error='Visuel non ajouté : '+e.message;})""")
rep("""#gst-app button.pv-add{display:block;""","""#gst-app button.pv-sk{position:relative;display:block;width:100%;min-height:0;padding:0;border:1px dashed #B9C4C4;border-radius:10px;background:#F4F6F6;overflow:hidden;cursor:pointer;text-align:left}#gst-app button.pv-sk:hover,#gst-app button.pv-sk:focus-visible{border-color:#1D9E75;background:#F2FAF7}#gst-app button.pv-sk:disabled{opacity:.6;cursor:default}
#gst-app .pv-sk .sk{display:block;padding:12px 12px 62px}#gst-app .pv-sk .sk i,#gst-app .pv-sk .sk>span,#gst-app .pv-sk .sk-img,#gst-app .pv-sk .sk-tx,#gst-app .pv-sk .sk-st{display:block}#gst-app .pv-sk .sk i,#gst-app .pv-sk .sk-hero,#gst-app .pv-sk .sk-img{background:#E1E6E6;border-radius:4px}
#gst-app .pv-sk .sk-top{display:grid!important;grid-template-columns:18% 1fr 12% 12%;gap:6%;align-items:center;padding-bottom:10px;border-bottom:1px solid #E1E6E6}#gst-app .pv-sk .sk-top i{height:8px}#gst-app .pv-sk .sk-top i:first-child{height:12px;background:#D3DADA}#gst-app .pv-sk .sk-top i:nth-child(2){background:none}
#gst-app .pv-sk .sk-hero{height:38px;margin-top:10px}#gst-app .pv-sk .sk-row{display:grid!important;grid-template-columns:42% 1fr;gap:10px;margin-top:10px}#gst-app .pv-sk .sk-img{aspect-ratio:4/3}#gst-app .pv-sk .sk-tx i{height:8px;margin-bottom:8px}#gst-app .pv-sk .w8{width:88%}#gst-app .pv-sk .w6{width:64%}#gst-app .pv-sk .w4{width:42%}
#gst-app .pv-sk .sk-st{display:flex!important;gap:4px;margin-bottom:8px}#gst-app .pv-sk .sk-st i{width:10px;height:10px;margin:0;border-radius:50%;background:#C9D2D2}#gst-app .pv-sk .sk-tx i.sk-cta{height:18px;width:70%;margin:10px 0 0;background:#D3DADA;border-radius:9px}
#gst-app .pv-sk .sk-row3{display:grid!important;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:12px}#gst-app .pv-sk .sk-row3 i{height:26px}
#gst-app .pv-skl{position:absolute;left:12px;right:12px;bottom:10px;display:flex;align-items:center;justify-content:center;min-height:44px;border-radius:8px;background:#fff;border:1px solid #1D9E75;color:#0E7C5D;font-weight:700;font-size:14px}
#gst-app button.pv-add{display:block;""")
assert s.count('v56.28')==1
s=s.replace('v56.28','v56.29')
open('repo/calculateur-sequentiel-v56-29.html','w',newline='').write(s);print(len(s))
# Graphique : sur mobile, la zone sous les tirets de futilité est légèrement grisée et nommée ; la phrase d'explication dit où l'on continue.
s=open('repo/calculateur-sequentiel-v56-29.html',newline='').read()
rep("""  if(k>1){s+='<path d="'+pe+' L'+xr+' '+T+' L'+xl+' '+T+' Z" fill="#EEF8F5"/>';""",
"""  if(k>1&&hasFut&&small)s+='<path class="futz" d="'+pf+' L'+xr+' '+yb+' L'+xl+' '+yb+' Z" fill="#EEF0F0"/>';
  if(k>1){s+='<path d="'+pe+' L'+xr+' '+T+' L'+xl+' '+T+' Z" fill="#EEF8F5"/>';""")
rep("""  if(!small&&k>1){s+='<g font-size="11" font-weight="600">""","""  if(small&&k>1&&hasFut){var jf=Math.min(k-2,Math.floor(k*0.6)),yf=y(fut[jf])+15;if(yf<y(-eff[jf])-4)s+='<text class="futl" x="'+x(jf)+'" y="'+yf+'" text-anchor="middle" font-size="10.5" fill="#464849">Futilité : on arrête</text>';}
  if(!small&&k>1){s+='<g font-size="11" font-weight="600">""")
rep("""'<p class="hint">Tant que la courbe bleue reste dans le couloir blanc, on continue. Dès qu\\'elle en sort, le test s\\'arrête.""",
"""'<p class="hint">'+(m.role==='principale'&&state.bounds&&state.bounds.fut&&state.bounds.fut.some(function(v){return Number.isFinite(v);})?'Tant que la courbe bleue reste entre la ligne verte et les tirets gris, on continue. Au-dessus de la ligne verte ou sous les tirets, le test s\\'arrête.':'Tant que la courbe bleue reste dans le couloir blanc, on continue. Dès qu\\'elle en sort, le test s\\'arrête.')+'""")
open('repo/calculateur-sequentiel-v56-29.html','w',newline='').write(s);print(len(s))

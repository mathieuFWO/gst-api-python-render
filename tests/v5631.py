# v56-31 : segmentation explicite (bouton « Segmenter par ... » sous chaque métrique, à la place du « + »),
# puce de sélection en début de ligne (bleue sur la métrique dont le graphique montre la trajectoire) à la place des pictogrammes de statut.
s=open('repo/calculateur-sequentiel-v56-30.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(a[:80],s.count(a));s=s.replace(a,b)
def cut(a,b,new):
    global s
    assert s.count(a)==1,(a[:60],s.count(a));i=s.index(a);j=s.index(b,i);s=s[:i]+new+s[j:]
# le « + » dans le nom : retiré
cut("""+(wk.dims&&wk.dims.length&&st?'<button type="button" class="sgp" data-act="segx\"""","""+'</div><div class="hint"><span class="mob num">'+fv(st&&st.mA)+' → '+fv(st&&st.mB)+(tags.length?' · ':'')+'</span>'+tags.join(' · ')+'</div></div>'""","")
rep("""+'</div><div class="hint"><span class="mob num">'+fv(st&&st.mA)+' → '+fv(st&&st.mB)+(tags.length?' · ':'')+'</span>'+tags.join(' · ')+'</div></div>'
    +'<div class="c-a num">'+fv(st&&st.mA)+'</div><div class="c-b num">'+fv(st&&st.mB)+'</div>'
    +'<div class="c-lift"><span class="lift num">'+pct(st&&st.lift)+'</span></div>'
    +'<div class="c-ci">'+ciBar(st,ax,tone)+'</div>'""",
"""+'</div><div class="hint"><span class="mob num">'+fv(st&&st.mA)+' → '+fv(st&&st.mB)+(tags.length?' · ':'')+'</span>'+tags.join(' · ')+'</div>'
      +(wk.dims&&wk.dims.length&&st?(function(){var on=!!(ui.segX&&ui.segX[m.id]),lab=wk.dims.length>1?'dimension':'« '+segDim(wk).n+' »';return '<button type="button" class="sgl" data-act="segx" data-v="'+m.id+'" aria-expanded="'+on+'"><svg aria-hidden="true" width="14" height="14" viewBox="0 0 14 14"><path d="M1.500 3h11M3.500 7h7M5.500 11h3" fill="none" stroke="currentColor" stroke-width="1.500" stroke-linecap="round"/></svg>'+(on?'Masquer le détail par ':'Segmenter par ')+esc(lab)+'</button>';})():'')+'</div>'
    +'<div class="c-a num">'+fv(st&&st.mA)+'</div><div class="c-b num">'+fv(st&&st.mB)+'</div>'
    +'<div class="c-lift"><span class="lift num">'+pct(st&&st.lift)+'</span></div>'
    +'<div class="c-ci">'+ciBar(st,ax,tone)+'</div>'""")
# puce de sélection à la place du pictogramme de statut
rep("""tabindex="0" role="button" aria-pressed="'+(m.id===sel)+'">'+ICON[tone||'n']""","""tabindex="0" role="button" aria-pressed="'+(m.id===sel)+'" title="'+(m.id===sel?'Métrique affichée dans le graphique':'Afficher cette métrique dans le graphique')+'"><span class="rsel" aria-hidden="true"></span>'""")
rep("""<h3>Trajectoire : '+esc(m.name)+'</h3>""","""<h3><span class="rsel on" aria-hidden="true"></span>Trajectoire : '+esc(m.name)+'</h3>""")
rep("""'C\\'est lui qui décide. Survolez ou sélectionnez une ligne pour le détail.'""","""'C\\'est lui qui décide. La puce bleue marque la métrique affichée dans le graphique : cliquez une autre ligne pour la changer.'""")
i=s.index("#gst-app .sgp{position:relative");j=s.index("#gst-app .sgs{border-top")
s=s[:i]+"""#gst-app .rsel{display:block;width:16px;height:16px;box-sizing:border-box;border-radius:50%;border:1.5px solid #B9C4C4;background:#fff;justify-self:center;grid-row:1;grid-column:1}#gst-app .mrw:not(.sub):hover .rsel{border-color:#0082C3}#gst-app .mrw.sel .rsel,#gst-app .rsel.on{border:4.5px solid #0082C3;background:#fff}#gst-app h3 .rsel{display:inline-block;margin-right:8px;vertical-align:-2px}
#gst-app .sgl{display:inline-flex;align-items:center;gap:6px;min-height:28px;margin:6px 0 0;padding:3px 10px;border:1px solid #A6CFEA;border-radius:999px;background:#F2F8FC;color:#00629A;font-size:12.5px;font-weight:600;line-height:1.2;white-space:normal;text-align:left;cursor:pointer}#gst-app .sgl:hover,#gst-app .sgl[aria-expanded=true]{border-color:#0082C3;background:#E6F2F9}#gst-app .sgl svg{flex:none}@media (max-width:760px){#gst-app .sgl{min-height:44px;padding:6px 12px;font-size:13px}}
"""+s[j:]
assert s.count('v56.30')==1
s=s.replace('v56.30','v56.31')
open('repo/calculateur-sequentiel-v56-31.html','w',newline='').write(s);print(len(s))

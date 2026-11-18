src='repo/calculateur-sequentiel-v56-13.html';dst='repo/calculateur-sequentiel-v56-14.html'
s=open(src,newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(s.count(a),a[:110]); s=s.replace(a,b)
rep("VERSION='v56.13'","VERSION='v56.14'")
# ===== la règle d'arrêt se choisit à la création du test : même composant dans l'onglet Plan et dans l'assistant =====
a=s.index("    +'<div><label>Quand le test peut-il s\\'arrêter avant la fin ?</label>'")
b=s.index(NL,s.index("data-p=\"testType\" value=\"1\"",a))
blk=s[a:b]
assert blk.rstrip().endswith("</label></div>'"),blk[-60:]
fn=blk.replace("    +'<div><label>","'<div><label>",1).replace('data-p="testType"',"'+at+'").replace('name="gst-tt"','name="\'+nm+\'"').replace("p.testType","tt")
s=s[:a]+"    +stopRule(p.testType,'data-p=\"testType\"','gst-tt')"+s[b:]
rep("function viewHome(){","function stopRule(tt,at,nm){return "+fn.replace(NL,NL+"  ")+";}"+NL+"function viewHome(){".replace('\n',NL))
# assistant, étape 2
rep("man:{step:1,name:'',k:4,alpha:0.05,power:0.8,","man:{step:1,name:'',k:4,alpha:0.05,power:0.8,testType:3,")
rep("p.k=m.k;p.alpha=m.alpha;p.power=m.power;p.beta=parseFloat((1-m.power).toFixed(4));","p.k=m.k;p.alpha=m.alpha;p.power=m.power;p.testType=m.testType===1?1:3;p.beta=parseFloat((1-m.power).toFixed(4));")
rep("Les baisser raccourcit le test, au prix de plus d\\'erreurs.</p></div>'","Les baisser raccourcit le test, au prix de plus d\\'erreurs.</p><div class=\"w2 wz-rule\">'+stopRule(m.testType===1?1:3,'data-man=\"testType\"','gst-mtt')+'</div></div>'")
rep("else if(mk==='alpha'||mk==='power'){ui.man[mk]=parseFloat(t.value);return later();}","else if(mk==='alpha'||mk==='power'){ui.man[mk]=parseFloat(t.value);return later();}else if(mk==='testType'){ui.man.testType=t.value==='1'?1:3;return later();}")
rep("if(mm.power>0&&mm.power<1)state.plan.power=mm.power;state.plan.beta=parseFloat((1-state.plan.power).toFixed(4));var mtv=","if(mm.power>0&&mm.power<1)state.plan.power=mm.power;state.plan.testType=mm.testType===1?1:3;state.plan.beta=parseFloat((1-state.plan.power).toFixed(4));var mtv=")
# premier import (fichier ou API) : la règle se choisit sur l'écran de vérification
rep("d.endTyped=!!(keep&&keep.endTyped);","d.tt=keep&&keep.tt===1?1:(keep&&keep.tt===3?3:(state.plan.testType===1?1:3));d.endTyped=!!(keep&&keep.endTyped);")
rep("var keep={name:d.name,k:d.k,startDate:d.startDate,endDate:d.endDate,","var keep={name:d.name,k:d.k,tt:d.tt,startDate:d.startDate,endDate:d.endDate,")
rep("else if(f==='sameOk'){","else if(f==='tt'){d.tt=t.value==='1'?1:3;}else if(f==='sameOk'){")
rep("  if(replace){state.plan.k=d.k;state.plan.startDate=d.startDate;}","  if(replace){state.plan.k=d.k;state.plan.startDate=d.startDate;if(d.mode==='instantane'||!state.bounds)state.plan.testType=d.tt===1?1:3;}")
rep("+'<div class=\"dv-sec\"><div class=\"kicker\">2 · Ce que l\\'outil a lu</div>","+(locked?'':'<div class=\"dv-rule\">'+stopRule(d.tt,'data-d=\"tt\"','gst-dtt')+'</div>')+'<div class=\"dv-sec\"><div class=\"kicker\">2 · Ce que l\\'outil a lu</div>")
rep("#gst-app .dv-gate.ko{","#gst-app label.opt input[type=radio]{flex:none;width:18px;height:18px;min-height:0;margin:2px 0 0;padding:0;accent-color:#028D6A}#gst-app label.opt>span{flex:1 1 auto;min-width:0}#gst-app .dv label.opt,#gst-app .wz label.opt,#gst-app .card label.opt{display:flex}@media (max-width:760px){#gst-app .dv-g>.dv-ct{grid-column:1/-1}}#gst-app .wz-rule{margin-top:4px}#gst-app .dv-rule{padding:0 0 4px}#gst-app .dv-rule>div>label,#gst-app .wz-rule>div>label{display:block;margin-bottom:8px}\n#gst-app .dv-gate.ko{")
rep("+'<div><label for=\"gst-dct\">Colonne du test</label>","+'<div class=\"dv-ct\"><label for=\"gst-dct\">Colonne du test</label>")
open(dst,'w',newline='').write(s);print(len(s))

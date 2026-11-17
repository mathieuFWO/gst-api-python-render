src='repo/calculateur-sequentiel-v55-5.html';dst='repo/calculateur-sequentiel-v55-6.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
rep("VERSION='v55.5'","VERSION='v55.6'")
rep("man:{step:1,name:'',k:4,startDate:todayISO(),","man:{step:1,name:'',k:4,alpha:0.05,power:0.8,startDate:todayISO(),")
rep("var p=JSON.parse(JSON.stringify(state.plan));p.k=m.k;var base=mdeBase()","var p=JSON.parse(JSON.stringify(state.plan));p.k=m.k;p.alpha=m.alpha;p.power=m.power;p.beta=parseFloat((1-m.power).toFixed(4));var msel=function(v,opts){return opts.map(function(o){return '<option value=\"'+o[0]+'\"'+(String(o[0])===String(v)?' selected':'')+'>'+o[1]+'</option>';}).join('');};var base=mdeBase()")
rep("""      +'<div><label for="gst-msd">Date de début du test</label><input id="gst-msd" type="date" data-man="startDate" value="'+esc(m.startDate)+'"></div></div>'""",
"""      +'<div class="wz-g"><div><label for="gst-ma">Confiance</label><select id="gst-ma" data-man="alpha">'+msel(m.alpha,[[0.2,'80 %'],[0.15,'85 %'],[0.1,'90 %'],[0.05,'95 %'],[0.01,'99 %']])+'</select></div><div><label for="gst-mp">Puissance</label><select id="gst-mp" data-man="power">'+msel(m.power,[[0.6,'60 %'],[0.7,'70 %'],[0.8,'80 %'],[0.85,'85 %'],[0.9,'90 %'],[0.95,'95 %']])+'</select></div><p class="fh w2" style="margin-top:-8px">Confiance : le risque accepté de voir un gain qui n\\'existe pas (95 % = 5 % de risque). Puissance : la chance de détecter un vrai gain. Les baisser raccourcit le test, au prix de plus d\\'erreurs.</p></div>'
      +'<div><label for="gst-msd">Date de début du test</label><input id="gst-msd" type="date" data-man="startDate" value="'+esc(m.startDate)+'"></div></div>'""")
rep("#gst-app .wz-g{grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}","#gst-app .wz-g{grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}",0) if False else None
rep("else ui.man[mk]=t.value;return;}","else if(mk==='alpha'||mk==='power'){ui.man[mk]=parseFloat(t.value);return later();}else ui.man[mk]=t.value;return;}")
rep("var mtv=toNum(ui.mde.traffic);if(mtv>0)state.plan.traffic=mtv;","if(mm.alpha>0&&mm.alpha<1)state.plan.alpha=mm.alpha;if(mm.power>0&&mm.power<1)state.plan.power=mm.power;state.plan.beta=parseFloat((1-state.plan.power).toFixed(4));var mtv=toNum(ui.mde.traffic);if(mtv>0)state.plan.traffic=mtv;")
# sur mobile, confiance et puissance restent côte à côte
rep("  #gst-app .wz-g,#gst-app .wz2{grid-template-columns:minmax(0,1fr)}","  #gst-app .wz-g,#gst-app .wz2{grid-template-columns:minmax(0,1fr)}#gst-app .wz2 .wz-g{grid-template-columns:repeat(2,minmax(0,1fr))}")
open(dst,'w',newline='').write(s);print(len(s))

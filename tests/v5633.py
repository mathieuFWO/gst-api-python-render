# v56-33 : sans trafic prévu dans le plan, la première lecture sert de référence (rythme hebdomadaire et effet détectable à ce rythme),
# au lieu de « Trafic prévu non renseigné ».
s=open('repo/calculateur-sequentiel-v56-32.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(a[:80],s.count(a));s=s.replace(a,b)
rep("""  var expQ=ptw*(UQ?WK(cur)/7:WK(cur)),rtQ=expQ>0?tot/expQ:null,lowQ=rtQ!=null&&rtQ<0.8,mdeTx='';
  if(lowQ&&binQ&&pr&&pr.st&&pr.st.mA>0&&pr.st.mA<1){var IFq=state.bounds&&state.bounds.IF>0?Math.sqrt(state.bounds.IF):1,m0=mdeAt(state.plan,{t:ptw,p:pr.st.mA},k,IFq),m1=mdeAt(state.plan,{t:ptw*rtQ,p:pr.st.mA},k,IFq);""",
"""  /* Sans trafic prévu, la première lecture donne le rythme de référence (suivi hebdomadaire). */
  var w0Q=state.weeks[0],ptwI=!ptw&&!UQ&&w0Q&&WK(0)>0&&w0Q.A.n+w0Q.B.n>0?(w0Q.A.n+w0Q.B.n)/WK(0):0,ptwD=ptw||ptwI,refQ='semaine '+WK(0),mdeRef='';
  var expQ=ptwD*(UQ?WK(cur)/7:WK(cur)),rtQ=expQ>0?tot/expQ:null,lowQ=rtQ!=null&&rtQ<0.8,mdeTx='';
  if(ptwI&&binQ&&pr&&pr.st&&pr.st.mA>0&&pr.st.mA<1){var mR=mdeAt(state.plan,{t:ptwI,p:pr.st.mA},k,state.bounds&&state.bounds.IF>0?Math.sqrt(state.bounds.IF):1);if(isFinite(mR)&&mR>0)mdeRef=' À ce rythme, l\\'effet détectable en '+k+' semaines est d\\'environ '+nf(mR*100,1)+' %.';}
  if(lowQ&&binQ&&pr&&pr.st&&pr.st.mA>0&&pr.st.mA<1){var IFq=state.bounds&&state.bounds.IF>0?Math.sqrt(state.bounds.IF):1,m0=mdeAt(state.plan,{t:ptwD,p:pr.st.mA},k,IFq),m1=mdeAt(state.plan,{t:ptwD*rtQ,p:pr.st.mA},k,IFq);""")
rep("""  var c2T=noinfo?'Volumes incohérents':lowQ?'Trafic sous le plan':rtQ!=null?'Trafic conforme au plan':'Trafic prévu non renseigné';""",
"""  var c2T=noinfo?'Volumes incohérents':ptwI?(lowQ?'Trafic sous le rythme de la '+refQ:cur===0?'Trafic de référence : '+refQ:'Trafic conforme au rythme de la '+refQ):lowQ?'Trafic sous le plan':rtQ!=null?'Trafic conforme au plan':'Trafic prévu non renseigné';""")
rep(""":rtQ!=null?nf(tot)+' visiteurs sur '+nf(Math.round(expQ))+' prévus à fin '""",""":ptwI?(cur===0?nf(tot)+' visiteurs en '+refQ+'.'+mdeRef+' Aucun trafic prévu n\\'est saisi dans l\\'onglet Plan : cette lecture sert de référence pour les suivantes.':nf(tot)+' visiteurs sur '+nf(Math.round(expQ))+' attendus au rythme de la '+refQ+(lowQ?', soit '+nf(rtQ*100,0)+' %.'+mdeTx:'.')):rtQ!=null?nf(tot)+' visiteurs sur '+nf(Math.round(expQ))+' prévus à fin '""")
rep("""(ptw>0?'Plan : '+nf(ptw)+' visiteurs par semaine. Alerte si le cumul passe sous 80 % du plan.':'Aucun trafic prévu dans le plan : seuls les volumes réels sont affichés.')""",
"""(ptw>0?'Plan : '+nf(ptw)+' visiteurs par semaine. Alerte si le cumul passe sous 80 % du plan.':ptwI?'Aucun trafic prévu dans le plan : la '+refQ+' sert de référence ('+nf(Math.round(ptwI))+' visiteurs par semaine). Alerte si le cumul passe sous 80 % de ce rythme.':'Aucun trafic prévu dans le plan : seuls les volumes réels sont affichés.')""")
rep("""<th scope="col">Du plan</th>""","""<th scope="col">'+(ptwI?'De la référence':'Du plan')+'</th>""")
rep("""(ptw>0&&o.span>0?nf((o.nA+o.nB)/(ptw*o.span)*100,0)+' %':'-')""","""(ptwD>0&&o.span>0?nf((o.nA+o.nB)/(ptwD*o.span)*100,0)+' %':'-')""")
assert s.count('v56.32')==1
s=s.replace('v56.32','v56.33')
open('repo/calculateur-sequentiel-v56-33.html','w',newline='').write(s);print(len(s))

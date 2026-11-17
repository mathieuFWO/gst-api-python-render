src='repo/calculateur-sequentiel-v55-3.html';dst='repo/calculateur-sequentiel-v55-4.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
rep("VERSION='v55.3'","VERSION='v55.4'")
# a. collision de classe : .sec (section, marge haute) s'appliquait au bouton .sec
rep("#gst-app button{white-space:normal}","#gst-app button{white-space:normal}\n#gst-app button.sec{margin:0}")
# b. envoi par email : bouton, adresse lue au clic, lien copié s'il est trop long pour un lien mailto
rep("""<a class="btn" href="mailto:'+encodeURIComponent(ui.shareTo||'')+'?subject='+encodeURIComponent(sub)+'&body='+encodeURIComponent(body)+'">Ouvrir dans ma messagerie</a></div>'""",
    """<button type="button" data-act="sharemail">Ouvrir dans ma messagerie</button></div>'+(ui.mailNote?'<p class="ok" role="status" style="margin-top:10px">'+(ui.mailNote==='long'?'<b>Lien copié.</b> Il est trop long pour être inséré automatiquement : collez-le dans le message qui s\\'ouvre (Ctrl+V).':'Le message s\\'ouvre dans votre messagerie.')+' Rien ne s\\'ouvre ? Ce poste n\\'a pas de messagerie par défaut : copiez le lien et collez-le dans votre email.</p>':'')""")
rep("var u=ui.shareUrl||'',sub='Résultats du test « '+(state.name||'test A/B')+' »',body='Bonjour,\\n\\nVoici les résultats du test « '+(state.name||'test A/B')+' » (lecture seule, données du '+frDate(todayISO())+') :\\n'+u+'\\n';","var u=ui.shareUrl||'';")
rep("if(t.getAttribute('data-f')==='shareto'){ui.shareTo=t.value.trim();return later();}","if(t.getAttribute('data-f')==='shareto'){ui.shareTo=t.value.trim();return;}")
rep("  else if(name==='sharecopy'){","""  else if(name==='sharemail'){var i3=root.querySelector('[data-f=shareto]'),to=(i3?i3.value:ui.shareTo||'').trim();ui.shareTo=to;if(!/^[^\\s@<>,;"']+@[^\\s@<>,;"']+\\.[^\\s@<>,;"']+$/.test(to))to='';
    var nm=state.name||'test A/B',head='mailto:'+to+'?subject='+encodeURIComponent('Résultats du test « '+nm+' »')+'&body=',intro='Bonjour,\\n\\nVoici les résultats du test « '+nm+' » (lecture seule, données du '+frDate(todayISO())+') :\\n',full=head+encodeURIComponent(intro+ui.shareUrl+'\\n');
    if(full.length>2000){full=head+encodeURIComponent(intro+'[collez ici le lien copié : Ctrl+V]\\n');ui.mailNote='long';try{if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(ui.shareUrl).catch(function(){});else{var i4=root.querySelector('[data-f=shareurl]');if(i4){i4.select();document.execCommand('copy');}}}catch(e){}}else ui.mailNote='ok';
    if(window.GST_NOMAIL)window.GST_NOMAIL(full);else location.href=full;render();return;}
  else if(name==='sharecopy'){""")
rep("else if(name==='share'){ui.share=!ui.share;ui.copied=false;","else if(name==='share'){ui.share=!ui.share;ui.copied=false;ui.mailNote='';")
# c. lien de contact du pied retiré
rep("""<a href="https://fwoptimisation.com/fwo-consultant-cro-contact/" target="_blank" rel="noopener">Contacter FWOptimisation</a><span class="logo">""","""<span class="logo">""")
# d. la démonstration ouvre directement les résultats (sauf si un test est déjà chargé : on garde l'écran de vérification)
rep("if(ui.draft){ui.draft.k=8;ui.draft.name='Exemple : 7 métriques';render();}return;}","if(ui.draft){ui.draft.k=8;ui.draft.name='Exemple : 7 métriques';if(!state.weeks.length){applyDraft();if(!ui.draft)ui.notice='Exemple chargé : 6 semaines sur 8 prévues, 7 métriques. Les chiffres sont fictifs.';}render();}return;}")
open(dst,'w',newline='').write(s);print(len(s))

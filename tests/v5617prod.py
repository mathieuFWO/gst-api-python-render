s=open('repo/calculateur-sequentiel-v56-16.html',newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(s.count(a),a[:110]); s=s.replace(a,b)
rep("VERSION='v56.16'","VERSION='v56.17'")
# 1. tableau de bord : le gain en vert léger, comme la pastille « Gain démontré » de l'écran de résultats
rep("#gst-app .dst.g{background:#0E7C5D;color:#fff;padding:3px 11px 3px 9px;border-radius:999px;align-items:center}#gst-app .dst.g i{background:#fff;transform:none}","#gst-app .dst.g{background:#DDF3EC;border:1px solid #8FD3BC;color:#0E7C5D;padding:2px 11px 2px 9px;border-radius:999px;align-items:center}#gst-app .dst.g i{background:#0E7C5D;transform:none}")
# 2. Piano : « Votre confidentialité » sous les deux champs de clé, avant « Mémoriser la clé ? »
a=s.index("""    +'</div><aside class="api-conf">""");b=s.index("</aside></div>';}",a)
aside=s[a+len("    +'</div>"):b]+"</aside>"
s=s[:a]+"    +'</div></div>';}"+s[b+len("</aside></div>';}"):]
P=NL+"""    +'<div class="api-f"><div><label for="gst-pak">"""
assert s.count(P)==1
i=s.index(P);j=s.index("""</div></div>'""",i)+len("</div></div>")
s=s[:j]+aside+s[j:]
rep("#gst-app .dec3{","#gst-app .apif .api-conf{margin-top:0}#gst-app .imp-d.wide .apiw{display:block}#gst-app .imp-d.wide .apif{max-width:760px}\n#gst-app .dec3{")
open('repo/calculateur-sequentiel-v56-17.html','w',newline='').write(s);print(len(s))

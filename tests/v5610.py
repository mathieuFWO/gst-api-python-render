src='repo/calculateur-sequentiel-v56-9.html';dst='repo/calculateur-sequentiel-v56-10.html'
s=open(src,newline='').read()
NL='\r\n' if '\r\n' in s else '\n'
def rep(a,b,n=1):
    global s
    a=a.replace('\n',NL);b=b.replace('\n',NL)
    assert s.count(a)==n,(s.count(a),a[:110]); s=s.replace(a,b)
rep("VERSION='v56.9'","VERSION='v56.10'")
# ===== tableau de bord resserré : décision en tête, avancement « 2/8 sem. » avec jauge, objectif sous le nom, corbeille =====
i=s.index("  h+='<div class=\"card dash\"><div class=\"dr dh\">");j=s.index("  return h;",i)
new=r"""  var rel=function(iso){var n=dayDiff(iso,todayISO());return !(n===n)?'':n<=0?'aujourd\'hui':n===1?'hier':n<7?'il y a '+n+' j':frDate(iso);},
    bin='<svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 4.5h11M6.5 4.5V3h3v1.5M4 4.5l.6 8.2a1 1 0 001 .8h4.8a1 1 0 001-.8l.6-8.2M6.6 7v4M9.4 7v4"/></svg>';
  h+='<div class="card dash"><div class="dr dh"><span>Test</span><span>Décision</span><span class="d-e">Écart</span><span>Avancement</span><span>Mis à jour</span><span></span></div>'
    +rows.map(function(t){var m=t.sum||{},st=dashStatus(t),u=m.u==='jour'?'j':'sem.',done=m.n?(m.dw!=null?m.dw+1:m.n):0,tone=st==='brouillon'?'d':m.c==='win'?'g':(m.c==='critical'||m.c==='stop')?'c':m.c==='discuss'?'a':'b',
        sub=[];if(m.m)sub.push(esc(m.m));if(t.mine&&rq[t.id])sub.push('<span class="tbadge" title="Mis à jour depuis Piano">Piano</span>');if(t.mine){if(t.shared&&t.shared.length)sub.push('partagé avec '+t.shared.length);}else sub.push('par '+esc(t.owner));
      return '<div class="dr" data-act="dashopen" data-v="'+t.id+'" tabindex="0" role="button"><span class="d-n"><b>'+esc(t.name)+'</b>'+(sub.length?'<span class="d-sub">'+sub.join(' · ')+'</span>':'')+'</span>'
        +'<span class="d-d"><span class="dst '+tone+'"><i></i>'+(st==='brouillon'?'Brouillon':esc(m.t||'En cours'))+'</span></span>'
        +'<span class="num d-e'+(tone==='g'||tone==='c'?' '+tone:'')+'">'+(typeof m.lift==='number'?pct(m.lift):'')+'</span>'
        +'<span class="d-a">'+(m.n&&m.k?'<span class="pbar'+(st==='fini'?' f':'')+'" aria-hidden="true"><i style="width:'+Math.round(Math.min(1,done/m.k)*100)+'%"></i></span><span class="num">'+done+'/'+m.k+' '+u+'</span>':'<span class="hint">À démarrer</span>')+'</span>'
        +'<span class="d-u">'+(t.updated?rel(t.updated):'')+'</span>'
        +'<span class="d-x">'+(t.mine?'<button type="button" class="ic" data-act="dashdel" data-v="'+t.id+'" aria-label="Supprimer le test '+esc(t.name)+'" title="Supprimer">'+bin+'</button>':'')+'</span></div>';}).join('')+'</div>'
    +'<p class="hint" style="margin-top:12px">Un clic sur une ligne ouvre le test. '+(ACC.who==='mes'?'Le partage se fait par invitation depuis le test.':'Ces tests sont en lecture seule.')+'</p>';
"""
s=s[:i]+new.replace('\n',NL)+s[j:]
# styles : anciennes règles de ligne remplacées
a=s.index("#gst-app .dash{margin-top:14px;padding:0;overflow:hidden}#gst-app .dr{");b=s.index(NL,s.index("#gst-app .dr>span{min-width:0;overflow-wrap:anywhere}"))
css="""#gst-app .dash{margin-top:14px;padding:0;overflow:hidden}#gst-app .dr{display:grid;grid-template-columns:minmax(0,1fr) minmax(150px,220px) 84px 150px 96px 32px;gap:0 18px;align-items:center;padding:11px 18px;border-top:1px solid var(--line);cursor:pointer;font-size:14px}
#gst-app .dr:first-child{border-top:0}#gst-app .dr.dh{cursor:default;padding-top:9px;padding-bottom:9px;font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--gray);background:#fff;border-bottom:1px solid var(--line)}#gst-app .dr.dh+.dr{border-top:0}#gst-app .dr:not(.dh):hover,#gst-app .dr:not(.dh):focus{background:#F8FBFA;outline:none}
#gst-app .dr>span{min-width:0;overflow-wrap:anywhere}#gst-app .d-n b{display:block;font-weight:600;line-height:1.35}#gst-app .d-sub{display:block;margin-top:2px;font-size:12px;color:var(--charcoal);line-height:1.5}#gst-app .d-sub .tbadge{margin-left:0}
#gst-app .dst{display:inline-flex;align-items:baseline;gap:8px;font-weight:600;font-size:13px;line-height:1.35}#gst-app .dst i{flex:none;width:8px;height:8px;border-radius:50%;background:var(--gray);transform:translateY(-1px)}#gst-app .dst.b i{background:var(--blue)}#gst-app .dst.g i{background:#028D6A}#gst-app .dst.g{color:#0E7C5D}#gst-app .dst.c i{background:var(--coral)}#gst-app .dst.c{color:#8f2c20}#gst-app .dst.a i{background:var(--amber)}#gst-app .dst.d{color:var(--charcoal);font-weight:400}
#gst-app .d-e{text-align:right;font-weight:600}#gst-app .d-e.g{color:#0E7C5D}#gst-app .d-e.c{color:#8f2c20}#gst-app .d-a{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--charcoal);white-space:nowrap}#gst-app .pbar{flex:none;width:56px;height:5px;border-radius:3px;background:var(--line);overflow:hidden}#gst-app .pbar i{display:block;height:100%;background:var(--blue);border-radius:3px}#gst-app .pbar.f i{background:var(--gray)}
#gst-app .d-u{font-size:13px;color:var(--charcoal);white-space:nowrap}#gst-app .d-x{text-align:right}#gst-app button.ic,#gst-app button.ic:focus{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;min-height:32px;padding:0;border:0;border-radius:6px;background:transparent;color:var(--gray)}#gst-app button.ic:hover{background:#FCF1EF;color:#8f2c20;border:0}#gst-app button.link.danger{color:#8f2c20}
#gst-app .apibar.slim .api-f{flex:2 1 320px}#gst-app .apibar.slim>span:first-of-type{flex:1 1 260px}"""
s=s[:a]+css.replace('\n',NL)+s[b:]
# mobile : trois lignes par test au lieu de sept
a=s.index("  #gst-app .dr.dh{display:none}#gst-app .dr{grid-template-columns:minmax(0,1fr) auto;gap:6px 12px;padding:14px 16px}");b=s.index("#gst-app .lg-l h2{font-size:24px}",a)
s=s[:a]+"  #gst-app .dr.dh{display:none}#gst-app .dr{grid-template-columns:minmax(0,1fr) auto;gap:6px 12px;padding:12px 14px}#gst-app .dr .d-n{grid-column:1;grid-row:1}#gst-app .dr .d-x{grid-column:2;grid-row:1;align-self:start;margin:-4px -6px 0 0}#gst-app .dr .d-d{grid-column:1;grid-row:2}#gst-app .dr .d-e{grid-column:2;grid-row:2}#gst-app .dr .d-a{grid-column:1;grid-row:3}#gst-app .dr .d-u{grid-column:2;grid-row:3;text-align:right}"+NL+"  "+s[b:]
rep("  return '<div class=\"apibar\"><span><b>'+pend.length+' test'","  return '<div class=\"apibar slim\"><span><b>'+pend.length+' test'")
open(dst,'w',newline='').write(s);print(len(s))

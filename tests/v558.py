src='repo/calculateur-sequentiel-v55-7.html';dst='repo/calculateur-sequentiel-v55-8.html'
s=open(src,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
rep("VERSION='v55.7'","VERSION='v55.8'")
rep("""'<button type="button" class="link lgd" data-act="legend" aria-expanded="'+!!ui.legend+'">Comment lire les statuts</button></div></div></div>';""","""'</div><p class="lgl"><button type="button" class="link lgd" data-act="legend" aria-expanded="'+!!ui.legend+'">Comment lire les statuts</button></p><!--lg--></div></div>';""")
a=s.index("""  if(ui.legend)h+='<div class="card legend" style="margin-top:8px">""");e=s.index("';",a)
seg=s[a:e]
assert "\n" not in seg
s=s[:a]+"""  if(ui.legend)h=h.replace('<!--lg-->','<div class="legend lgin">"""+seg[len("""  if(ui.legend)h+='<div class="card legend" style="margin-top:8px">"""):]+"');"+s[e+2:]
rep("#gst-app .tools.hx1{justify-content:flex-end}","#gst-app .tools.hx1{justify-content:flex-end}\n#gst-app .v-main p.lgl{margin:10px 0 0;font-size:13px}#gst-app button.link.lgd{margin-left:0}\n#gst-app .legend.lgin{margin-top:10px;padding:14px 16px;background:#fff;border:1px solid var(--border);border-radius:8px;font-size:13px;line-height:1.5}#gst-app .legend.lgin .pill{margin-right:6px}")
open(dst,'w',newline='').write(s);print(len(s))

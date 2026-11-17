import sys,difflib,json,hashlib,gzip,base64
a=open(sys.argv[1],newline='').read();b=open(sys.argv[2],newline='').read()
al=a.splitlines(True);bl=b.splitlines(True)
u16=lambda s:len(s.encode('utf-16-le'))//2
pos=[0]
for l in al:pos.append(pos[-1]+u16(l))
ops=[]
for tag,i1,i2,j1,j2 in difflib.SequenceMatcher(None,al,bl,autojunk=False).get_opcodes():
    if tag=='equal':continue
    old=''.join(al[i1:i2]);new=''.join(bl[j1:j2])
    # rogner préfixe/suffixe communs
    p=0
    while p<min(len(old),len(new)) and old[p]==new[p]:p+=1
    q=0
    while q<min(len(old),len(new))-p and old[-1-q]==new[-1-q]:q+=1
    o=old[p:len(old)-q];n=new[p:len(new)-q]
    ops.append([pos[i1]+u16(old[:p]),u16(o),n])
# vérif
r=a.encode('utf-16-le')
for p_,l_,t in reversed(ops):r=r[:p_*2]+t.encode('utf-16-le')+r[(p_+l_)*2:]
assert r.decode('utf-16-le')==b
j=json.dumps(ops,ensure_ascii=False,separators=(',',':'))
z=base64.b64encode(gzip.compress(j.encode('utf-8'),9)).decode()
open(sys.argv[3],'w').write(z)
print(len(ops),'ops',len(j),'json',len(z),'b64','sha_old',hashlib.sha256(a.encode()).hexdigest(),'sha_new',hashlib.sha256(b.encode()).hexdigest(),'len16',u16(a),u16(b))

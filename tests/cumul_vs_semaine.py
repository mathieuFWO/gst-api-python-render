# Vérification : cumul de visiteurs uniques depuis le 1er jour  vs  somme d'exports « par semaine »
# Test A/A (aucun effet réel) : on mesure le taux de faux positifs à 5 % bilatéral, et le biais sur le taux affiché.
import numpy as np
rng=np.random.default_rng(20261117)
def sim(N,weeks,p_ret,mean,conc,sims):
    rej_c=rej_s=0;infl=[];rate_c=[];rate_s=[]
    for _ in range(sims):
        res=[]
        for arm in range(2):
            first=rng.integers(0,weeks,N)                       # semaine d'arrivée
            act=np.zeros((N,weeks),bool)
            for w in range(weeks):
                act[:,w]=(first==w)|((first<w)&(rng.random(N)<p_ret))   # présent la semaine w
            prop=rng.beta(mean*conc,(1-mean)*conc,N)            # propension propre au visiteur
            did=act&(rng.random((N,weeks))<prop[:,None])        # a fait l'action cette semaine-là
            n_c=N;c_c=did.any(1).sum()                          # cumul : visiteurs uniques, visiteurs uniques ayant fait l'action
            n_s=act.sum();c_s=did.sum()                         # somme des semaines : un visiteur revenu compte plusieurs fois
            res.append((n_c,c_c,n_s,c_s))
        (na,ca,nsa,csa),(nb,cb,nsb,csb)=res
        def z(n1,c1,n2,c2):
            p=(c1+c2)/(n1+n2);return (c2/n2-c1/n1)/np.sqrt(p*(1-p)*(1/n1+1/n2))
        rej_c+=abs(z(na,ca,nb,cb))>1.96;rej_s+=abs(z(nsa,csa,nsb,csb))>1.96
        infl.append(nsa/na);rate_c.append(ca/na);rate_s.append(csa/nsa)
    return rej_c/sims,rej_s/sims,np.mean(infl),np.mean(rate_c),np.mean(rate_s)
S=4000
print('sims',S,'| 10 000 visiteurs par variation, 4 semaines')
for lab,p_ret,mean,conc in [('achat rare, peu de retours',0.15,0.05,2),('achat rare, retours fréquents',0.40,0.05,2),('action fréquente (fiche produit), retours fréquents',0.40,0.55,2),('rebond, retours fréquents',0.40,0.40,1)]:
    a,b,i,rc,rs=sim(10000,4,p_ret,mean,conc,S)
    print(f'{lab:52s} faux positifs cumul {a*100:4.1f} % | somme des semaines {b*100:4.1f} % | visiteurs gonflés x{i:.2f} | taux affiché {rc*100:.1f} % -> {rs*100:.1f} %')
print('marge d erreur sur 5 % avec',S,'simulations : +/-',round(196*np.sqrt(0.05*0.95/S),1),'point')

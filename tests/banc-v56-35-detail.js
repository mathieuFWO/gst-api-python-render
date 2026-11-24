// Banc v56-35 : dimensions à l'import, lecture globale, détail par dimension sous chaque métrique (« + »), date de fin proposée, structure inchangée repliée, montants.
const { chromium } = require('playwright'); const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-35.html'); const SHOTS=process.argv[3];
const res=[]; let fails=0; const ok=(n,c,i)=>{res.push((c?'✅ ':'❌ ')+n+(i!==undefined?' — '+JSON.stringify(i):''));if(!c)fails++;};
const R=[['Desktop','0Original',7326,541,'34 231,63 €'],['Desktop','2093615Variation 1',7240,526,'34 184,02 €'],['Mobile Phone','0Original',37900,1560,'75 298,50 €'],['Mobile Phone','2093615Variation 1',38119,1453,'72 292,98 €'],['Tablet','0Original',335,23,'1 264,53 €'],['Tablet','2093615Variation 1',289,11,'578,57 €']];
const mkcsv=(m,tot)=>'﻿Appareil - Type;MVT - Variante;Visiteurs;Visiteurs convertis;Visiteurs avec rebond;CA TTC (visites)\n'+R.map(r=>[r[0],r[1],Math.round(r[2]*m),Math.round(r[3]*m),Math.round(r[2]*m*0.4),r[4]].map(x=>'"'+x+'"').join(';')).join('\n')+(tot?'\n"Total (Tous les éléments)";"";90795;4099;36000;"217 418,75 €"':'')+'\n';
// deux dimensions croisées : appareil x source
const R2=[['Desktop','Direct','A',4000,300],['Desktop','SEO','A',3326,241],['Desktop','Direct','B',3900,290],['Desktop','SEO','B',3340,236],['Mobile','Direct','A',20000,800],['Mobile','SEO','A',17900,760],['Mobile','Direct','B',20100,750],['Mobile','SEO','B',18019,703]];
const csv2='Appareil;Source;Variation;Visiteurs;Achats\n'+R2.map(r=>r.join(';')).join('\n')+'\n';
const iso=d=>d.toISOString().slice(0,10),addD=(s,n)=>{const d=new Date(s+'T00:00:00Z');d.setUTCDate(d.getUTCDate()+n);return iso(d);};
(async()=>{ const b=await chromium.launch();
 const mk=async(vw)=>{const p=await b.newPage({viewport:{width:vw,height:900}});p.errs=[];p.on('pageerror',e=>p.errs.push(String(e)));p.on('dialog',d=>d.accept());
  await p.route('**/*',r=>r.request().url().startsWith('file://')?r.continue():r.fulfill({status:200,body:''}));await p.goto('file://'+path.resolve(FILE));await p.waitForTimeout(200);return p;};
 const setD=async(p,f,v)=>{await p.fill('[data-d='+f+']',v);await p.dispatchEvent('[data-d='+f+']','change');await p.waitForTimeout(250);};
 const tick=async p=>{await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()}));await p.waitForTimeout(250);};
 const st=p=>p.evaluate(()=>window.GST.getState());
 const errs=p=>p.evaluate(()=>[...document.querySelectorAll('#gst-app .err')].map(e=>e.textContent));
 const ov=p=>p.evaluate(()=>document.scrollingElement.scrollWidth-window.innerWidth);
 const clean=t=>t.replace(/ | /g,' ');
 for(const vw of [360,1280]){ const p=await mk(vw);const Y=await p.evaluate(()=>{const d=new Date();d.setDate(d.getDate()-1);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');});
  for(const tot of [false,true]){
   await p.evaluate(c=>window.GST.openCSV(c,'Test A_B Naizfit.csv'),mkcsv(1,tot));await p.waitForTimeout(300);
   const v=await p.evaluate(()=>({dims:[...document.querySelectorAll('#gst-app .dv-dc')].map(e=>e.textContent.replace(/\s+/g,' ').trim()),note:(document.querySelector('#gst-app p.dv-seg')||{}).textContent||'',read:[...document.querySelectorAll('#gst-app .dv-read')].map(e=>e.textContent).join(' '),na:[...document.querySelectorAll('#gst-app .dv-m.na')].map(e=>e.querySelector('.pill').textContent+'|'+e.querySelector('input').disabled+'|'+e.querySelector('.dv-na').textContent),mets:[...document.querySelectorAll('#gst-app .dv-m:not(.na)')].length}));
   ok(vw+(tot?' avec':' sans')+' ligne Total : dimensions listées (variations, segmentation avec 3 valeurs)',v.dims.length===2&&/MVT - Variante.*variations/.test(v.dims[0])&&/Appareil - Type.*segmentation · 3 valeurs/.test(v.dims[1])&&/au global/.test(v.note),v.dims);
   ok(vw+' : cumul lu = somme des trois appareils (45 561 et 45 648)',/45.561/.test(v.read)&&/45.648/.test(v.read),v.read);
   ok(vw+' : chiffre d\'affaires « Montant », non cochable, message sans renvoi à BigQuery',v.na.length===1&&/^Montant\|true\|/.test(v.na[0])&&/export agrégé/.test(v.na[0])&&!/BigQuery/.test(v.na[0])&&v.mets===2,v.na);
   ok(vw+' : import, aucun débordement horizontal',await ov(p)<=0);
  }
  // dates : hier par défaut, puis fin de première semaine dès que le début est saisi
  ok(vw+' : sans autre information, la date de fin proposée est hier',await p.inputValue('[data-d=endDate]')===Y,[await p.inputValue('[data-d=endDate]'),Y]);
  await setD(p,'startDate','2026-10-07');
  let g=await p.evaluate(()=>document.querySelector('#gst-app .dv-gate').textContent);
  ok(vw+' : début au 07/10 saisi : fin proposée au 13/10 (fin de première semaine), avec la mention',await p.inputValue('[data-d=endDate]')==='2026-10-13'&&/fin de la première semaine/.test(g)&&/semaine 1 sur/.test(g),g);
  { const near=addD(Y,-8);await setD(p,'startDate',near);ok(vw+' : test commencé il y a 9 jours : fin proposée = hier (suivi en direct)',await p.inputValue('[data-d=endDate]')===Y,[near,await p.inputValue('[data-d=endDate]')]);await setD(p,'startDate','2026-10-07'); }
  ok(vw+' : la date proposée reste à confirmer',await p.evaluate(()=>!!document.querySelector('#gst-app .dv-ck input[data-d=endOk]')&&!document.querySelector('#gst-app .dv-ck input[data-d=endOk]').checked));
  if(SHOTS)await p.screenshot({path:path.join(SHOTS,'import-'+vw+'.png'),fullPage:true});
  await tick(p);await p.click('[data-act=apply]');await p.waitForTimeout(700);
  let s=await st(p),e=await errs(p);const m=s.metrics[0]&&s.metrics[0].id,w=s.weeks[0];
  ok(vw+' : lecture globale : 45 561 / 2 124 et 45 648 / 1 990',e.length===0&&s.weeks.length===1&&w.A.n===45561&&w.A.m[m].c===2124&&w.B.n===45648&&w.B.m[m].c===1990&&s.metrics.length===2&&w.end==='2026-10-13',{e,A:w.A,B:w.B});
  ok(vw+' : détail gardé : 1 dimension, 3 valeurs triées par trafic',w.dims&&w.dims.length===1&&w.dims[0].n==='Appareil - Type'&&w.dims[0].v.map(x=>x.l).join()==='Mobile Phone,Desktop,Tablet'&&w.dims[0].v[0].A.m[m].c===1560&&!w.seg,w.dims&&w.dims[0].v.map(x=>[x.l,x.A.n]));
  ok(vw+' : la somme des valeurs redonne le global',w.dims[0].v.reduce((a,x)=>a+x.A.n,0)===w.A.n&&w.dims[0].v.reduce((a,x)=>a+x.B.m[m].c,0)===w.B.m[m].c);
  // résultats : un « + » par métrique, fermé par défaut
  let r=await p.evaluate(()=>({plus:[...document.querySelectorAll('#gst-app .sgl')].map(b=>b.textContent.trim()+'|'+b.getAttribute('aria-expanded')),h:(()=>{const b=document.querySelector('#gst-app .sgl'),a=getComputedStyle(b,'::after');return Math.round(b.getBoundingClientRect().height-2*parseFloat(a.top));})(),col:getComputedStyle(document.querySelector('#gst-app .mrw.sel .rsel')).borderTopColor,lcol:getComputedStyle(document.querySelector('#gst-app .sgl')).color,lbg:getComputedStyle(document.querySelector('#gst-app .sgl')).backgroundColor,puce:[...document.querySelectorAll('#gst-app .mrw:not(.hd):not(.sub)')].map(r=>!!r.querySelector('.rsel')&&!r.querySelector('svg.ic')&&(r.classList.contains('sel')?parseFloat(getComputedStyle(r.querySelector('.rsel')).borderTopWidth)>3:parseFloat(getComputedStyle(r.querySelector('.rsel')).borderTopWidth)<3)),nsel:document.querySelectorAll('#gst-app .mrw.sel').length,traj:document.querySelector('#gst-app .card.detail h3').textContent,trajPuce:!!document.querySelector('#gst-app .card.detail h3 .rsel'),sub:document.querySelectorAll('#gst-app .mrw.sub').length,old:!!document.querySelector('#gst-app [data-act=segtog]'),dec:document.querySelector('#gst-app .verdict').dataset.title,big:document.querySelector('#gst-app .tp-v').textContent,hit:0}));
  ok(vw+' : un lien gris « Segmenter » à côté du nom de chacune des 2 métriques, sans fond, détail fermé par défaut, zone de clic de 40 px au moins',r.plus.length===2&&r.plus.every(x=>x==='Segmenter|false')&&r.sub===0&&!r.old&&r.h>=40&&r.lcol==='rgb(111, 115, 116)'&&/rgba\(0, 0, 0, 0\)|transparent/.test(r.lbg),r);
  ok(vw+' : puce en début de chaque ligne, pleine et noire sur la seule ligne active, plus de pictogramme de statut ; pas de puce devant le titre du graphique',r.puce.length===2&&r.puce.every(Boolean)&&r.nsel===1&&!r.trajPuce&&r.col==='rgb(26, 29, 31)'&&/Trajectoire : Visiteurs convertis/.test(r.traj),r);
  { const other=s.metrics[1].id;await p.click('#gst-app .mrw[data-v="'+other+'"] .c-lift');await p.waitForTimeout(400);const t=await p.evaluate(()=>({sel:document.querySelector('#gst-app .mrw.sel').getAttribute('data-v'),traj:document.querySelector('#gst-app .card.detail h3').textContent,n:document.querySelectorAll('#gst-app .mrw.sel').length}));
    ok(vw+' : cliquer une autre ligne déplace la puce et change le graphique',t.sel===other&&t.n===1&&/Visiteurs avec rebond/.test(t.traj),t);await p.click('#gst-app .mrw[data-v="'+m+'"] .c-lift');await p.waitForTimeout(400); }
  const dec0=r.dec,big0=r.big;
  await p.click('#gst-app .sgl[data-v="'+m+'"]');await p.waitForTimeout(300);
  r=await p.evaluate(()=>({rows:[...document.querySelectorAll('#gst-app .mrw.sub')].map(x=>({n:x.querySelector('.mn').textContent,h:x.querySelector('.hint').textContent,a:x.querySelector('.c-a').textContent,b:x.querySelector('.c-b').textContent,l:x.querySelector('.lift').textContent,bar:!!x.querySelector('.c-ci rect'),act:x.getAttribute('data-act')})),head:document.querySelector('#gst-app .sgs-h').textContent,note:document.querySelector('#gst-app .sgs-n').textContent,pos:(()=>{const m=document.querySelector('#gst-app .mrw.sel')||document.querySelector('#gst-app .ml.prim .mrw:not(.hd)'),s=document.querySelector('#gst-app .sgs');return s.previousElementSibling===document.querySelector('#gst-app .ml.prim .mrw:not(.hd):not(.sub)');})(),dec:document.querySelector('#gst-app .verdict').dataset.title,big:document.querySelector('#gst-app .tp-v').textContent,exp:document.querySelector('#gst-app .sgl').getAttribute('aria-expanded'),lab:document.querySelector('#gst-app .sgl').textContent.trim(),selKept:document.querySelector('#gst-app .mrw.sel').getAttribute('data-v'),sel:!!document.querySelector('#gst-app [data-act=segdim]')}));
  const lift=(a,b)=>{const v=(b[1]/b[0])/(a[1]/a[0])-1,x=Math.round(v*1e4)/100;return (x>0?'+':'')+x.toLocaleString('fr-FR',{minimumFractionDigits:2,maximumFractionDigits:2})+' %';};
  const exp=[['Mobile Phone',[37900,1560],[38119,1453]],['Desktop',[7326,541],[7240,526]],['Tablet',[335,23],[289,11]]];
  ok(vw+' : au clic, 3 lignes sous la métrique, dans le même tableau, non cliquables',r.rows.length===3&&r.rows.map(x=>x.n).join()==='Mobile Phone,Desktop,Tablet'&&r.pos&&r.rows.every(x=>!x.act&&x.bar)&&r.exp==='true'&&/^Masquer/.test(r.lab)&&r.selKept===m&&!r.sel,r.rows.map(x=>x.n));
  ok(vw+' : écarts par appareil justes (recalculés à part)',exp.every((x,i)=>clean(r.rows[i].l)===clean(lift(x[1],x[2]))),{vus:r.rows.map(x=>x.l),attendus:exp.map(x=>lift(x[1],x[2]))});
  ok(vw+' : taux, trafic et part affichés (Mobile Phone : 4,12 % et 3,81 %, 76 019 visiteurs, 83,3 %)',/4,12 %/.test(r.rows[0].a)&&/3,81 %/.test(r.rows[0].b)&&/76 019 visiteurs · 83,3 %/.test(clean(r.rows[0].h)),r.rows[0]);
  ok(vw+' : mention « Exploratoire » ; décision et écart principal inchangés',/exploratoire/.test(r.head)&&/Appareil - Type/.test(r.head)&&/non corrigés/.test(r.note)&&r.dec===dec0&&r.big===big0,r.head);
  ok(vw+' : résultats ouverts, aucun débordement horizontal',await ov(p)<=0,await ov(p));
  if(SHOTS)await p.screenshot({path:path.join(SHOTS,'resultats-'+vw+'.png'),fullPage:true});
  await p.click('#gst-app .sgl[data-v="'+s.metrics[1].id+'"]');await p.waitForTimeout(300);
  r=await p.evaluate(()=>({n:document.querySelectorAll('#gst-app .sgs').length,sub:document.querySelectorAll('#gst-app .mrw.sub').length,a:[...document.querySelectorAll('#gst-app .sgs')][1].querySelector('.c-a').textContent}));
  ok(vw+' : deux métriques détaillées en même temps (rebond : 40,00 %)',r.n===2&&r.sub===6&&/40,00 %/.test(r.a),r);
  await p.click('#gst-app .sgl[data-v="'+m+'"]');await p.waitForTimeout(300);ok(vw+' : un second clic referme le détail',await p.evaluate(()=>document.querySelectorAll('#gst-app .sgs').length)===1);
  // semaine 2 : même fichier grossi -> date à J+7, structure repliée
  await p.evaluate(c=>window.GST.openCSV(c,'s2.csv'),mkcsv(2,false));await p.waitForTimeout(300);
  r=await p.evaluate(()=>({end:document.querySelector('[data-d=endDate]').value,gate:document.querySelector('#gst-app .dv-gate').textContent,same:(document.querySelector('#gst-app .dv-same')||{}).textContent||'',sec:[...document.querySelectorAll('#gst-app .dv-sec .kicker')].map(x=>x.textContent),dims:document.querySelectorAll('#gst-app .dv-dc').length,warn:document.querySelectorAll('#gst-app .dv-warn,#gst-app .err').length,link:(document.querySelector('#gst-app [data-act=dvfull]')||{getBoundingClientRect:()=>({height:0})}).getBoundingClientRect().height}));
  ok(vw+' : lecture suivante : fin proposée 7 jours après la précédente (20/10), et non hier',r.end==='2026-10-20'&&/7 jours après la lecture précédente \(13\/10\/2026\)/.test(r.gate)&&/semaine 2 sur/.test(r.gate),r.gate);
  ok(vw+' : même structure : sections 2 et 3 repliées en une ligne, aucune alerte, lien « Voir le détail » de 44 px',/Même structure que la lecture précédente/.test(r.same)&&/2 métriques retrouvés/.test(r.same)&&/Appareil - Type/.test(r.same)&&/91.122/.test(r.same)&&r.sec.length===1&&r.dims===0&&r.warn===0&&r.link>=44,r);
  ok(vw+' : lecture suivante, aucun débordement horizontal',await ov(p)<=0);
  if(SHOTS)await p.screenshot({path:path.join(SHOTS,'suite-'+vw+'.png'),fullPage:true});
  await p.click('#gst-app [data-act=dvfull]');await p.waitForTimeout(300);
  ok(vw+' : « Voir le détail » rouvre les sections 2 et 3',await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-sec .kicker').length)===3&&await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-dc').length)===2);
  await tick(p);await p.click('[data-act=apply]');await p.waitForTimeout(700);
  s=await st(p);ok(vw+' : la semaine 2 est acceptée, avec son détail et sa date',s.weeks.length===2&&s.weeks[1].A.n===91122&&s.weeks[1].dims[0].v[0].A.n===75800&&s.weeks[1].end==='2026-10-20',s.weeks.map(x=>[x.A.n,x.end]));
  // semaine 3 : colonne renommée -> structure différente, sections affichées
  await p.evaluate(c=>window.GST.openCSV(c,'s3.csv'),'MVT - Variante;Visiteurs;Visiteurs convertis;Visiteurs avec rebond\n0Original;136000;6300;54000\n2093615Variation 1;136900;5900;54500\n');await p.waitForTimeout(300);
  r=await p.evaluate(()=>({end:document.querySelector('[data-d=endDate]').value,same:!!document.querySelector('#gst-app .dv-same'),sec:document.querySelectorAll('#gst-app .dv-sec .kicker').length}));
  ok(vw+' : fichier sans la dimension : la structure a changé, les sections restent affichées ; fin proposée au 27/10',!r.same&&r.sec===3&&r.end==='2026-10-27',r);
  await tick(p);await p.click('[data-act=apply]');await p.waitForTimeout(700);s=await st(p);
  await p.selectOption('#gst-app [data-act=weeksel]','2');await p.waitForTimeout(300);
  ok(vw+' : cette lecture est acceptée au global, sans « + » quand on la relit',s.weeks.length===3&&!s.weeks[2].dims&&await p.evaluate(()=>document.querySelectorAll('#gst-app .sgl').length)===0,s.weeks.length);
  ok(vw+' : aucune erreur de script',p.errs.length===0,p.errs);await p.close();
  // deux dimensions croisées
  const q=await mk(vw);await q.evaluate(c=>window.GST.openCSV(c,'croise.csv'),csv2);await q.waitForTimeout(300);
  r=await q.evaluate(()=>[...document.querySelectorAll('#gst-app .dv-dc.seg')].map(e=>e.textContent.replace(/\s+/g,' ').trim()));
  ok(vw+' : deux dimensions croisées : toutes deux listées',r.length===2&&/Appareil.*2 valeurs/.test(r[0])&&/Source.*2 valeurs/.test(r[1]),r);
  await setD(q,'startDate','2026-10-07');await tick(q);await q.click('[data-act=apply]');await q.waitForTimeout(700);
  s=await st(q);const w2=s.weeks[0],m2=s.metrics[0].id;
  ok(vw+' : global = somme de toutes les lignes (45 226 / 2 101) ; marges par dimension justes',w2&&w2.A.n===45226&&w2.A.m[m2].c===2101&&w2.dims.length===2&&w2.dims[0].v.find(x=>x.l==='Desktop').A.n===7326&&w2.dims[1].v.find(x=>x.l==='SEO').B.n===21359&&w2.dims[1].v.find(x=>x.l==='SEO').B.m[m2].c===939,w2&&w2.dims.map(d=>d.v.map(x=>[x.l,x.A.n,x.B.n])));
  await q.click('#gst-app .sgl');await q.waitForTimeout(300);
  r=await q.evaluate(()=>({opts:[...document.querySelectorAll('#gst-app .sgt')].map(o=>o.textContent+(o.classList.contains('on')?'*':'')),rows:[...document.querySelectorAll('#gst-app .mrw.sub .mn')].map(x=>x.textContent)}));
  ok(vw+' : choix de la dimension dans le détail (Appareil par défaut)',r.opts.join()==='Appareil*,Source'&&r.rows.join()==='Mobile,Desktop',r);
  await q.click('#gst-app .sgt:not(.on)');await q.waitForTimeout(300);
  r=await q.evaluate(()=>[...document.querySelectorAll('#gst-app .mrw.sub')].map(x=>x.querySelector('.mn').textContent+' '+x.querySelector('.lift').textContent));
  ok(vw+' : passage à « Source » : Direct et SEO, écarts recalculés à part',r.length===2&&clean(r[0])===clean('Direct '+lift([24000,1100],[24000,1040]))&&clean(r[1])===clean('SEO '+lift([21226,1001],[21359,939])),r);
  ok(vw+' : deux dimensions, aucun débordement ni erreur',await ov(q)<=0&&q.errs.length===0,q.errs);
  // ancien format (v56-28/29 : seg + map.sc) relu comme une dimension
  const leg=await q.evaluate(()=>{const s=JSON.parse(JSON.stringify(window.GST.getState()));const k=Object.keys(localStorage).find(x=>/^gstSeq_v40_/.test(x));return k||'';});
  await q.close();
  // refus conservés
  const z=await mk(vw);await z.evaluate(c=>window.GST.openCSV(c,'dbl.csv'),'MVT - Variante;Visiteurs;Visiteurs convertis\n0Original;100;10\n0Original;200;20\nVariation 1;300;30\nVariation 1;310;31\n');await z.waitForTimeout(300);
  await setD(z,'startDate','2026-10-07');await tick(z);await z.click('[data-act=apply]');await z.waitForTimeout(400);
  e=await errs(z);s=await st(z);ok(vw+' : doublons sans colonne de texte : toujours refusés, jamais additionnés',s.weeks.length===0&&e.some(x=>/2 ligne\(s\)/.test(x)&&/variation seule/.test(x)),e);
  await z.evaluate(c=>window.GST.openCSV(c,'rep.csv'),'Appareil;MVT - Variante;Visiteurs;Visiteurs convertis\nDesktop;0Original;100;10\nDesktop;0Original;200;20\nDesktop;Variation 1;300;30\nDesktop;Variation 1;310;31\n');await z.waitForTimeout(300);
  await setD(z,'startDate','2026-10-07');await tick(z);await z.click('[data-act=apply]');await z.waitForTimeout(400);
  e=await errs(z);s=await st(z);ok(vw+' : même combinaison répétée : refusé, jamais additionné',s.weeks.length===0&&e.some(x=>/2 ligne\(s\)/.test(x)),e);
  await z.evaluate(c=>window.GST.openCSV(c,'simple.csv'),'MVT - Variante;Visiteurs;Visiteurs convertis;Pages vues\n0Original;45561;2124;130000\n2093615Variation 1;45648;1990;131000\n');await z.waitForTimeout(300);
  const sv=await z.evaluate(()=>({seg:document.querySelectorAll('#gst-app .dv-dc.seg').length,note:!!document.querySelector('#gst-app p.dv-seg'),na:[...document.querySelectorAll('#gst-app .dv-m.na .pill')].map(x=>x.textContent)}));
  ok(vw+' : fichier simple : aucune dimension de segmentation ; « Pages vues » marqué « Volume »',!sv.seg&&!sv.note&&sv.na.join()==='Volume',sv);
  ok(vw+' : aucune erreur de script (2)',z.errs.length===0,z.errs);await z.close();
 }
 console.log(res.join('\n'));console.log(fails?`❌ ${fails} échec(s) sur ${res.length}`:`✅ ${res.length}/${res.length}`);await b.close();process.exit(fails?1:0);})();

// Banc v56-29 : export détaillé par une autre colonne (appareil) : lecture globale, détail au clic ; montants et volumes non analysables.
const { chromium } = require('playwright'); const path=require('path');
const FILE=process.argv[2]||path.join(__dirname,'..','calculateur-sequentiel-v56-29.html'); const SHOTS=process.argv[3];
const res=[]; let fails=0; const ok=(n,c,i)=>{res.push((c?'✅ ':'❌ ')+n+(i!==undefined?' — '+JSON.stringify(i):''));if(!c)fails++;};
const rows=(m)=>[['Desktop','0Original',7326,541,'34 231,63 €'],['Desktop','2093615Variation 1',7240,526,'34 184,02 €'],['Mobile Phone','0Original',37900,1560,'75 298,50 €'],['Mobile Phone','2093615Variation 1',38119,1453,'72 292,98 €'],['Tablet','0Original',335,23,'1 264,53 €'],['Tablet','2093615Variation 1',289,11,'578,57 €']].map(r=>[r[0],r[1],Math.round(r[2]*m),Math.round(r[3]*m),Math.round(r[2]*m*0.4),r[4]]);
const mkcsv=(m,tot)=>'﻿Appareil - Type;MVT - Variante;Visiteurs;Visiteurs convertis;Visiteurs avec rebond;CA TTC (visites)\n'+rows(m).map(r=>r.map(x=>'"'+x+'"').join(';')).join('\n')+(tot?'\n"Total (Tous les éléments)";"";90795;4099;36000;"217 418,75 €"':'')+'\n';
(async()=>{ const b=await chromium.launch();
 const mk=async(vw)=>{const p=await b.newPage({viewport:{width:vw,height:900}});p.errs=[];p.on('pageerror',e=>p.errs.push(String(e)));p.on('dialog',d=>d.accept());
  await p.route('**/*',r=>r.request().url().startsWith('file://')?r.continue():r.fulfill({status:200,body:''}));await p.goto('file://'+path.resolve(FILE));await p.waitForTimeout(200);return p;};
 const setD=async(p,f,v)=>{await p.fill('[data-d='+f+']',v);await p.dispatchEvent('[data-d='+f+']','change');await p.waitForTimeout(250);};
 const tick=async p=>{await p.evaluate(()=>document.querySelectorAll('#gst-app .dv-ck input').forEach(x=>{if(!x.checked)x.click()}));await p.waitForTimeout(250);};
 const st=p=>p.evaluate(()=>window.GST.getState());
 const errs=p=>p.evaluate(()=>[...document.querySelectorAll('#gst-app .err')].map(e=>e.textContent));
 const ov=p=>p.evaluate(()=>document.scrollingElement.scrollWidth-window.innerWidth);
 for(const vw of [360,1280]){ const p=await mk(vw);
  for(const tot of [false,true]){
   await p.evaluate(c=>window.GST.openCSV(c,'Test A_B Naizfit.csv'),mkcsv(1,tot));await p.waitForTimeout(300);
   const v=await p.evaluate(()=>({seg:(document.querySelector('#gst-app .dv-seg')||{}).textContent||'',sel:!!document.querySelector('#gst-dsg'),read:[...document.querySelectorAll('#gst-app .dv-read')].map(e=>e.textContent).join(' '),na:[...document.querySelectorAll('#gst-app .dv-m.na')].map(e=>e.querySelector('.pill').textContent+'|'+e.querySelector('input').disabled),mets:[...document.querySelectorAll('#gst-app .dv-m:not(.na)')].length}));
   ok(vw+(tot?' avec':' sans')+' ligne Total : le détail par appareil est reconnu et annoncé, sans choix à faire',/Appareil - Type/.test(v.seg)&&/Desktop, Mobile Phone, Tablet/.test(v.seg)&&/au global/.test(v.seg)&&!v.sel,v.seg);
   ok(vw+' : cumul lu = somme des trois appareils (45 561 et 45 648)',/45.561/.test(v.read)&&/45.648/.test(v.read),v.read);
   ok(vw+' : le chiffre d\'affaires est marqué « Montant », non cochable ; deux métriques proposées',v.na.length===1&&v.na[0]==='Montant|true'&&v.mets===2,v);
   ok(vw+' : import, aucun débordement horizontal',await ov(p)<=0);
   if(SHOTS&&!tot)await p.screenshot({path:path.join(SHOTS,'detail-'+vw+'.png'),fullPage:true});
  }
  await setD(p,'startDate','2026-10-07');await setD(p,'endDate','2026-10-13');await tick(p);await p.click('[data-act=apply]');await p.waitForTimeout(700);
  let s=await st(p),e=await errs(p);const m=s.metrics[0]&&s.metrics[0].id,w=s.weeks[0];
  ok(vw+' : lecture globale : 45 561 / 2 124 et 45 648 / 1 990',e.length===0&&s.weeks.length===1&&w.A.n===45561&&w.A.m[m].c===2124&&w.B.n===45648&&w.B.m[m].c===1990&&s.metrics.length===2&&s.labels.A==='Original',{e,A:w.A,B:w.B});
  ok(vw+' : détail gardé : 3 valeurs triées par trafic, colonne mémorisée',w.seg&&w.seg.map(x=>x.l).join()==='Mobile Phone,Desktop,Tablet'&&w.seg[0].A.n===37900&&w.seg[0].A.m[m].c===1560&&w.seg[2].B.m[m].c===11&&s.map.sc==='Appareil - Type',w.seg&&w.seg.map(x=>[x.l,x.A.n,x.B.n]));
  const sumOK=w.seg.reduce((a,x)=>a+x.A.n,0)===w.A.n&&w.seg.reduce((a,x)=>a+x.B.m[m].c,0)===w.B.m[m].c;ok(vw+' : la somme des valeurs redonne le global',sumOK);
  // résultats : fermé par défaut, ouvert au clic
  let r=await p.evaluate(()=>({btn:(document.querySelector('#gst-app [data-act=segtog]')||{}).textContent||'',open:!!document.querySelector('#gst-app .sgx-t'),h:(document.querySelector('#gst-app [data-act=segtog]')||{getBoundingClientRect:()=>({height:0})}).getBoundingClientRect().height,dec:document.querySelector('#gst-app .verdict').dataset.title,big:document.querySelector('#gst-app .tp-v').textContent}));
  ok(vw+' : résultats : bouton « Segmenter par « Appareil - Type » », détail fermé par défaut, cible de 44 px',/Segmenter par « Appareil - Type »/.test(r.btn)&&!r.open&&r.h>=44,r);
  const dec0=r.dec,big0=r.big;
  await p.click('#gst-app [data-act=segtog]');await p.waitForTimeout(300);
  r=await p.evaluate(()=>({rows:[...document.querySelectorAll('#gst-app .sgx-r:not(.hd)')].map(x=>[...x.children].map(c=>c.textContent.replace(/\s+/g,' ').trim())),note:(document.querySelector('#gst-app .sgx>p.hint')||{}).textContent||'',sel:[...document.querySelectorAll('#gst-app [data-act=segmet] option')].map(o=>o.textContent),dec:document.querySelector('#gst-app .verdict').dataset.title,big:document.querySelector('#gst-app .tp-v').textContent,btn:document.querySelector('#gst-app [data-act=segtog]').textContent}));
  // attendus calculés à part : écart relatif = (cB/nB)/(cA/nA)-1
  const lift=(a,b)=>{const v=(b[1]/b[0])/(a[1]/a[0])-1,x=Math.round(v*1e4)/100;return (x>0?'+':'')+x.toLocaleString('fr-FR',{minimumFractionDigits:2,maximumFractionDigits:2})+' %';};
  const exp=[['Global',[45561,2124],[45648,1990]],['Mobile Phone',[37900,1560],[38119,1453]],['Desktop',[7326,541],[7240,526]],['Tablet',[335,23],[289,11]]];
  ok(vw+' : au clic, 4 lignes : Global puis les trois appareils',r.rows.length===4&&r.rows.map(x=>x[0].split(/\d/)[0].trim()).join()==='Global,Mobile Phone,Desktop,Tablet',r.rows.map(x=>x[0]));
  ok(vw+' : écarts par appareil justes (recalculés à part)',exp.every((x,i)=>r.rows[i]&&r.rows[i][2].replace(/ | /g,' ').indexOf(lift(x[1],x[2]).replace(/ | /g,' '))===0),{vus:r.rows.map(x=>x[2]),attendus:exp.map(x=>lift(x[1],x[2]))});
  ok(vw+' : l\'écart global du détail est celui du bandeau',r.rows[0][2].replace(/\s/g,'').indexOf(big0.replace(/\s/g,''))===0,[r.rows[0][2],big0]);
  ok(vw+' : mention « Lecture exploratoire » ; la décision et l\'écart principal ne bougent pas',/Lecture exploratoire/.test(r.note)&&/sans correction/.test(r.note)&&r.dec===dec0&&r.big===big0&&/Masquer/.test(r.btn),r.note);
  ok(vw+' : taux et parts affichés (Mobile Phone : 4,12 % → 3,81 %, 83,3 % du trafic)',/4,12 % → 3,81 %/.test(r.rows[1][1])&&/83,3 %/.test(r.rows[1][0])&&/76 019/.test(r.rows[1][0].replace(/ | /g,' ')),r.rows[1]);
  ok(vw+' : volume très faible signalé ? non pour Tablet (11 conversions)',!/volume très faible/.test(r.rows[3][2]),r.rows[3]);
  ok(vw+' : résultats ouverts, aucun débordement horizontal',await ov(p)<=0,await ov(p));
  if(SHOTS){const el=await p.$('#gst-app .sgx');await el.screenshot({path:path.join(SHOTS,'segmenter-'+vw+'.png')});await p.screenshot({path:path.join(SHOTS,'resultats-'+vw+'.png'),fullPage:true});}
  await p.selectOption('#gst-app [data-act=segmet]',{index:1});await p.waitForTimeout(300);
  r=await p.evaluate(()=>({hd:(document.querySelector('#gst-app .sgx-r.hd')||{}).textContent||'',row:document.querySelectorAll('#gst-app .sgx-r:not(.hd)')[1].children[1].textContent,foc:document.activeElement&&document.activeElement.getAttribute('data-act')}));
  ok(vw+' : changement de métrique dans le détail (rebond : 40,00 %)',/40,00 %/.test(r.row),r);
  // semaine 2 : même colonne
  await p.evaluate(c=>window.GST.openCSV(c,'s2.csv'),mkcsv(2,false));await p.waitForTimeout(300);await setD(p,'endDate','2026-10-20');await tick(p);await p.click('[data-act=apply]');await p.waitForTimeout(700);
  s=await st(p);ok(vw+' : la semaine 2 est acceptée, avec son détail',s.weeks.length===2&&s.weeks[1].A.n===91122&&s.weeks[1].seg&&s.weeks[1].seg[0].A.n===75800,s.weeks.map(x=>x.A.n));
  // semaine 3 : fichier sans la colonne -> global accepté, pas de détail pour cette lecture
  await p.evaluate(c=>window.GST.openCSV(c,'s3.csv'),'MVT - Variante;Visiteurs;Visiteurs convertis;Visiteurs avec rebond\n0Original;136000;6300;54000\n2093615Variation 1;136900;5900;54500\n');await p.waitForTimeout(300);await setD(p,'endDate','2026-10-27');await tick(p);await p.click('[data-act=apply]');await p.waitForTimeout(700);
  s=await st(p);e=await errs(p);await p.selectOption('#gst-app [data-act=weeksel]','2');await p.waitForTimeout(300);const hasBtn=await p.evaluate(()=>!!document.querySelector('#gst-app [data-act=segtog]'));
  ok(vw+' : une lecture sans la colonne reste possible ; pas de bouton quand on relit cette lecture',s.weeks.length===3&&!s.weeks[2].seg&&!hasBtn,{e,n:s.weeks.length,hasBtn});
  // le détail survit à un enregistrement / rechargement (nettoyage de l'état)
  const kept=await p.evaluate(()=>{const s=window.GST.getState();const c=JSON.parse(JSON.stringify(s));c.weeks[0].seg.push({l:'<b>x</b>'.repeat(30),A:{n:'a',m:{zzz:{c:1}}},B:null});return typeof window.GST.cleanState==='function'?window.GST.cleanState(c).weeks[0].seg.map(x=>x.l.length+':'+Object.keys(x.A.m).length):null;});
  if(kept)ok(vw+' : nettoyage de l\'état : libellés bornés à 60 caractères, métriques inconnues écartées',kept.length===4&&kept[3]==='60:0',kept);
  ok(vw+' : aucune erreur de script',p.errs.length===0,p.errs);await p.close();
  // fichiers sans détail, doublons sans colonne de texte, volume
  const q=await mk(vw);await q.evaluate(c=>window.GST.openCSV(c,'simple.csv'),'MVT - Variante;Visiteurs;Visiteurs convertis;Pages vues\n0Original;45561;2124;130000\n2093615Variation 1;45648;1990;131000\n');await q.waitForTimeout(300);
  const sv=await q.evaluate(()=>({seg:!!document.querySelector('#gst-app .dv-seg'),na:[...document.querySelectorAll('#gst-app .dv-m.na .pill')].map(x=>x.textContent)}));
  ok(vw+' : fichier simple : pas d\'annonce de détail ; « Pages vues » marqué « Volume »',!sv.seg&&sv.na.join()==='Volume',sv);
  await setD(q,'startDate','2026-10-07');await setD(q,'endDate','2026-10-13');await tick(q);await q.click('[data-act=apply]');await q.waitForTimeout(700);
  s=await st(q);ok(vw+' : fichier simple : import inchangé, pas de bouton « Segmenter »',s.weeks.length===1&&!s.weeks[0].seg&&!(await q.$('#gst-app [data-act=segtog]')),s.weeks.length);await q.close();
  const z=await mk(vw);await z.evaluate(c=>window.GST.openCSV(c,'dbl.csv'),'MVT - Variante;Visiteurs;Visiteurs convertis\n0Original;100;10\n0Original;200;20\nVariation 1;300;30\nVariation 1;310;31\n');await z.waitForTimeout(300);
  await setD(z,'startDate','2026-10-07');await setD(z,'endDate','2026-10-13');await tick(z);await z.click('[data-act=apply]');await z.waitForTimeout(400);
  e=await errs(z);s=await st(z);ok(vw+' : doublons sans colonne de texte : toujours refusés, jamais additionnés',s.weeks.length===0&&e.some(x=>/2 ligne\(s\)/.test(x)&&/variation seule/.test(x)),e);
  // même valeur répétée dans la colonne de texte (autre dimension cachée) : refus
  await z.evaluate(c=>window.GST.openCSV(c,'rep.csv'),'Appareil;MVT - Variante;Visiteurs;Visiteurs convertis\nDesktop;0Original;100;10\nDesktop;0Original;200;20\nDesktop;Variation 1;300;30\nDesktop;Variation 1;310;31\n');await z.waitForTimeout(300);
  await setD(z,'startDate','2026-10-07');await setD(z,'endDate','2026-10-13');await tick(z);await z.click('[data-act=apply]');await z.waitForTimeout(400);
  e=await errs(z);s=await st(z);ok(vw+' : valeur répétée dans la colonne de texte : refusé, jamais additionné',s.weeks.length===0&&e.some(x=>/2 ligne\(s\)/.test(x)),e);
  ok(vw+' : aucune erreur de script (2)',z.errs.length===0,z.errs);await z.close();
 }
 console.log(res.join('\n'));console.log(fails?`❌ ${fails} échec(s) sur ${res.length}`:`✅ ${res.length}/${res.length}`);await b.close();process.exit(fails?1:0);})();

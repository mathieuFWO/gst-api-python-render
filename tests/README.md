# Bancs de test du front (v39.1)

Chargent le **vrai** `calculateur-sequentiel.html` dans Chromium (Playwright). Les CDN (jStat, Highcharts,
jQuery) sont simulés ; l'API est rejouée à partir des **bornes relevées sur la prod le 15/11/2026**
(k=8, α=0,05, KimDeMets/HSD(−2), testType 3, β=0,20 et 0,10), le Z observé étant recalculé par la
formule de l'API (contrôlée au démarrage contre la valeur prod 1,9196).

```
node tests/banc-front.js calculateur-sequentiel.html        # 27 contrôles
node tests/banc-superiorite.js calculateur-sequentiel.html  # mode Supériorité, Z<0
```
Référence : v39.1 = 27/27 ; v39.0 = 12/27 (le banc rougit sur chaque défaut corrigé).
Non couvert : autres α, O'Brien-Fleming, Pocock (correctif R non testable sans R), rendu réel Highcharts.

# VALIDATION V1 — Phase 1 (sémantique de décision v39.0)

- **Date** : 2026-07-05
- **Fichier** : `calculateur-sequentiel.html` (front, v38.22 → **v39.0**)
- **API** : **non touchée** (Phase 1 front-only).
- **Méthode** : harness headless Node qui extrait le **vrai** bloc de décision et les
  **vraies** fonctions du fichier (pas une copie) et rejoue les scénarios.
  Scripts : `/tmp/v1_harness.mjs`, `/tmp/v1d_harness.mjs`.

## Principe « seuil paramétré nommé » appliqué à la validation
Chaque scénario **fige explicitement la marge de non-régression** `niMarginRel` utilisée.
Un « ça passe » n'est reproductible que si la marge est nommée.

## Résultats

| Scénario | Marge NI figée | Attendu | Résultat |
|---|---|---|---|
| **V1.a** guardrail positif non significatif, dernière étape (principal POSITIF, z_séc=+0.5, zNi=0.8) | **1,0 %** | PAS régression/négatif → `AUCUN_SIGNAL`, classe `decision-discuss` | ✅ `guardState=AUCUN_SIGNAL`, non critique, aucun texte « Régression démontrée » |
| **V1.a′** même cas, marge élargie (zNi=2.3 ≥ effB) | **5,0 %** | `SECURITE_DEMONTREE` → `decision-stop-win` | ✅ |
| **V1.b** principal en futilité avec lift positif (z=+0.7 ≤ futB=+0.9, effB=2.0, stage 3/4) | n/a (pas de guardrail) | `FUTILE` → #5 « NON CONCLUANT », **pas** « négatif » | ✅ `principalState=FUTILE`, texte « NON CONCLUANT »+« futilité », sans « négatif démontré » |
| **V1.c** principal massivement négatif (z=−3.0 ≤ −effB=−2.0) | n/a | `NEGATIF_DEMONTRE` → #4 « Effet négatif démontré » | ✅ |
| **#1** régression écrase principal positif (z_séc=−2.5 ≤ −effB) | 1,0 % | `decision-stop-critical` | ✅ |
| **#2** principal positif seul (sans guardrail) | n/a | `decision-stop-win` | ✅ |
| **#6** principal neutre, étape < K | n/a | `decision-continue` | ✅ |
| **V1.d** rechargement test **v38** (ni `niMarginRel`, ni `observedZNiSecondary`) | défaut **1,0 %** | défauts G4 + **replay** de `observedZNiSecondary` depuis les données cumulées | ✅ reconstruit `[1.1364, 1.6071, 1.9683]` ; sans replay → tableau vide (régression silencieuse démontrée puis évitée) |
| **V1.d′** parité formule NI vs calcul manuel (S2) | 1,0 % | identiques | ✅ |

**Total : 17 assertions, 17 OK, 0 KO** (12 logique de décision + 5 rétrocompat/formule).

## V1.e — canoniques inchangés
**Trivialement vrai par construction** : la Phase 1 ne modifie **que** le front, l'API et le
script R des bornes ne sont pas touchés par ce lot. → **À confirmer sur sortie prod** une
fois `phase0-collect.sh` exécuté (diff des champs existants = 0, cf. `reference/README.md`).

## Points optionnels / nuances consignées
- **Ligne pointillée −efficacyZ sur le graphique principal** (§4.5, optionnel) : **reportée**
  pour ce lot (non bloquante, pas un critère de sortie de Phase 1). Les états de décision et
  la coloration du tableau lift portent déjà la sémantique de nocivité miroir.
- **Coloration du mini-graphique lift (sécurité)** : `indicatorIsPositive` reflète désormais
  `SECURITE_DEMONTREE` (Z de non-infériorité ≥ borne) et `indicatorIsNegative` la régression
  miroir (`z ≤ −effB`). Le gate visuel existant `data.lift > 0.01 / < −0.01` est conservé
  (évite une flèche verte sur un lift franchement négatif) → **à confirmer visuellement** en
  recette manuelle sur la page.
- `INDICATOR_STATE` (ancienne enum) devient une constante morte inoffensive ; les sélecteurs
  `futBoundaryDisplaySecondary` pointent vers un span retiré mais restent gardés par `if(...)`
  (no-op sûrs). Nettoyage cosmétique possible en fin de lot.

## Changements livrés (résumé)
- Champ de planification `niMarginRel` (défaut 1,0 %, D1) synchronisé avec le KPI de sécurité,
  persisté, défaut au rechargement v38.
- `computeObservedZNi()` (Wald, SE pooled, cohérent avec `computeObservedZ`), tableau
  `observedZNiSecondary[]` (calculé à chaque saisie, persisté, **reconstruit au chargement**).
- Nouvelle machine à états (principal : NEUTRE/POSITIF/NEGATIF_DEMONTRE/FUTILE ; guardrail :
  NON_APPLICABLE/SECURITE_DEMONTREE/REGRESSION_DEMONTREE/AUCUN_SIGNAL) + matrice 7 cas.
- Alignements : couleurs lift (nocivité miroir + NI), labels bornes (principal type 3
  « Efficacité/Futilité » ; sécurité « Sécurité démontrée si Z(NI) ≥ … / Régression si Z ≤ −… »),
  affichage `Z(NI) cumulé`. En-tête → v39.0.

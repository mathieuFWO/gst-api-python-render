# PHASE 0 — RAPPORT D'INVESTIGATION (BRIEF GST-V39)

- **Date** : 2026-07-05
- **Branche** : `claude/check-git-access-vzJy6`
- **Périmètre** : read-only (G1). Aucune modification du moteur statistique ni du front dans cette phase.
- **Livrables produits** : ce rapport, `backup/front-v38.22-20260705.html`, `reference/phase0-collect.sh`, `reference/README.md`.

---

## ⚠️ Contrainte d'exécution majeure (à lire en premier)

L'agent tourne dans un **sandbox sans egress réseau** : tout accès sortant est bloqué
(vérifié — `403` / *« Host not in allowlist »* sur `my-gst-api.onrender.com`,
`code.highcharts.com`, `cdn.jsdelivr.net`, `fwoptimisation.com`). **R/gsDesign ne sont pas
installés** localement et ne peuvent l'être (CRAN injoignable).

**Conséquence** : les relevés empiriques de la Phase 0 — canoniques A/B, valeur exacte de
H1, vecteur H2, versions CDN, hashes SRI, plan Render — **ne peuvent pas être produits ici
sans violer G2** (« ne jamais inventer de valeurs »). Ils sont marqués `[À RELEVER]` et
seront remplis en lançant **`reference/phase0-collect.sh`** depuis une machine connectée
(script fourni, autonome). Les points *déterminables hors-ligne depuis le code source*
(schéma localStorage, intégration WordPress, inventaire CDN, conflit `infoFraction`) sont,
eux, traités et conclus ci-dessous.

---

## 🔴 Découverte critique — conflit `infoFraction` avec le brief

La session précédente (commit `9faa938`, avant ce brief) a déjà modifié le script R **sur
cette branche** :

```r
# main (production) :
info_frac <- get_numeric_or_na(design$n.I[[i]])   # porte le facteur d'inflation
# claude/check-git-access-vzJy6 (HEAD actuel) :
info_frac <- timing[i]                             # = i/k, normalisé 0..1
```

Or le brief (H1 §3.3 + Phase 3b §6.2) **suppose que l'API retourne encore `n.I`** :
- H1 lit `boundaries[7].infoFraction` et attend une valeur **> 1.0** = le facteur d'inflation.
- Phase 3b « si H1 vraie » veut **lire ce facteur** (`IF = boundaries[k-1].infoFraction`),
  afficher la pénalité MDE `×√IF`, et corriger l'affichage du tableau par
  `infoFraction[i]/infoFraction[k-1]`.

**Ma modification précédente est donc contre-productive vis-à-vis du brief** : en
normalisant `i/k` côté serveur, elle rend le tableau des bornes correct MAIS **détruit
l'information du facteur d'inflation** que la Phase 3b veut exploiter. Elle change aussi la
sortie du champ `infoFraction` → impact G5/G6 (les références doivent être générées contre
`main`, pas contre cette branche).

### Rappel technique (pourquoi H1 est presque certainement vraie)
Dans `gsDesign` avec `n.fix=1` (défaut ici), `design$n.I[i] = timing[i] × IF`, où
`IF = n.I[k]` est le facteur d'inflation du design séquentiel (ratio taille max
séquentielle / taille à horizon fixe), typiquement **1.00–1.15**. Donc
`n.I[i]/n.I[k] = timing[i] = i/k`. → La dernière valeur `n.I[k]` **est** le facteur
d'inflation. C'est exactement l'hypothèse H1.

### RÉSOLUTION V0 (décidée par Mat, appliquée sur la branche)
On **ne parie plus sur H1** ; l'information est rendue explicite :
1. `infoFraction` **reverté** à `design$n.I[[i]]` → strictement identique à la production
   (G5/G6 ; les canoniques de référence se capturent sur la prod, pas sur la branche).
2. Deux champs **additifs** ajoutés à la réponse R :
   - `boundaries[i].timing = i/k` (vraie fraction, dernière = 1.0) ;
   - `inflationFactor` (top-level) = `design$n.I[[k]]` (scalaire ;
     **critère d'acceptation canonique A : ∈ [1.00 ; 1.30], sinon STOP**).
3. La Phase 3b consomme `inflationFactor` + `timing` explicitement ; H1 devient une simple
   observation à consigner depuis la sortie prod.
4. **G6 précisé** : après tout déploiement API, les champs *existants* des canoniques
   doivent rester identiques ; les champs *additifs* sont exclus du diff.

⚠️ **Ordre de capture** : générer les canoniques de référence sur la **prod actuelle**
AVANT tout déploiement de ce revert (condition posée par Mat).

---

## 1. Localisation du front dans WordPress

- **Page cible** : `https://fwoptimisation.com/calculateur-analyse-sequentielle-ab-test/`.
- **Mode d'intégration** : bloc HTML/JS autonome (v38.22) embarqué dans la page (widget HTML
  Elementor ou snippet — **`[À CONFIRMER par Mat dans l'admin WP]`**). Le fichier ne dépend
  d'aucun build : Highcharts + jStat + jQuery/Bootstrap sont chargés par CDN, tout le JS est
  inline dans un `<script>` en fin de page.
- **Plugin backend associé** (hors page, non requis pour la V1) : `my-ab-tool-api.php`
  (repo, historique git) — endpoints REST WordPress pour la future V2 (Piano, comptes).
  **Non concerné par ce lot.**
- **Backup G3** : `backup/front-v38.22-20260705.html` créé à partir de la version de travail
  du repo. **⚠️ Ce n'est pas une capture fraîche de la page en ligne.** Action requise :
  diff entre la page live (View Source) et ce fichier pour **confirmer que la production est
  strictement v38.22** (item 1 du brief). Commande suggérée :
  ```bash
  curl -s https://fwoptimisation.com/calculateur-analyse-sequentielle-ab-test/ > live.html
  # extraire le bloc outil et diff avec backup/front-v38.22-20260705.html
  ```

## 2. Sorties canoniques de référence

`[À RELEVER — lancer reference/phase0-collect.sh]` → `reference/canonique-A.json`,
`reference/canonique-B.json`. Critère de non-régression : `boundaries[]` + `observedZ`
identiques après chaque phase touchant l'API (G6).

## 3. Hypothèse H1 — `infoFraction` porte le facteur d'inflation

- **Attendu** : `boundaries[7].infoFraction` (canonique A, production/`main`) **> 1.0**,
  ~1.00–1.15. → H1 vraie, Phase 3b sur le chemin nominal.
- **Valeur exacte** : `[À RELEVER]` (imprimée par `phase0-collect.sh`).
- **Voir la découverte critique ci-dessus** : mesurer H1 **contre `main`** (production), car
  la branche courante a neutralisé ce champ.

## 4. Hypothèse H2 — bornes RCI (`testType=2`, `alpha=0.025`)

- **Attendu** : bornes d'efficacité toutes **≥ 1.96**, décroissantes, finale ∈ [1.96 ; 2.30].
- **Vecteur exact** : `[À RELEVER]` → `reference/h2-rci.json`.
- **Garde** : si finale < 1.96 → **STOP, retour Mat** avant Phase 3a (le script le signale).

## 5. Versions CDN effectives + SRI

Inventaire exact des dépendances externes du front (relevé du code source) :

| Ligne | Dépendance | URL actuelle | Problème |
|---|---|---|---|
| 12–15 | Highcharts (core, more, solid-gauge, bullet) | `code.highcharts.com/…` | **rolling** (non versionné, pas de SRI) |
| 16 | jStat | `cdn.jsdelivr.net/npm/jstat@latest/…` | **`@latest`** (non versionné, pas de SRI) |
| 574 | jQuery slim | `code.jquery.com/jquery-3.2.1.slim.min.js` | épinglé mais **ancien**, pas de SRI |
| 575 | Popper | `cdnjs…/popper.js/1.12.9/…` | épinglé, pas de SRI |
| 576 | Bootstrap | `maxcdn.bootstrapcdn.com/bootstrap/4.0.0/…` | **maxcdn déprécié** (à vérifier online), pas de SRI |

- **Versions résolues + hashes SRI** : `[À RELEVER]` → `reference/cdn-versions.txt`.
- **Joignabilité `maxcdn.bootstrapcdn.com`** : `[À RELEVER]` (testée par le script).
- **CORRECTION (constat initial erroné)** : `jStat` **EST utilisé** — `jStat.normal.inv`
  est appelé 3× dans `calculateAndDisplayMDEForecast()` (lignes 908–910 : `zBeta`,
  `zAlpha_principal`, `zAlpha_secondary`). Tout le tableau MDE de l'Étape 1 en dépend.
  → **Aucune suppression.** Action Phase 6 : épingler la version + SRI uniquement.

## 6. Plan Render

`[À RELEVER par Mat — dashboard Render]` : free vs payant, RAM, impact cold start.
Détermine en Phase 5 le nombre de workers Gunicorn possible (`--workers 2` ≈ 300–400 Mo
avec 2 process R concurrents ; sinon rester à 1 worker + rate limiting).
Le free tier confirme le besoin du **ping de préchauffage** (Phase 6 §9.3).

## 7. Schéma localStorage (rétrocompat G4)

- **Préfixe** : `STORAGE_PREFIX = "gstSequentialAnalysis_v321_"` — **inchangé** (G4).
- **Champs sauvegardés** (`saveCurrentTestState`) :
  `name, timestamp, baselineTraffic, baselineTotalConversions,
  baselineTotalConversionsSecondary, isSecondaryKpiPlanned, testStartDate, mdeConfidence,
  mdePower, mdeTestType, designSpendingFunction, designSpendingFunctionLower, designK,
  currentDesignParams, currentBoundariesApiResultPrincipal,
  currentBoundariesApiResultSecondary, weeklyEnteredData, observedZDataPrincipal,
  observedZDataSecondary, apiUrl`.
- **Nouveaux champs à défaut au chargement** (`loadSelectedTestState`), pour ne pas casser
  les tests v38 :
  | Champ (à venir) | Phase | Défaut au rechargement v38 |
  |---|---|---|
  | `niMarginRel` | 1 | `1.0` (D1) |
  | `observedZNiSecondary[]` | 1 | tableau de `null` |
  | `rciBounds[]` | 3a | `null` → fallback IC 95 % naïf (1.96) |
- Précédent déjà en place : `computeObservedZ()` reconstruit `observedZDataPrincipal`
  manquant au chargement (session précédente) — bon patron à suivre pour les nouveaux champs.

---

## Décisions tranchées par Mat (gate V0) — ARRÊTÉES

- **D0** — Revert `infoFraction` → `design$n.I[[i]]` (identique prod) + champs additifs
  `timing` (i/k) et `inflationFactor` (`n.I[k]`, ∈ [1.00 ; 1.30] sinon STOP). ✅ **APPLIQUÉ**
  sur la branche (non déployé).
- **D1** — Marge de non-régression guardrail : **champ de planification, défaut 1,0 %
  relatif**, modifiable. → Phase 1.
- **D2** — Seuil SRM : **0,001 (χ² > 10,828)**, FAQ de la page à aligner. → Phase 4.
- **D3** — `testType=1` : **conservé tel quel + tooltip** « pas d'arrêt anticipé pour
  futilité dans ce mode ». → Phase 1.
- **D4** — Front : **épinglage + SRI uniquement** dans ce lot. Upgrade
  jQuery/Bootstrap/Popper → **micro-lot séparé après V6** (la page bouge déjà avec la
  refonte éditoriale, pas de staging, on ne cumule pas les risques). → Phase 6.

## Prochain pas proposé

1. Mat lance `reference/phase0-collect.sh` (ou fournit les sorties API) → remplit les
   `[À RELEVER]`.
2. Mat tranche **D0** et **D1** (les deux qui débloquent la suite immédiate).
3. Sur GO V0 : démarrage **Phase 1** (front-only, ne touche pas l'API — indépendante des
   relevés canoniques, donc réalisable même avant que le réseau soit disponible côté agent).

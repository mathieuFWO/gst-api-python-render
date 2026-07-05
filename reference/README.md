# reference/ — Références de non-régression (BRIEF GST-V39, garde-fou G6)

Ce dossier contient les **sorties canoniques de référence** de l'API GST. Elles servent
à garantir qu'aucune phase touchant l'API ne modifie les bornes calculées (écart toléré : 0).

## Protocole

1. **Générer les références** (une machine avec accès réseau) :
   ```bash
   bash reference/phase0-collect.sh
   ```
   Produit : `canonique-A.json`, `canonique-B.json`, `h2-rci.json`, `cdn-versions.txt`.

2. **Après toute phase touchant l'API** (Phase 5, ou Phase 3b plan B), rejouer les payloads
   et comparer :
   ```bash
   diff <(curl -s -X POST "$API" -H "Content-Type: application/json" -d @canonique-A.payload.json | python3 -m json.tool) \
        <(python3 -m json.tool canonique-A.json)
   ```
   Le champ `boundaries[]` (efficacyZ, futilityZ) et `observedZ` doivent être **identiques
   à l'arrondi retourné par R**. Un `diff` non vide = régression numérique = STOP.

## Payloads canoniques (§2 du brief)

| Fichier | Payload |
|---|---|
| canonique-A | `{"k":8,"alpha":0.05,"power":0.80,"sfu":"KimDeMets","sfl":"HSD","testType":3}` |
| canonique-B | idem A + `visitors_a:40000, conversions_a:2000, visitors_b:40000, conversions_b:2120` |
| h2-rci (H2) | `{"k":8,"alpha":0.025,"power":0.80,"sfu":"KimDeMets","testType":2}` |

## ⚠️ Point de vigilance : champ `infoFraction`

Le script R de la branche `claude/check-git-access-vzJy6` a modifié `infoFraction`
(`design$n.I[[i]]` → `timing[i] = i/k`). Cela **change la sortie du champ `infoFraction`**
par rapport à `main` et à la production actuelle. Voir `PHASE0-RAPPORT.md` §3 (H1) :
cette modification doit être **tranchée par Mat** avant de figer les références, car elle
interagit avec la Phase 3b (facteur d'inflation). Générer les références **contre la
production actuelle** (branche `main` déployée), pas contre cette branche, tant que
la décision n'est pas prise.

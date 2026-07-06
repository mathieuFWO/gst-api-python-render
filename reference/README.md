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

## ⚠️ Point de vigilance : champ `infoFraction` (D0 — RÉSOLU)

Décision V0 appliquée : `infoFraction` **reste `design$n.I[[i]]`** (identique à la prod),
et deux champs **additifs** sont ajoutés à la réponse R : `boundaries[i].timing` (= i/k)
et `inflationFactor` (= `n.I[k]`).

**Ordre impératif** (condition posée par Mat) :
1. **Capturer les canoniques sur la PROD actuelle** (`main` déployée), via
   `phase0-collect.sh`, **AVANT** tout déploiement du revert D0.
2. Après déploiement de l'API augmentée : le diff de non-régression porte **uniquement sur
   les champs existants** (`observedZ`, `boundaries[].efficacyZ/futilityZ/infoFraction/…`,
   `parameters`). Ils doivent être **identiques** à la référence prod.
3. Les champs **additifs** (`timing`, `inflationFactor`) sont **exclus du diff** (G6).

Commande de diff filtré (exclut les champs additifs) :
```bash
python3 - <<'PY'
import json
ref  = json.load(open("canonique-A.json"))          # capturé sur prod
new  = json.load(open("canonique-A.after.json"))     # après déploiement API augmentée
def strip(d):
    d = json.loads(json.dumps(d)); d.pop("inflationFactor", None)
    for b in d.get("boundaries", []): b.pop("timing", None)
    return d
print("IDENTIQUE" if strip(ref) == strip(new) else "⚠️ RÉGRESSION sur champ existant")
PY
```

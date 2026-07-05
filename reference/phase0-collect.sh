#!/usr/bin/env bash
# =============================================================================
# phase0-collect.sh — Collecte des relevés empiriques de la Phase 0 (BRIEF GST-V39)
#
# À exécuter depuis une machine AYANT un accès réseau sortant (l'environnement
# de l'agent Claude est en sandbox sans egress : il ne peut PAS produire ces
# valeurs lui-même — G2 interdit de les inventer).
#
# Ce script :
#   1. Interroge l'API Render avec les payloads canoniques A et B  -> reference/canonique-A.json / -B.json
#   2. Extrait H1 (boundaries[7].infoFraction du canonique A)
#   3. Interroge l'API pour les bornes RCI (H2)                     -> reference/h2-rci.json
#   4. Résout les versions CDN effectives + calcule les hashes SRI  -> reference/cdn-versions.txt
#   5. Teste la joignabilité de maxcdn.bootstrapcdn.com
#
# Dépendances : curl, openssl, python3 (tous standard). jq optionnel.
# Usage : bash reference/phase0-collect.sh
# =============================================================================
set -uo pipefail

API="${API_URL:-https://my-gst-api.onrender.com/api/calculate-boundaries}"
HEALTH="${HEALTH_URL:-https://my-gst-api.onrender.com/}"
DIR="$(cd "$(dirname "$0")" && pwd)"

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }

# --- petit extracteur JSON via python3 (pas de dépendance jq obligatoire) ---
jget() { python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(eval(sys.argv[2]))" "$1" "$2" 2>/dev/null; }

say "0. Réveil de l'API (cold start Render possible, jusqu'à 60 s)…"
curl -s -m 90 -o /dev/null -w "   health GET / -> HTTP %{http_code}\n" "$HEALTH"

# --- 1. Canonique A ---------------------------------------------------------
say "1. Canonique A (design seul)"
curl -s -m 90 -X POST "$API" -H "Content-Type: application/json" \
  -d '{"k":8,"alpha":0.05,"power":0.80,"sfu":"KimDeMets","sfl":"HSD","testType":3}' \
  -o "$DIR/canonique-A.json" -w "   HTTP %{http_code}\n"
python3 -m json.tool "$DIR/canonique-A.json" >/dev/null 2>&1 && echo "   JSON valide -> reference/canonique-A.json" || echo "   ⚠️ réponse non-JSON, inspecter le fichier"

# --- 2. Canonique B ---------------------------------------------------------
say "2. Canonique B (design + données semaine intermédiaire)"
curl -s -m 90 -X POST "$API" -H "Content-Type: application/json" \
  -d '{"k":8,"alpha":0.05,"power":0.80,"sfu":"KimDeMets","sfl":"HSD","testType":3,"visitors_a":40000,"conversions_a":2000,"visitors_b":40000,"conversions_b":2120}' \
  -o "$DIR/canonique-B.json" -w "   HTTP %{http_code}\n"
echo "   observedZ = $(jget "$DIR/canonique-B.json" "d['observedZ']")"

# --- 3. H1 : infoFraction porte-t-il le facteur d'inflation ? ---------------
say "3. H1 — boundaries[7].infoFraction (dernière étape, canonique A)"
H1=$(jget "$DIR/canonique-A.json" "d['boundaries'][7]['infoFraction']")
echo "   infoFraction[8] = $H1"
python3 - "$H1" <<'PY'
import sys
try:
    v=float(sys.argv[1])
    if v>1.0001: print(f"   => H1 VRAIE : {v} > 1.0  (facteur d'inflation ~{v:.4f}, MDE penalty x{v**0.5:.4f})")
    elif abs(v-1.0)<=1e-4: print("   => H1 FAUSSE : infoFraction[8] == 1.0  -> Phase 3b bascule sur PLAN B (exporter inflationFactor côté R)")
    else: print(f"   => Valeur inattendue {v} < 1.0 : à investiguer avant Phase 3b")
except Exception as e:
    print("   ⚠️ valeur non numérique, inspecter reference/canonique-A.json :", e)
PY

# --- 4. H2 : bornes RCI (testType=2, alpha=0.025) ---------------------------
say "4. H2 — bornes RCI (superiority two-sided proxy, alpha=0.025)"
curl -s -m 90 -X POST "$API" -H "Content-Type: application/json" \
  -d '{"k":8,"alpha":0.025,"power":0.80,"sfu":"KimDeMets","testType":2}' \
  -o "$DIR/h2-rci.json" -w "   HTTP %{http_code}\n"
python3 - "$DIR/h2-rci.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
eff=[b.get('efficacyZ') for b in d.get('boundaries',[])]
print("   efficacyZ =", eff)
try:
    fin=eff[-1]
    ok_all = all((z is not None and z>=1.96) for z in eff)
    ok_dec = all(eff[i]>=eff[i+1] for i in range(len(eff)-1) if eff[i] is not None and eff[i+1] is not None)
    print(f"   toutes >= 1.96 : {ok_all} | décroissantes : {ok_dec} | borne finale : {fin}")
    if fin is not None and fin < 1.96:
        print("   => ⚠️ STOP : H2 INVALIDE (borne finale < 1.96). Retour vers Mat avant Phase 3a.")
    elif fin is not None and 1.96 <= fin <= 2.30 and ok_all and ok_dec:
        print("   => H2 VALIDE : bornes RCI exploitables pour les IC séquentiels (Phase 3a).")
    else:
        print("   => à examiner manuellement (hors intervalle attendu).")
except Exception as e:
    print("   ⚠️", e)
PY

# --- 5. Versions CDN + SRI --------------------------------------------------
say "5. Versions CDN effectives + hashes SRI (SHA-384)"
CDN_OUT="$DIR/cdn-versions.txt"
: > "$CDN_OUT"
sri() { # url -> ligne SRI + URL résolue
  local url="$1" resolved hash
  resolved=$(curl -s -o /dev/null -w '%{url_effective}' -L "$url")
  hash=$(curl -s -L "$url" | openssl dgst -sha384 -binary | openssl base64 -A)
  printf 'source demandée : %s\n  URL résolue    : %s\n  integrity      : sha384-%s\n\n' "$url" "$resolved" "$hash" | tee -a "$CDN_OUT"
}
echo "# Relevé du $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$CDN_OUT"
sri "https://cdn.jsdelivr.net/npm/jstat@latest/dist/jstat.min.js"
sri "https://code.highcharts.com/highcharts.js"
sri "https://code.highcharts.com/highcharts-more.js"
sri "https://code.highcharts.com/modules/solid-gauge.js"
sri "https://code.highcharts.com/modules/bullet.js"
sri "https://code.jquery.com/jquery-3.2.1.slim.min.js"
sri "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js"

say "5b. maxcdn.bootstrapcdn.com encore en ligne ?"
curl -s -m 15 -o /dev/null -w "   bootstrap 4.0.0 -> HTTP %{http_code}\n" \
  "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"

say "TERMINÉ. Fichiers produits dans reference/. Colle le contenu de :"
echo "  - reference/canonique-A.json / canonique-B.json / h2-rci.json"
echo "  - reference/cdn-versions.txt"
echo "  + les valeurs H1/H2 imprimées ci-dessus, pour finaliser PHASE0-RAPPORT.md."

import os
import sys
import subprocess
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Configuration ---
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024  # 64 KB max payload

origins = ["https://fwoptimisation.com", "https://www.fwoptimisation.com"]
CORS(app, origins=origins, methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type"], supports_credentials=False)

R_EXECUTABLE = 'Rscript'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
R_SCRIPT_PATH = os.path.join(BASE_DIR, 'calculate_gs_design.R')

# Bornes de validation des paramètres d'entrée
K_MAX = 50
ALPHA_MIN, ALPHA_MAX = 1e-6, 0.5
BETA_MIN, BETA_MAX  = 0.0, 0.99


def _safe_stderr(stderr_text: str, max_chars: int = 300) -> str:
    """Tronque stderr pour éviter l'exposition d'informations internes."""
    if not stderr_text:
        return "Aucun détail disponible."
    sanitized = stderr_text.replace('\n', ' ').strip()
    if len(sanitized) > max_chars:
        sanitized = sanitized[:max_chars] + "…"
    return sanitized


@app.route('/api/calculate-boundaries', methods=['POST'])
def calculate_boundaries():
    print("--> Requête reçue sur /api/calculate-boundaries")

    if not request.is_json:
        return jsonify({"error": True, "message": "Requête doit être au format JSON"}), 400

    params = request.get_json(silent=True)
    if params is None:
        return jsonify({"error": True, "message": "Corps JSON invalide ou vide."}), 400

    print(f"Paramètres reçus: {params}")

    # --- Validation des paramètres critiques côté Python ---
    k = params.get('k')
    if not isinstance(k, int) or k <= 0 or k > K_MAX:
        return jsonify({"error": True, "message": f"Paramètre 'k' invalide (entier entre 1 et {K_MAX})."}), 400

    alpha = params.get('alpha', 0.05)
    beta  = params.get('beta', 0.20)
    try:
        alpha = float(alpha)
        beta  = float(beta)
    except (TypeError, ValueError):
        return jsonify({"error": True, "message": "Paramètres 'alpha' et 'beta' doivent être numériques."}), 400

    if not (ALPHA_MIN < alpha < ALPHA_MAX):
        return jsonify({"error": True, "message": f"Paramètre 'alpha' hors bornes ({ALPHA_MIN}, {ALPHA_MAX})."}), 400
    if not (BETA_MIN <= beta < BETA_MAX):
        return jsonify({"error": True, "message": f"Paramètre 'beta' hors bornes [{BETA_MIN}, {BETA_MAX})."}), 400
    if alpha + beta >= 1:
        return jsonify({"error": True, "message": "La somme alpha + beta doit être inférieure à 1."}), 400

    try:
        input_json_string = json.dumps(params)
    except Exception as e:
        return jsonify({"error": True, "message": "Erreur lors de la sérialisation JSON."}), 500

    command = [R_EXECUTABLE, R_SCRIPT_PATH, input_json_string]
    print(f"Exécution de la commande R (k={k})")

    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=30
        )

        print(f"Script R terminé (code {proc.returncode})")
        print(f"R stdout (début): {proc.stdout[:500]}...")
        if proc.stderr:
            print(f"R stderr: {proc.stderr}")

        if proc.returncode != 0:
            error_details = _safe_stderr(proc.stderr)
            print(f"Erreur R: {error_details}")
            return jsonify({
                "error": True,
                "message": f"Erreur lors du calcul (code {proc.returncode}).",
                "details": error_details
            }), 500

        try:
            result = json.loads(proc.stdout)

            error_value = result.get('error')
            is_r_error = isinstance(error_value, list) and len(error_value) > 0 and error_value[0] is True

            if is_r_error:
                r_message_list = result.get('message', ["Erreur R non spécifiée."])
                r_message = r_message_list[0] if isinstance(r_message_list, list) and r_message_list else "Erreur R non spécifiée."
                print(f"Erreur applicative R: {r_message}")
                return jsonify({"error": True, "message": r_message}), 400

            print("Succès: Renvoi du résultat JSON.")
            return jsonify(result)

        except json.JSONDecodeError as json_err:
            print(f"Erreur parsing JSON sortie R: {json_err}")
            print(f"Sortie R brute: {proc.stdout[:500]}")
            return jsonify({
                "error": True,
                "message": "Impossible de parser la réponse du moteur de calcul."
            }), 500

    except FileNotFoundError:
        print(f"Erreur critique: '{R_EXECUTABLE}' ou '{R_SCRIPT_PATH}' non trouvé.")
        return jsonify({"error": True, "message": "Moteur de calcul introuvable sur le serveur."}), 500
    except subprocess.TimeoutExpired:
        print("Erreur: Timeout du script R.")
        return jsonify({"error": True, "message": "Le calcul a dépassé le délai maximum (30 s)."}), 504
    except Exception as e:
        print(f"Erreur serveur inattendue: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return jsonify({"error": True, "message": "Erreur serveur inattendue."}), 500


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "API GST en ligne"})

# Pas de app.run() pour la production avec Gunicorn

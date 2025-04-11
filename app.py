import os
import sys
import subprocess
import json
from flask import Flask, request, jsonify
from flask_cors import CORS # Importer CORS

# --- Configuration ---
app = Flask(__name__)

# --- CONFIGURATION CORS PLUS EXPLICITE ---
# Remplacez par votre/vos origine(s) réelle(s)
origins = ["https://fwoptimisation.com", "https://www.fwoptimisation.com"] # Exemple avec www et non-www

# Appliquer CORS à toute l'application avec des options spécifiques
CORS(app, origins=origins, methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type"], supports_credentials=False)

# --- Reste de la configuration (chemins R, etc.) ---
R_EXECUTABLE = 'Rscript'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
R_SCRIPT_PATH = os.path.join(BASE_DIR, 'calculate_gs_design.R')

# --- Endpoint API ---
@app.route('/api/calculate-boundaries', methods=['POST'])
def calculate_boundaries():
    print("--> Requête reçue sur /api/calculate-boundaries") # Log pour Render
    if not request.is_json:
        print("Erreur: Requête non JSON")
        return jsonify({"error": True, "message": "Requête doit être au format JSON"}), 400

    params = request.get_json()
    print(f"Paramètres reçus: {params}")

    # Validation basique
    if not params or not isinstance(params.get('k'), int) or params['k'] <= 0:
        print("Erreur: Paramètre 'k' invalide")
        return jsonify({"error": True, "message": "Paramètre 'k' (nombre d'étapes) manquant ou invalide."}), 400

    # Conversion en chaîne JSON pour R
    try:
        input_json_string = json.dumps(params)
    except Exception as e:
        print(f"Erreur JSON dump: {e}")
        return jsonify({"error": True, "message": f"Erreur lors de la sérialisation JSON: {e}"}), 500

    # Préparation de la commande R
    command = [R_EXECUTABLE, R_SCRIPT_PATH, input_json_string]
    print(f"Exécution de la commande: {' '.join(command)}")

    # --- Bloc TRY principal pour l'exécution du subprocess ---
    try:
        # Exécution du script R
        proc = subprocess.run(command,
                              capture_output=True,
                              text=True,
                              check=False, # Ne pas lever d'erreur ici pour lire stderr
                              timeout=30) # Timeout

        print(f"Script R terminé (code {proc.returncode})")
        print(f"R stdout (début): {proc.stdout[:500]}...")
        if proc.stderr:
            print(f"R stderr: {proc.stderr}")

        # Gestion des erreurs d'exécution du script R
        if proc.returncode != 0:
            error_message = f"Erreur exécution script R (code {proc.returncode})."
            details = proc.stderr or "Pas de détails stderr disponibles."
            print(error_message, details)
            return jsonify({"error": True, "message": error_message, "details": details}), 500

        # --- Bloc TRY interne pour le parsing JSON ---
        try:
            result = json.loads(proc.stdout)

            # Vérification d'erreur applicative retournée par R
            error_value = result.get('error')
            is_r_error = isinstance(error_value, list) and len(error_value) > 0 and error_value[0] is True

            if is_r_error:
                r_message_list = result.get('message', ["Erreur R non spécifiée."])
                r_message = r_message_list[0] if isinstance(r_message_list, list) and r_message_list else "Erreur R non spécifiée."
                print(f"Le script R a retourné une erreur interne: {r_message}")
                return jsonify({"error": True, "message": r_message, "details": result.get('details')}), 400
            else:
                print("Succès: Renvoi du résultat JSON.")
                return jsonify(result)

        except json.JSONDecodeError as json_err:
            print(f"Erreur parsing JSON de la sortie R: {json_err}")
            print(f"Sortie R brute: {proc.stdout}")
            return jsonify({
                "error": True,
                "message": "Impossible de parser la sortie JSON du script R.",
                "raw_output": proc.stdout,
                "parse_error": str(json_err)
            }), 500

    # --- EXCEPT pour FileNotFoundError (externe) ---
    except FileNotFoundError:
         print(f"Erreur critique: '{R_EXECUTABLE}' ou '{R_SCRIPT_PATH}' non trouvé.")
         return jsonify({"error": True, "message": "Fichier Rscript ou script R introuvable sur le serveur."}), 500
    # --- EXCEPT pour TimeoutExpired (externe) ---
    except subprocess.TimeoutExpired:
         print("Erreur: Timeout du script R.")
         return jsonify({"error": True, "message": "Le calcul R a dépassé le délai."}), 500
    # --- EXCEPT général (externe) ---
    except Exception as e:
        print(f"Erreur serveur inattendue: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return jsonify({"error": True, "message": f"Erreur serveur inattendue: {e}"}), 500

# --- Point de terminaison pour vérifier si l'API est en ligne ---
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "API GST en ligne"})

# Pas de app.run() pour la production avec Gunicorn

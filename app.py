import os
import sys
import subprocess
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Configuration ---
app = Flask(__name__)
# Autoriser les requêtes depuis n'importe quelle origine (pour WordPress)
CORS(app)

# Chemin vers l'exécutable Rscript (suppose qu'il est dans le PATH du conteneur Docker)
R_EXECUTABLE = 'Rscript'
# Chemin vers le script R (dans le même dossier que app.py dans le conteneur)
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
                              check=False, # Important: ne pas lever d'erreur ici pour pouvoir lire stderr
                              timeout=30) # Timeout de 30 secondes

        print(f"Script R terminé (code {proc.returncode})")
        print(f"R stdout (début): {proc.stdout[:500]}...") # Log tronqué pour lisibilité
        if proc.stderr:
            print(f"R stderr: {proc.stderr}") # Afficher les erreurs R s'il y en a

        # Gestion des erreurs d'exécution du script R
        if proc.returncode != 0:
            error_message = f"Erreur exécution script R (code {proc.returncode})."
            details = proc.stderr or "Pas de détails stderr disponibles."
            print(error_message, details)
            # Renvoyer une erreur 500 car c'est un problème côté serveur
            return jsonify({"error": True, "message": error_message, "details": details}), 500

        # --- Bloc TRY interne pour le parsing JSON ---
        # Ce try est imbriqué car on veut essayer de parser même si l'exécution a réussi
        try:
            result = json.loads(proc.stdout)

            # Vérification d'erreur applicative retournée par R
            # Vérifier si 'error' existe, est une liste, n'est pas vide, et si son premier élément est True.
            error_value = result.get('error')
            is_r_error = isinstance(error_value, list) and len(error_value) > 0 and error_value[0] is True

            if is_r_error:
                r_message_list = result.get('message', ["Erreur R non spécifiée."])
                r_message = r_message_list[0] if isinstance(r_message_list, list) and r_message_list else "Erreur R non spécifiée."
                print(f"Le script R a retourné une erreur interne: {r_message}")
                # Retourner l'erreur spécifique, potentiellement 400 si c'est une erreur client (mauvais params R)
                return jsonify({"error": True, "message": r_message, "details": result.get('details')}), 400
            else:
                # Succès, renvoyer le résultat
                print("Succès: Renvoi du résultat JSON.")
                return jsonify(result)

        # --- EXCEPT pour le parsing JSON (interne) ---
        except json.JSONDecodeError as json_err:
            print(f"Erreur parsing JSON de la sortie R: {json_err}")
            print(f"Sortie R brute: {proc.stdout}")
            # Erreur serveur car on n'a pas pu interpréter la sortie R correcte
            return jsonify({
                "error": True,
                "message": "Impossible de parser la sortie JSON du script R.",
                "raw_output": proc.stdout,
                "parse_error": str(json_err)
            }), 500

    # --- EXCEPT pour FileNotFoundError (externe) ---
    except FileNotFoundError:
         print(f"Erreur critique: '{R_EXECUTABLE}' ou '{R_SCRIPT_PATH}' non trouvé.")
         return jsonify({
             "error": True,
             "message": "Fichier Rscript ou script R introuvable sur le serveur.",
             "details": f"Tentative d'exécution de '{R_EXECUTABLE}'"
         }), 500
    # --- EXCEPT pour TimeoutExpired (externe) ---
    except subprocess.TimeoutExpired:
         print("Erreur: Timeout du script R.")
         return jsonify({
             "error": True,
             "message": "Le calcul R a dépassé le délai."
         }), 500
    # --- EXCEPT général (externe) ---
    except Exception as e:
        # Capturer toute autre erreur inattendue lors de l'appel subprocess etc.
        print(f"Erreur serveur inattendue: {e}", file=sys.stderr)
        # Imprimer la traceback pour plus de détails dans les logs Render
        import traceback
        traceback.print_exc()
        return jsonify({"error": True, "message": f"Erreur serveur inattendue: {e}"}), 500

# --- Point de terminaison pour vérifier si l'API est en ligne ---
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "API GST en ligne"})

# Note importante: La ligne ci-dessous est pour les tests locaux SEULEMENT.
# Gunicorn (utilisé par Render via le Dockerfile CMD) lancera l'application en production.
# NE PAS décommenter cette partie pour le déploiement sur Render.
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)

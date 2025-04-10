# --- START OF FILE app.py ---

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
    print(f"Paramètres reçus: {params}") # Log les paramètres bruts

    # Validation basique des paramètres du design
    # Note: Les données cumulées (visitors_a, etc.) sont optionnelles ici,
    #       le script R gère leur absence pour le calcul Z.
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
    # Tentative: Mettre explicitement des quotes autour de l'argument JSON
    # command = [R_EXECUTABLE, R_SCRIPT_PATH, f"'{input_json_string}'"] # <--- ESSAYER CECI ? Moins standard
    # Revenir à la version standard qui est plus fiable normalement:
    command = [R_EXECUTABLE, R_SCRIPT_PATH, input_json_string]
    print(f"Exécution de la commande: {' '.join(command)}")

    # --- Bloc TRY principal pour l'exécution du subprocess ---
    try:
        # Exécution du script R
        proc = subprocess.run(command,
                              capture_output=True,
                              text=True, # Pour obtenir stdout/stderr en texte
                              check=False, # Ne pas lever d'erreur ici pour lire stderr
                              timeout=30) # Timeout de 30 secondes

        print(f"Script R terminé (code {proc.returncode})")
        # Log tronqué pour éviter les logs trop longs
        print(f"R stdout (début): {proc.stdout[:500]}...")
        if proc.stderr:
            # Log complet de stderr car souvent informatif
            print(f"R stderr: {proc.stderr}")

        # Gestion des erreurs d'exécution du script R lui-même
        if proc.returncode != 0:
            error_message = f"Erreur exécution script R (code {proc.returncode})."
            # Essayer de récupérer le message d'erreur de R stderr s'il existe
            details = proc.stderr or "Pas de détails stderr disponibles."
            print(error_message, details) # Log l'erreur
            return jsonify({"error": True, "message": error_message, "details": details}), 500

        # --- Bloc TRY interne pour le parsing JSON de la sortie R ---
        try:
            # Essayer de parser la sortie standard du script R comme JSON
            result = json.loads(proc.stdout)

            # Vérification d'une erreur applicative retournée par le script R lui-même
            # (ex: validation de paramètre interne à R, erreur de calcul gsDesign)
            if isinstance(result, dict) and result.get('error') is True:
                 r_message = result.get('message', "Erreur interne retournée par le script R.")
                 r_details = result.get('details') # Optionnel
                 print(f"Le script R a retourné une erreur applicative: {r_message} Details: {r_details}")
                 return jsonify({"error": True, "message": r_message, "details": r_details}), 400 # Bad request si erreur logique R
            else:
                # Si tout va bien (pas d'erreur d'exécution et pas d'erreur applicative R)
                print("Succès: Renvoi du résultat JSON du script R.")
                # On retourne le JSON complet tel que reçu de R
                return jsonify(result)

        except json.JSONDecodeError as json_err:
            # Gérer le cas où la sortie R n'est pas un JSON valide
            print(f"Erreur parsing JSON de la sortie R: {json_err}")
            print(f"Sortie R brute (stdout): {proc.stdout}") # Log la sortie brute qui a échoué
            return jsonify({
                "error": True,
                "message": "Impossible de parser la sortie JSON du script R.",
                "raw_output": proc.stdout, # Inclure la sortie brute peut aider au débogage
                "parse_error": str(json_err)
            }), 500

    # --- EXCEPT pour FileNotFoundError (Rscript ou .R introuvable) ---
    except FileNotFoundError:
         print(f"Erreur critique: '{R_EXECUTABLE}' ou '{R_SCRIPT_PATH}' non trouvé.")
         return jsonify({"error": True, "message": "Fichier Rscript ou script R introuvable sur le serveur."}), 500
    # --- EXCEPT pour TimeoutExpired ---
    except subprocess.TimeoutExpired:
         print("Erreur: Timeout du script R.")
         return jsonify({"error": True, "message": "Le calcul R a dépassé le délai imparti."}), 500
    # --- EXCEPT général pour autres erreurs inattendues ---
    except Exception as e:
        # Log l'erreur complète côté serveur
        print(f"Erreur serveur inattendue lors de l'exécution du script R: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc() # Imprime la trace complète dans les logs serveur
        # Retourne un message d'erreur générique au client
        return jsonify({"error": True, "message": f"Erreur serveur inattendue."}), 500

# --- Point de terminaison pour vérifier si l'API est en ligne ---
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "API GST en ligne"})

# Pas de app.run() nécessaire pour Gunicorn en production
# Gunicorn est lancé via le Procfile ou la commande de démarrage Render

# --- END OF FILE app.py ---

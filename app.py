import os
import sys
import subprocess
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Configuration ---
app = Flask(__name__)
# Autoriser les requêtes depuis n'importe quelle origine (pour WordPress)
# Vous pourriez restreindre cela en production si nécessaire
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

    try:
        # Exécution du script R
        proc = subprocess.run(command,
                              capture_output=True,
                              text=True,
                              check=False,
                              timeout=30) # Timeout de 30 secondes

        print(f"Script R terminé (code {proc.returncode})")
        print(f"R stdout (début): {proc.stdout[:500]}...")
        if proc.stderr:
            print(f"R stderr: {proc.stderr}")

        # Gestion des erreurs R
        if proc.returncode != 0:
            error_message = f"Erreur exécution script R (code {proc.returncode})."
            details = proc.stderr or "Pas de détails stderr."
            print(error_message, details)
            return jsonify({"error": True, "message": error_message, "details": details}), 500

                   # Parsing de la sortie R
            try:
                result = json.loads(proc.stdout)

                # *** CORRECTION DE LA CONDITION D'ERREUR ***
                # Vérifier si 'error' existe, est une liste/tableau, n'est pas vide,
                # et si son premier élément est True.
                error_value = result.get('error')
                is_r_error = isinstance(error_value, list) and len(error_value) > 0 and error_value[0] is True

                if is_r_error:
                    r_message = result.get('message', ["Erreur R non spécifiée."])[0] # Prendre le premier message
                    print(f"Le script R a retourné une erreur interne: {r_message}")
                    # Retourner l'erreur spécifique telle que fournie par R
                    return jsonify({"error": True, "message": r_message, "details": result.get('details')}), 400 # ou 500
                else:
                    # Assurer que les scalaires sont bien 'déboxés' si nécessaire avant de renvoyer
                    # (Optionnel, mais peut simplifier le JS)
                    # On pourrait itérer et simplifier les listes de longueur 1, mais
                    # laissons le JSON tel quel pour l'instant, le JS devrait pouvoir le gérer.
                    print("Succès: Renvoi du résultat JSON.")
                    return jsonify(result) # Renvoi du succès

            except json.JSONDecodeError as json_err:
                print(f"Erreur parsing JSON de la sortie R: {json_err}")
                print(f"Sortie R brute: {proc.stdout}")
                return jsonify({
                    "error": True,
                    "message": "Impossible de parser la sortie JSON du script R.",
                    "raw_output": proc.stdout,
                    "parse_error": str(json_err)
                }), 500

# --- Point de terminaison pour vérifier si l'API est en ligne ---
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "API GST en ligne"})

# Note: app.run() n'est pas nécessaire ici car Gunicorn lance l'application

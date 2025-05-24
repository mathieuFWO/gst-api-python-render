# app.py - Version étendue avec gestion des expérimentations
import os
import sys
import subprocess
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

# --- Configuration ---
app = Flask(__name__)

# --- CONFIGURATION CORS ---
origins = ["https://fwoptimisation.com", "https://www.fwoptimisation.com"]
CORS(app, origins=origins, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
     allow_headers=["Content-Type"], supports_credentials=False)

# --- Configuration Base de Données WordPress ---
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'wordpress'),
    'user': os.getenv('DB_USER', 'wp_user'),
    'password': os.getenv('DB_PASSWORD', 'wp_password'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

# --- Configuration R ---
R_EXECUTABLE = 'Rscript'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
R_SCRIPT_PATH = os.path.join(BASE_DIR, 'calculate_gs_design.R')

# --- Fonctions Utilitaires Base de Données ---
def get_db_connection():
    """Établit une connexion à la base de données WordPress"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Erreur connexion BDD: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    """Exécute une requête SQL"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall() if fetch == 'all' else cursor.fetchone()
        else:
            connection.commit()
            result = cursor.lastrowid
            
        cursor.close()
        connection.close()
        return result
        
    except Error as e:
        print(f"Erreur requête SQL: {e}")
        if connection:
            connection.close()
        return None

# --- Endpoints Expérimentations ---

@app.route('/api/experiments', methods=['GET'])
def get_experiments():
    """Récupère la liste des expérimentations d'un utilisateur"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({"error": True, "message": "user_id requis"}), 400
    
    query = """
        SELECT id, name, url, status, created_at, updated_at, parameters, boundaries, weekly_data
        FROM wp_ab_experiments 
        WHERE user_id = %s 
        ORDER BY updated_at DESC
    """
    
    experiments = execute_query(query, (user_id,), fetch='all')
    
    if experiments is None:
        return jsonify({"error": True, "message": "Erreur lors de la récupération"}), 500
    
    # Parsing JSON des colonnes
    for exp in experiments:
        exp['parameters'] = json.loads(exp['parameters']) if exp['parameters'] else {}
        exp['boundaries'] = json.loads(exp['boundaries']) if exp['boundaries'] else []
        exp['weekly_data'] = json.loads(exp['weekly_data']) if exp['weekly_data'] else {}
    
    return jsonify({"error": False, "experiments": experiments})

@app.route('/api/experiments', methods=['POST'])
def create_experiment():
    """Crée une nouvelle expérimentation"""
    data = request.get_json()
    
    if not data or not data.get('user_id'):
        return jsonify({"error": True, "message": "Données invalides"}), 400
    
    # Validation des champs requis
    required_fields = ['name', 'user_id', 'status']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": True, "message": f"Champ {field} requis"}), 400
    
    query = """
        INSERT INTO wp_ab_experiments 
        (user_id, name, url, status, parameters, boundaries, weekly_data, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
    """
    
    params = (
        data['user_id'],
        data['name'],
        data.get('url', ''),
        data['status'],
        json.dumps(data.get('parameters', {})),
        json.dumps(data.get('boundaries', [])),
        json.dumps(data.get('weeklyData', {}))
    )
    
    experiment_id = execute_query(query, params)
    
    if experiment_id is None:
        return jsonify({"error": True, "message": "Erreur lors de la création"}), 500
    
    # Récupérer l'expérimentation créée
    experiment = execute_query(
        "SELECT * FROM wp_ab_experiments WHERE id = %s", 
        (experiment_id,), 
        fetch='one'
    )
    
    return jsonify({"error": False, "experiment": experiment})

@app.route('/api/experiments/<int:experiment_id>', methods=['GET'])
def get_experiment(experiment_id):
    """Récupère une expérimentation spécifique"""
    query = "SELECT * FROM wp_ab_experiments WHERE id = %s"
    experiment = execute_query(query, (experiment_id,), fetch='one')
    
    if not experiment:
        return jsonify({"error": True, "message": "Expérimentation non trouvée"}), 404
    
    # Parse JSON fields
    experiment['parameters'] = json.loads(experiment['parameters']) if experiment['parameters'] else {}
    experiment['boundaries'] = json.loads(experiment['boundaries']) if experiment['boundaries'] else []
    experiment['weekly_data'] = json.loads(experiment['weekly_data']) if experiment['weekly_data'] else {}
    
    return jsonify({"error": False, "experiment": experiment})

@app.route('/api/experiments/<int:experiment_id>', methods=['PUT'])
def update_experiment(experiment_id):
    """Met à jour une expérimentation"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": True, "message": "Données invalides"}), 400
    
    # Construction dynamique de la requête UPDATE
    update_fields = []
    params = []
    
    allowed_fields = ['name', 'url', 'status', 'parameters', 'boundaries', 'weekly_data']
    
    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field} = %s")
            if field in ['parameters', 'boundaries', 'weekly_data']:
                params.append(json.dumps(data[field]))
            else:
                params.append(data[field])
    
    if not update_fields:
        return jsonify({"error": True, "message": "Aucune donnée à mettre à jour"}), 400
    
    update_fields.append("updated_at = NOW()")
    params.append(experiment_id)
    
    query = f"UPDATE wp_ab_experiments SET {', '.join(update_fields)} WHERE id = %s"
    
    result = execute_query(query, params)
    
    if result is None:
        return jsonify({"error": True, "message": "Erreur lors de la mise à jour"}), 500
    
    return jsonify({"error": False, "message": "Expérimentation mise à jour"})

@app.route('/api/experiments/<int:experiment_id>', methods=['DELETE'])
def delete_experiment(experiment_id):
    """Supprime une expérimentation"""
    # Vérifier que l'expérimentation existe
    experiment = execute_query(
        "SELECT id FROM wp_ab_experiments WHERE id = %s", 
        (experiment_id,), 
        fetch='one'
    )
    
    if not experiment:
        return jsonify({"error": True, "message": "Expérimentation non trouvée"}), 404
    
    # Supprimer les liens de partage associés
    execute_query("DELETE FROM wp_ab_experiment_shares WHERE experiment_id = %s", (experiment_id,))
    
    # Supprimer l'expérimentation
    result = execute_query("DELETE FROM wp_ab_experiments WHERE id = %s", (experiment_id,))
    
    if result is None:
        return jsonify({"error": True, "message": "Erreur lors de la suppression"}), 500
    
    return jsonify({"error": False, "message": "Expérimentation supprimée"})

@app.route('/api/experiments/<int:experiment_id>/share', methods=['POST'])
def create_share_link(experiment_id):
    """Crée un lien de partage protégé par mot de passe"""
    data = request.get_json()
    password = data.get('password')
    
    if not password:
        return jsonify({"error": True, "message": "Mot de passe requis"}), 400
    
    # Vérifier que l'expérimentation existe
    experiment = execute_query(
        "SELECT id FROM wp_ab_experiments WHERE id = %s", 
        (experiment_id,), 
        fetch='one'
    )
    
    if not experiment:
        return jsonify({"error": True, "message": "Expérimentation non trouvée"}), 404
    
    # Générer un token unique
    share_token = secrets.token_urlsafe(32)
    
    # Hasher le mot de passe
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Supprimer les anciens liens de partage pour cette expérimentation
    execute_query("DELETE FROM wp_ab_experiment_shares WHERE experiment_id = %s", (experiment_id,))
    
    # Créer le nouveau lien
    query = """
        INSERT INTO wp_ab_experiment_shares 
        (experiment_id, share_token, password_hash, created_at, expires_at)
        VALUES (%s, %s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY))
    """
    
    result = execute_query(query, (experiment_id, share_token, password_hash))
    
    if result is None:
        return jsonify({"error": True, "message": "Erreur lors de la création du lien"}), 500
    
    # Construire l'URL de partage
    base_url = request.host_url.rstrip('/')
    share_url = f"{base_url}/shared/{share_token}"
    
    return jsonify({
        "error": False, 
        "share_url": share_url,
        "token": share_token,
        "expires_in_days": 30
    })

@app.route('/api/shared/<share_token>', methods=['POST'])
def access_shared_experiment(share_token):
    """Accède à une expérimentation partagée avec mot de passe"""
    data = request.get_json()
    password = data.get('password')
    
    if not password:
        return jsonify({"error": True, "message": "Mot de passe requis"}), 400
    
    # Récupérer le lien de partage
    query = """
        SELECT s.experiment_id, s.password_hash, e.name, e.url, e.status, 
               e.parameters, e.boundaries, e.weekly_data, e.created_at
        FROM wp_ab_experiment_shares s
        JOIN wp_ab_experiments e ON s.experiment_id = e.id
        WHERE s.share_token = %s AND s.expires_at > NOW()
    """
    
    share_data = execute_query(query, (share_token,), fetch='one')
    
    if not share_data:
        return jsonify({"error": True, "message": "Lien invalide ou expiré"}), 404
    
    # Vérifier le mot de passe
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if password_hash != share_data['password_hash']:
        return jsonify({"error": True, "message": "Mot de passe incorrect"}), 401
    
    # Préparer les données de l'expérimentation (sans données sensibles)
    experiment_data = {
        'id': share_data['experiment_id'],
        'name': share_data['name'],
        'url': share_data['url'],
        'status': share_data['status'],
        'created_at': share_data['created_at'],
        'parameters': json.loads(share_data['parameters']) if share_data['parameters'] else {},
        'boundaries': json.loads(share_data['boundaries']) if share_data['boundaries'] else [],
        'weekly_data': json.loads(share_data['weekly_data']) if share_data['weekly_data'] else {}
    }
    
    return jsonify({"error": False, "experiment": experiment_data, "readonly": True})

# --- Endpoint de Calcul (Existant) ---
@app.route('/api/calculate-boundaries', methods=['POST'])
def calculate_boundaries():
    """Endpoint existant pour le calcul des bornes séquentielles"""
    print("--> Requête reçue sur /api/calculate-boundaries")
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

    # Bloc TRY principal pour l'exécution du subprocess
    try:
        # Exécution du script R
        proc = subprocess.run(command,
                              capture_output=True,
                              text=True,
                              check=False,
                              timeout=30)

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

        # Bloc TRY interne pour le parsing JSON
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

    except FileNotFoundError:
         print(f"Erreur critique: '{R_EXECUTABLE}' ou '{R_SCRIPT_PATH}' non trouvé.")
         return jsonify({"error": True, "message": "Fichier Rscript ou script R introuvable sur le serveur."}), 500
    except subprocess.TimeoutExpired:
         print("Erreur: Timeout du script R.")
         return jsonify({"error": True, "message": "Le calcul R a dépassé le délai."}), 500
    except Exception as e:
        print(f"Erreur serveur inattendue: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return jsonify({"error": True, "message": f"Erreur serveur inattendue: {e}"}), 500

# --- Point de terminaison pour vérifier si l'API est en ligne ---
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "API GST v2.0 en ligne"})

# --- Point de terminaison pour créer les tables (utilitaire) ---
@app.route('/api/setup-database', methods=['POST'])
def setup_database():
    """Crée les tables nécessaires (à utiliser une seule fois)"""
    
    # Authentification basique pour sécuriser cet endpoint
    auth_token = request.headers.get('Authorization')
    expected_token = os.getenv('SETUP_TOKEN', 'setup_secret_token')
    
    if not auth_token or auth_token != f"Bearer {expected_token}":
        return jsonify({"error": True, "message": "Non autorisé"}), 401
    
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": True, "message": "Impossible de se connecter à la base"}), 500
        
        cursor = connection.cursor()
        
        # Création table expérimentations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wp_ab_experiments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name VARCHAR(255) NOT NULL,
                url TEXT,
                status ENUM('actif', 'brouillon', 'termine') DEFAULT 'brouillon',
                parameters JSON,
                boundaries JSON,
                weekly_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Création table partages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wp_ab_experiment_shares (
                id INT AUTO_INCREMENT PRIMARY KEY,
                experiment_id INT NOT NULL,
                share_token VARCHAR(64) UNIQUE NOT NULL,
                password_hash VARCHAR(64) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (experiment_id) REFERENCES wp_ab_experiments(id) ON DELETE CASCADE,
                INDEX idx_share_token (share_token),
                INDEX idx_expires_at (expires_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"error": False, "message": "Tables créées avec succès"})
        
    except Error as e:
        return jsonify({"error": True, "message": f"Erreur création tables: {e}"}), 500

# --- Gestion des erreurs globales ---
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": True, "message": "Endpoint non trouvé"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": True, "message": "Erreur serveur interne"}), 500

if __name__ == '__main__':
    # Pour le développement uniquement
    app.run(debug=True, host='0.0.0.0', port=8080)

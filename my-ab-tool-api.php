<?php
/**
 * Plugin Name:       Mon Outil A/B - Intégration API
 * Plugin URI:        https://fwoptimisation.com/mon-outil-ab
 * Description:       Fournit les endpoints API REST pour l'outil d'analyse séquentielle A/B et gère la logique backend, y compris l'intégration PMSP et la gestion des clés API Piano utilisateur.
 * Version:           1.0.2
 * Author:            Fauveaux Mathieu
 * Author URI:        https://fwoptimisation.com
 * License:           GPL v2 or later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       myabtool
 * Domain Path:       /languages
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit; // Exit if accessed directly.
}

define('MYABTOOL_ENCRYPTION_KEY_ENV_VAR', 'MYABTOOL_ENCRYPTION_KEY');
define('MYABTOOL_CIPHER_METHOD', 'aes-256-cbc');
define('MYABTOOL_USER_META_PREFIX', 'myabtool_exp_');
define('MYABTOOL_PIANO_API_KEY_META', 'myabtool_piano_api_key_v2');
define('MYABTOOL_PIANO_SITE_ID_META', 'myabtool_piano_site_id_v2');

/**
 * Récupère la clé de chiffrement depuis les variables d'environnement.
 * La variable d'environnement DOIT contenir une clé binaire de 32 octets, encodée en base64.
 */
function myabtool_get_encryption_key_binary() {
    static $binary_key = null;
    if ($binary_key === null) {
        $env_key_base64 = getenv(MYABTOOL_ENCRYPTION_KEY_ENV_VAR);
        if (empty($env_key_base64)) {
            error_log('MYABTOOL ERROR: MYABTOOL_ENCRYPTION_KEY environment variable is not set. Encryption/Decryption will fail.');
            if (defined('WP_DEBUG') && WP_DEBUG) { // Pour ne pas planter le site en dev si la clé n'est pas là
                return str_pad('!!INSECURE_DEV_KEY_32_BYTES!!', 32, "\0"); 
            }
            return null;
        }

        $decoded_key = base64_decode($env_key_base64, true);
        if ($decoded_key === false || strlen($decoded_key) !== 32) {
            error_log('MYABTOOL ERROR: MYABTOOL_ENCRYPTION_KEY from environment is not a valid base64 encoded 32-byte key. Length after decode: ' . strlen($decoded_key));
             if (defined('WP_DEBUG') && WP_DEBUG) {
                return str_pad('!!INSECURE_DEV_KEY_32_BYTES!!', 32, "\0");
            }
            return null;
        }
        $binary_key = $decoded_key;
    }
    return $binary_key;
}

/**
 * Chiffre les données.
 */
function myabtool_encrypt_data($data_string) {
    $key = myabtool_get_encryption_key_binary();
    if (!$key || $data_string === null || $data_string === '') {
        error_log('MYABTOOL Encrypt: Invalid key or empty data string.');
        return null;
    }

    $ivlen = openssl_cipher_iv_length(MYABTOOL_CIPHER_METHOD);
    if ($ivlen === false) {
        error_log('MYABTOOL Encrypt: Unknown cipher method: ' . MYABTOOL_CIPHER_METHOD);
        return null;
    }
    $iv = openssl_random_pseudo_bytes($ivlen);
    $ciphertext_raw = openssl_encrypt($data_string, MYABTOOL_CIPHER_METHOD, $key, OPENSSL_RAW_DATA, $iv);
    
    if ($ciphertext_raw === false) {
        error_log('MYABTOOL Encrypt: openssl_encrypt failed. Error: ' . openssl_error_string());
        return null;
    }
    return base64_encode($iv . $ciphertext_raw);
}

/**
 * Déchiffre les données.
 */
function myabtool_decrypt_data($encrypted_string_base64) {
    $key = myabtool_get_encryption_key_binary();
    if (!$key || empty($encrypted_string_base64)) {
        error_log('MYABTOOL Decrypt: Invalid key or empty encrypted string.');
        return null;
    }

    $encrypted_data_with_iv = base64_decode($encrypted_string_base64, true);
    if ($encrypted_data_with_iv === false) {
        error_log('MYABTOOL Decrypt: base64_decode failed.');
        return null;
    }

    $ivlen = openssl_cipher_iv_length(MYABTOOL_CIPHER_METHOD);
    if ($ivlen === false) {
        error_log('MYABTOOL Decrypt: Unknown cipher method: ' . MYABTOOL_CIPHER_METHOD);
        return null;
    }

    if (strlen($encrypted_data_with_iv) < $ivlen) {
        error_log('MYABTOOL Decrypt: Encrypted data too short. Length: ' . strlen($encrypted_data_with_iv) . ', IVLen: ' . $ivlen);
        return null;
    }
    $iv = substr($encrypted_data_with_iv, 0, $ivlen);
    $ciphertext_raw = substr($encrypted_data_with_iv, $ivlen);

    $original_plaintext = openssl_decrypt($ciphertext_raw, MYABTOOL_CIPHER_METHOD, $key, OPENSSL_RAW_DATA, $iv);
    
    if ($original_plaintext === false) {
        error_log('MYABTOOL Decrypt: openssl_decrypt failed. Error: ' . openssl_error_string());
        return null;
    }
    return $original_plaintext;
}

/**
 * Enregistre les routes API REST.
 */
function myabtool_register_rest_routes() {
    $namespace = 'myabtool/v1';

    // Hook pour ajouter les en-têtes CORS
    // Note: 'rest_pre_serve_request' est un bon endroit, mais on peut aussi le faire plus tôt si besoin.
    // S'assurer que cela ne cause pas de conflits avec d'autres plugins gérant CORS.
    add_filter( 'rest_pre_serve_request', 'myabtool_add_cors_headers', 10, 4 );


    register_rest_route( $namespace, '/check-access', array(
        'methods'             => 'GET',
        'callback'            => 'myabtool_check_access_callback',
        'permission_callback' => 'myabtool_user_logged_in_permission_check', 
    ) );

    register_rest_route( $namespace, '/piano-config', array(
        array(
            'methods'             => 'POST',
            'callback'            => 'myabtool_save_piano_config_callback',
            'permission_callback' => 'myabtool_user_logged_in_permission_check_with_nonce',
        ),
        array( 
            'methods'             => 'GET',
            'callback'            => 'myabtool_get_piano_config_callback',
            'permission_callback' => 'myabtool_user_logged_in_permission_check',
        ),
    ) );

    register_rest_route( $namespace, '/experiments', array(
        array(
            'methods'             => 'GET',
            'callback'            => 'myabtool_get_experiments_callback',
            'permission_callback' => 'myabtool_user_logged_in_permission_check',
        ),
        array(
            'methods'             => 'POST',
            'callback'            => 'myabtool_save_experiment_callback',
            'permission_callback' => 'myabtool_user_logged_in_permission_check_with_nonce',
        ),
    ) );

    register_rest_route( $namespace, '/experiments/(?P<test_name_slug>[a-zA-Z0-9\-_]+)', array(
        'methods'             => 'DELETE',
        'callback'            => 'myabtool_delete_experiment_callback',
        'permission_callback' => 'myabtool_user_logged_in_permission_check_with_nonce',
        'args'                => array(
            'test_name_slug' => array( 'validate_callback' => function($param) { return is_string( $param ) && !empty($param); } )
        ),
    ) );
    
    register_rest_route( $namespace, '/get-piano-data-proxy', array(
        'methods'  => 'POST',
        'callback' => 'myabtool_piano_proxy_callback',
        'permission_callback' => 'myabtool_user_logged_in_permission_check_with_nonce', // Sécuriser aussi cet appel
    ));
}
add_action( 'rest_api_init', 'myabtool_register_rest_routes' );


/**
 * Ajoute les en-têtes CORS.
 */
function myabtool_add_cors_headers( $served, $result, $request, $server ) {
    // Remplacez par l'URL de votre site WordPress où l'outil est hébergé
    // ATTENTION: Ne mettez PAS '*' en production si vous utilisez 'Access-Control-Allow-Credentials: true'
    $allowed_origin = 'https://fwoptimisation.com'; // Mettez votre domaine WordPress ici

    $origin = get_http_origin();
    if ($origin && (strtolower($origin) === strtolower($allowed_origin) || (defined('WP_DEBUG') && WP_DEBUG && $origin === '*'))) { // Permettre '*' en debug si besoin
        header( 'Access-Control-Allow-Origin: ' . $origin );
        header( 'Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS' );
        header( 'Access-Control-Allow-Headers: Content-Type, X-WP-Nonce, Authorization, X-Requested-With' );
        header( 'Access-Control-Allow-Credentials: true' );
        header( 'Vary: Origin' ); // Important pour le caching
    }
    
    // Si c'est une requête OPTIONS (pre-flight), on arrête ici après avoir envoyé les headers
    if ( 'OPTIONS' === $request->get_method() ) {
        status_header( 200 ); // Répondre OK aux requêtes pre-flight
        exit(); // Important pour terminer la requête pre-flight
    }

    return $served; // Doit retourner $served pour que la requête continue
}


/**
 * Callback de permission : Vérifie si l'utilisateur est connecté.
 */
function myabtool_user_logged_in_permission_check( WP_REST_Request $request ) {
    if ( !is_user_logged_in() ) {
        return new WP_Error( 'rest_not_logged_in', 'Vous devez être connecté pour effectuer cette action.', array( 'status' => 401 ) );
    }
    return true;
}

/**
 * Callback de permission : Vérifie si l'utilisateur est connecté ET valide le nonce.
 */
function myabtool_user_logged_in_permission_check_with_nonce( WP_REST_Request $request ) {
    if ( !is_user_logged_in() ) {
        return new WP_Error( 'rest_not_logged_in', 'Vous devez être connecté pour effectuer cette action.', array( 'status' => 401 ) );
    }
    // Pour les requêtes qui modifient des données, on vérifie le nonce
    $nonce = $request->get_header( 'X-WP-Nonce' );
    if ( ! $nonce || ! wp_verify_nonce( $nonce, 'wp_rest' ) ) {
        return new WP_Error( 'rest_cookie_invalid_nonce', 'Le jeton de sécurité (nonce) est invalide.', array( 'status' => 403 ) );
    }
    return true;
}


/**
 * Callback pour /check-access.
 * Vérifie si l'utilisateur a un abonnement PMSP actif.
 */
function myabtool_check_access_callback( WP_REST_Request $request ) {
    $user_id = get_current_user_id();

    // !! IMPORTANT : REMPLACEZ CES ID PAR LES VRAIS ID DE VOS PLANS PMSP !!
    $required_subscription_plan_ids = array(11156, 11155); // Exemple: Plan ID 123 et Plan ID 456
    $has_active_subscription = false;

    if ( !function_exists('pms_get_member_subscriptions') ) {
        error_log('MYABTOOL ERROR: Paid Member Subscriptions Pro function pms_get_member_subscriptions() not found.');
        return new WP_REST_Response( array( 'has_access' => false, 'message' => 'Erreur de configuration: Plugin d\'abonnement non détecté ou fonction indisponible.' ), 500 );
    }

    $member_subscriptions = pms_get_member_subscriptions( array( 'user_id' => $user_id ) );

    if ( !empty($member_subscriptions) ) {
        foreach ( $member_subscriptions as $subscription ) {
            // Vérifier si l'ID du plan est dans notre liste requise ET si le statut est actif
            if ( in_array( $subscription->subscription_plan_id, $required_subscription_plan_ids ) && $subscription->status === 'active' ) {
                $has_active_subscription = true;
                break;
            }
        }
    }

    if ( !$has_active_subscription ) {
        return new WP_REST_Response( array( 'has_access' => false, 'message' => 'Un abonnement actif est requis pour utiliser cet outil.' ), 200 ); // Renvoyer 200 pour que le JS puisse lire le message
    }

    return new WP_REST_Response( array( 'has_access' => true, 'message' => 'Accès autorisé.' ), 200 );
}


function myabtool_get_meta_key_for_test($test_name) {
    $slug = sanitize_title( $test_name );
    return MYABTOOL_USER_META_PREFIX . $slug;
}

function myabtool_save_piano_config_callback( WP_REST_Request $request ) {
    $user_id = get_current_user_id();
    $params = $request->get_json_params();
    $api_key = isset($params['api_key']) ? sanitize_text_field($params['api_key']) : null;
    $site_id = isset($params['site_id']) ? sanitize_text_field($params['site_id']) : null;

    if (empty($api_key) || empty($site_id)) {
        return new WP_Error('missing_params', 'Clé API et ID de site sont requis.', array('status' => 400));
    }
    if (!ctype_digit($site_id)) {
         return new WP_Error('invalid_site_id', 'L\'ID de site Piano doit être numérique.', array('status' => 400));
    }

    $encrypted_api_key = myabtool_encrypt_data($api_key);
    if ($encrypted_api_key === null) {
         return new WP_Error('encryption_failed', 'Échec du chiffrement de la clé API.', array('status' => 500));
    }

    update_user_meta($user_id, MYABTOOL_PIANO_API_KEY_META, $encrypted_api_key);
    update_user_meta($user_id, MYABTOOL_PIANO_SITE_ID_META, $site_id);

    return new WP_REST_Response(array('success' => true, 'message' => 'Configuration Piano sauvegardée.'), 200);
}

function myabtool_get_piano_config_callback( WP_REST_Request $request ) {
    $user_id = get_current_user_id();
    $site_id = get_user_meta($user_id, MYABTOOL_PIANO_SITE_ID_META, true);
    $api_key_is_set = !empty(get_user_meta($user_id, MYABTOOL_PIANO_API_KEY_META, true));

    return new WP_REST_Response(array(
        'success' => true, 
        'site_id' => $site_id ? $site_id : null,
        'api_key_set' => $api_key_is_set 
    ), 200);
}

function myabtool_get_experiments_callback( WP_REST_Request $request ) {
    $user_id = get_current_user_id();
    global $wpdb;
    $meta_keys_query = $wpdb->prepare(
        "SELECT meta_key, meta_value FROM {$wpdb->usermeta} WHERE user_id = %d AND meta_key LIKE %s",
        $user_id,
        $wpdb->esc_like(MYABTOOL_USER_META_PREFIX) . '%'
    );
    $user_meta_results = $wpdb->get_results($meta_keys_query);

    $experiments = array();
    if ($user_meta_results) {
        foreach ( $user_meta_results as $meta_entry ) {
            $experiment_data = json_decode($meta_entry->meta_value, true);
            if (is_array($experiment_data) && isset($experiment_data['name'])) {
                $experiments[] = $experiment_data;
            }
        }
    }
    return new WP_REST_Response( $experiments, 200 );
}

function myabtool_save_experiment_callback( WP_REST_Request $request ) {
    $user_id = get_current_user_id();
    $test_state = $request->get_json_params();

    if ( empty( $test_state ) || !isset( $test_state['name'] ) || empty(trim($test_state['name'])) ) {
        return new WP_Error( 'missing_data', 'Données de test ou nom de test invalide manquant.', array( 'status' => 400 ) );
    }

    $meta_key = myabtool_get_meta_key_for_test( $test_state['name'] );

    $result = update_user_meta( $user_id, $meta_key, wp_json_encode($test_state) );

    if ( false === $result && !get_user_meta($user_id, $meta_key, true) ) {
        return new WP_Error( 'save_error', 'Erreur lors de la sauvegarde de l\'expérimentation.', array( 'status' => 500 ) );
    }
    return new WP_REST_Response( array( 'success' => true, 'message' => 'Expérimentation sauvegardée.' ), 200 );
}

function myabtool_delete_experiment_callback( WP_REST_Request $request ) {
    $user_id = get_current_user_id();
    $test_name_slug = $request['test_name_slug']; 
    $meta_key = MYABTOOL_USER_META_PREFIX . $test_name_slug;

    if ( delete_user_meta( $user_id, $meta_key ) ) {
        return new WP_REST_Response( array( 'success' => true, 'message' => 'Expérimentation supprimée.' ), 200 );
    } else {
        return new WP_Error( 'delete_error', 'Erreur lors de la suppression ou expérimentation non trouvée.', array( 'status' => 404 ) );
    }
}

function myabtool_piano_proxy_callback( WP_REST_Request $request ) {
    $user_id = get_current_user_id();

    $user_piano_api_key_encrypted = get_user_meta($user_id, MYABTOOL_PIANO_API_KEY_META, true);
    $user_piano_site_id = get_user_meta($user_id, MYABTOOL_PIANO_SITE_ID_META, true);

    if (empty($user_piano_api_key_encrypted) || empty($user_piano_site_id)) {
        return new WP_Error('piano_config_missing', 'Configuration Piano Analytics (clé API ou ID de site) manquante pour cet utilisateur. Veuillez l\'enregistrer dans la section "Configuration Piano Analytics" de l\'outil.', array('status' => 400));
    }

    $piano_api_key = myabtool_decrypt_data($user_piano_api_key_encrypted);
    if (!$piano_api_key) {
         return new WP_Error('decryption_failed', 'Échec du déchiffrement de la clé API Piano. Vérifiez la clé de chiffrement du serveur.', array('status' => 500));
    }

    $params_from_frontend = $request->get_json_params();
    $test_id_filter = isset($params_from_frontend['test_id']) ? sanitize_text_field($params_from_frontend['test_id']) : null;
    $start_date     = isset($params_from_frontend['start_date']) ? sanitize_text_field($params_from_frontend['start_date']) : null;
    $end_date       = isset($params_from_frontend['end_date']) ? sanitize_text_field($params_from_frontend['end_date']) : null;

    if (!$test_id_filter || !$start_date || !$end_date) {
        return new WP_Error('missing_proxy_params', 'Paramètres manquants pour la requête Piano proxy (ID test, date début/fin).', array('status' => 400));
    }

    $piano_request_params = array(
        "columns"     => array("mv_test", "mv_creation", "m_unique_visitors", "m_conv1_visitors"),
        "sort"        => array("-m_unique_visitors"),
        "filter"      => array("property" => array("mv_test" => array("\$eq" => $test_id_filter))),
        "space"       => array("s" => array(intval($user_piano_site_id))),
        "period"      => array("p1" => array(array("type" => "D", "start" => $start_date, "end" => $end_date))),
        "max-results" => 50, 
        "page-num"    => 1
    );

    $base_url      = "https://api.atinternet.io/v3/data/getData";
    $encoded_params = urlencode(json_encode($piano_request_params));
    $request_url   = "{$base_url}?param={$encoded_params}";

    $headers = array( 'X-API-Key' => $piano_api_key ); 
    
    $piano_response = wp_remote_get( $request_url, array(
        'headers' => $headers,
        'timeout' => 25, 
    ) );

    if ( is_wp_error( $piano_response ) ) {
        return new WP_Error('piano_request_failed', 'Erreur de communication avec l\'API Piano: ' . $piano_response->get_error_message(), array('status' => 502));
    }

    $response_code = wp_remote_retrieve_response_code( $piano_response );
    $response_body = wp_remote_retrieve_body( $piano_response );
    $piano_data    = json_decode( $response_body, true );

    if ( $response_code >= 400 || !$piano_data ) {
        $error_message = isset($piano_data['message']) ? $piano_data['message'] : (isset($piano_data['error']['message']) ? $piano_data['error']['message'] : $response_body);
        error_log("MYABTOOL Piano API Error ({$response_code}): " . $response_body);
        return new WP_Error('piano_api_error', "Erreur de l'API Piano ({$response_code}): " . esc_html(substr($error_message, 0, 200)), array('status' => $response_code));
    }

    $processed_data = array();
    if (isset($piano_data["DataFeed"]) && count($piano_data["DataFeed"]) > 0 && isset($piano_data["DataFeed"][0]["Rows"])) {
        $rows = $piano_data["DataFeed"][0]["Rows"];
        $distinct_creations = array();
        foreach ($rows as $row) {
            $mv_creation_name = isset($row["mv_creation"]) ? $row["mv_creation"] : null;
            if ($mv_creation_name && !isset($distinct_creations[$mv_creation_name])) { 
                $distinct_creations[$mv_creation_name] = array(
                    "mv_creation" => $mv_creation_name,
                    "visitors"    => isset($row["m_unique_visitors"]) ? intval($row["m_unique_visitors"]) : 0,
                    "conversions" => isset($row["m_conv1_visitors"]) ? intval($row["m_conv1_visitors"]) : 0
                );
            }
        }
        $processed_data = array_values($distinct_creations);
    }

    if (empty($processed_data)) {
        return new WP_REST_Response(array('success' => false, 'message' => 'Aucune donnée de variation trouvée pour ce test et cette période dans Piano. Vérifiez les filtres et la disponibilité des données.', 'data' => array()), 200);
    }

    return new WP_REST_Response(array('success' => true, 'message' => 'Données récupérées avec succès.', 'data' => $processed_data), 200);
}

/**
 * Enqueue scripts and localize data for the frontend, including REST API nonce.
 */
function myabtool_frontend_tool_scripts() {
    // Remplacez 'slug-de-votre-page-outil' par le slug réel de la page où l'outil est affiché
    if ( is_page('slug-de-votre-page-outil') || is_page_template('page-template-ab-tool.php') ) { 
        // Si vous avez un fichier JS séparé pour l'outil:
        // wp_enqueue_script( 
        // 'myabtool-main-script', 
        // plugin_dir_url( __FILE__ ) . 'js/ab-tool-main.js', // Assurez-vous que ce chemin est correct
        // array('jquery', 'highcharts'), // Dépendances
        // '1.0.2', // Version de votre script
        // true // Charger dans le footer
        // );

        // Passer des données au script, y compris l'URL de base de l'API REST et le nonce
        wp_localize_script( 'myabtool-main-script', // Le handle de votre script principal
            'myabtool_vars', 
            array(
                'rest_url' => esc_url_raw( rest_url( 'myabtool/v1/' ) ), 
                'nonce'    => wp_create_nonce( 'wp_rest' ) // Nonce standard pour l'API REST
            ) 
        );
    }
}
// Décommentez et ajustez cette ligne si vous mettez votre JS principal en file d'attente.
// add_action( 'wp_enqueue_scripts', 'myabtool_frontend_tool_scripts' );

?>
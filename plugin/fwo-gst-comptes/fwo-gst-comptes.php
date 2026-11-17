<?php
/**
 * Plugin Name: FWO - Comptes du calculateur séquentiel
 * Description: Comptes, tableau de bord et partage par invitation pour le calculateur d'analyse séquentielle. Connexion par lien envoyé par email, sans mot de passe.
 * Version: 0.1.0
 * Author: FWOptimisation
 * Requires at least: 6.0
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

const FWO_GST_NS        = 'fwo-gst/v1';
const FWO_GST_CPT       = 'fwo_gst_test';
const FWO_GST_MAX_TESTS = 200;      // tests par compte
const FWO_GST_MAX_BYTES = 400000;   // taille d'un test (JSON)
const FWO_GST_MAX_SHARE = 20;       // invités par test
const FWO_GST_TTL       = 900;      // durée de vie d'un lien de connexion (secondes)

/** Page de l'outil : modifiable par le filtre fwo_gst_tool_url. */
function fwo_gst_tool_url() {
    return apply_filters('fwo_gst_tool_url', home_url('/calculateur-analyse-sequentielle-ab-test/'));
}

add_action('init', function () {
    register_post_type(FWO_GST_CPT, [
        'public' => false, 'show_ui' => false, 'show_in_rest' => false, 'exclude_from_search' => true,
        'supports' => ['title', 'author'], 'rewrite' => false, 'query_var' => false,
    ]);
});

/** Les comptes créés ici sont de simples abonnés : pas de barre d'administration, pas d'accès à wp-admin. */
add_filter('show_admin_bar', function ($show) { return current_user_can('edit_posts') ? $show : false; });
add_action('admin_init', function () {
    if (is_user_logged_in() && !current_user_can('edit_posts') && !wp_doing_ajax()) { wp_safe_redirect(fwo_gst_tool_url()); exit; }
});

function fwo_gst_ip() { return isset($_SERVER['REMOTE_ADDR']) ? sanitize_text_field(wp_unslash($_SERVER['REMOTE_ADDR'])) : '0'; }

/** Limite de débit : $max essais par fenêtre de $ttl secondes pour une clé. */
function fwo_gst_throttle($key, $max, $ttl) {
    $k = 'fwo_gst_rl_' . md5($key); $n = (int) get_transient($k);
    if ($n >= $max) { return false; }
    set_transient($k, $n + 1, $ttl); return true;
}

function fwo_gst_auth() { return is_user_logged_in(); }

function fwo_gst_user_payload() {
    if (!is_user_logged_in()) { return null; }
    $u = wp_get_current_user();
    return ['email' => $u->user_email, 'name' => $u->display_name];
}

function fwo_gst_shares($id) {
    $s = get_post_meta($id, '_fwo_gst_share', false);
    return array_values(array_unique(array_map('strval', is_array($s) ? $s : [])));
}

/** Accès à un test : 'owner', 'guest' ou false. */
function fwo_gst_access($post) {
    if (!$post || $post->post_type !== FWO_GST_CPT || $post->post_status !== 'private') { return false; }
    $u = wp_get_current_user();
    if ((int) $post->post_author === (int) $u->ID) { return 'owner'; }
    return in_array(strtolower($u->user_email), fwo_gst_shares($post->ID), true) ? 'guest' : false;
}

function fwo_gst_row($post, $access) {
    $sum = json_decode((string) get_post_meta($post->ID, '_fwo_gst_sum', true), true);
    $owner = get_userdata($post->post_author);
    return [
        'id' => $post->ID, 'name' => $post->post_title, 'sum' => is_array($sum) ? $sum : null,
        'updated' => mysql2date('Y-m-d', $post->post_modified), 'mine' => $access === 'owner',
        'owner' => $owner ? $owner->display_name : '', 'shared' => $access === 'owner' ? fwo_gst_shares($post->ID) : [],
    ];
}

/** Valide et normalise le corps d'un test. Renvoie WP_Error ou [nom, état JSON, résumé JSON]. */
function fwo_gst_payload(WP_REST_Request $r) {
    $name = sanitize_text_field((string) $r->get_param('name'));
    if ($name === '') { return new WP_Error('fwo_gst_name', 'Nom du test manquant.', ['status' => 400]); }
    $state = $r->get_param('state'); $sum = $r->get_param('sum');
    if (!is_array($state) || !isset($state['plan'], $state['metrics'], $state['weeks'])) { return new WP_Error('fwo_gst_state', 'Test illisible.', ['status' => 400]); }
    $js = wp_json_encode($state);
    if ($js === false || strlen($js) > FWO_GST_MAX_BYTES) { return new WP_Error('fwo_gst_size', 'Test trop volumineux.', ['status' => 413]); }
    $keep = [];
    if (is_array($sum)) { foreach (['t', 'c', 'm', 'd', 'u'] as $k) { if (isset($sum[$k])) { $keep[$k] = sanitize_text_field((string) $sum[$k]); } }
        foreach (['n', 'k', 'dw'] as $k) { if (isset($sum[$k]) && is_numeric($sum[$k])) { $keep[$k] = (int) $sum[$k]; } }
        if (isset($sum['lift']) && is_numeric($sum['lift'])) { $keep['lift'] = (float) $sum['lift']; } }
    return [mb_substr($name, 0, 120), $js, wp_json_encode($keep)];
}

add_action('rest_api_init', function () {
    register_rest_route(FWO_GST_NS, '/me', ['methods' => 'GET', 'permission_callback' => '__return_true', 'callback' => function () {
        return ['enabled' => true, 'user' => fwo_gst_user_payload()];
    }]);

    // Demande d'un lien de connexion. Réponse identique que le compte existe ou non.
    register_rest_route(FWO_GST_NS, '/login-link', ['methods' => 'POST', 'permission_callback' => '__return_true', 'callback' => function (WP_REST_Request $r) {
        $email = strtolower(sanitize_email((string) $r->get_param('email')));
        if (!is_email($email)) { return new WP_Error('fwo_gst_email', 'Adresse email invalide.', ['status' => 400]); }
        if (!fwo_gst_throttle('ip' . fwo_gst_ip(), 8, FWO_GST_TTL) || !fwo_gst_throttle('em' . $email, 3, FWO_GST_TTL)) {
            return new WP_Error('fwo_gst_rate', 'Trop de demandes. Réessayez dans quelques minutes.', ['status' => 429]);
        }
        $u = get_user_by('email', $email);
        if ($u && user_can($u, 'edit_posts')) { return ['sent' => true]; } // jamais de lien pour un compte d'administration
        $token = wp_generate_password(48, false);
        $test = absint($r->get_param('test'));
        set_transient('fwo_gst_tk_' . hash('sha256', $token), ['email' => $email, 'test' => $test], FWO_GST_TTL);
        $link = add_query_arg('token', rawurlencode($token), rest_url(FWO_GST_NS . '/login'));
        wp_mail($email, 'Votre lien de connexion au calculateur séquentiel',
            "Bonjour,\n\nCliquez sur ce lien pour ouvrir votre espace (valable 15 minutes, utilisable une seule fois) :\n" . $link . "\n\nSi vous n'êtes pas à l'origine de cette demande, ignorez ce message.\n\nFWOptimisation");
        return ['sent' => true];
    }]);

    // Clic sur le lien reçu : crée le compte si besoin, ouvre la session, renvoie vers l'outil.
    register_rest_route(FWO_GST_NS, '/login', ['methods' => 'GET', 'permission_callback' => '__return_true', 'callback' => function (WP_REST_Request $r) {
        $back = fwo_gst_tool_url();
        $key = 'fwo_gst_tk_' . hash('sha256', (string) $r->get_param('token'));
        $d = get_transient($key); delete_transient($key);
        if (!fwo_gst_throttle('lg' . fwo_gst_ip(), 20, FWO_GST_TTL) || !is_array($d) || empty($d['email'])) { wp_safe_redirect($back . '#lien-expire'); exit; }
        $u = get_user_by('email', $d['email']);
        if ($u && user_can($u, 'edit_posts')) { wp_safe_redirect($back . '#lien-expire'); exit; }
        if (!$u) {
            $login = sanitize_user(strstr($d['email'], '@', true) . '_' . wp_generate_password(6, false, false), true);
            $id = wp_insert_user(['user_login' => $login, 'user_email' => $d['email'], 'user_pass' => wp_generate_password(32, true, true),
                'display_name' => strstr($d['email'], '@', true), 'role' => 'subscriber']);
            if (is_wp_error($id)) { wp_safe_redirect($back . '#lien-expire'); exit; }
            $u = get_userdata($id);
        }
        wp_set_current_user($u->ID); wp_set_auth_cookie($u->ID, true);
        wp_safe_redirect($back . (!empty($d['test']) ? '#test=' . (int) $d['test'] : '#compte')); exit;
    }]);

    register_rest_route(FWO_GST_NS, '/logout', ['methods' => 'POST', 'permission_callback' => 'fwo_gst_auth', 'callback' => function () { wp_logout(); return ['ok' => true]; }]);

    register_rest_route(FWO_GST_NS, '/tests', [
        ['methods' => 'GET', 'permission_callback' => 'fwo_gst_auth', 'callback' => function () {
            $u = wp_get_current_user(); $out = [];
            $mine = get_posts(['post_type' => FWO_GST_CPT, 'post_status' => 'private', 'author' => $u->ID, 'numberposts' => FWO_GST_MAX_TESTS, 'orderby' => 'modified', 'order' => 'DESC']);
            foreach ($mine as $p) { $out[] = fwo_gst_row($p, 'owner'); }
            $theirs = get_posts(['post_type' => FWO_GST_CPT, 'post_status' => 'private', 'author__not_in' => [$u->ID], 'numberposts' => 200, 'orderby' => 'modified', 'order' => 'DESC',
                'meta_query' => [['key' => '_fwo_gst_share', 'value' => strtolower($u->user_email)]]]);
            foreach ($theirs as $p) { $out[] = fwo_gst_row($p, 'guest'); }
            return ['tests' => $out];
        }],
        ['methods' => 'POST', 'permission_callback' => 'fwo_gst_auth', 'callback' => function (WP_REST_Request $r) {
            $p = fwo_gst_payload($r); if (is_wp_error($p)) { return $p; }
            $n = count(get_posts(['post_type' => FWO_GST_CPT, 'post_status' => 'private', 'author' => get_current_user_id(), 'numberposts' => FWO_GST_MAX_TESTS + 1, 'fields' => 'ids']));
            if ($n >= FWO_GST_MAX_TESTS) { return new WP_Error('fwo_gst_quota', 'Nombre maximal de tests atteint.', ['status' => 409]); }
            $id = wp_insert_post(['post_type' => FWO_GST_CPT, 'post_status' => 'private', 'post_title' => $p[0], 'post_author' => get_current_user_id()], true);
            if (is_wp_error($id)) { return $id; }
            update_post_meta($id, '_fwo_gst_state', wp_slash($p[1])); update_post_meta($id, '_fwo_gst_sum', wp_slash($p[2]));
            return fwo_gst_row(get_post($id), 'owner');
        }],
    ]);

    register_rest_route(FWO_GST_NS, '/tests/(?P<id>\d+)', [
        ['methods' => 'GET', 'permission_callback' => 'fwo_gst_auth', 'callback' => function (WP_REST_Request $r) {
            $post = get_post((int) $r['id']); $a = fwo_gst_access($post);
            if (!$a) { return new WP_Error('fwo_gst_404', 'Test introuvable.', ['status' => 404]); }
            $row = fwo_gst_row($post, $a); $row['state'] = json_decode((string) get_post_meta($post->ID, '_fwo_gst_state', true), true);
            return $row;
        }],
        ['methods' => 'PUT', 'permission_callback' => 'fwo_gst_auth', 'callback' => function (WP_REST_Request $r) {
            $post = get_post((int) $r['id']);
            if (fwo_gst_access($post) !== 'owner') { return new WP_Error('fwo_gst_404', 'Test introuvable.', ['status' => 404]); }
            $p = fwo_gst_payload($r); if (is_wp_error($p)) { return $p; }
            wp_update_post(['ID' => $post->ID, 'post_title' => $p[0]]);
            update_post_meta($post->ID, '_fwo_gst_state', wp_slash($p[1])); update_post_meta($post->ID, '_fwo_gst_sum', wp_slash($p[2]));
            return fwo_gst_row(get_post($post->ID), 'owner');
        }],
        ['methods' => 'DELETE', 'permission_callback' => 'fwo_gst_auth', 'callback' => function (WP_REST_Request $r) {
            $post = get_post((int) $r['id']);
            if (fwo_gst_access($post) !== 'owner') { return new WP_Error('fwo_gst_404', 'Test introuvable.', ['status' => 404]); }
            wp_delete_post($post->ID, true); return ['ok' => true];
        }],
    ]);

    // Invitation : la personne invitée voit le test en lecture seule, avec les données à jour.
    register_rest_route(FWO_GST_NS, '/tests/(?P<id>\d+)/share', [
        ['methods' => 'POST', 'permission_callback' => 'fwo_gst_auth', 'callback' => function (WP_REST_Request $r) {
            $post = get_post((int) $r['id']);
            if (fwo_gst_access($post) !== 'owner') { return new WP_Error('fwo_gst_404', 'Test introuvable.', ['status' => 404]); }
            $email = strtolower(sanitize_email((string) $r->get_param('email')));
            if (!is_email($email)) { return new WP_Error('fwo_gst_email', 'Adresse email invalide.', ['status' => 400]); }
            $s = fwo_gst_shares($post->ID);
            if (!in_array($email, $s, true)) {
                if (count($s) >= FWO_GST_MAX_SHARE) { return new WP_Error('fwo_gst_quota', 'Nombre maximal d\'invités atteint.', ['status' => 409]); }
                if (!fwo_gst_throttle('sh' . get_current_user_id(), 30, HOUR_IN_SECONDS)) { return new WP_Error('fwo_gst_rate', 'Trop d\'invitations. Réessayez plus tard.', ['status' => 429]); }
                add_post_meta($post->ID, '_fwo_gst_share', $email);
                $me = wp_get_current_user();
                wp_mail($email, $me->display_name . ' partage un test A/B avec vous',
                    "Bonjour,\n\n" . $me->display_name . ' (' . $me->user_email . ") vous invite à suivre le test « " . $post->post_title . " ».\n\nOuvrez ce lien, puis connectez-vous avec cette adresse email (" . $email . ") :\n" . fwo_gst_tool_url() . '#test=' . $post->ID . "\n\nFWOptimisation");
            }
            return ['shared' => fwo_gst_shares($post->ID)];
        }],
        ['methods' => 'DELETE', 'permission_callback' => 'fwo_gst_auth', 'callback' => function (WP_REST_Request $r) {
            $post = get_post((int) $r['id']);
            if (fwo_gst_access($post) !== 'owner') { return new WP_Error('fwo_gst_404', 'Test introuvable.', ['status' => 404]); }
            delete_post_meta($post->ID, '_fwo_gst_share', strtolower(sanitize_email((string) $r->get_param('email'))));
            return ['shared' => fwo_gst_shares($post->ID)];
        }],
    ]);

    // Suppression du compte et de ses tests (comptes abonnés uniquement).
    register_rest_route(FWO_GST_NS, '/account', ['methods' => 'DELETE', 'permission_callback' => 'fwo_gst_auth', 'callback' => function () {
        if (current_user_can('edit_posts')) { return new WP_Error('fwo_gst_admin', 'Compte d\'administration : suppression impossible ici.', ['status' => 403]); }
        $id = get_current_user_id();
        foreach (get_posts(['post_type' => FWO_GST_CPT, 'post_status' => 'any', 'author' => $id, 'numberposts' => -1, 'fields' => 'ids']) as $pid) { wp_delete_post($pid, true); }
        require_once ABSPATH . 'wp-admin/includes/user.php';
        wp_logout(); wp_delete_user($id);
        return ['ok' => true];
    }]);
});

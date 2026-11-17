<?php
/**
 * Plugin Name: FWO - Comptes du calculateur séquentiel
 * Description: Comptes, tableau de bord et partage par invitation pour le calculateur d'analyse séquentielle. Connexion par lien envoyé par email, sans mot de passe.
 * Version: 0.3.2
 * Author: FWOptimisation
 * Requires at least: 6.0
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

const FWO_GST_NS        = 'fwo-gst/v1';
const FWO_GST_CPT       = 'fwo_gst_test';
const FWO_GST_ROLE      = 'fwo_gst_user';
const FWO_GST_MAX_TESTS = 50;       // tests par compte
const FWO_GST_MAX_BYTES = 150000;   // taille d'un test (JSON)
const FWO_GST_MAX_MAILS = 150;      // emails envoyés par heure, tous comptes confondus
const FWO_GST_MAX_NEW   = 200;      // comptes créés par jour
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

/** Les comptes créés ici ont un rôle dédié, sans aucune capacité WordPress. */
register_activation_hook(__FILE__, function () { add_role(FWO_GST_ROLE, 'Compte calculateur', []); });
add_action('init', function () { if (!get_role(FWO_GST_ROLE)) { add_role(FWO_GST_ROLE, 'Compte calculateur', []); } }, 5);

function fwo_gst_is_member($user = null) {
    if ($user === false) { return false; }
    $u = $user ? $user : wp_get_current_user();
    return $u && $u->exists() && in_array(FWO_GST_ROLE, (array) $u->roles, true);
}

/** Ces comptes n'ont accès ni à wp-admin, ni à admin-ajax (sauf le jeton REST), ni au reste de l'API REST. */
add_filter('show_admin_bar', function ($show) { return fwo_gst_is_member() ? false : $show; });
add_action('admin_init', function () {
    if (!fwo_gst_is_member()) { return; }
    if (wp_doing_ajax()) {
        $action = isset($_REQUEST['action']) ? sanitize_key(wp_unslash($_REQUEST['action'])) : '';
        if ($action === 'rest-nonce') { return; }
        wp_set_current_user(0); return; // pour le reste du site (formulaires), ce compte est traité comme un visiteur anonyme
    }
    wp_safe_redirect(fwo_gst_tool_url()); exit;
}, 1);
add_filter('rest_pre_dispatch', function ($res, $server, $req) {
    if (fwo_gst_is_member() && strpos($req->get_route(), '/' . FWO_GST_NS . '/') !== 0) {
        wp_set_current_user(0); // hors des routes de l'outil, ce compte est traité comme un visiteur anonyme
    }
    return $res;
}, 10, 3);
/** L'adresse email d'un compte calculateur ne change jamais (elle sert de clé aux invitations). */
add_filter('wp_pre_insert_user_data', function ($data, $update, $id) {
    if ($update && $id && fwo_gst_is_member(get_userdata($id)) && !current_user_can('edit_users')) {
        $old = get_userdata($id); if ($old) { $data['user_email'] = $old->user_email; }
    }
    return $data;
}, 10, 3);
add_filter('wp_is_application_passwords_available_for_user', function ($ok, $u) { return $ok && !fwo_gst_is_member($u); }, 10, 2);
add_filter('allow_password_reset', function ($ok, $id) { return fwo_gst_is_member(get_userdata($id)) ? false : $ok; }, 10, 2);

/** Plages de Cloudflare (cloudflare.com/ips-v4 et ips-v6, relevées le 17 novembre 2026). */
function fwo_gst_cf_ranges() {
    return ['173.245.48.0/20', '103.21.244.0/22', '103.22.200.0/22', '103.31.4.0/22', '141.101.64.0/18', '108.162.192.0/18', '190.93.240.0/20', '188.114.96.0/20',
        '197.234.240.0/22', '198.41.128.0/17', '162.158.0.0/15', '104.16.0.0/13', '104.24.0.0/14', '172.64.0.0/13', '131.0.72.0/22',
        '2400:cb00::/32', '2606:4700::/32', '2803:f800::/32', '2405:b500::/32', '2405:8100::/32', '2a06:98c0::/29', '2c0f:f248::/32'];
}
function fwo_gst_in_range($ip, $cidr) {
    list($net, $bits) = explode('/', $cidr); $a = @inet_pton($ip); $b = @inet_pton($net); $bits = (int) $bits;
    if ($a === false || $b === false || strlen($a) !== strlen($b)) { return false; }
    $full = intdiv($bits, 8); $rem = $bits % 8;
    if ($full && substr($a, 0, $full) !== substr($b, 0, $full)) { return false; }
    if ($rem === 0) { return true; }
    $mask = chr((0xFF << (8 - $rem)) & 0xFF);
    return (($a[$full] & $mask) === ($b[$full] & $mask));
}
/** Adresse du visiteur. Derrière Cloudflare, l'adresse réelle est lue dans CF-Connecting-IP, et seulement si la requête vient bien d'une plage de Cloudflare.
    En IPv6 on retient le préfixe /64 pour qu'un même abonné ne dispose pas de milliards de clés. */
function fwo_gst_ip() {
    $ip = isset($_SERVER['REMOTE_ADDR']) ? sanitize_text_field(wp_unslash($_SERVER['REMOTE_ADDR'])) : '0';
    if (!empty($_SERVER['HTTP_CF_CONNECTING_IP'])) {
        $cf = sanitize_text_field(wp_unslash($_SERVER['HTTP_CF_CONNECTING_IP']));
        if (@inet_pton($cf) !== false) { foreach (fwo_gst_cf_ranges() as $r) { if (fwo_gst_in_range($ip, $r)) { $ip = $cf; break; } } }
    }
    $bin = @inet_pton($ip);
    return ($bin !== false && strlen($bin) === 16) ? bin2hex(substr($bin, 0, 8)) : $ip;
}

/** Envoi d'email sous plafond global : le site ne doit pas pouvoir servir de relais. */
function fwo_gst_mail($to, $subject, $body) {
    if (!fwo_gst_throttle('mail_global', FWO_GST_MAX_MAILS, HOUR_IN_SECONDS)) { return false; }
    return wp_mail($to, $subject, $body);
}

/** Limite de débit : $max essais par fenêtre de $ttl secondes pour une clé. */
function fwo_gst_throttle($key, $max, $ttl) {
    $k = 'fwo_gst_rl_' . md5($key); $v = get_transient($k); $now = time();
    if (!is_array($v) || !isset($v['n'], $v['exp']) || $v['exp'] <= $now) { $v = ['n' => 0, 'exp' => $now + $ttl]; } // fenêtre fixe : l'échéance ne recule pas à chaque appel
    if ($v['n'] >= $max) { return false; }
    $v['n']++; set_transient($k, $v, max(1, $v['exp'] - $now)); return true;
}

/** Les routes de l'outil sont réservées aux comptes calculateur et aux administrateurs du site. */
function fwo_gst_auth() { return fwo_gst_is_member() || current_user_can('manage_options'); }

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

/** Résumé et invités d'une liste de tests en une seule requête, sans charger l'état (volumineux) de chaque test. */
function fwo_gst_meta_light($ids) {
    global $wpdb; $out = [];
    $ids = array_values(array_filter(array_map('intval', $ids)));
    if (!$ids) { return $out; }
    $in = implode(',', $ids);
    $rows = $wpdb->get_results("SELECT post_id, meta_key, meta_value FROM {$wpdb->postmeta} WHERE meta_key IN ('_fwo_gst_sum','_fwo_gst_share') AND post_id IN ($in)");
    foreach ((array) $rows as $r) {
        $pid = (int) $r->post_id; if (!isset($out[$pid])) { $out[$pid] = ['sum' => null, 'share' => []]; }
        if ($r->meta_key === '_fwo_gst_sum') { $j = json_decode((string) $r->meta_value, true); $out[$pid]['sum'] = is_array($j) ? $j : null; }
        else { $out[$pid]['share'][] = (string) $r->meta_value; }
    }
    return $out;
}

function fwo_gst_row($post, $access, $light = null) {
    if ($light === null) { $light = fwo_gst_meta_light([$post->ID]); }
    $m = isset($light[$post->ID]) ? $light[$post->ID] : ['sum' => null, 'share' => []];
    $owner = get_userdata($post->post_author);
    return [
        'id' => $post->ID, 'name' => $post->post_title, 'sum' => $m['sum'],
        'updated' => mysql2date('Y-m-d', $post->post_modified), 'mine' => $access === 'owner',
        'owner' => $owner ? $owner->user_email : '', 'shared' => $access === 'owner' ? array_values(array_unique($m['share'])) : [],
    ];
}

/** Reconstruit un test champ par champ : types et valeurs contrôlés, rien d'autre n'est conservé (même règle que cleanState côté outil). */
function fwo_gst_num($v, $d) { return (is_int($v) || is_float($v) || (is_string($v) && is_numeric($v))) && is_finite((float) $v) ? (float) $v : $d; }
function fwo_gst_clean_state($s) {
    $p = isset($s['plan']) && is_array($s['plan']) ? $s['plan'] : [];
    $a = fwo_gst_num($p['alpha'] ?? null, 0.05); $pw = fwo_gst_num($p['power'] ?? null, 0.8); $tr = fwo_gst_num($p['traffic'] ?? null, 0);
    $pw = ($pw >= 0.5 && $pw < 1) ? $pw : 0.8;
    $plan = [
        'k' => (int) min(50, max(1, round(fwo_gst_num($p['k'] ?? null, 4)))), 'alpha' => ($a > 0 && $a < 0.5) ? $a : 0.05, 'power' => $pw, 'beta' => round(1 - $pw, 4),
        'testType' => ((int) fwo_gst_num($p['testType'] ?? null, 3)) === 1 ? 1 : 3, 'sfu' => (($p['sfu'] ?? '') === 'OF') ? 'OF' : 'KimDeMets',
        'sfl' => in_array($p['sfl'] ?? '', ['HSD', 'KimDeMets', 'OF'], true) ? $p['sfl'] : 'HSD',
        'startDate' => (is_string($p['startDate'] ?? null) && preg_match('/^\d{4}-\d{2}-\d{2}\z/', $p['startDate'])) ? $p['startDate'] : gmdate('Y-m-d'),
        'unit' => (($p['unit'] ?? '') === 'jour') ? 'jour' : 'semaine',
    ];
    if ($tr > 0) { $plan['traffic'] = $tr; }
    $metrics = []; $ids = [];
    foreach (array_slice(is_array($s['metrics'] ?? null) ? $s['metrics'] : [], 0, 15) as $m) {
        if (!is_array($m) || !is_string($m['id'] ?? null) || !preg_match('/^[A-Za-z0-9_-]{1,40}\z/', $m['id']) || isset($ids[$m['id']])) { continue; }
        $ids[$m['id']] = true;
        $metrics[] = ['id' => $m['id'], 'src' => mb_substr(sanitize_text_field((string) ($m['src'] ?? '')), 0, 160), 'name' => mb_substr(sanitize_text_field((string) ($m['name'] ?? '')), 0, 120),
            'type' => (($m['type'] ?? '') === 'continue') ? 'continue' : 'binaire', 'role' => in_array($m['role'] ?? '', ['principale', 'garde-fou', 'secondaire'], true) ? $m['role'] : 'secondaire',
            'sens' => (($m['sens'] ?? '') === 'baisse') ? 'baisse' : 'hausse', 'marge' => fwo_gst_num($m['marge'] ?? null, 1)];
    }
    $arm = function ($x) use ($ids) {
        $r = ['n' => fwo_gst_num(is_array($x) ? ($x['n'] ?? null) : null, 0), 'm' => new stdClass()]; $mm = [];
        foreach ((is_array($x) && is_array($x['m'] ?? null)) ? $x['m'] : [] as $key => $v) {
            if (!isset($ids[(string) $key]) || !is_array($v)) { continue; }
            $q = []; foreach (['c', 's', 'ss', 'n'] as $f) { if (isset($v[$f])) { $q[$f] = fwo_gst_num($v[$f], 0); } }
            $mm[(string) $key] = $q;
        }
        if ($mm) { $r['m'] = $mm; }
        return $r;
    };
    $weeks = [];
    foreach (array_slice(is_array($s['weeks'] ?? null) ? $s['weeks'] : [], 0, 60) as $w) { if (is_array($w)) {
        $row = ['A' => $arm($w['A'] ?? null), 'B' => $arm($w['B'] ?? null)];
        // 0.3.2 : date de fin des données et semaine calendaire de la lecture
        if (isset($w['end']) && is_string($w['end']) && preg_match('/^\d{4}-\d{2}-\d{2}$/', $w['end'])) { $row['end'] = $w['end']; }
        if (isset($w['wk']) && is_numeric($w['wk'])) { $wk = (int) round((float) $w['wk']); if ($wk >= 1 && $wk <= 60) { $row['wk'] = $wk; } }
        $weeks[] = $row; } }
    // 0.3.2 : colonnes choisies à l'import (noms d'en-têtes et libellés, texte seul)
    $map = null;
    if (is_array($s['map'] ?? null)) { $map = []; foreach (['test' => 160, 'vr' => 160, 'vis' => 160, 'tv' => 300, 'c' => 160, 'v' => 160] as $k => $len) { $map[$k] = mb_substr(sanitize_text_field((string) ($s['map'][$k] ?? '')), 0, $len); } }
    $L = is_array($s['labels'] ?? null) ? $s['labels'] : [];
    return ['plan' => $plan, 'metrics' => $metrics,
        'labels' => ['A' => mb_substr(sanitize_text_field((string) ($L['A'] ?? 'Contrôle')), 0, 60), 'B' => mb_substr(sanitize_text_field((string) ($L['B'] ?? 'Variante')), 0, 60)], 'weeks' => $weeks] + ($map ? ['map' => $map] : []);
}

/** Valide et normalise le corps d'un test. Renvoie WP_Error ou [nom, état JSON, résumé JSON]. */
function fwo_gst_payload(WP_REST_Request $r) {
    $name = sanitize_text_field((string) $r->get_param('name'));
    if ($name === '') { return new WP_Error('fwo_gst_name', 'Nom du test manquant.', ['status' => 400]); }
    $state = $r->get_param('state'); $sum = $r->get_param('sum');
    if (!is_array($state) || !isset($state['plan'], $state['metrics'], $state['weeks'])) { return new WP_Error('fwo_gst_state', 'Test illisible.', ['status' => 400]); }
    $state = fwo_gst_clean_state($state);
    if (!$state) { return new WP_Error('fwo_gst_state', 'Test illisible.', ['status' => 400]); }
    $js = wp_json_encode($state);
    if ($js === false || strlen($js) > FWO_GST_MAX_BYTES) { return new WP_Error('fwo_gst_size', 'Test trop volumineux.', ['status' => 413]); }
    $keep = [];
    if (is_array($sum)) { foreach (['t', 'c', 'm', 'd', 'u'] as $k) { if (isset($sum[$k])) { $keep[$k] = mb_substr(sanitize_text_field((string) $sum[$k]), 0, 160); } }
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
        if (!fwo_gst_throttle('ip' . fwo_gst_ip(), 8, FWO_GST_TTL) || !fwo_gst_throttle('em' . $email, 5, FWO_GST_TTL)) {
            return new WP_Error('fwo_gst_rate', 'Trop de demandes. Réessayez dans quelques minutes.', ['status' => 429]);
        }
        $u = get_user_by('email', $email);
        if ($u && !fwo_gst_is_member($u)) { // jamais de lien pour un compte du site (administration, rédaction, abonné existant) ; même délai de réponse
            fwo_gst_mail($email, 'Connexion au calculateur séquentiel', "Bonjour,\n\nCette adresse correspond à un compte du site : connectez-vous par votre accès habituel.\n\nFWOptimisation");
            return ['sent' => true];
        }
        $token = wp_generate_password(48, false);
        $test = absint($r->get_param('test'));
        set_transient('fwo_gst_tk_' . hash('sha256', $token), ['email' => $email, 'test' => $test, 'exp' => time() + FWO_GST_TTL], FWO_GST_TTL);
        $link = add_query_arg('token', rawurlencode($token), rest_url(FWO_GST_NS . '/login'));
        fwo_gst_mail($email, 'Votre lien de connexion au calculateur séquentiel',
            "Bonjour,\n\nOuvrez ce lien puis confirmez pour accéder à votre espace (valable 15 minutes, utilisable une seule fois) :\n" . $link . "\n\nSi vous n'êtes pas à l'origine de cette demande, ignorez ce message.\n\nFWOptimisation");
        return ['sent' => true];
    }]);

    // Lien reçu par email. La visite (GET) n'ouvre rien : elle affiche une confirmation qui nomme l'adresse.
    // Seul l'envoi du formulaire (POST) consomme le lien, crée le compte si besoin et ouvre la session.
    register_rest_route(FWO_GST_NS, '/login', ['methods' => ['GET', 'POST'], 'permission_callback' => '__return_true', 'callback' => function (WP_REST_Request $r) {
        $back = fwo_gst_tool_url(); $token = (string) $r->get_param('token');
        $key = 'fwo_gst_tk_' . hash('sha256', $token); $d = get_transient($key);
        nocache_headers();
        if (!fwo_gst_throttle('lg' . fwo_gst_ip(), 30, FWO_GST_TTL) || !is_array($d) || empty($d['email'])) { wp_safe_redirect($back . '#lien-expire'); exit; }
        $page = function ($body) { header('Content-Type: text/html; charset=utf-8'); header('X-Robots-Tag: noindex, nofollow'); header('X-Frame-Options: DENY'); header('Referrer-Policy: no-referrer');
            echo '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Connexion au calculateur</title>'
               . '<style>body{font-family:system-ui,sans-serif;background:#F8FBFA;color:#1A1D1F;margin:0;padding:24px 16px}main{max-width:460px;margin:8vh auto 0;background:#fff;border:1px solid #D9D9D9;border-radius:12px;padding:24px}h1{font-size:22px;margin:0 0 12px}p{line-height:1.5}button{background:#028D6A;color:#fff;border:0;border-radius:8px;padding:14px 20px;font-size:16px;font-weight:600;cursor:pointer;width:100%}a{color:#0E7C5D}</style></head><body><main>'
               . $body . '</main></body></html>'; exit; };
        $cur = wp_validate_auth_cookie('', 'logged_in'); $curUser = $cur ? get_userdata($cur) : null;
        if ($curUser && !fwo_gst_is_member($curUser)) {
            $page('<h1>Vous êtes connecté au site</h1><p>Ce lien ouvre un compte du calculateur, mais ce navigateur est connecté avec un compte du site. Déconnectez-vous d\'abord, ou ouvrez le lien dans une fenêtre de navigation privée.</p><p><a href="' . esc_url($back) . '">Revenir au calculateur</a></p>');
        }
        if ($r->get_method() !== 'POST') {
            $c = wp_generate_password(40, false, false); $d['c'] = hash('sha256', $c); set_transient($key, $d, max(1, (int) ($d['exp'] ?? 0) - time())); // la visite ne prolonge pas le lien
            setcookie('fwo_gst_c', $c, ['expires' => time() + FWO_GST_TTL, 'path' => '/', 'secure' => is_ssl(), 'httponly' => true, 'samesite' => 'Strict']);
            $page('<h1>Ouvrir votre espace</h1><p>Vous allez être connecté avec l\'adresse <strong>' . esc_html($d['email']) . '</strong>.</p><p>Si ce n\'est pas votre adresse, fermez cette page.</p>'
                . '<form method="post" action="' . esc_url(rest_url(FWO_GST_NS . '/login')) . '"><input type="hidden" name="token" value="' . esc_attr($token) . '"><button type="submit">Ouvrir mon espace</button></form>');
        }
        $c = isset($_COOKIE['fwo_gst_c']) ? (string) wp_unslash($_COOKIE['fwo_gst_c']) : '';
        if (empty($d['c']) || $c === '' || !hash_equals((string) $d['c'], hash('sha256', $c))) { wp_safe_redirect(add_query_arg('token', rawurlencode($token), rest_url(FWO_GST_NS . '/login'))); exit; }
        delete_transient($key); setcookie('fwo_gst_c', '', ['expires' => time() - 3600, 'path' => '/', 'secure' => is_ssl(), 'httponly' => true, 'samesite' => 'Strict']);
        $u = get_user_by('email', $d['email']);
        if ($u && !fwo_gst_is_member($u)) { wp_safe_redirect($back . '#lien-expire'); exit; }
        if (!$u) {
            if (!fwo_gst_throttle('new_accounts', FWO_GST_MAX_NEW, DAY_IN_SECONDS)) { wp_safe_redirect($back . '#lien-expire'); exit; }
            $login = 'gst_' . strtolower(wp_generate_password(14, false, false));
            $id = wp_insert_user(['user_login' => $login, 'user_nicename' => $login, 'user_email' => $d['email'], 'user_pass' => wp_generate_password(40, true, true),
                'display_name' => 'Compte calculateur', 'nickname' => $login, 'role' => FWO_GST_ROLE, 'show_admin_bar_front' => 'false']);
            if (is_wp_error($id)) { wp_safe_redirect($back . '#lien-expire'); exit; }
            $u = get_userdata($id);
        }
        wp_set_current_user($u->ID); wp_set_auth_cookie($u->ID, false);
        wp_safe_redirect($back . (!empty($d['test']) ? '#test=' . (int) $d['test'] : '#compte')); exit;
    }]);

    register_rest_route(FWO_GST_NS, '/logout', ['methods' => 'POST', 'permission_callback' => 'fwo_gst_auth', 'callback' => function () { wp_logout(); return ['ok' => true]; }]);

    register_rest_route(FWO_GST_NS, '/tests', [
        ['methods' => 'GET', 'permission_callback' => 'fwo_gst_auth', 'callback' => function () {
            $u = wp_get_current_user(); $out = [];
            $mine = get_posts(['post_type' => FWO_GST_CPT, 'post_status' => 'private', 'author' => $u->ID, 'numberposts' => FWO_GST_MAX_TESTS, 'orderby' => 'modified', 'order' => 'DESC', 'update_post_meta_cache' => false, 'update_post_term_cache' => false]);
            $light = fwo_gst_meta_light(array_merge(wp_list_pluck($mine, 'ID'), []));
            foreach ($mine as $p) { $out[] = fwo_gst_row($p, 'owner', $light); }
            $theirs = get_posts(['post_type' => FWO_GST_CPT, 'post_status' => 'private', 'author__not_in' => [$u->ID], 'numberposts' => 50, 'orderby' => 'modified', 'order' => 'DESC', 'update_post_meta_cache' => false, 'update_post_term_cache' => false,
                'meta_query' => [['key' => '_fwo_gst_share', 'value' => strtolower($u->user_email)]]]);
            $light2 = fwo_gst_meta_light(wp_list_pluck($theirs, 'ID'));
            foreach ($theirs as $p) { $out[] = fwo_gst_row($p, 'guest', $light2); }
            return ['tests' => $out];
        }],
        ['methods' => 'POST', 'permission_callback' => 'fwo_gst_auth', 'callback' => function (WP_REST_Request $r) {
            $p = fwo_gst_payload($r); if (is_wp_error($p)) { return $p; }
            $n = count(get_posts(['post_type' => FWO_GST_CPT, 'post_status' => 'private', 'author' => get_current_user_id(), 'numberposts' => FWO_GST_MAX_TESTS + 1, 'fields' => 'ids']));
            if ($n >= FWO_GST_MAX_TESTS) { return new WP_Error('fwo_gst_quota', 'Nombre maximal de tests atteint.', ['status' => 409]); }
            $id = wp_insert_post(['post_type' => FWO_GST_CPT, 'post_status' => 'private', 'post_title' => wp_slash($p[0]), 'post_author' => get_current_user_id()], true);
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
            wp_update_post(['ID' => $post->ID, 'post_title' => wp_slash($p[0])]);
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
                if (!fwo_gst_throttle('sh' . get_current_user_id(), 10, HOUR_IN_SECONDS)) { return new WP_Error('fwo_gst_rate', 'Trop d\'invitations. Réessayez plus tard.', ['status' => 429]); }
                add_post_meta($post->ID, '_fwo_gst_share', $email);
                $me = wp_get_current_user();
                fwo_gst_mail($email, 'Un test A/B est partagé avec vous',
                    "Bonjour,\n\n" . $me->user_email . " vous invite à suivre un test A/B en lecture seule.\n\nOuvrez ce lien, puis connectez-vous avec cette adresse email (" . $email . ") :\n" . fwo_gst_tool_url() . '#test=' . $post->ID . "\n\nSi vous ne connaissez pas cette personne, ignorez ce message.\n\nFWOptimisation");
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
        if (!fwo_gst_is_member()) { return new WP_Error('fwo_gst_admin', 'Compte du site : suppression impossible ici.', ['status' => 403]); }
        $id = get_current_user_id(); global $wpdb;
        $wpdb->delete($wpdb->postmeta, ['meta_key' => '_fwo_gst_share', 'meta_value' => strtolower(wp_get_current_user()->user_email)]);
        foreach (get_posts(['post_type' => FWO_GST_CPT, 'post_status' => 'any', 'author' => $id, 'numberposts' => -1, 'fields' => 'ids']) as $pid) { wp_delete_post($pid, true); }
        require_once ABSPATH . 'wp-admin/includes/user.php';
        wp_logout(); wp_delete_user($id);
        return ['ok' => true];
    }]);
});

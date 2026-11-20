p='repo/plugin/fwo-gst-comptes/fwo-gst-comptes.php';s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:60],s.count(a));s=s.replace(a,b)
rep(" * Version: 0.3.2"," * Version: 0.4.0")
rep("const FWO_GST_TTL       = 900;      // durée de vie d'un lien de connexion (secondes)",
"""const FWO_GST_TTL       = 900;      // durée de vie d'un lien de connexion (secondes)
const FWO_GST_MAX_VIS   = 4;        // visuels par variation
const FWO_GST_MAX_IMG   = 2097152;  // taille d'un visuel reçu (2 Mo)
const FWO_GST_IMG_W     = 1600;     // largeur maximale conservée (pixels)
const FWO_GST_IMG_PX    = 16000000; // surface maximale acceptée (pixels)""")
rep("    return ['email' => $u->user_email, 'name' => $u->display_name];",
    "    return ['email' => $u->user_email, 'name' => $u->display_name, 'org' => (string) get_user_meta($u->ID, 'fwo_gst_org', true)];")
NEW=r"""
/** 0.4.0 : présentation du test (texte seul, longueurs bornées). */
function fwo_gst_clean_pres($p) {
    $o = [];
    foreach (['problem' => 2000, 'page' => 160, 'hyp' => 2000] as $k => $len) {
        $o[$k] = mb_substr(sanitize_textarea_field((string) (is_array($p) ? ($p[$k] ?? '') : '')), 0, $len);
    }
    return $o;
}
function fwo_gst_pres($id) { $j = json_decode((string) get_post_meta($id, '_fwo_gst_pres', true), true); return fwo_gst_clean_pres(is_array($j) ? $j : []); }
function fwo_gst_save_pres($id, WP_REST_Request $r) {
    if ($r->has_param('pres')) { update_post_meta($id, '_fwo_gst_pres', wp_slash(wp_json_encode(fwo_gst_clean_pres($r->get_param('pres'))))); }
}

/** 0.4.0 : visuels des variations. Ils sont réécrits par le serveur (JPEG), rangés dans un dossier au nom aléatoire,
    et ne sont servis que par les routes de l'outil, après contrôle d'accès. */
function fwo_gst_vis_base() {
    $up = wp_upload_dir(null, false);
    return empty($up['error']) ? trailingslashit($up['basedir']) . 'fwo-gst-private' : false;
}
function fwo_gst_vis_dir($post_id, $create = false) {
    $base = fwo_gst_vis_base(); if (!$base) { return false; }
    $slug = get_post_meta($post_id, '_fwo_gst_vdir', true);
    if (!is_string($slug) || !preg_match('/^[a-f0-9]{40}\z/', $slug)) {
        if (!$create) { return false; }
        $slug = bin2hex(random_bytes(20)); update_post_meta($post_id, '_fwo_gst_vdir', $slug);
    }
    $dir = $base . '/' . $slug;
    if ($create && !is_dir($dir)) {
        if (!wp_mkdir_p($dir)) { return false; }
        foreach ([$base, $dir] as $d) { if (!file_exists($d . '/index.php')) { @file_put_contents($d . '/index.php', "<?php // Silence.\n"); } }
        if (!file_exists($base . '/.htaccess')) {
            @file_put_contents($base . '/.htaccess', "<IfModule mod_authz_core.c>\nRequire all denied\n</IfModule>\n<IfModule !mod_authz_core.c>\nOrder deny,allow\nDeny from all\n</IfModule>\n");
        }
    }
    return is_dir($dir) ? $dir : false;
}
function fwo_gst_vis($id) {
    $v = json_decode((string) get_post_meta($id, '_fwo_gst_vis', true), true); $out = [];
    foreach (is_array($v) ? $v : [] as $x) {
        if (is_array($x) && isset($x['id'], $x['arm'], $x['f']) && preg_match('/^[a-f0-9]{12}\z/', (string) $x['id']) && in_array($x['arm'], ['A', 'B'], true) && preg_match('/^[a-f0-9]{40}\.jpg\z/', (string) $x['f'])) {
            $out[] = ['id' => $x['id'], 'arm' => $x['arm'], 'f' => $x['f'], 'w' => (int) ($x['w'] ?? 0), 'h' => (int) ($x['h'] ?? 0)];
        }
    }
    return $out;
}
function fwo_gst_vis_public($id) {
    $o = []; foreach (fwo_gst_vis($id) as $x) { $o[] = ['id' => $x['id'], 'arm' => $x['arm'], 'w' => $x['w'], 'h' => $x['h']]; } return $o;
}
function fwo_gst_vis_send($post_id, $vid) {
    $dir = fwo_gst_vis_dir($post_id);
    foreach (fwo_gst_vis($post_id) as $x) {
        if (hash_equals($x['id'], (string) $vid) && $dir && is_file($dir . '/' . $x['f'])) {
            nocache_headers(); header('Content-Type: image/jpeg'); header('X-Content-Type-Options: nosniff'); header('Content-Disposition: inline; filename="visuel.jpg"');
            header('X-Robots-Tag: noindex, nofollow'); header('Content-Length: ' . filesize($dir . '/' . $x['f']));
            readfile($dir . '/' . $x['f']); exit;
        }
    }
    return new WP_Error('fwo_gst_404', 'Visuel introuvable.', ['status' => 404]);
}
function fwo_gst_vis_purge($post_id) {
    $dir = fwo_gst_vis_dir($post_id); if (!$dir) { return; }
    foreach ((array) glob($dir . '/*') as $f) { if (is_file($f)) { @unlink($f); } }
    @rmdir($dir);
}
add_action('before_delete_post', function ($pid) { if (get_post_type($pid) === FWO_GST_CPT) { fwo_gst_vis_purge($pid); } });

/** 0.4.0 : clé de lecture publique d'une présentation (lien de partage). Lue dans l'en-tête X-FWO-Key, jamais dans l'adresse. */
function fwo_gst_public_post(WP_REST_Request $r) {
    if (!fwo_gst_throttle('pub' . fwo_gst_ip(), 240, FWO_GST_TTL)) { return new WP_Error('fwo_gst_rate', 'Trop de demandes. Réessayez dans quelques minutes.', ['status' => 429]); }
    $post = get_post((int) $r['id']); $key = (string) $r->get_header('x_fwo_key');
    $ref = ($post && $post->post_type === FWO_GST_CPT && $post->post_status === 'private') ? (string) get_post_meta($post->ID, '_fwo_gst_pkey', true) : '';
    if ($ref === '' || !preg_match('/^[a-f0-9]{48}\z/', $key) || !hash_equals($ref, $key)) { return new WP_Error('fwo_gst_404', 'Lien introuvable.', ['status' => 404]); }
    return $post;
}
"""
rep("\n/** Valide et normalise le corps d'un test. Renvoie WP_Error ou [nom, état JSON, résumé JSON]. */",NEW+"\n/** Valide et normalise le corps d'un test. Renvoie WP_Error ou [nom, état JSON, résumé JSON]. */")
# /me : organisation
rep("""        return ['enabled' => true, 'user' => fwo_gst_user_payload()];
    }]);""","""        return ['enabled' => true, 'user' => fwo_gst_user_payload(), 'v' => '0.4.0'];
    }]);
    // 0.4.0 : nom de l'organisation (texte seul), demandé à la première connexion.
    register_rest_route(FWO_GST_NS, '/me', ['methods' => 'POST', 'permission_callback' => 'fwo_gst_auth', 'callback' => function (WP_REST_Request $r) {
        update_user_meta(get_current_user_id(), 'fwo_gst_org', wp_slash(mb_substr(sanitize_text_field((string) $r->get_param('org')), 0, 120)));
        return ['user' => fwo_gst_user_payload()];
    }]);""")
rep("""            update_post_meta($id, '_fwo_gst_state', wp_slash($p[1])); update_post_meta($id, '_fwo_gst_sum', wp_slash($p[2]));
            return fwo_gst_row(get_post($id), 'owner');""","""            update_post_meta($id, '_fwo_gst_state', wp_slash($p[1])); update_post_meta($id, '_fwo_gst_sum', wp_slash($p[2])); fwo_gst_save_pres($id, $r);
            return fwo_gst_row(get_post($id), 'owner');""")
rep("""            $row = fwo_gst_row($post, $a); $row['state'] = json_decode((string) get_post_meta($post->ID, '_fwo_gst_state', true), true);
            return $row;""","""            $row = fwo_gst_row($post, $a); $row['state'] = json_decode((string) get_post_meta($post->ID, '_fwo_gst_state', true), true);
            $row['pres'] = fwo_gst_pres($post->ID); $row['visuals'] = fwo_gst_vis_public($post->ID);
            if ($a === 'owner') { $row['pkey'] = (string) get_post_meta($post->ID, '_fwo_gst_pkey', true); }
            return $row;""")
rep("""            update_post_meta($post->ID, '_fwo_gst_state', wp_slash($p[1])); update_post_meta($post->ID, '_fwo_gst_sum', wp_slash($p[2]));
            return fwo_gst_row(get_post($post->ID), 'owner');""","""            update_post_meta($post->ID, '_fwo_gst_state', wp_slash($p[1])); update_post_meta($post->ID, '_fwo_gst_sum', wp_slash($p[2])); fwo_gst_save_pres($post->ID, $r);
            return fwo_gst_row(get_post($post->ID), 'owner');""")
ROUTES=r"""
    // 0.4.0 : visuels des variations (propriétaire : ajout et retrait ; invité : lecture).
    register_rest_route(FWO_GST_NS, '/tests/(?P<id>\d+)/visuals', ['methods' => 'POST', 'permission_callback' => 'fwo_gst_auth', 'callback' => function (WP_REST_Request $r) {
        $post = get_post((int) $r['id']);
        if (fwo_gst_access($post) !== 'owner') { return new WP_Error('fwo_gst_404', 'Test introuvable.', ['status' => 404]); }
        if (!fwo_gst_throttle('vis' . get_current_user_id(), 80, HOUR_IN_SECONDS)) { return new WP_Error('fwo_gst_rate', 'Trop d\'envois. Réessayez plus tard.', ['status' => 429]); }
        if (!function_exists('imagecreatefromstring') || !function_exists('imagejpeg')) { return new WP_Error('fwo_gst_gd', 'Le serveur ne peut pas traiter les images.', ['status' => 501]); }
        $arm = (string) $r->get_param('arm'); if (!in_array($arm, ['A', 'B'], true)) { return new WP_Error('fwo_gst_arm', 'Variation inconnue.', ['status' => 400]); }
        $list = fwo_gst_vis($post->ID); $n = 0; foreach ($list as $x) { if ($x['arm'] === $arm) { $n++; } }
        if ($n >= FWO_GST_MAX_VIS) { return new WP_Error('fwo_gst_quota', 'Nombre maximal de visuels atteint pour cette variation.', ['status' => 409]); }
        $b64 = (string) $r->get_param('data'); $c = strpos($b64, ','); if (strncmp($b64, 'data:', 5) === 0 && $c !== false) { $b64 = substr($b64, $c + 1); }
        if (strlen($b64) > (int) ceil(FWO_GST_MAX_IMG * 4 / 3) + 16) { return new WP_Error('fwo_gst_size', 'Image trop lourde (2 Mo au plus).', ['status' => 413]); }
        $raw = base64_decode($b64, true);
        if ($raw === false || strlen($raw) < 64 || strlen($raw) > FWO_GST_MAX_IMG) { return new WP_Error('fwo_gst_size', 'Image illisible ou trop lourde (2 Mo au plus).', ['status' => 413]); }
        $info = @getimagesizefromstring($raw);
        if (!$info || !in_array($info[2], [IMAGETYPE_JPEG, IMAGETYPE_PNG], true) || $info[0] < 16 || $info[1] < 16 || $info[0] > 8000 || $info[1] > 12000 || $info[0] * $info[1] > FWO_GST_IMG_PX) {
            return new WP_Error('fwo_gst_type', 'Format non accepté : PNG ou JPG, 16 millions de pixels au plus.', ['status' => 415]);
        }
        $im = @imagecreatefromstring($raw);
        if (!$im) { return new WP_Error('fwo_gst_type', 'Image illisible.', ['status' => 415]); }
        $w = imagesx($im); $h = imagesy($im); $nw = min($w, FWO_GST_IMG_W); $nh = max(1, (int) round($h * $nw / $w));
        $dst = imagecreatetruecolor($nw, $nh); imagefill($dst, 0, 0, imagecolorallocate($dst, 255, 255, 255)); // fond blanc : la transparence est aplatie
        imagecopyresampled($dst, $im, 0, 0, 0, 0, $nw, $nh, $w, $h); imagedestroy($im);
        $dir = fwo_gst_vis_dir($post->ID, true);
        if (!$dir) { imagedestroy($dst); return new WP_Error('fwo_gst_fs', 'Enregistrement impossible.', ['status' => 500]); }
        $f = bin2hex(random_bytes(20)) . '.jpg'; $ok = imagejpeg($dst, $dir . '/' . $f, 86); imagedestroy($dst);
        if (!$ok) { return new WP_Error('fwo_gst_fs', 'Enregistrement impossible.', ['status' => 500]); }
        $list[] = ['id' => bin2hex(random_bytes(6)), 'arm' => $arm, 'f' => $f, 'w' => $nw, 'h' => $nh];
        update_post_meta($post->ID, '_fwo_gst_vis', wp_slash(wp_json_encode($list)));
        return ['visuals' => fwo_gst_vis_public($post->ID)];
    }]);
    register_rest_route(FWO_GST_NS, '/tests/(?P<id>\d+)/visuals/(?P<vid>[a-f0-9]{12})', [
        ['methods' => 'GET', 'permission_callback' => 'fwo_gst_auth', 'callback' => function (WP_REST_Request $r) {
            $post = get_post((int) $r['id']);
            if (!fwo_gst_access($post)) { return new WP_Error('fwo_gst_404', 'Test introuvable.', ['status' => 404]); }
            return fwo_gst_vis_send($post->ID, $r['vid']);
        }],
        ['methods' => 'DELETE', 'permission_callback' => 'fwo_gst_auth', 'callback' => function (WP_REST_Request $r) {
            $post = get_post((int) $r['id']);
            if (fwo_gst_access($post) !== 'owner') { return new WP_Error('fwo_gst_404', 'Test introuvable.', ['status' => 404]); }
            $dir = fwo_gst_vis_dir($post->ID); $keep = [];
            foreach (fwo_gst_vis($post->ID) as $x) { if (hash_equals($x['id'], (string) $r['vid'])) { if ($dir && is_file($dir . '/' . $x['f'])) { @unlink($dir . '/' . $x['f']); } } else { $keep[] = $x; } }
            update_post_meta($post->ID, '_fwo_gst_vis', wp_slash(wp_json_encode($keep)));
            return ['visuals' => fwo_gst_vis_public($post->ID)];
        }],
    ]);

    // 0.4.0 : lien de partage de la présentation. La clé est créée par le propriétaire et peut être retirée.
    register_rest_route(FWO_GST_NS, '/tests/(?P<id>\d+)/publink', [
        ['methods' => 'POST', 'permission_callback' => 'fwo_gst_auth', 'callback' => function (WP_REST_Request $r) {
            $post = get_post((int) $r['id']);
            if (fwo_gst_access($post) !== 'owner') { return new WP_Error('fwo_gst_404', 'Test introuvable.', ['status' => 404]); }
            $k = (string) get_post_meta($post->ID, '_fwo_gst_pkey', true);
            if (!preg_match('/^[a-f0-9]{48}\z/', $k)) { $k = bin2hex(random_bytes(24)); update_post_meta($post->ID, '_fwo_gst_pkey', $k); }
            return ['key' => $k];
        }],
        ['methods' => 'DELETE', 'permission_callback' => 'fwo_gst_auth', 'callback' => function (WP_REST_Request $r) {
            $post = get_post((int) $r['id']);
            if (fwo_gst_access($post) !== 'owner') { return new WP_Error('fwo_gst_404', 'Test introuvable.', ['status' => 404]); }
            delete_post_meta($post->ID, '_fwo_gst_pkey'); return ['ok' => true];
        }],
    ]);
    register_rest_route(FWO_GST_NS, '/public/(?P<id>\d+)', ['methods' => 'GET', 'permission_callback' => '__return_true', 'callback' => function (WP_REST_Request $r) {
        $post = fwo_gst_public_post($r); if (is_wp_error($post)) { return $post; }
        $o = get_userdata($post->post_author);
        return ['name' => $post->post_title, 'pres' => fwo_gst_pres($post->ID), 'visuals' => fwo_gst_vis_public($post->ID), 'org' => $o ? (string) get_user_meta($o->ID, 'fwo_gst_org', true) : ''];
    }]);
    register_rest_route(FWO_GST_NS, '/public/(?P<id>\d+)/visuals/(?P<vid>[a-f0-9]{12})', ['methods' => 'GET', 'permission_callback' => '__return_true', 'callback' => function (WP_REST_Request $r) {
        $post = fwo_gst_public_post($r); if (is_wp_error($post)) { return $post; }
        return fwo_gst_vis_send($post->ID, $r['vid']);
    }]);
"""
rep("\n    // Suppression du compte et de ses tests (comptes abonnés uniquement).",ROUTES+"\n    // Suppression du compte et de ses tests (comptes abonnés uniquement).")
open(p,'w').write(s)
u='repo/plugin/fwo-gst-comptes/uninstall.php';t=open(u).read()
a="require_once ABSPATH . 'wp-admin/includes/user.php';"
assert t.count(a)==1
t=t.replace(a,"""// 0.4.0 : visuels des variations
$fwo_up = wp_upload_dir(null, false);
if (empty($fwo_up['error'])) {
    $fwo_base = trailingslashit($fwo_up['basedir']) . 'fwo-gst-private';
    if (is_dir($fwo_base)) {
        foreach ((array) glob($fwo_base . '/*', GLOB_ONLYDIR) as $fwo_d) { foreach ((array) glob($fwo_d . '/*') as $fwo_f) { if (is_file($fwo_f)) { @unlink($fwo_f); } } @rmdir($fwo_d); }
        foreach (['/index.php', '/.htaccess'] as $fwo_f) { if (is_file($fwo_base . $fwo_f)) { @unlink($fwo_base . $fwo_f); } }
        @rmdir($fwo_base);
    }
}
"""+a)
open(u,'w').write(t)

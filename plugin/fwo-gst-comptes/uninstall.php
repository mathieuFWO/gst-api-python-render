<?php
/** Désinstallation : supprime les tests enregistrés, le rôle dédié et ses comptes. */
if (!defined('WP_UNINSTALL_PLUGIN')) { exit; }
foreach (get_posts(['post_type' => 'fwo_gst_test', 'post_status' => 'any', 'numberposts' => -1, 'fields' => 'ids']) as $pid) { wp_delete_post($pid, true); }
// 0.4.0 : visuels des variations
$fwo_up = wp_upload_dir(null, false);
if (empty($fwo_up['error'])) {
    $fwo_base = trailingslashit($fwo_up['basedir']) . 'fwo-gst-private';
    if (is_dir($fwo_base)) {
        foreach ((array) glob($fwo_base . '/*', GLOB_ONLYDIR) as $fwo_d) { foreach ((array) glob($fwo_d . '/*') as $fwo_f) { if (is_file($fwo_f)) { @unlink($fwo_f); } } @rmdir($fwo_d); }
        foreach (['/index.php', '/.htaccess'] as $fwo_f) { if (is_file($fwo_base . $fwo_f)) { @unlink($fwo_base . $fwo_f); } }
        @rmdir($fwo_base);
    }
}
require_once ABSPATH . 'wp-admin/includes/user.php';
foreach (get_users(['role' => 'fwo_gst_user', 'fields' => 'ID']) as $uid) { wp_delete_user($uid); }
remove_role('fwo_gst_user');

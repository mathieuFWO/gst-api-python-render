<?php
/** Désinstallation : supprime les tests enregistrés, le rôle dédié et ses comptes. */
if (!defined('WP_UNINSTALL_PLUGIN')) { exit; }
foreach (get_posts(['post_type' => 'fwo_gst_test', 'post_status' => 'any', 'numberposts' => -1, 'fields' => 'ids']) as $pid) { wp_delete_post($pid, true); }
require_once ABSPATH . 'wp-admin/includes/user.php';
foreach (get_users(['role' => 'fwo_gst_user', 'fields' => 'ID']) as $uid) { wp_delete_user($uid); }
remove_role('fwo_gst_user');

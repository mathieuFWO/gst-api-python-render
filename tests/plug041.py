# Extension 0.4.1 : garde le détail par valeur d'une dimension (appareil...) et le nom de cette colonne.
p='repo/plugin/fwo-gst-comptes/fwo-gst-comptes.php';s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:60],s.count(a));s=s.replace(a,b)
rep(" * Version: 0.4.0"," * Version: 0.4.1")
rep("'tv' => 300, 'c' => 160, 'v' => 160] as $k","'tv' => 300, 'c' => 160, 'v' => 160, 'sc' => 160] as $k")
rep("'v' => '0.4.0'];","'v' => '0.4.1'];")
rep("""        $weeks[] = $row; } }""","""        // 0.4.1 : détail par valeur d'une dimension (12 valeurs au plus, libellé en texte seul)
        if (is_array($w['seg'] ?? null)) { $seg = []; foreach (array_slice($w['seg'], 0, 12) as $x) { if (!is_array($x)) { continue; }
            $l = mb_substr(sanitize_text_field((string) ($x['l'] ?? '')), 0, 60); if ($l === '') { continue; }
            $seg[] = ['l' => $l, 'A' => $arm($x['A'] ?? null), 'B' => $arm($x['B'] ?? null)]; }
            if (count($seg) > 1) { $row['seg'] = $seg; } }
        $weeks[] = $row; } }""")
open(p,'w').write(s)

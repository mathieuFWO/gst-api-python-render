# Extension 0.4.2 : garde le détail par dimension (3 dimensions, 12 valeurs chacune) avec chaque lecture.
p='repo/plugin/fwo-gst-comptes/fwo-gst-comptes.php';s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:60],s.count(a));s=s.replace(a,b)
rep(" * Version: 0.4.1"," * Version: 0.4.2")
rep("'v' => '0.4.1'];","'v' => '0.4.2'];")
i=s.index("        // 0.4.1 : détail par valeur d'une dimension");j=s.index("        $weeks[] = $row; } }")
s=s[:i]+"""        // 0.4.2 : détail par dimension (3 dimensions, 12 valeurs chacune, libellés en texte seul). « seg » : format de la v56.28, relu comme une dimension.
        $segs = function ($list) use ($arm) { $seg = []; foreach (array_slice(is_array($list) ? $list : [], 0, 12) as $x) { if (!is_array($x)) { continue; }
            $l = mb_substr(sanitize_text_field((string) ($x['l'] ?? '')), 0, 60); if ($l === '') { continue; }
            $seg[] = ['l' => $l, 'A' => $arm($x['A'] ?? null), 'B' => $arm($x['B'] ?? null)]; } return $seg; };
        $dims = [];
        if (is_array($w['dims'] ?? null)) { foreach (array_slice($w['dims'], 0, 3) as $dm) { if (!is_array($dm)) { continue; } $v = $segs($dm['v'] ?? null);
            if (count($v) > 1) { $n = mb_substr(sanitize_text_field((string) ($dm['n'] ?? '')), 0, 160); $dims[] = ['n' => $n !== '' ? $n : 'Dimension', 'v' => $v]; } } }
        elseif (is_array($w['seg'] ?? null)) { $v = $segs($w['seg']); if (count($v) > 1) { $n = mb_substr(sanitize_text_field((string) (is_array($s['map'] ?? null) ? ($s['map']['sc'] ?? '') : '')), 0, 160); $dims[] = ['n' => $n !== '' ? $n : 'Dimension', 'v' => $v]; } }
        if ($dims) { $row['dims'] = $dims; }
"""+s[j:]
open(p,'w').write(s)

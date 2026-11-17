# Revue indépendante : calculateur séquentiel v55-2 → v56-3

Dossier des scripts et sorties : `/tmp/claude-0/-home-claude/f6658268-8fe7-580d-9107-6939e43c6edb/scratchpad/revue563/`
Fichiers relus : `calculateur-sequentiel-v55-2.html` (avant), `calculateur-sequentiel-v56-3.html` (après). Aucun fichier du dépôt modifié.
Les numéros de ligne renvoient à `b.p.js` (le script de v56-3 extrait et remis en forme par prettier, dans le même dossier) ; le nom de fonction vaut pour le fichier d'origine.

## Verdict

1. **Sécurité : rien trouvé.** 472 contrôles d'injection (CSV, lien de partage forgé, sauvegarde locale forgée) sans aucune balise injectée ni script exécuté. Le seul défaut est une injection de paramètres dans le `mailto`, possible uniquement par l'utilisateur lui-même.
2. **Calcul : aucune régression.** Décisions, bornes et intervalles strictement identiques entre v55-2 et v56-3 sur 5 scénarios (égalité stricte des nombres).
3. **Fiabilité des données importées : 4 défauts de gravité haute.** L'outil peut mélanger deux tests différents sans alerte, accepte des instantanés non cumulés sans alerte, laisse inverser A et B en cours de test, et la règle des semaines complètes désynchronise « semaine N sur k » du calendrier réel. Je ne recommande pas de présenter l'import instantané comme fiable tant que les constats 1 à 4 ne sont pas corrigés.

## Constats

### Critique

Aucun.

### Haut

**1. Test absent du second fichier : l'outil prend un autre test et l'ajoute comme semaine suivante, sans alerte.**
- Ce qui se passe : 1er import du test « Test fiche » (1 000 / 1 004 visiteurs). 2e fichier ne contenant que « Autre test » (mêmes libellés de variations). L'écran présélectionne « Autre test », affiche la coche verte « Dernier cumul lu : 9 000 / 9 100 », et l'import est accepté : semaine 2 = données d'un autre test. Aucun message.
- Reproduire : `node cd.js`, cas D4 (sortie dans `cd.out`). Même effet si l'utilisateur change lui-même le test au 2e import (cas D8 : 5 000 / 5 100 acceptés).
- En cause : `analyze`, l. 1194-1201 : quand `MP.tv` (test mémorisé) est absent, repli sur `two || d.tests[0]`. Le repli existait déjà en v55-2 (`d.tests[0]`), ce n'est pas une régression, mais la mémorisation de v56-3 était l'occasion de le fermer et ne le fait pas.
- Correction : si `state.weeks.length` et `state.map.tv` non vide et absent de `d.tests`, ne rien présélectionner et refuser dans `buildWeeks` (« Le test "X" n'est pas dans ce fichier »). Si l'utilisateur choisit un autre test que `map.tv`, refuser ou exiger une confirmation explicite.

**2. Contrôle et variante inversables au 2e import : A et B échangés dans une semaine.**
- Ce qui se passe : au 2e import, les métriques sont verrouillées mais pas les listes « Contrôle (A) » / « Variante (B) ». En choisissant « Nouvelle » comme contrôle, l'import est accepté : semaines = `1000/1004 ; 2008/2000`, libellés inchangés (A = Témoin). Le résultat de la semaine 2 est calculé à l'envers.
- Reproduire : `node cd.js`, cas D7.
- En cause : `viewData` l. 3842-3858 (listes non désactivées quand `locked`), `applyDraft` l. 1472-1485 (`state.labels` n'est mis à jour que si `replace`, aucun contrôle de cohérence avec `state.map.c` / `state.map.v`).
- Correction : quand `locked`, désactiver les deux listes si `map.c` et `map.v` sont présents dans le fichier ; sinon refuser tout import où `d.control !== map.c` ou `d.variant !== map.v` sans confirmation.

**3. Instantanés non cumulés acceptés sans aucune alerte.**
- Ce qui se passe : l'alerte « non cumulé » ne tourne qu'en mode série (`nc = d.mode === "serie" ? notCumul(vis) : null`). Un utilisateur qui exporte chaque semaine « la semaine écoulée » (cas le plus courant de l'erreur) importe 10 000, puis 10 400, puis 10 900 visiteurs : tout est accepté comme cumul, 3 lectures, aucune alerte. Seule une baisse stricte est refusée.
- Reproduire : `node cd.js`, bloc C2.
- En cause : `viewData` l. 3768 ; `buildWeeks` l. 1403-1416 (seul contrôle : `c.n < p.n`).
- Correction : en mode instantané, comparer à la lecture précédente avec les dates déjà connues : si les jours de données passent de 7 à 14 et que les visiteurs augmentent de moins de (par exemple) 40 % du prorata attendu, afficher l'alerte. La donnée nécessaire (`weeks[i].end`, `plan.startDate`) existe déjà.

**4. « Semaine N sur k » compte les lectures, pas les semaines : la durée prévue n'est plus respectée dès qu'une lecture est sautée ou tardive.**
- Ce qui se passe (horloge figée, k = 4, début 05/10) : lectures à J7, J21, J28. À J28, fin de la durée prévue, l'outil affiche « Décision · semaine 3 sur 4 : Continuer ». L'analyse finale n'a lieu qu'à J35 (« semaine 4 sur 4 »), et un import à J42 est encore accepté comme 5e lecture pour k = 4. Même cause au premier import : 14 ou 28 jours de données sont enregistrés comme « Semaine 1 » (« 28 jours de données, soit 4 semaines complètes » puis « semaine 1 sur 2 »).
- Reproduire : `node dates.js`, blocs B1, B9, B10 (sortie `dates.out`).
- En cause : `weekGate` l. 1304-1308 calcule bien `w` (semaines écoulées) mais `buildWeeks` l. 1364 et `applyDraft` empilent la lecture à l'indice `state.weeks.length`. Le contrôle de durée l. 1422 ne peut jamais se déclencher en instantané car `d.k = Math.max(nW, state.plan.k)` (l. 1241) s'aligne tout seul (déjà vrai en v55-2).
- Conséquence : un utilisateur de bonne foi qui rate une semaine ne peut pas conclure à la date prévue ; le libellé de semaine affiché est faux.
- Correction : soit refuser/alerter quand `w` dépasse `wl + 1` en expliquant le décalage, soit étiqueter la lecture avec `w` et traiter la lecture faite à `w >= k` comme analyse finale. Dans tous les cas, refuser une lecture quand `state.weeks.length >= state.plan.k` (comme le fait `addManual` l. 4873).

### Moyen

**5. La règle des semaines complètes se contourne en déplaçant la date de début dans l'onglet Plan.**
- Reproduit : après une lecture à J7, 4 imports en 4 jours consécutifs (J8, J9, J10, J11), chacun refusé d'abord puis accepté après avoir reculé la date de début d'un jour dans Plan. Aucune confirmation n'est demandée (`planKey` n'inclut pas `startDate`). Aussi : date de début au 01/01/1900 acceptée (« 6 620 semaines complètes »).
- Reproduire : `node dates.js`, blocs B7 et B3.
- En cause : `weekGate` l. 1295-1307 (tout repose sur `state.plan.startDate`, modifiable librement) ; `act('applyplan')` l. 4832.
- Correction : exiger aussi `dayDiff(last.end, E) >= 7` (ou au moins 5) entre deux lectures datées ; demander confirmation quand la date de début change après une lecture ; borner la date de début (pas plus de `k` semaines + marge avant la fin).
- Autres contournements non fermés, par conception : un fichier avec colonne « Semaine » (remplace tout, pas de règle), la saisie manuelle, le mode « chaque jour ».

**6. Tests en cours créés avant v56-3 : le prochain import hebdomadaire est refusé.**
- Ce qui se passe : en v55-2, un test alimenté par instantanés garde comme date de début la date du premier import (vérifié : 02/11 proposé par défaut le 02/11). Repris en v56-3 avec 2 lectures sans date de fin, le 3e import hebdomadaire normal (16/11) est refusé : « Pas de nouvelle semaine complète… Prochaine lecture… jusqu'au 22/11/2026 ». Le message indique bien la sortie (corriger la date dans Plan), mais la date « 22/11 » annoncée est fausse tant que le début n'est pas corrigé.
- Reproduire : `node misc.js`, bloc 1.
- Correction : quand la dernière lecture n'a pas de date de fin, afficher d'abord la question « Votre test a-t-il bien commencé le JJ/MM ? » avec le champ de date modifiable directement dans l'écran d'import (aujourd'hui masqué car `locked`).

**7. « Données jusqu'au » = aujourd'hui est accepté.**
- Une journée en cours compte comme un jour complet : 6 jours pleins + la matinée du 7e passent pour « 1 semaine complète ». Reproduit : `node dates.js`, B3 « fin = aujourd'hui » → importé.
- En cause : `weekGate` l. 1302 (`E > todayISO()`), et `max="today"` sur le champ l. 3807.
- Correction : `E >= todayISO()` refusé (ou alerte explicite), `max` = hier.

**8. Alerte « non cumulé » (série) : faux positifs au texte faux, faux négatifs sur trafic croissant, et alerte non bloquante.**
- Faux positifs (4 sur 7 séries cumulées plausibles) : `[30000, 45000, 58000]`, `[40000, 55000, 70000]`, `[40000, 60000, 72000, 79000]`, `[20000, 24000]`. Le texte dit « Les visiteurs n'augmentent presque pas entre la semaine 1 (30 000) et la semaine 3 (58 000) » : c'est faux (+93 %).
- Faux négatifs (4 sur 8 séries non cumulées) : `[20000, 26000]`, `[20000, 30000, 42000]`, `[10000, 13000, 17000, 22000]`, série de 8 semaines en hausse lente. Cas réaliste : montée en charge progressive du test.
- Cohérence : quand l'alerte s'affiche sans baisse stricte (`[20000, 20500]`, `[20000, 25000]`), l'import est accepté d'un clic, sans confirmation.
- Reproduire : `node cd.js`, bloc C.
- En cause : `notCumul` l. 1276-1285 (seuil unique « dernier < 2 × premier »).
- Correction : comparer les incréments au cumul précédent (un export non cumulé a `t[i]` proche de `t[i-1]`, pas de `t[0] × (i+1)`) ; adapter le texte au motif réel ; exiger une case « Je confirme que ces chiffres sont cumulés » quand l'alerte est levée.

**9. Colonnes mémorisées perdues par le lien de partage (et, par lecture du code, par les comptes).**
- Reproduit : après import avec colonnes choisies à la main, ouvrir le lien de partage puis « Ouvrir une copie modifiable » : `state.map` vaut `undefined`, l'import suivant revient à « Aucune : un seul test / — / — ». `weeks[].end` est bien conservé.
- Reproduire : `node misc.js`, bloc 4.
- En cause : `sharePayload` l. 2023 et `openShared` l. 2045 ne transportent pas `map`. Même omission dans `accSave` l. 2271 et `accOpen` l. 2242 : **non reproduit** (pas de serveur de comptes dans le bac à sable), constat par lecture seule.
- Correction : ajouter `map` au contenu enregistré côté compte (et décider si le lien de partage doit le porter) ; `cleanState` le filtre déjà correctement.

**10. Partage par email, lien trop long : « Lien copié. » s'affiche même si la copie a échoué.**
- Reproduit avec un presse-papiers qui refuse l'écriture : le message reste « Lien copié. Il est trop long… collez-le (Ctrl+V) ». L'utilisateur colle alors dans son email ce que contenait son presse-papiers avant (contenu sans rapport, potentiellement sensible).
- Reproduire : `node e.js`, dernier bloc (« presse-papiers refus »).
- En cause : `act('sharemail')` l. 4734-4747 : `ui.mailNote = "long"` posé avant le résultat, `.catch(function () {})` avale l'échec.
- Correction : n'afficher « Lien copié » que dans le `then` ; en cas d'échec, afficher « Copiez le lien ci-dessus puis collez-le dans le message ».
- Seuil vérifié : bascule autour de 1 550 à 1 600 caractères de lien (lien de 1 512 inséré, lien de 1 596 non inséré).

**11. Assistant, étape 3 : les chiffres saisis sont effacés à la moindre erreur, et parfois sans erreur.**
- Déterministe : une seule valeur invalide (« 9999 » conversions pour 5 010 visiteurs) → message d'erreur et **tous** les champs vidés. Reproduire : `node e2.js`, dernière ligne.
- Dépendant du rythme : si l'utilisateur commence à taper moins de 700 ms environ après « Continuer », un rendu différé efface les champs dès qu'il clique hors d'un champ (12 essais sur 12 à 0-400 ms, 0 sur 6 à 800 ms). Reproduire : `HP=400 node e3.js` puis `HP=800 node e3.js` (sortie `e3.out`). À un rythme humain normal le défaut ne se produit pas ; il touche surtout la navigation au clavier.
- En cause : les champs `data-mw` ne sont stockés nulle part et `render()` réécrit tout (`addManual` l. 4874-4876) ; `needIF` l. 4067 relance `softRender` tant que `ui.howto === "manuel" && ui.man.step === 2`, condition toujours vraie à l'étape 3 (`manstart` ne change pas `ui.man.step`).
- Correction : mémoriser les valeurs saisies (par exemple `ui.mw`) et les réinjecter au rendu ; dans `needIF`, ajouter `&& !ui.manFlow`.

### Faible

**12. Injection de paramètres dans le `mailto` par le champ d'adresse.** L'expression de validation (l. 4729) laisse passer `?`, `&`, `%`, `#`, `:` et l'adresse n'est pas encodée. Reproduit (`node cd.js`, bloc Mailto) : `a@b.fr?bcc=x%40y.z&x=` produit `mailto:a@b.fr?bcc=x%40y.z&x=?subject=…` ; `a@b.fr?body=…&x=` remplace le corps. Seul l'utilisateur peut saisir ce champ (il n'est alimenté par aucun lien ni fichier), d'où la gravité faible. Les sauts de ligne, virgules, chevrons et doubles `@` sont bien rejetés. Correction : expression stricte `^[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$` et `encodeURIComponent(to)`.

**13. `cleanLabs` abîme des libellés légitimes.** « 3D viewer » / « 4K video » deviennent « D viewer » / « K video » (`node cd.js`, bloc cleanLabs). En cause : l. 1072, tout préfixe de 1 à 12 chiffres suivi d'une lettre. Correction : n'ôter que si l'un des deux préfixes est `0` ou si les deux ont au moins 4 chiffres.

**14. Dates au format américain mal lues.** `11/16/2026` est lu `2026-16-11` et refusé comme « dans le futur » (message trompeur) ; une date ambiguë comme `03/04/2026` serait lue sans alerte dans le mauvais sens. `node dates.js`, B14. En cause : `isoD` l. 1092-1099.

**15. Trafic « 20.000 » lu comme 20.** Dans l'assistant et l'onglet Plan, `20.000` / `1.000` donne un effet détectable de 390,67 % sans avertissement, alors que `20 000` et `20,000` sont bien lus (`node e.js`, bloc E2). En cause : `toNum` l. 1037-1038. Correction : traiter `^\d{1,3}(\.\d{3})+$` comme séparateur de milliers.

**16. Durée prévue par défaut de 2 semaines au premier import instantané** (`Math.max(nW, 2)`, l. 1241), quelle que soit la durée réelle ; déjà présent en v55-2. Un utilisateur qui ne touche à rien obtient un plan de 2 semaines.

**17. Un test vide reste enregistré après « Retour » depuis l'étape 3 de l'assistant.** `manstart` appelle `autosave()` ; après retour arrière puis rechargement, « Mes tests (1) : Mon test » propose un test sans données (`node e.js`, bloc E3).

**18. Onglet Plan à 360 px : « Durée prévue (semaines) » et « Date de début » désalignés de 17 px** (libellé sur deux lignes). Mesuré : champs à top = 779,1 et 761,7 (`ui.out`). Je n'ai pas vérifié si c'était déjà le cas en v55-2.

**19. Écran d'import à 360 px : listes tronquées.** « Test à analyser » (texte de 396 px dans 284), « Variante (B) » (« 2129001Variati… »), « Colonne du test » (« Aucune : un seul test », 139 px dans 135). Les identifiants Piano ne sont retirés que dans la phrase « Dernier cumul lu », pas dans les listes.

**20. Lien de partage : la date « données du … » est celle que le lien déclare** (`o.d`, seule la forme `AAAA-MM-JJ…` est filtrée). Un lien forgé peut afficher n'importe quelle date ; aucune injection possible (`frDate` ne restitue que des chiffres).

**21. Texte : « Le fichier contient N semaines pour une durée prévue de k »** (l. 1422) est formulé pour une série ; et le bouton « Voir la démonstration », quand un test est déjà chargé, ouvre l'écran d'import avec « le fichier remplace les données du test » (`node misc.js`, bloc 2) : un clic de plus écrase le test en cours.

## Vérifié sans rien trouver

- **A. Sécurité.**
  - CSV hostile (`sec1.js`, 290 contrôles, 0 échec) : 10 charges × 2 modes (série, instantané) placées dans tous les en-têtes, le nom du test, les deux libellés de variation, les noms de métriques (taux et moyenne) et le nom de fichier ; contrôle après chaque écran : import, après choix des colonnes, résultats, données, plan, légende, détail, sélection de lignes, partage, métriques suivies, saisie manuelle avec erreurs, second import refusé, accueil après rechargement, rechargement depuis la sauvegarde locale.
  - Liens `#t=j…` forgés et sauvegardes locales forgées (`sec2.js`, 182 contrôles, 0 échec) : charges dans le nom, les métriques (nom, id, src, rôle, sens, type, marge), les libellés, tous les champs du plan, `startDate`, `d`, `weeks[].end` (pur, suffixé, en tableau), nombres remplacés par des chaînes, clés `__proto__` / `constructor`, puis copie modifiable et import par-dessus ; sauvegarde locale avec `map` et `end` hostiles puis import d'un fichier dont les en-têtes sont ces charges.
  - `h.replace('<!--lg-->', …)` : le texte inséré est statique ; charge `$& $' <!--lg-->` dans tous les champs : une seule légende insérée, rien d'injecté.
  - `cleanState` : `weeks[i].end` et `plan.startDate` ne passent que sous la forme stricte `AAAA-MM-JJ` ; `map` est tronqué et toujours échappé à l'affichage.
  - Adresse email : 13 valeurs essayées ; seul le constat 12.
- **B. Dates** (`dates.js`, 47 cas) : 1, 6, 7, 8, 13, 14, 15, 28 jours au premier import ; valeurs par défaut ; fin future, fin avant début, champs vides ; second import à +0, +1, +6, +7, +8, +13, +14 jours ; lecture précédente sans date ; changements d'heure du 29/03 et du 25/10/2026, fin de mois, 29 février 2028, passage d'année, 4 fuseaux ; valeur par défaut à 00 h 30 et 23 h 30 ; mode jour. Le décompte des jours est exact partout (calcul en UTC), aucun décalage d'un jour.
- **C.** 15 séries (7 cumulées, 8 non cumulées) + 2 instantanés : voir constats 3 et 8. Le fichier `non-cumule.csv` du dépôt est bien alerté et refusé.
- **D.** 11 cas : colonnes réordonnées (reprises par nom, correct), en-têtes renommés (refus clair), test en 2e position (bon test repris), deux tests de même nom (refus), passage à « Aucune » colonne de test, premier fichier sans colonne de test puis fichier à 2 tests (refus), export Piano réel (colonne « MVT - Test » trouvée, ligne « N/A » écartée, 4 tests proposés, libellés nettoyés).
- **E.** Égalité stricte des 6 effets détectables entre l'assistant et l'onglet Plan pour 5 jeux de réglages × 2 largeurs (10 sur 10 identiques) ; le plan créé reprend confiance, puissance, durée, trafic et date dans les 10 cas ; 13 couples trafic/conversions absurdes sans erreur JavaScript ; 6 saisies absurdes à l'étape 3 correctement refusées ; retour arrière : toutes les valeurs des étapes 1 et 2 conservées.
- **F.** `regr.js` : `exemple-8-metriques.csv` avec k par défaut, k = 6, k = 12, la démonstration, et le même fichier importé en 6 instantanés successifs. 42 lignes métrique × semaine par scénario : décision, statuts, Z, bornes d'efficacité et de futilité, bornes des garde-fous et secondaires, intervalles, tous strictement égaux.
- **G.** `ui.js`, règles du thème injectées, 25 écrans à chaque largeur (accueil : 5 onglets d'outil et dernière image de chaque tutoriel ; assistant : 3 étapes, vide, rempli, en erreur ; import : série, non cumulé avec alerte et erreurs, Piano, refus de date ; résultats, légende ouverte, détail, partage avant et après email, données, plan). Aux deux largeurs : débordement horizontal 0 px sur les 50 mesures, aucun élément hors écran, aucun bouton ne change de taille au survol (7 à 16 boutons survolés par écran), aucun libellé de bouton coupé. À 360 px : seuls les constats 18 et 19. À 1280 px : aucun désalignement ni texte coupé ; le lien « Comment lire les statuts » fait 152 × 24 px et le lien « Parlez-en à Mathieu Fauveaux » 17 px de haut (cibles petites, sans gravité sur ordinateur). La FAQ de l'accueil n'a pas été ouverte (aucun bouton `data-act=faq` trouvé par le script).

## Non vérifié, et pourquoi

- **Comptes** (extension WordPress) : aucun serveur dans le bac à sable. La perte de `map` à l'enregistrement dans un compte (constat 9) et le rendu du tableau de bord sont lus dans le code, pas rejoués.
- **Ouverture réelle de la messagerie** : le `mailto` est intercepté par `GST_NOMAIL` ; le comportement d'Outlook ou de Gmail face à un lien de 2 000 caractères ou à un paramètre injecté n'est pas testé.
- **Images du tutoriel** : pas de réseau, donc ni chargement, ni dimensions réelles, ni saut de mise en page à l'arrivée des images.
- **Thème WordPress réel** : seules les 3 règles fournies sont injectées ; les autres règles d'Elementor (polices, `input`, `select`) ne sont pas simulées.
- **Navigateurs** : Chromium uniquement ; ni Safari iOS (champ date, presse-papiers), ni Firefox.
- **Mode « chaque jour »** : seule l'absence de règle des semaines est vérifiée ; les injections y sont couvertes par le rendu, mais pas par un parcours dédié.
- **Diff ligne à ligne** : fait (385 lignes de diff), mais je n'ai pas relu une à une les règles CSS modifiées ; la partie CSS est jugée par la mesure, pas par la lecture.
- **Bancs du constructeur** (`repo/tests/banc-v56-3*.js`) : lus en partie, non lancés.

-- =====================================================================
-- REQUETE TYPE : export cumule d'un test A/B pour l'analyse sequentielle
-- ---------------------------------------------------------------------
-- Ce qu'elle produit : une ligne par variation, une colonne par
-- metrique, en cumul depuis le premier jour du test. C'est le fichier
-- a importer dans l'outil d'analyse sequentielle.
--
-- Comment l'utiliser : a chaque lecture, on ne change que la date "fin"
-- dans les parametres. La requete repart toujours du premier jour : on
-- n'additionne donc jamais deux exports, et aucun visiteur n'est compte
-- deux fois.
--
-- Ce qu'il faut adapter une fois, au demarrage : les noms de tables,
-- la cle d'identite, les noms d'evenements et la colonne de montant.
-- Ces endroits sont marques par une fleche "<-".
--
-- Tables de votre outil de test (hors export Google Analytics 4).
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1. PARAMETRES : les seules lignes a modifier
-- ---------------------------------------------------------------------
DECLARE test  STRING DEFAULT 'ID_DU_TEST';
  -- Identifiant du test tel qu'il est stocke dans la table d'exposition.

DECLARE debut DATE DEFAULT DATE '2027-01-11';
  -- Premier jour du test. Ne change jamais apres le lancement.

DECLARE fin   DATE DEFAULT DATE '2027-01-31';
  -- "Donnees jusqu'au" : dernier jour COMPLET. Ne jamais mettre la date
  -- du jour, dont les donnees sont partielles.

DECLARE declencheur STRING DEFAULT NULL;
  -- Definit la population analysee.
  --
  -- NULL (par defaut) : tous les utilisateurs affectes au test.
  --   A utiliser quand le changement est visible des l'arrivee sur la
  --   page testee (ex. : nouveau bandeau en haut de page).
  --
  -- Un nom d'evenement : uniquement les utilisateurs qui ont atteint
  --   l'endroit ou se trouve le changement. Les conversions ne comptent
  --   alors qu'a partir de ce moment.
  --
  -- EXEMPLE : on teste un nouveau bloc de recommandations place en bas
  -- de la fiche produit. Une grande partie des visiteurs ne descend
  -- jamais jusque-la : ils diluent l'effet. On restreint donc a ceux
  -- qui ont atteint la zone :
  --
  --   DECLARE declencheur STRING DEFAULT 'scroll_zone_recommandations';
  --
  -- Autres exemples valables :
  --   'view_cart'        test sur la page panier
  --   'begin_checkout'   test sur une etape du tunnel de commande
  --   'ouverture_menu'   test sur le contenu du menu, si l'ouverture
  --                      du menu est identique dans les deux variations
  --
  -- REGLE : l'evenement doit se declencher de la meme facon dans le
  -- controle et dans la variation. Il marque "l'utilisateur est arrive
  -- la ou le changement se trouve", pas "l'utilisateur a vu ou utilise
  -- le nouvel element".
  --
  -- A NE PAS FAIRE :
  --   'clic_recommandation'  le clic est un effet de la variation :
  --                          filtrer dessus fausse la comparaison.
  --                          Il se mesure en metrique (bloc 7).
  --   'vue_nouveau_bloc'     l'evenement n'existe que dans la variation :
  --                          le controle n'aurait aucun utilisateur.


WITH

-- ---------------------------------------------------------------------
-- 2. AFFECTATION : un utilisateur, sa variation, sa premiere affectation
-- ---------------------------------------------------------------------
-- On part de la table ou l'outil de test enregistre "tel utilisateur a
-- ete place dans telle variation". On garde la premiere fois.
affect AS (
  SELECT
    visitor_id      AS uid,        -- <- CLE D'IDENTITE. C'est ici, et seulement
                                   --    ici, que se regle la continuite
                                   --    utilisateur : identifiant de compte,
                                   --    identifiant d'appareil, ou autre.
    variation,
    MIN(event_ts)   AS t_affect
  FROM `projet.dataset.expositions`  -- <- table d'exposition a adapter
  WHERE test_id = test
    AND DATE(event_ts) BETWEEN debut AND fin
      -- DATE(event_ts) decoupe les jours en UTC. Si vos jours sont en
      -- heure de Paris : DATE(event_ts, 'Europe/Paris'), ici et plus bas.
  GROUP BY uid, variation
),

-- ---------------------------------------------------------------------
-- 3. NETTOYAGE : exclure les utilisateurs vus dans plusieurs variations
-- ---------------------------------------------------------------------
-- Un utilisateur qui a vu le controle ET la variation ne peut etre
-- attribue a aucun des deux. On l'exclut. La part exclue se surveille
-- a chaque lecture (controle en bas de fichier).
propres AS (
  SELECT
    uid,
    ANY_VALUE(variation) AS variation,
    MIN(t_affect)        AS t_affect
  FROM affect
  GROUP BY uid
  HAVING COUNT(*) = 1   -- une seule variation pour cet utilisateur
),

-- ---------------------------------------------------------------------
-- 4. POPULATION ANALYSEE et instant de depart (t0)
-- ---------------------------------------------------------------------
-- t0 = moment a partir duquel on compte les conversions.
-- Sans declencheur : t0 = l'affectation.
-- Avec declencheur : t0 = premier passage par l'evenement declencheur,
--                    apres l'affectation.
-- Les deux branches ne s'executent jamais ensemble : c'est le parametre
-- "declencheur" qui choisit.
exposes AS (
  -- Branche A : pas de declencheur, tous les affectes
  SELECT uid, variation, t_affect AS t0
  FROM propres
  WHERE declencheur IS NULL

  UNION ALL

  -- Branche B : declencheur renseigne, seulement ceux qui l'ont atteint
  SELECT p.uid, p.variation, MIN(e.event_ts) AS t0
  FROM propres p
  JOIN `projet.dataset.evenements` e  -- <- table d'evenements a adapter
    ON  e.visitor_id = p.uid
    AND e.event_ts  >= p.t_affect     -- apres l'affectation uniquement
    AND DATE(e.event_ts) <= fin
    AND e.event_name = declencheur
  WHERE declencheur IS NOT NULL
  GROUP BY p.uid, p.variation
),

-- ---------------------------------------------------------------------
-- 5. COMMANDES DEDOUBLONNEES : une ligne par commande
-- ---------------------------------------------------------------------
-- Un meme achat peut etre envoye deux fois (rechargement de la page de
-- confirmation, double marquage). On ramene donc a une ligne par numero
-- de commande avant de compter ou de sommer quoi que ce soit.
commandes_dedup AS (
  SELECT
    visitor_id          AS uid,
    order_id,
    MIN(event_ts)       AS t_commande,
    ANY_VALUE(revenue)  AS montant    -- <- colonne de montant a adapter.
                                      --    Fixer une fois pour toutes :
                                      --    HT ou TTC, avec ou sans livraison.
  FROM `projet.dataset.evenements`
  WHERE event_name = 'purchase'       -- <- nom de l'evenement d'achat
    AND DATE(event_ts) BETWEEN debut AND fin
  GROUP BY uid, order_id
),

-- ---------------------------------------------------------------------
-- 6. ACHATS PAR UTILISATEUR : uniquement apres t0
-- ---------------------------------------------------------------------
-- Une commande passee avant que l'utilisateur soit expose au test ne
-- peut pas etre un effet du test : elle est ignoree.
achats AS (
  SELECT
    x.uid,
    COUNT(*)        AS nb_commandes,
    SUM(c.montant)  AS ca
  FROM exposes x
  JOIN commandes_dedup c
    ON  c.uid = x.uid
    AND c.t_commande >= x.t0
  GROUP BY x.uid
),

-- ---------------------------------------------------------------------
-- 7. AUTRES CONVERSIONS PAR UTILISATEUR : uniquement apres t0
-- ---------------------------------------------------------------------
-- Metriques binaires : l'utilisateur l'a fait au moins une fois, ou non.
-- Pour ajouter une metrique : une ligne MAX(IF(...)) ci-dessous, le nom
-- de l'evenement dans la liste du WHERE, puis une colonne dans la
-- sortie (bloc 8).
-- Exemple pour le clic sur les recommandations :
--   MAX(IF(e.event_name = 'clic_recommandation', 1, 0)) AS clic_reco
autres AS (
  SELECT
    x.uid,
    MAX(IF(e.event_name = 'add_to_cart', 1, 0)) AS panier
  FROM exposes x
  JOIN `projet.dataset.evenements` e
    ON  e.visitor_id = x.uid
    AND e.event_ts  >= x.t0
    AND DATE(e.event_ts) <= fin
  WHERE e.event_name IN ('add_to_cart')  -- <- liste des evenements suivis
  GROUP BY x.uid
)

-- ---------------------------------------------------------------------
-- 8. SORTIE : le fichier a importer dans l'outil
-- ---------------------------------------------------------------------
-- Une ligne par variation. Les utilisateurs sans achat ni conversion
-- sont conserves (LEFT JOIN) : ils comptent dans les visiteurs.
-- Les deux dates sont dans le fichier : l'outil lit la periode seul.
SELECT
  debut AS debut_test,
  fin   AS fin_donnees,
  x.variation,

  COUNT(*) AS visiteurs,
    -- Des visiteurs uniques, pas des visites. C'est le denominateur de
    -- toutes les metriques, et la base du controle de repartition.

  -- Metriques binaires (taux = colonne / visiteurs)
  COUNTIF(a.nb_commandes > 0) AS acheteurs,       -- objectif principal
  COUNTIF(v.panier = 1)       AS ajouts_panier,   -- metrique secondaire

  -- Metrique continue : le CA par visiteur.
  -- L'outil a besoin de deux colonnes, la somme et la somme des carres,
  -- nommees <metrique>_somme et <metrique>_somme_carres. Il en tire la
  -- moyenne et la dispersion, non-acheteurs inclus (a zero).
  ROUND(SUM(IFNULL(a.ca, 0)), 2)         AS ca_par_visiteur_somme,
  ROUND(SUM(POW(IFNULL(a.ca, 0), 2)), 2) AS ca_par_visiteur_somme_carres,

  -- Utilisateurs vus dans plusieurs variations : ecartes, mais comptes.
  (SELECT COUNT(*) FROM (SELECT uid FROM affect GROUP BY uid
                         HAVING COUNT(*) > 1)) AS exclus_deux_variations

FROM exposes x
LEFT JOIN achats a USING (uid)
LEFT JOIN autres v USING (uid)
GROUP BY x.variation
ORDER BY x.variation;


-- =====================================================================
-- NOTE : PANIER MOYEN ET CA PAR VISITEUR
-- ---------------------------------------------------------------------
-- Le test repartit des VISITEURS au hasard. La metrique continue qui se
-- teste proprement est donc le CA par visiteur.
--
-- Le panier moyen se calcule sur les seuls acheteurs, une population
-- que la variation peut elle-meme modifier. Exemple : la variation
-- convainc davantage de petits acheteurs. Le panier moyen BAISSE alors
-- que le CA par visiteur MONTE. Lu seul, le panier moyen ferait rejeter
-- un test gagnant.
--
-- Il se lit donc comme une decomposition :
--   taux d'achat  x  panier moyen  =  CA par visiteur
--
-- Le nombre de commandes et le panier moyen ne sont pas dans la sortie :
-- l'outil lirait ces colonnes comme des taux. Pour les lire a cote :
--   SUM(IFNULL(a.nb_commandes, 0))                     AS commandes
--   SAFE_DIVIDE(SUM(a.ca), SUM(a.nb_commandes))        AS panier_moyen
--
-- Montants tres eleves : quelques commandes peuvent dominer le resultat.
-- Si un plafonnement des montants est retenu, il se decide AVANT le
-- test, jamais apres avoir vu les donnees.
--
--
-- CONTROLES A FAIRE A CHAQUE LECTURE
-- ---------------------------------------------------------------------
-- 1) Repartition entre variations : comparer la colonne "visiteurs"
--    a la repartition prevue (50/50 en general). Un ecart net signale
--    un defaut technique : ne rien conclure avant de l'avoir explique.
--    Avec un declencheur, ce controle est indispensable : un
--    desequilibre signifie que le declencheur est biaise.
--
-- 2) Part des utilisateurs vus dans plusieurs variations (memes
--    parametres, meme bloc "affect") :
--
--   SELECT
--     COUNTIF(n > 1)                            AS multi_variations,
--     COUNT(*)                                  AS total,
--     ROUND(100 * COUNTIF(n > 1) / COUNT(*), 2) AS part_pct
--   FROM (SELECT uid, COUNT(*) AS n FROM affect GROUP BY uid);
--
--    Si cette part monte, c'est un probleme d'affectation ou de
--    continuite utilisateur a remonter, pas une ligne a nettoyer en
--    silence.
-- =====================================================================
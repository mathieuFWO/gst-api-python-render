#!/usr/bin/env Rscript
# Script pour calculer les bornes GST avec gsDesign ET le Z-score observé
# (Version intégrant Z-score observé - sfHSD gamma=-2 pour futilité par défaut)
# (AUCUN CHANGEMENT DANS CE FICHIER POUR CORRIGER LE PROBLEME D'AFFICHAGE Z-SCORE JS)

# --- Configuration initiale ---
# Désactiver la notation scientifique pour une meilleure lisibilité des messages
options(scipen = 999)

# --- Chargement des librairies ---
# Utiliser tryCatch pour gérer les erreurs de chargement de package
load_packages <- function() {
    suppressPackageStartupMessages({
        if (!requireNamespace("gsDesign", quietly = TRUE)) install.packages("gsDesign", repos = "https://cloud.r-project.org/")
        if (!requireNamespace("jsonlite", quietly = TRUE)) install.packages("jsonlite", repos = "https://cloud.r-project.org/")
        library(gsDesign)
        library(jsonlite, warn.conflicts = FALSE)
    })
}

# Tentative de chargement sécurisée
tryCatch({
    load_packages()
}, error = function(e) {
    # En cas d'échec, préparer une réponse JSON d'erreur et quitter
    error_msg <- gsub('"', '\\\\"', paste("Erreur chargement/installation package R:", e$message))
    error_json <- sprintf('{"error": true, "message": "%s"}', error_msg)
    writeLines(error_json, con = stdout())
    quit(save = "no", status = 1, runLast = FALSE)
})


# --- Fonctions utilitaires ---
# Fonction pour créer une réponse JSON d'erreur et quitter
exit_with_error <- function(message, details = NULL) {
    response <- list(error = TRUE, message = message)
    if (!is.null(details)) {
        response$details <- details
    }
    cat(toJSON(response, auto_unbox = TRUE, na = "null"))
    quit(save = "no", status = 1, runLast = FALSE)
}

# Fonction pour obtenir une valeur numérique ou NA (plus robuste)
get_numeric_or_na <- function(value) {
    if (is.null(value) || length(value) != 1) return(NA_real_)
    num_val <- suppressWarnings(as.numeric(value))
    if (is.na(num_val) || !is.finite(num_val)) return(NA_real_)
    return(num_val)
}


# --- Récupération et Validation des Arguments ---
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) {
    exit_with_error("Usage: Rscript calculate_gs_design.R '<json_input>'")
}
input_json <- args[1]

# --- Parsing du JSON d'entrée ---
params <- tryCatch({
    fromJSON(input_json, simplifyVector = TRUE) # simplifyVector est important
}, error = function(e) {
    exit_with_error(paste("Erreur parsing JSON:", e$message))
})

# --- Validation des Paramètres du Design Séquentiel ---
`%||%` <- function(a, b) { if (is.null(a) || length(a) == 0 || is.na(a)) b else a } # Robuste pour NULL, NA, length 0

k <- params$k
if (is.null(k) || !is.numeric(k) || k <= 0 || k != floor(k) || k > 50) { exit_with_error("Paramètre 'k' (nombre d'étapes, 1-50) invalide ou manquant.") }
k <- as.integer(k)

alpha <- get_numeric_or_na(params$alpha %||% 0.05)
if (is.na(alpha) || alpha <= 0 || alpha >= 1) { exit_with_error("Paramètre 'alpha' invalide (doit être entre 0 et 1).") }

beta <- get_numeric_or_na(params$beta %||% 0.20)
if (is.na(beta) || beta < 0 || beta >= 1) { # Beta peut être 0 (pas de contrôle erreur type II)
    exit_with_error("Paramètre 'beta' invalide (doit être entre 0 et 1).")
}
power <- 1 - beta

test_type <- as.integer(params$testType %||% 1)
if (!(test_type %in% c(1, 2, 3, 4, 5, 6))) { # gsDesign supporte 1 à 6
    exit_with_error("Paramètre 'testType' invalide (doit être 1-6, typiquement 1 ou 3).")
}

sfu_name_req <- tolower(params$sfu %||% "kimdemets") # Défaut à kimdemets, en minuscule
sfl_name_req <- tolower(params$sfl %||% "hsd") # Par défaut à HSD pour futilité (avec gamma)
sfl_param_req <- params$sflpar %||% -2 # Par défaut à gamma = -2 pour HSD

# --- Configuration des Fonctions de Dépense (Spending Functions) ---

# Efficacité (Upper bound)
sfu_param_val <- NULL
sfu_func <- NULL
sfu_standard_name <- NULL

if (sfu_name_req == "pocock") {
    sfu_func <- gsDesign::sfPocock
    sfu_standard_name <- "Pocock"
} else if (sfu_name_req == "of" || sfu_name_req == "obrienfleming") {
    sfu_func <- gsDesign::sfLDOF # O'Brien-Fleming like
    sfu_standard_name <- "OF"
} else if (sfu_name_req == "kimdemets") {
    sfu_func <- gsDesign::sfPower # sfPower est Kim-DeMets
    sfu_param_val <- 3 # Paramètre par défaut pour Kim-DeMets
    sfu_standard_name <- "KimDeMets"
} else if (sfu_name_req == "hsd") {
     sfu_func <- gsDesign::sfHSD
     sfu_param_val <- params$sfupar %||% 1 # Gamma pour HSD, défaut 1 si non fourni
     if(!is.numeric(sfu_param_val)) { exit_with_error("Paramètre 'sfupar' pour HSD (efficacité) doit être numérique.")}
     sfu_standard_name <- paste0("HSD(", sfu_param_val, ")")
} else {
     # Si non reconnu, utiliser O'Brien-Fleming par défaut
     warning(paste("Fonction SFU '", sfu_name_req, "' non reconnue, utilisation de O'Brien-Fleming (sfLDOF)."))
     sfu_func <- gsDesign::sfLDOF
     sfu_standard_name <- "OF"
     sfu_name_req <- "of" # Normaliser le nom
}

# Futilité (Lower bound) - Si test.type le permet (ex: 3, 4, 5, 6)
sfl_func <- NULL
sfl_param_val <- NULL
sfl_standard_name <- NULL

# Le paramètre sfl est seulement utilisé si test.type le requiert (non-binding ou binding)
if (test_type %in% c(3, 4, 5, 6)) {
    if (sfl_name_req == "hsd") {
        sfl_func <- gsDesign::sfHSD
        sfl_param_val <- sfl_param_req # Utilise la valeur par défaut (-2) ou celle fournie
        if(!is.numeric(sfl_param_val)) { exit_with_error("Paramètre 'sflpar' pour HSD (futilité) doit être numérique.")}
        sfl_standard_name <- paste0("HSD(", sfl_param_val, ")")
    } else if (sfl_name_req == "identity") { # Une autre option possible
        sfl_func <- gsDesign::sfLinear
        sfl_param_val <- 1 # Pente de 1 pour dépense linéaire
        sfl_standard_name <- "Linear"
     } else if (sfl_name_req == "pocock") { # Pocock pour futilité
         sfl_func <- gsDesign::sfPocock
         sfl_standard_name <- "Pocock"
     } else if (sfl_name_req == "of" || sfl_name_req == "obrienfleming") { # OF pour futilité
          sfl_func <- gsDesign::sfLDOF
          sfl_standard_name <- "OF"
     } else if (sfl_name_req == "kimdemets") { # KimDeMets pour futilité
          sfl_func <- gsDesign::sfPower
          sfl_param_val <- params$sflpar %||% 3 # Gamma=3 par défaut si KimDeMets
          if(!is.numeric(sfl_param_val)) { exit_with_error("Paramètre 'sflpar' pour KimDeMets (futilité) doit être numérique.")}
          sfl_standard_name <- paste0("KimDeMets(", sfl_param_val, ")")
    } else {
         warning(paste("Fonction SFL '", sfl_name_req, "' non reconnue ou non applicable, utilisation de HSD(-2)."))
         sfl_func <- gsDesign::sfHSD
         sfl_param_val <- -2
         sfl_standard_name <- "HSD(-2)"
         sfl_name_req <- "hsd" # Normaliser
    }
} else {
    # Pour test.type 1 ou 2, il n'y a pas de borne inférieure de futilité définie par sfl
    sfl_standard_name <- "None (test.type 1/2)"
}


# Timing (Fraction d'information)
timing <- (1:k) / k # Suppose des étapes équitablement espacées par défaut

# --- Calcul des Bornes Séquentielles avec gsDesign ---
message(paste("Appel gsDesign: k=", k, ", test.type=", test_type, ", alpha=", alpha, ", beta=", beta))
message(paste("Using sfu:", sfu_standard_name, " (param:", if(is.null(sfu_param_val)) "NULL" else sfu_param_val, ")"))
if (!is.null(sfl_func)) {
    message(paste("Using sfl:", sfl_standard_name, " (param:", if(is.null(sfl_param_val)) "NULL" else sfl_param_val, ")"))
}

design_result <- NULL
design_error <- NULL
design <- tryCatch({
    # Appel gsDesign en utilisant les fonctions et paramètres déterminés
    # Note: sfupar et sflpar sont ignorés si la fonction correspondante ne prend pas de paramètre (ex: sfPocock, sfLDOF)
    gsDesign(k = k, test.type = test_type, alpha = alpha, beta = beta, timing = timing,
             sfu = sfu_func, sfupar = sfu_param_val,
             sfl = sfl_func, sflpar = sfl_param_val) # sfl/sflpar seront ignorés par gsDesign si test.type=1 ou 2
}, error = function(e) {
    design_error <<- e$message
    NULL # Retourne NULL en cas d'erreur
})

if (is.null(design)) {
    exit_with_error(paste("Erreur lors de l'exécution de gsDesign:", design_error), details = capture.output(traceback()))
}

# --- Calcul du Z-score Observé (si données fournies) ---
observed_z <- NA_real_ # Initialiser à NA réel
observed_z_message <- "Données A/B non fournies ou invalides, Z observé non calculé."
data_provided <- FALSE

# Vérifier la présence des clés nécessaires pour le calcul du Z observé
required_data_keys <- c("visitors_a", "conversions_a", "visitors_b", "conversions_b")
if (all(required_data_keys %in% names(params))) {
    data_provided <- TRUE
    # Essayer de convertir et valider les données
    visitors_a <- get_numeric_or_na(params$visitors_a)
    conversions_a <- get_numeric_or_na(params$conversions_a)
    visitors_b <- get_numeric_or_na(params$visitors_b)
    conversions_b <- get_numeric_or_na(params$conversions_b)

    # Validation des données numériques
    if (anyNA(c(visitors_a, conversions_a, visitors_b, conversions_b))) {
        observed_z_message <- "Données A/B contiennent des valeurs non numériques ou manquantes."
    } else if (visitors_a <= 0 || visitors_b <= 0) {
        observed_z_message <- "Le nombre de visiteurs (A et B) doit être supérieur à zéro."
    } else if (conversions_a < 0 || conversions_b < 0 || conversions_a > visitors_a || conversions_b > visitors_b) {
        observed_z_message <- "Nombre de conversions invalide (doit être >= 0 et <= visiteurs)."
    } else {
        # Toutes les validations de base sont passées, tenter le calcul
        tryCatch({
            p1 <- conversions_a / visitors_a
            p2 <- conversions_b / visitors_b
            n1 <- visitors_a
            n2 <- visitors_b

            # Calcul du taux pondéré (pooled proportion)
            p_pooled <- (conversions_a + conversions_b) / (n1 + n2)

            # Calcul de l'erreur standard pondérée (pooled standard error)
            # Gérer le cas p_pooled = 0 ou 1 -> variance nulle
            if (p_pooled <= 0 || p_pooled >= 1) {
                # Si les taux sont identiques (tous 0 ou tous 1), la différence est 0
                if (abs(p1 - p2) < .Machine$double.eps) {
                     observed_z <- 0.0
                     observed_z_message <- "Z observé calculé (p_pooled 0 ou 1, p1=p2)."
                } else {
                    # Taux différents, variance nulle -> Z techniquement infini
                    observed_z <- ifelse(p2 > p1, Inf, -Inf)
                    observed_z_message <- "Z observé calculé (p_pooled 0 ou 1, p1!=p2 -> +/- Inf)."
                    # Remplacer Inf par un grand nombre ou NA pour JSON ? NA est plus sûr.
                    observed_z <- NA_real_
                    observed_z_message <- "Z observé non calculé (p_pooled 0 ou 1, p1!=p2 -> variance nulle)."

                }
            } else {
                 # Calcul standard
                 se_pooled <- sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))

                 # Gérer le cas où SE est très proche de zéro (peut arriver avec N très grand)
                 if (se_pooled < .Machine$double.eps * 100) { # Marge de sécurité
                      observed_z <- NA_real_
                      observed_z_message <- "Z observé non calculé (Erreur standard pooled quasi-nulle)."
                 } else {
                      observed_z <- (p2 - p1) / se_pooled
                      observed_z_message <- paste("Z observé calculé avec succès:", round(observed_z, 5))
                 }
            }
        }, error = function(e) {
            # En cas d'erreur inattendue pendant le calcul
            observed_z <<- NA_real_ # Assurer que c'est NA
            observed_z_message <<- paste("Erreur lors du calcul du Z-score observé:", e$message)
        })
    }
}
message(observed_z_message) # Afficher le message sur stderr pour le log

# --- Préparation de la Sortie JSON ---
results <- list(
    error = FALSE,
    message = "Calcul des bornes et/ou Z-score terminé.",
    observedZ = ifelse(is.na(observed_z), NA, round(observed_z, 5)), # Retourne NA si non calculé/erreur, sinon arrondi
    observedZMessage = observed_z_message, # Message sur le statut du calcul Z
    parameters = list(
        k = k,
        alpha = alpha,
        beta = beta,
        power = power,
        testType = test_type,
        timing = timing,
        sfu = sfu_standard_name,
        sfuParam = sfu_param_val, # Peut être NULL
        sfl = sfl_standard_name, # Peut être "None" ou le nom de la fonction
        sflParam = sfl_param_val  # Peut être NULL
    ),
    boundaries = list() # Initialiser comme liste vide
)

# Remplir les détails des bornes pour chaque étape
# Utiliser les noms de colonnes directement depuis l'objet design$upper et design$lower
# Utiliser `[[` pour extraire les vecteurs, plus sûr que `$` dans une boucle
for (i in seq_len(k)) {
    # Initialiser les valeurs à NA réel pour cette étape
    info_frac <- NA_real_
    eff_z <- NA_real_
    fut_z <- NA_real_
    alpha_cum <- NA_real_
    beta_cum <- NA_real_

    # Extraire les valeurs si elles existent dans l'objet design
    info_frac <- get_numeric_or_na(design$n.I[[i]]) # Fraction d'information cumulée

    if (!is.null(design$upper) && length(design$upper$bound) >= i) {
        eff_z <- get_numeric_or_na(design$upper$bound[[i]]) # Borne Z d'efficacité
    }
     if (!is.null(design$upper) && length(design$upper$spend) >= i) {
        alpha_cum <- get_numeric_or_na(design$upper$spend[[i]]) # Alpha cumulé dépensé
    }

    # Les bornes inférieures existent selon test.type et la configuration
    if (!is.null(design$lower) && length(design$lower$bound) >= i) {
        fut_z <- get_numeric_or_na(design$lower$bound[[i]]) # Borne Z de futilité
    }
    if (!is.null(design$lower) && length(design$lower$spend) >= i) {
         beta_cum <- get_numeric_or_na(design$lower$spend[[i]]) # Beta cumulé dépensé (futilité)
    }


    results$boundaries[[i]] <- list(
        stage = i,
        infoFraction = info_frac,
        efficacyZ = eff_z,
        futilityZ = fut_z,
        alphaSpentCumulative = alpha_cum,
        betaSpentCumulative = beta_cum
    )
}

# --- Imprimer le JSON sur stdout et Quitter Proprement ---
cat(toJSON(results, pretty = FALSE, auto_unbox = TRUE, na = "null"))
quit(save = "no", status = 0, runLast = FALSE)

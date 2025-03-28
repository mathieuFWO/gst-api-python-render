#!/usr/bin/env Rscript
# Script pour calculer les bornes GST avec gsDesign (Version 7 - sfHSD gamma=-4)

# Charger les librairies nécessaires
# Utiliser tryCatch pour gérer les erreurs de chargement
tryCatch({
    suppressPackageStartupMessages(library(gsDesign))
    suppressPackageStartupMessages(library(jsonlite, warn.conflicts = FALSE))
}, error = function(e) {
    # En cas d'erreur de chargement, essayer d'écrire une erreur JSON valide
    error_response <- list(error = TRUE, message = paste("Erreur chargement package R:", e$message))
    # Utiliser writeLines car cat(toJSON(...)) pourrait échouer si jsonlite n'est pas chargé
    writeLines(sprintf('{"error": true, "message": "Erreur chargement package R: %s"}', gsub('"', '\\\\"', e$message)), con = stdout())
    quit(status = 1)
})


# --- Récupérer les arguments de la ligne de commande ---
args <- commandArgs(trailingOnly = TRUE)
error_response <- list(error = TRUE, message = "Erreur interne dans le script R.") # Défaut

# Vérifier le nombre d'arguments
if (length(args) != 1) {
  error_response$message <- "Usage: Rscript calculate_gs_design.R '<json_input>'"
  # Utiliser toJSON ici car jsonlite est chargé si on arrive ici
  cat(toJSON(error_response, auto_unbox = TRUE, na = "null"))
  quit(status = 1)
}

input_json <- args[1]

# --- Parser le JSON d'entrée ---
params <- tryCatch({
  fromJSON(input_json)
}, error = function(e) {
  error_response$message <- paste("Erreur lors du parsing JSON:", e$message)
  cat(toJSON(error_response, auto_unbox = TRUE, na = "null"))
  quit(status = 1)
})

# --- Validation et Paramètres par défaut ---
# Helper pour valeur par défaut si NULL
`%||%` <- function(a, b) { if (is.null(a)) b else a }

# Récupération et valeurs par défaut
k <- params$k
alpha <- params$alpha %||% 0.05
beta <- params$beta %||% 0.20
test_type <- params$testType %||% 1 # Défaut Supériorité (1)
sfu_name_req <- params$sfu %||% "KimDeMets" # Défaut KimDeMets pour sfu
# sfl_name_req n'est plus utilisé, car sfl est forcé ci-dessous pour type 1/3

# Vérifications basiques des paramètres
if (is.null(k) || !is.numeric(k) || k <= 0 || k > 50) { # Limiter K
  error_response$message <- "Le paramètre 'k' (1-50) est manquant ou invalide."
  cat(toJSON(error_response, auto_unbox = TRUE, na = "null"))
  quit(status = 1)
}
if (is.null(alpha) || !is.numeric(alpha) || alpha <= 0 || alpha >= 1) {
    error_response$message <- "Le paramètre 'alpha' est manquant ou invalide."
    cat(toJSON(error_response, auto_unbox = TRUE, na = "null"))
    quit(status = 1)
}
if (is.null(beta) || !is.numeric(beta) || beta <= 0 || beta >= 1) {
    error_response$message <- "Le paramètre 'beta' est manquant ou invalide."
    cat(toJSON(error_response, auto_unbox = TRUE, na = "null"))
    quit(status = 1)
}
# Vérifier que test_type est bien 1 ou 3 pour cette logique
if (!(test_type %in% c(1, 3))) {
    error_response$message <- "Type de test invalide (1='Supériorité' ou 3='Non-régression')."
    cat(toJSON(error_response, auto_unbox = TRUE, na = "null"))
    quit(status = 1)
}
k <- as.integer(k)

# --- Obtenir fonction/paramètre pour SFU (Efficacité) ---
get_spending_info_sfu <- function(name) {
  safe_name <- tolower(name %||% "kimdemets")
  param_val <- NULL
  func <- gsDesign::sfLDOF # Default OF
  standard_name <- "OF"

  if (safe_name == "pocock") {
    func <- gsDesign::sfPocock
    standard_name <- "Pocock"
  } else if (safe_name == "kimdemets") {
    func <- gsDesign::sfPower
    param_val <- 3
    standard_name <- "KimDeMets"
  } # else, reste OF

  return(list(func = func, param = param_val, name = standard_name))
}
sfu_info <- get_spending_info_sfu(sfu_name_req)

# --- Définir fonction/paramètre pour SFL (Futilité/Inf) ---
# Utilisation de sfHSD avec gamma = -4 pour les types 1 et 3
sfl_gamma <- -4 # *** PARAMETRE GAMMA MODIFIÉ ICI ***
sfl_info <- list(func = gsDesign::sfHSD, param = sfl_gamma, name = paste0("HSD(", sfl_gamma, ")"))

# Timing (inchangé)
timing <- (1:k) / k

# --- Appel à gsDesign ---
# Ajouter des logs pour débogage dans Render
message(paste("Appel gsDesign: k=", k, ", alpha=", alpha, ", beta=", beta, ", test.type=", test_type))
message(paste("Using sfu:", sfu_info$name, "with param:", sfu_info$param %||% "NULL"))
message(paste("Using sfl:", sfl_info$name, "with param:", sfl_info$param %||% "NULL")) # Affichera HSD(-4)

design <- tryCatch({
  gsDesign(
    k = k,
    test.type = test_type,
    alpha = alpha,
    beta = beta,
    timing = timing,
    sfu = sfu_info$func,
    sfupar = sfu_info$param,
    sfl = sfl_info$func,
    sflpar = sfl_info$param # Utilise sfHSD et param gamma modifié
  )
}, error = function(e) {
  # En cas d'erreur DANS gsDesign
  error_response$message <<- paste("Erreur lors de l'appel à gsDesign:", e$message) # Utiliser <<- pour modifier variable externe
  error_response$details <<- capture.output(traceback())
  NULL # Retourner NULL pour indiquer l'échec
})

# Vérifier si l'appel gsDesign a échoué
if (is.null(design)) {
  cat(toJSON(error_response, auto_unbox = TRUE, na = "null")) # Utiliser na="null"
  quit(status = 1)
}

# --- Préparer la sortie JSON ---
results <- list(
  error = FALSE, # Sera [false]
  message = "Calcul des bornes réussi.", # Sera ["Calcul..."]
  parameters = list(
      k = k, alpha = alpha, beta = beta, testType = test_type, timing = timing,
      sfu = sfu_info$name, sfl = sfl_info$name # Utiliser noms standardisés
  ),
  boundaries = list()
)

# Fonction helper pour obtenir une valeur numérique ou NA
get_numeric_or_na <- function(value) {
  # Vérifie si c'est un nombre unique, fini, et pas NULL
  if (!is.null(value) && is.numeric(value) && length(value) == 1 && is.finite(value)) {
    return(value)
  } else {
    return(NA) # Utiliser NA
  }
}

# Boucle pour créer les boundaries
for (i in seq_len(k)) {
  # Vérifier l'existence des sous-listes avant d'accéder
  upper_bound <- if (!is.null(design$upper)) get_numeric_or_na(design$upper$bound[i]) else NA
  lower_bound <- if (!is.null(design$lower)) get_numeric_or_na(design$lower$bound[i]) else NA
  upper_spend <- if (!is.null(design$upper)) get_numeric_or_na(design$upper$spend[i]) else NA
  lower_spend <- if (!is.null(design$lower)) get_numeric_or_na(design$lower$spend[i]) else NA

  results$boundaries[[i]] <- list(
    stage = i, # Sera [i]
    infoFraction = get_numeric_or_na(design$n.I[i]), # Sera [val] ou null
    efficacyZ = upper_bound, # Sera [val] ou null
    futilityZ = lower_bound, # Sera [val] ou null
    alphaSpentCumulative = upper_spend, # Sera [val] ou null
    betaSpentCumulative = lower_spend # Sera [val] ou null
  )
}

# --- Imprimer le JSON sur stdout ---
# Forcer na = "null"
cat(toJSON(results, pretty = FALSE, na = "null"))

quit(status = 0) # Succès

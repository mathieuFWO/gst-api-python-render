#!/usr/bin/env Rscript
# Script pour calculer les bornes GST avec gsDesign (Version 5)

# Charger les librairies nécessaires
suppressPackageStartupMessages(library(gsDesign))
suppressPackageStartupMessages(library(jsonlite, warn.conflicts = FALSE))

# --- Récupérer les arguments de la ligne de commande ---
args <- commandArgs(trailingOnly = TRUE)
error_response <- list(error = TRUE, message = "Erreur interne dans le script R.")
if (length(args) != 1) {
  error_response$message <- "Usage: Rscript calculate_gs_design.R '<json_input>'"
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

k <- params$k
alpha <- params$alpha %||% 0.05
beta <- params$beta %||% 0.20
test_type <- params$testType %||% 2 # Défaut Bilatéral (2) si non fourni
sfu_name_req <- params$sfu %||% "KimDeMets" # Défaut KimDeMets pour sfu
sfl_name_req <- params$sfl %||% sfu_name_req # Utiliser la même par défaut pour sfl

# Vérifications basiques
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
if (!(test_type %in% c(1, 2, 3, 4, 5, 6))) { # Vérifier les types supportés par gsDesign
    error_response$message <- "Le paramètre 'testType' est invalide (doit être 1-6)."
    cat(toJSON(error_response, auto_unbox = TRUE, na = "null"))
    quit(status = 1)
}
k <- as.integer(k)

# --- Obtenir la fonction de dépense de base et son paramètre ---
get_spending_info <- function(name) {
  safe_name <- tolower(name %||% "kimdemets") # Défaut KimDeMets si name est NULL
  param_val <- NULL
  func <- gsDesign::sfLDOF # Initialisation défaut

  if (safe_name == "pocock") {
    func <- gsDesign::sfPocock
  } else if (safe_name == "kimdemets") {
    func <- gsDesign::sfPower
    param_val <- 3
  } else if (safe_name == "of") { # Explicite pour O'Brien-Fleming
      func <- gsDesign::sfLDOF
  }
  # Si inconnu, on garde sfLDOF et param_val=NULL

  # Retourner le nom standardisé pour l'affichage
  standard_name <- switch(safe_name,
                          "pocock" = "Pocock",
                          "kimdemets" = "KimDeMets",
                          "of" = "OF", # Utiliser OF pour O'Brien-Fleming
                          "OF") # Défaut

  return(list(func = func, param = param_val, name = standard_name))
}

# Obtenir les infos pour les bornes sup (sfu) et inf (sfl)
sfu_info <- get_spending_info(sfu_name_req)
sfl_info <- get_spending_info(sfl_name_req)

# Timing : Supposer des étapes équi-espacées en information par défaut
timing <- (1:k) / k

# --- Appel à gsDesign ---
message(paste("Appel gsDesign: k=", k, "alpha=", alpha, "beta=", beta, "test.type=", test_type))
message(paste("Using sfu:", sfu_info$name, "with param:", sfu_info$param %||% "NULL"))
message(paste("Using sfl:", sfl_info$name, "with param:", sfl_info$param %||% "NULL"))

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
    sflpar = sfl_info$param
  )
}, error = function(e) {
  error_response$message <- paste("Erreur lors de l'appel à gsDesign:", e$message)
  error_response$details <- capture.output(traceback())
  NULL
})

if (is.null(design)) {
  cat(toJSON(error_response, auto_unbox = TRUE, na = "null"))
  quit(status = 1)
}

# --- Préparer la sortie JSON ---
results <- list(
  error = FALSE,
  message = "Calcul des bornes réussi.",
  parameters = list(
      k = k, alpha = alpha, beta = beta, testType = test_type, timing = timing,
      sfu = sfu_info$name, sfl = sfl_info$name # Utiliser les noms standardisés
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
    stage = i,
    infoFraction = get_numeric_or_na(design$n.I[i]), # design$n.I devrait toujours exister
    efficacyZ = upper_bound, # Correspond à la borne supérieure
    futilityZ = lower_bound, # Correspond à la borne inférieure
    alphaSpentCumulative = upper_spend,
    betaSpentCumulative = lower_spend
  )
}

# --- Imprimer le JSON sur stdout ---
# Forcer na = "null"
cat(toJSON(results, pretty = FALSE, na = "null"))

quit(status = 0) # Succès

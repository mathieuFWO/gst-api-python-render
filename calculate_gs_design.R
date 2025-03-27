#!/usr/bin/env Rscript
# Script pour calculer les bornes GST avec gsDesign

# Charger les librairies nécessaires
suppressPackageStartupMessages(library(gsDesign))
suppressPackageStartupMessages(library(jsonlite))

# --- Récupérer les arguments de la ligne de commande ---
args <- commandArgs(trailingOnly = TRUE)

# Initialiser la réponse d'erreur par défaut
error_response <- list(error = TRUE, message = "Erreur interne dans le script R.")

if (length(args) != 1) {
  error_response$message <- "Usage: Rscript calculate_gs_design.R '<json_input>'"
  cat(toJSON(error_response, auto_unbox = TRUE))
  quit(status = 1)
}

input_json <- args[1]

# --- Parser le JSON d'entrée ---
params <- tryCatch({
  fromJSON(input_json)
}, error = function(e) {
  error_response$message <- paste("Erreur lors du parsing JSON:", e$message)
  cat(toJSON(error_response, auto_unbox = TRUE))
  quit(status = 1)
})

# --- Validation et Paramètres par défaut ---
# Helper pour valeur par défaut si NULL
`%||%` <- function(a, b) {
  if (is.null(a)) b else a
}

k <- params$k
alpha <- params$alpha %||% 0.05
beta <- params$beta %||% 0.20
test_type <- params$testType %||% 1 # 1 = one-sided (supériorité)
sfu_name_req <- params$sfu %||% "OF" # Nom demandé pour sfu
sfl_name_req <- params$sfl %||% sfu_name_req # Nom demandé pour sfl

# Vérifications basiques
if (is.null(k) || !is.numeric(k) || k <= 0) {
  error_response$message <- "Le paramètre 'k' (nombre d'étapes) est manquant ou invalide."
  cat(toJSON(error_response, auto_unbox = TRUE))
  quit(status = 1)
}
if (is.null(alpha) || !is.numeric(alpha) || alpha <= 0 || alpha >= 1) {
    error_response$message <- "Le paramètre 'alpha' est manquant ou invalide."
    cat(toJSON(error_response, auto_unbox = TRUE))
    quit(status = 1)
}
k <- as.integer(k)

# --- Obtenir la fonction de dépense de base et son paramètre (MODIFIÉ) ---
get_spending_info <- function(name) {
  safe_name <- tolower(name %||% "of")
  param_val <- NULL # Pas de paramètre par défaut
  func <- gsDesign::sfLDOF # Fonction par défaut

  if (safe_name == "pocock") {
    func <- gsDesign::sfPocock
  } else if (safe_name == "kimdemets") {
    func <- gsDesign::sfPower
    param_val <- 3 # Paramètre pour KimDeMets approx
  }
  # Si c'est "of" ou inconnu, on garde sfLDOF et param_val=NULL

  return(list(func = func, param = param_val, name = safe_name))
}

# Obtenir les infos pour les bornes sup (sfu) et inf (sfl)
sfu_info <- get_spending_info(sfu_name_req)
sfl_info <- get_spending_info(sfl_name_req)

# Timing : Supposer des étapes équi-espacées en information par défaut
timing <- (1:k) / k

# --- Appel à gsDesign (MODIFIÉ) ---
# Utilisation de sfu, sfl, sfupar, sflpar
message(paste("Appel gsDesign: k=", k, "alpha=", alpha, "beta=", beta)) # Log simplifié
message(paste("Using sfu:", sfu_info$name, "with param:", sfu_info$param %||% "NULL"))
message(paste("Using sfl:", sfl_info$name, "with param:", sfl_info$param %||% "NULL"))

design <- tryCatch({
  gsDesign(
    k = k,
    test.type = test_type,
    alpha = alpha,
    beta = beta,
    timing = timing,
    sfu = sfu_info$func,     # Fonction de base pour borne sup
    sfupar = sfu_info$param, # Paramètre pour borne sup (sera NULL si OF/Pocock)
    sfl = sfl_info$func,     # Fonction de base pour borne inf
    sflpar = sfl_info$param  # Paramètre pour borne inf (sera NULL si OF/Pocock)
                             # Note: Passer 'param=3' à sfl est une convention pour
                             # obtenir une forme similaire, même si 'alpha' n'est
                             # pas directement utilisé pour la dépense beta ici.
  )
}, error = function(e) {
  error_response$message <- paste("Erreur lors de l'appel à gsDesign:", e$message)
  error_response$details <- capture.output(traceback()) # Obtenir la trace
  NULL # Retourne NULL en cas d'erreur
})

if (is.null(design)) {
  cat(toJSON(error_response, auto_unbox = TRUE))
  quit(status = 1)
}


# --- Préparer la sortie JSON ---
results <- list(
  error = FALSE,
  message = "Calcul des bornes réussi.",
  parameters = list(
      k = k,
      alpha = alpha,
      beta = beta,
      testType = test_type,
      timing = timing,
      sfu = sfu_info$name, # Utiliser le nom identifié
      sfl = sfl_info$name  # Utiliser le nom identifié
  ),
  boundaries = list()
)

# Utiliser seq_len pour être sûr
for (i in seq_len(k)) {
  results$boundaries[[i]] <- list(
    stage = i,
    infoFraction = design$n.I[i],
    efficacyZ = design$upper$bound[i],
    futilityZ = design$lower$bound[i],
    alphaSpentCumulative = design$upper$spend[i],
    betaSpentCumulative = design$lower$spend[i]
  )
}

# --- Imprimer le JSON sur stdout ---
cat(toJSON(results, auto_unbox = TRUE, pretty = FALSE))

quit(status = 0) # Succès

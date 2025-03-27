#!/usr/bin/env Rscript
# Script pour calculer les bornes GST avec gsDesign

# Charger les librairies nécessaires
suppressPackageStartupMessages(library(gsDesign))
suppressPackageStartupMessages(library(jsonlite, warn.conflicts = FALSE))

# --- Récupérer les arguments ... (inchangé) ---
args <- commandArgs(trailingOnly = TRUE)
error_response <- list(error = TRUE, message = "Erreur interne dans le script R.")
if (length(args) != 1) {
  error_response$message <- "Usage: Rscript calculate_gs_design.R '<json_input>'"
  cat(toJSON(error_response, auto_unbox = TRUE, na = "null")) # Garder auto_unbox pour les erreurs simples
  quit(status = 1)
}
input_json <- args[1]

# --- Parser le JSON ... (inchangé) ---
params <- tryCatch({
  fromJSON(input_json)
}, error = function(e) {
  error_response$message <- paste("Erreur lors du parsing JSON:", e$message)
  cat(toJSON(error_response, auto_unbox = TRUE, na = "null"))
  quit(status = 1)
})

# --- Validation et Paramètres ... (inchangé) ---
`%||%` <- function(a, b) { if (is.null(a)) b else a }
k <- params$k
alpha <- params$alpha %||% 0.05
beta <- params$beta %||% 0.20
test_type <- params$testType %||% 1
sfu_name_req <- params$sfu %||% "OF"
sfl_name_req <- params$sfl %||% sfu_name_req
if (is.null(k) || !is.numeric(k) || k <= 0) {
  error_response$message <- "Paramètre 'k' manquant ou invalide."
  cat(toJSON(error_response, auto_unbox = TRUE, na = "null"))
  quit(status = 1)
}
if (is.null(alpha) || !is.numeric(alpha) || alpha <= 0 || alpha >= 1) {
    error_response$message <- "Paramètre 'alpha' manquant ou invalide."
    cat(toJSON(error_response, auto_unbox = TRUE, na = "null"))
    quit(status = 1)
}
k <- as.integer(k)

# --- Obtenir fonction/paramètre ... (inchangé) ---
get_spending_info <- function(name) {
  safe_name <- tolower(name %||% "of")
  param_val <- NULL
  func <- gsDesign::sfLDOF
  if (safe_name == "pocock") { func <- gsDesign::sfPocock }
  else if (safe_name == "kimdemets") { func <- gsDesign::sfPower; param_val <- 3 }
  return(list(func = func, param = param_val, name = safe_name))
}
sfu_info <- get_spending_info(sfu_name_req)
sfl_info <- get_spending_info(sfl_name_req)
timing <- (1:k) / k

# --- Appel à gsDesign ... (inchangé) ---
message(paste("Appel gsDesign: k=", k, "alpha=", alpha, "beta=", beta))
message(paste("Using sfu:", sfu_info$name, "with param:", sfu_info$param %||% "NULL"))
message(paste("Using sfl:", sfl_info$name, "with param:", sfl_info$param %||% "NULL"))
design <- tryCatch({
  gsDesign(k = k, test.type = test_type, alpha = alpha, beta = beta, timing = timing,
           sfu = sfu_info$func, sfupar = sfu_info$param,
           sfl = sfl_info$func, sflpar = sfl_info$param)
}, error = function(e) {
  error_response$message <- paste("Erreur lors de l'appel à gsDesign:", e$message)
  error_response$details <- capture.output(traceback())
  NULL
})
if (is.null(design)) {
  cat(toJSON(error_response, auto_unbox = TRUE, na = "null"))
  quit(status = 1)
}

# --- Préparer la sortie JSON ... (inchangé) ---
results <- list(
  error = FALSE,
  message = "Calcul des bornes réussi.",
  parameters = list(
      k = k, alpha = alpha, beta = beta, testType = test_type, timing = timing,
      sfu = sfu_info$name, sfl = sfl_info$name
  ),
  boundaries = list()
)
get_numeric_or_na <- function(value) {
  if (is.numeric(value) && length(value) == 1 && is.finite(value)) {
    return(value)
  } else {
    return(NA)
  }
}
for (i in seq_len(k)) {
  results$boundaries[[i]] <- list(
    stage = i,
    infoFraction = get_numeric_or_na(design$n.I[i]),
    efficacyZ = get_numeric_or_na(design$upper$bound[i]),
    futilityZ = get_numeric_or_na(design$lower$bound[i]),
    alphaSpentCumulative = get_numeric_or_na(design$upper$spend[i]),
    betaSpentCumulative = get_numeric_or_na(design$lower$spend[i])
  )
}

# --- Imprimer le JSON sur stdout (MODIFIÉ) ---
# Forcer na = "null" et retirer auto_unbox pour le résultat principal
cat(toJSON(results, pretty = FALSE, na = "null"))

quit(status = 0) # Succès

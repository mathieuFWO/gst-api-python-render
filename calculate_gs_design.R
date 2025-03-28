#!/usr/bin/env Rscript
# Script pour calculer les bornes GST avec gsDesign (Version 6 - sfHSD pour futility)

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

# --- Parser le JSON ... (inchangé) ---
params <- tryCatch({ fromJSON(input_json) }, error = function(e) { /* ... gestion erreur ... */ })

# --- Validation et Paramètres ... (inchangé) ---
`%||%` <- function(a, b) { if (is.null(a)) b else a }
k <- params$k; alpha <- params$alpha %||% 0.05; beta <- params$beta %||% 0.20
test_type <- params$testType %||% 1 # Défaut Supériorité si non fourni
sfu_name_req <- params$sfu %||% "KimDeMets"
# sfl_name_req n'est plus lu directement depuis params, on le force pour test unilatéral/non-reg
if (is.null(k) || !is.numeric(k) || k <= 0 || k > 50) { /* ... gestion erreur ... */ }
if (is.null(alpha) || !is.numeric(alpha) || alpha <= 0 || alpha >= 1) { /* ... gestion erreur ... */ }
if (is.null(beta) || !is.numeric(beta) || beta <= 0 || beta >= 1) { /* ... gestion erreur ... */ }
if (!(test_type %in% c(1, 3))) { # Accepter seulement 1 (Sup) ou 3 (Non-reg) pour l'instant
    error_response$message <- "Type de test invalide (1='Supériorité', 3='Non-régression')."
    cat(toJSON(error_response, auto_unbox = TRUE, na = "null")); quit(status = 1)
}
k <- as.integer(k)

# --- Obtenir fonction/paramètre pour SFU (Efficacité) ---
get_spending_info_sfu <- function(name) {
  safe_name <- tolower(name %||% "kimdemets")
  param_val <- NULL; func <- gsDesign::sfLDOF; standard_name <- "OF"
  if (safe_name == "pocock") { func <- gsDesign::sfPocock; standard_name <- "Pocock" }
  else if (safe_name == "kimdemets") { func <- gsDesign::sfPower; param_val <- 3; standard_name <- "KimDeMets"}
  else { standard_name <- "OF" } # Défaut OF si inconnu
  return(list(func = func, param = param_val, name = standard_name))
}
sfu_info <- get_spending_info_sfu(sfu_name_req)

# --- Définir fonction/paramètre pour SFL (Futilité) - TOUJOURS sfHSD pour type 1 et 3 ---
# Utilisation de sfHSD avec gamma = -2 (valeur courante, produit des bornes croissantes)
sfl_info <- list(func = gsDesign::sfHSD, param = -2, name = "HSD(-2)")

# Timing
timing <- (1:k) / k

# --- Appel à gsDesign (utilise sfl_info forcé) ---
message(paste("Appel gsDesign: k=", k, "alpha=", alpha, "beta=", beta, "test.type=", test_type))
message(paste("Using sfu:", sfu_info$name, "with param:", sfu_info$param %||% "NULL"))
message(paste("Using sfl:", sfl_info$name, "with param:", sfl_info$param %||% "NULL")) # Affichera HSD(-2)

design <- tryCatch({
  gsDesign(k = k, test.type = test_type, alpha = alpha, beta = beta, timing = timing,
           sfu = sfu_info$func, sfupar = sfu_info$param,
           sfl = sfl_info$func, sflpar = sfl_info$param) # Utilise sfHSD et param -2 pour sfl
}, error = function(e) { /* ... gestion erreur ... */ NULL })

if (is.null(design)) { /* ... gestion erreur ... */ }

# --- Préparer la sortie JSON (inchangé - utilise get_numeric_or_na) ---
results <- list( error = FALSE, message = "Calcul des bornes réussi.", parameters = list( k = k, alpha = alpha, beta = beta, testType = test_type, timing = timing, sfu = sfu_info$name, sfl = sfl_info$name ), boundaries = list() )
get_numeric_or_na <- function(value) { if (!is.null(value) && is.numeric(value) && length(value) == 1 && is.finite(value)) { return(value) } else { return(NA) } }
for (i in seq_len(k)) {
    upper_bound <- if (!is.null(design$upper)) get_numeric_or_na(design$upper$bound[i]) else NA
    lower_bound <- if (!is.null(design$lower)) get_numeric_or_na(design$lower$bound[i]) else NA # Devrait maintenant être numérique
    upper_spend <- if (!is.null(design$upper)) get_numeric_or_na(design$upper$spend[i]) else NA
    lower_spend <- if (!is.null(design$lower)) get_numeric_or_na(design$lower$spend[i]) else NA # Devrait maintenant être numérique
    results$boundaries[[i]] <- list( stage = i, infoFraction = get_numeric_or_na(design$n.I[i]), efficacyZ = upper_bound, futilityZ = lower_bound, alphaSpentCumulative = upper_spend, betaSpentCumulative = lower_spend )
}

# --- Imprimer le JSON sur stdout (inchangé) ---
cat(toJSON(results, pretty = FALSE, na = "null"))
quit(status = 0)

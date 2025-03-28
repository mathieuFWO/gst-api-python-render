#!/usr/bin/env Rscript
# Script pour calculer les bornes GST avec gsDesign (Version 8 - sfHSD gamma=-2)

# Charger les librairies nécessaires
tryCatch({
    suppressPackageStartupMessages(library(gsDesign))
    suppressPackageStartupMessages(library(jsonlite, warn.conflicts = FALSE))
}, error = function(e) {
    error_response <- list(error = TRUE, message = paste("Erreur chargement package R:", e$message))
    writeLines(sprintf('{"error": true, "message": "Erreur chargement package R: %s"}', gsub('"', '\\\\"', e$message)), con = stdout())
    quit(status = 1)
})

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
params <- tryCatch({ fromJSON(input_json) }, error = function(e) { error_response$message <- paste("Erreur parsing JSON:", e$message); cat(toJSON(error_response, auto_unbox = TRUE, na = "null")); quit(status = 1) })

# --- Validation et Paramètres par défaut ---
`%||%` <- function(a, b) { if (is.null(a)) b else a }
k <- params$k; alpha <- params$alpha %||% 0.05; beta <- params$beta %||% 0.20; test_type <- params$testType %||% 1; sfu_name_req <- params$sfu %||% "KimDeMets";
if (is.null(k) || !is.numeric(k) || k <= 0 || k > 50) { error_response$message <- "K (1-50) invalide."; cat(toJSON(error_response, auto_unbox = TRUE, na = "null")); quit(status = 1) }
if (is.null(alpha) || !is.numeric(alpha) || alpha <= 0 || alpha >= 1) { error_response$message <- "Alpha invalide."; cat(toJSON(error_response, auto_unbox = TRUE, na = "null")); quit(status = 1) }
if (is.null(beta) || !is.numeric(beta) || beta <= 0 || beta >= 1) { error_response$message <- "Beta invalide."; cat(toJSON(error_response, auto_unbox = TRUE, na = "null")); quit(status = 1) }
if (!(test_type %in% c(1, 3))) { error_response$message <- "Type test invalide (1 ou 3)."; cat(toJSON(error_response, auto_unbox = TRUE, na = "null")); quit(status = 1) }
k <- as.integer(k)

# --- Obtenir fonction/paramètre pour SFU (Efficacité) ---
get_spending_info_sfu <- function(name) { safe_name <- tolower(name %||% "kimdemets"); param_val <- NULL; func <- gsDesign::sfLDOF; standard_name <- "OF"; if (safe_name == "pocock") { func <- gsDesign::sfPocock; standard_name <- "Pocock" } else if (safe_name == "kimdemets") { func <- gsDesign::sfPower; param_val <- 3; standard_name <- "KimDeMets"} else { standard_name <- "OF" }; return(list(func = func, param = param_val, name = standard_name)) }
sfu_info <- get_spending_info_sfu(sfu_name_req)

# --- Définir fonction/paramètre pour SFL (Futilité/Inf) ---
# *** MODIFICATION : Revenir à gamma = -2 ***
sfl_gamma <- -2
sfl_info <- list(func = gsDesign::sfHSD, param = sfl_gamma, name = paste0("HSD(", sfl_gamma, ")"))

# Timing
timing <- (1:k) / k

# --- Appel à gsDesign ---
message(paste("Appel gsDesign: k=", k, ", alpha=", alpha, ", beta=", beta, ", test.type=", test_type))
message(paste("Using sfu:", sfu_info$name, "with param:", sfu_info$param %||% "NULL"))
message(paste("Using sfl:", sfl_info$name, "with param:", sfl_info$param %||% "NULL")) # Affichera HSD(-2)

design <- tryCatch({
  gsDesign(k = k, test.type = test_type, alpha = alpha, beta = beta, timing = timing,
           sfu = sfu_info$func, sfupar = sfu_info$param,
           sfl = sfl_info$func, sflpar = sfl_info$param)
}, error = function(e) { error_response$message <<- paste("Erreur gsDesign:", e$message); error_response$details <<- capture.output(traceback()); NULL })

if (is.null(design)) { cat(toJSON(error_response, auto_unbox = TRUE, na = "null")); quit(status = 1) }

# --- Préparer la sortie JSON ---
results <- list( error = FALSE, message = "Calcul des bornes réussi.", parameters = list( k = k, alpha = alpha, beta = beta, testType = test_type, timing = timing, sfu = sfu_info$name, sfl = sfl_info$name ), boundaries = list() )
get_numeric_or_na <- function(value) { if (!is.null(value) && is.numeric(value) && length(value) == 1 && is.finite(value)) { return(value) } else { return(NA) } }
for (i in seq_len(k)) { upper_bound <- if (!is.null(design$upper)) get_numeric_or_na(design$upper$bound[i]) else NA; lower_bound <- if (!is.null(design$lower)) get_numeric_or_na(design$lower$bound[i]) else NA; upper_spend <- if (!is.null(design$upper)) get_numeric_or_na(design$upper$spend[i]) else NA; lower_spend <- if (!is.null(design$lower)) get_numeric_or_na(design$lower$spend[i]) else NA; results$boundaries[[i]] <- list( stage = i, infoFraction = get_numeric_or_na(design$n.I[i]), efficacyZ = upper_bound, futilityZ = lower_bound, alphaSpentCumulative = upper_spend, betaSpentCumulative = lower_spend ) }

# --- Imprimer le JSON sur stdout ---
cat(toJSON(results, pretty = FALSE, na = "null"))
quit(status = 0)

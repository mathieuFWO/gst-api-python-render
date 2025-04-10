#!/usr/bin/env Rscript
# Script pour calculer les bornes GST avec gsDesign ET le Z-score observé
# ET les bornes ajustées pour le guardrail (v37.15 - Fix Syntax Error)

# --- Configuration initiale ---
options(scipen = 999)

# --- Chargement des librairies ---
load_packages <- function() { suppressPackageStartupMessages({ if (!requireNamespace("gsDesign", quietly = TRUE)) install.packages("gsDesign", repos = "https://cloud.r-project.org/") ; if (!requireNamespace("jsonlite", quietly = TRUE)) install.packages("jsonlite", repos = "https://cloud.r-project.org/") ; library(gsDesign) ; library(jsonlite, warn.conflicts = FALSE) }) }
tryCatch({ load_packages() }, error = function(e) { error_msg <- gsub('"', '\\\\"', paste("Erreur chargement/installation package R:", e$message)); error_json <- sprintf('{"error": true, "message": "%s"}', error_msg); writeLines(error_json, con = stdout()); quit(save = "no", status = 1, runLast = FALSE) })

# --- Fonctions utilitaires ---
exit_with_error <- function(message, details = NULL) { response <- list(error = TRUE, message = message); if (!is.null(details)) response$details <- details; cat(toJSON(response, auto_unbox = TRUE, na = "null")); quit(save = "no", status = 1, runLast = FALSE) }
get_numeric_or_na <- function(value) { if (is.null(value) || length(value) != 1) return(NA_real_); num_val <- suppressWarnings(as.numeric(value)); if (is.na(num_val) || !is.finite(num_val)) return(NA_real_); return(num_val) }

# --- Récupération et Validation des Arguments ---
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) exit_with_error("Usage: Rscript script.R '<json_input>'")
input_json <- args[1]
params <- tryCatch({ fromJSON(input_json, simplifyVector = TRUE) }, error = function(e) { exit_with_error(paste("Erreur parsing JSON:", e$message)) })

# --- Validation des Paramètres Principaux ---
`%||%` <- function(a, b) { if (is.null(a) || length(a) == 0 || is.na(a)) b else a }
k <- params$k; if (is.null(k) || !is.numeric(k) || k <= 0 || k != floor(k) || k > 50) exit_with_error("K (1-50) invalide.") ; k <- as.integer(k)
alpha <- get_numeric_or_na(params$alpha %||% 0.05); if (is.na(alpha) || alpha <= 0 || alpha >= 1) exit_with_error("Alpha invalide.")
beta <- get_numeric_or_na(params$beta %||% 0.20); if (is.na(beta) || beta < 0 || beta >= 1) exit_with_error("Beta invalide.") ; power <- 1 - beta
test_type <- as.integer(params$testType %||% 1); if (!(test_type %in% c(1, 2, 3, 4, 5, 6))) exit_with_error("TestType invalide (1-6).")
sfu_name_req <- tolower(params$sfu %||% "kimdemets"); sfl_name_req <- tolower(params$sfl %||% "hsd"); sfl_param_req <- params$sflpar %||% -2

# --- Configuration SFU/SFL Principal ---
sfu_param_val <- NULL; sfu_func <- NULL; sfu_standard_name <- NULL; if (sfu_name_req == "pocock") { sfu_func <- gsDesign::sfPocock; sfu_standard_name <- "Pocock" } else if (sfu_name_req == "of" || sfu_name_req == "obrienfleming") { sfu_func <- gsDesign::sfLDOF; sfu_standard_name <- "OF" } else if (sfu_name_req == "kimdemets") { sfu_func <- gsDesign::sfPower; sfu_param_val <- 3; sfu_standard_name <- "KimDeMets"} else if (sfu_name_req == "hsd") { sfu_func <- gsDesign::sfHSD; sfu_param_val <- params$sfupar %||% 1; if(!is.numeric(sfu_param_val)) exit_with_error("Param sfupar invalide."); sfu_standard_name <- paste0("HSD(", sfu_param_val, ")") } else { warning(paste("SFU '", sfu_name_req, "' non reconnue -> OF")); sfu_func <- gsDesign::sfLDOF; sfu_standard_name <- "OF"; sfu_name_req <- "of" }
sfl_func <- NULL; sfl_param_val <- NULL; sfl_standard_name <- NULL; if (test_type %in% c(3, 4, 5, 6)) { if (sfl_name_req == "hsd") { sfl_func <- gsDesign::sfHSD; sfl_param_val <- sfl_param_req; if(!is.numeric(sfl_param_val)) exit_with_error("Param sflpar invalide."); sfl_standard_name <- paste0("HSD(", sfl_param_val, ")") } else if (sfl_name_req == "identity") { sfl_func <- gsDesign::sfLinear; sfl_param_val <- 1; sfl_standard_name <- "Linear" } else if (sfl_name_req == "pocock") { sfl_func <- gsDesign::sfPocock; sfl_standard_name <- "Pocock" } else if (sfl_name_req == "of" || sfl_name_req == "obrienfleming") { sfl_func <- gsDesign::sfLDOF; sfl_standard_name <- "OF" } else if (sfl_name_req == "kimdemets") { sfl_func <- gsDesign::sfPower; sfl_param_val <- params$sflpar %||% 3; if(!is.numeric(sfl_param_val)) exit_with_error("Param sflpar KimDeMets invalide."); sfl_standard_name <- paste0("KimDeMets(", sfl_param_val, ")") } else { warning(paste("SFL '", sfl_name_req, "' non reconnue -> HSD(-2)")); sfl_func <- gsDesign::sfHSD; sfl_param_val <- -2; sfl_standard_name <- "HSD(-2)"; sfl_name_req <- "hsd" } } else { sfl_standard_name <- "None (test.type 1/2)" }
timing <- (1:k) / k

# --- Calcul Bornes Principales ---
message(paste("Appel gsDesign Principal: k=", k, ", test.type=", test_type, ", alpha=", alpha, ", beta=", beta))
message(paste("Using sfu:", sfu_standard_name, " (param:", if(is.null(sfu_param_val)) "NULL" else sfu_param_val, ")"))
if (!is.null(sfl_func)) message(paste("Using sfl:", sfl_standard_name, " (param:", if(is.null(sfl_param_val)) "NULL" else sfl_param_val, ")"))
design_primary <- NULL; design_error <- NULL;
design_primary <- tryCatch({ gsDesign(k=k, test.type=test_type, alpha=alpha, beta=beta, timing=timing, sfu=sfu_func, sfupar=sfu_param_val, sfl=sfl_func, sflpar=sfl_param_val) }, error = function(e) { design_error <<- e$message; NULL })
if (is.null(design_primary)) exit_with_error(paste("Erreur gsDesign Principal:", design_error), details = capture.output(traceback()))

# --- Calcul Bornes Guardrail Ajustées ---
alpha_guardrail <- 0.05
sfl_guardrail_func <- gsDesign::sfLDOF
sfl_guardrail_name <- "OF (Guardrail)"
message(paste("Calcul Bornes Guardrail: k=", k, ", alpha_guardrail=", alpha_guardrail, " (mappé à beta)"))
message(paste("Using sfl (Guardrail):", sfl_guardrail_name))
design_guardrail <- NULL; guardrail_error <- NULL;
design_guardrail <- tryCatch({ gsDesign(k=k, test.type=4, alpha=0.00001, beta=alpha_guardrail, timing=timing, sfu=NULL, sfupar=NULL, sfl=sfl_guardrail_func, sflpar=NULL) }, error = function(e) { guardrail_error <<- e$message; NULL }) # Added sfupar/sflpar=NULL explicitly
guardrail_boundaries_z <- NA
if (is.null(design_guardrail)) { warning(paste("Erreur calcul bornes guardrail:", guardrail_error)); guardrail_boundaries_z <- rep(NA_real_, k) }
else { if (!is.null(design_guardrail$lower) && length(design_guardrail$lower$bound) == k) { guardrail_boundaries_z <- design_guardrail$lower$bound; message("Bornes Guardrail calculées.") } else { warning("Structure inattendue retournée par gsDesign pour bornes guardrail."); guardrail_boundaries_z <- rep(NA_real_, k) } }

# --- Calcul Z-score Observé Principal ---
observed_z <- NA_real_ ; observed_z_message <- "Données A/B primaires non fournies ou invalides."
required_data_keys <- c("visitors_a", "conversions_a", "visitors_b", "conversions_b")
if (all(required_data_keys %in% names(params))) {
    visitors_a <- get_numeric_or_na(params$visitors_a); conversions_a <- get_numeric_or_na(params$conversions_a); visitors_b <- get_numeric_or_na(params$visitors_b); conversions_b <- get_numeric_or_na(params$conversions_b)
    if (anyNA(c(visitors_a, conversions_a, visitors_b, conversions_b))) { observed_z_message <- "Données A/B primaires non numériques ou manquantes." }
    else if (visitors_a <= 0 || visitors_b <= 0) { observed_z_message <- "Visiteurs primaires (A et B) doivent être > 0." }
    else if (conversions_a < 0 || conversions_b < 0 || conversions_a > visitors_a || conversions_b > visitors_b) { observed_z_message <- "Conversions primaires invalides (>= 0 et <= visiteurs)." }
    else {
        tryCatch({ p1 <- conversions_a / visitors_a; p2 <- conversions_b / visitors_b; n1 <- visitors_a; n2 <- visitors_b; p_pooled <- (conversions_a + conversions_b) / (n1 + n2);
            if (p_pooled <= 0 || p_pooled >= 1) { if (abs(p1 - p2) < .Machine$double.eps) { observed_z <- 0.0; observed_z_message <- "Z primaire calculé (p_pooled 0 ou 1, p1=p2)." } else { observed_z <- NA_real_; observed_z_message <- "Z primaire non calculé (p_pooled 0 ou 1, variance nulle)." } }
            else { se_pooled <- sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2)); if (se_pooled < .Machine$double.eps * 100) { observed_z <- NA_real_; observed_z_message <- "Z primaire non calculé (SE pooled quasi-nulle)." } else { observed_z <- (p2 - p1) / se_pooled; observed_z_message <- paste("Z primaire calculé:", round(observed_z, 5)) } }
        }, error = function(e) { observed_z <<- NA_real_; observed_z_message <<- paste("Erreur calcul Z primaire:", e$message) })
    }
} else { # Else for 'if (all required_data_keys...)'
     observed_z_message <- "Données A/B primaires non fournies ou invalides."
} # *** Corrected: Removed the extra dangling 'else' block that was here ***

message(observed_z_message)

# --- Préparation Sortie JSON ---
results <- list( error = FALSE, message = "Calcul terminé.", observedZ = ifelse(is.na(observed_z), NA, round(observed_z, 5)), observedZMessage = observed_z_message, parameters = list( k = k, alpha = alpha, beta = beta, power = power, testType = test_type, timing = timing, sfu = sfu_standard_name, sfuParam = sfu_param_val, sfl = sfl_standard_name, sflParam = sfl_param_val, alphaGuardrail = alpha_guardrail, sflGuardrail = sfl_guardrail_name ), boundaries = list(), guardrailBoundariesZ = if(all(is.na(guardrail_boundaries_z))) NA else round(guardrail_boundaries_z, 3) )
for (i in seq_len(k)) { info_frac <- get_numeric_or_na(design_primary$n.I[[i]]); eff_z <- NA_real_; alpha_cum <- NA_real_; fut_z <- NA_real_; beta_cum <- NA_real_; if (!is.null(design_primary$upper) && length(design_primary$upper$bound) >= i) eff_z <- get_numeric_or_na(design_primary$upper$bound[[i]]); if (!is.null(design_primary$upper) && length(design_primary$upper$spend) >= i) alpha_cum <- get_numeric_or_na(design_primary$upper$spend[[i]]); if (!is.null(design_primary$lower) && length(design_primary$lower$bound) >= i) fut_z <- get_numeric_or_na(design_primary$lower$bound[[i]]); if (!is.null(design_primary$lower) && length(design_primary$lower$spend) >= i) beta_cum <- get_numeric_or_na(design_primary$lower$spend[[i]]); results$boundaries[[i]] <- list( stage = i, infoFraction = info_frac, efficacyZ = eff_z, futilityZ = fut_z, alphaSpentCumulative = alpha_cum, betaSpentCumulative = beta_cum ) }

# --- Imprimer JSON et Quitter ---
cat(toJSON(results, pretty = FALSE, auto_unbox = TRUE, na = "null"))
quit(save = "no", status = 0, runLast = FALSE)

# --- END OF FILE calculate_gs_design.R ---

#!/usr/bin/env Rscript
# Script pour calculer les bornes GST (Primaire) et Guardrail (Secondaire)
# ET les Z-scores observés pour les deux métriques.
# (v37.14 - Sequential Guardrail)

# --- Configuration initiale ---
options(scipen = 999)

# --- Chargement des librairies ---
load_packages <- function() {
    suppressPackageStartupMessages({
        if (!requireNamespace("gsDesign", quietly = TRUE)) install.packages("gsDesign", repos = "https://cloud.r-project.org/")
        if (!requireNamespace("jsonlite", quietly = TRUE)) install.packages("jsonlite", repos = "https://cloud.r-project.org/")
        library(gsDesign)
        library(jsonlite, warn.conflicts = FALSE)
    })
}
tryCatch({ load_packages() }, error = function(e) { error_msg <- gsub('"', '\\\\"', paste("Erreur chargement package R:", e$message)); error_json <- sprintf('{"error": true, "message": "%s"}', error_msg); writeLines(error_json, con = stdout()); quit(save = "no", status = 1, runLast = FALSE); })

# --- Fonctions utilitaires ---
exit_with_error <- function(message, details = NULL) { response <- list(error = TRUE, message = message); if (!is.null(details)) { response$details <- details; }; cat(toJSON(response, auto_unbox = TRUE, na = "null")); quit(save = "no", status = 1, runLast = FALSE); }
get_numeric_or_na <- function(value) { if (is.null(value) || length(value) != 1) return(NA_real_); num_val <- suppressWarnings(as.numeric(value)); if (is.na(num_val) || !is.finite(num_val)) return(NA_real_); return(num_val); }
`%||%` <- function(a, b) { if (is.null(a) || length(a) == 0 || is.na(a)) b else a }

# --- Calculateur de Z-score (Fonction Réutilisable) ---
calculate_z_score <- function(vA, cA, vB, cB) {
    result <- list(z = NA_real_, message = "Données insuffisantes ou invalides pour Z.")
    visitors_a <- get_numeric_or_na(vA); conversions_a <- get_numeric_or_na(cA)
    visitors_b <- get_numeric_or_na(vB); conversions_b <- get_numeric_or_na(cB)

    if (anyNA(c(visitors_a, conversions_a, visitors_b, conversions_b))) {
        result$message <- "Données contiennent des NA."
        return(result)
    }
    if (visitors_a <= 0 || visitors_b <= 0) {
         result$message <- "Visiteurs <= 0."
         return(result)
     }
     if (conversions_a < 0 || conversions_b < 0 || conversions_a > visitors_a || conversions_b > visitors_b) {
         result$message <- "Conversions invalides."
         return(result)
     }

    tryCatch({
        p1 <- conversions_a / visitors_a; p2 <- conversions_b / visitors_b
        n1 <- visitors_a; n2 <- visitors_b
        p_pooled <- (conversions_a + conversions_b) / (n1 + n2)
        if (p_pooled <= 0 || p_pooled >= 1) {
            if (abs(p1 - p2) < .Machine$double.eps) { result$z <- 0.0; result$message <- "Z=0 (p_pooled 0 ou 1, p1=p2)."; }
            else { result$z <- NA_real_; result$message <- "Z=NA (p_pooled 0 ou 1, p1!=p2)."; }
        } else {
            se_pooled <- sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))
            if (se_pooled < .Machine$double.eps * 100) { result$z <- NA_real_; result$message <- "Z=NA (SE pooled quasi-nul)."; }
            else { result$z <- (p2 - p1) / se_pooled; result$message <- paste("Z calculé succès:", round(result$z, 5)); }
        }
    }, error = function(e) { result$z <<- NA_real_; result$message <<- paste("Erreur calcul Z:", e$message); })
    return(result)
}

# --- Fonction pour obtenir la fonction de dépense R ---
get_spending_function <- function(name_req, default_func = gsDesign::sfLDOF) {
    safe_name <- tolower(name_req %||% "")
    func_info <- list(func = default_func, param = NULL, name = "Default") # Default to OF-like if not found

    if (safe_name == "pocock") { func_info <- list(func = gsDesign::sfPocock, param = NULL, name = "Pocock") }
    else if (safe_name == "of" || safe_name == "obrienfleming") { func_info <- list(func = gsDesign::sfLDOF, param = NULL, name = "OF") }
    else if (safe_name == "kimdemets") { func_info <- list(func = gsDesign::sfPower, param = 3, name = "KimDeMets") } # Default rho=3
    else if (safe_name == "hsd") { func_info <- list(func = gsDesign::sfHSD, param = NULL, name = "HSD") } # Param needed separately
    # Add other functions here if needed

    return(func_info)
}


# --- Récupération et Validation des Arguments ---
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) { exit_with_error("Usage: Rscript calculate_gs_design.R '<json_input>'") }
input_json <- args[1]
params <- tryCatch({ fromJSON(input_json, simplifyVector = TRUE) }, error = function(e) { exit_with_error(paste("Erreur parsing JSON:", e$message)) })

# --- Validation Paramètres Design Primaire ---
k <- params$k; if (is.null(k) || !is.numeric(k) || k <= 0 || k != floor(k) || k > 50) { exit_with_error("K (1-50) invalide."); }
k <- as.integer(k)
alpha <- get_numeric_or_na(params$alpha %||% 0.05); if (is.na(alpha) || alpha <= 0 || alpha >= 1) { exit_with_error("Alpha invalide."); }
beta <- get_numeric_or_na(params$beta %||% 0.20); if (is.na(beta) || beta < 0 || beta >= 1) { exit_with_error("Beta invalide."); }
power <- 1 - beta
test_type <- as.integer(params$testType %||% 1); if (!(test_type %in% c(1, 2, 3, 4, 5, 6))) { exit_with_error("TestType invalide."); }
sfu_req <- params$sfu %||% "KimDeMets"; sfl_req <- params$sfl %||% "HSD" # Note: sfl from primary design might be used differently now

# --- Validation Paramètres Design Guardrail (Nouveaux) ---
# Alpha pour le guardrail (probabilité acceptable de fausse alerte de dégradation)
alpha_guardrail <- get_numeric_or_na(params$alpha_guardrail %||% 0.05) # Default 5%
if (is.na(alpha_guardrail) || alpha_guardrail <= 0 || alpha_guardrail >= 1) { exit_with_error("alpha_guardrail invalide."); }
# Fonction de dépense pour le guardrail
sfg_req <- params$sfg %||% "OF" # Default to OF-like for guardrail, often conservative early
sfg_info <- get_spending_function(sfg_req, default_func = gsDesign::sfLDOF)
# Paramètre spécifique pour la fonction de dépense du guardrail (si nécessaire, ex: HSD)
sfg_param_val <- NULL
if (sfg_info$name == "HSD") {
    sfg_param_val <- get_numeric_or_na(params$sfgpar %||% -2) # Default gamma=-2 for HSD guardrail
    if(is.na(sfg_param_val)) exit_with_error("Paramètre 'sfgpar' invalide pour HSD guardrail.")
    sfg_info$param <- sfg_param_val
    sfg_info$name <- paste0("HSD(", sfg_param_val, ")")
} else if (sfg_info$name == "KimDeMets") {
     sfg_param_val <- get_numeric_or_na(params$sfgpar %||% 3) # Default rho=3
     if(is.na(sfg_param_val)) exit_with_error("Paramètre 'sfgpar' invalide pour KimDeMets guardrail.")
     sfg_info$param <- sfg_param_val
     sfg_info$name <- paste0("KimDeMets(", sfg_param_val, ")")
}
message(paste("Guardrail params: alpha_guardrail=", alpha_guardrail, ", sfg=", sfg_info$name, "(param:", sfg_info$param %||% "NULL", ")"))


# --- Obtenir Fonctions de Dépense Primaires ---
sfu_info <- get_spending_function(sfu_req, default_func = gsDesign::sfLDOF)
sfl_info <- get_spending_function(sfl_req, default_func = gsDesign::sfHSD) # Default SFL HSD
# Gérer les paramètres spécifiques pour SFU/SFL primaires si HSD/KimDeMets
if(sfu_info$name == "HSD") { sfu_param_val <- get_numeric_or_na(params$sfupar %||% 1); if(is.na(sfu_param_val)) exit_with_error("sfupar invalide pour HSD"); sfu_info$param <- sfu_param_val; sfu_info$name <- paste0("HSD(", sfu_param_val, ")"); }
if(sfu_info$name == "KimDeMets") { sfu_param_val <- get_numeric_or_na(params$sfupar %||% 3); if(is.na(sfu_param_val)) exit_with_error("sfupar invalide pour KimDeMets"); sfu_info$param <- sfu_param_val; sfu_info$name <- paste0("KimDeMets(", sfu_param_val, ")"); }
if(sfl_info$name == "HSD") { sfl_param_val <- get_numeric_or_na(params$sflpar %||% -2); if(is.na(sfl_param_val)) exit_with_error("sflpar invalide pour HSD"); sfl_info$param <- sfl_param_val; sfl_info$name <- paste0("HSD(", sfl_param_val, ")"); }
if(sfl_info$name == "KimDeMets") { sfl_param_val <- get_numeric_or_na(params$sflpar %||% 3); if(is.na(sfl_param_val)) exit_with_error("sflpar invalide pour KimDeMets"); sfl_info$param <- sfl_param_val; sfl_info$name <- paste0("KimDeMets(", sfl_param_val, ")"); }

# --- Calcul des Bornes Séquentielles Primaires ---
timing <- (1:k) / k
message(paste("Appel gsDesign (Primaire): k=", k, ", test.type=", test_type, ", alpha=", alpha, ", beta=", beta))
message(paste("Using sfu (Primaire):", sfu_info$name, "(param:", sfu_info$param %||% "NULL", ")"))
if (test_type %in% c(3, 4, 5, 6)) { message(paste("Using sfl (Primaire):", sfl_info$name, "(param:", sfl_info$param %||% "NULL", ")")) } else { sfl_info$func <- NULL; } # Ignore SFL if test type doesn't use it

design_primary <- NULL; design_error <- NULL
design_primary <- tryCatch({
    gsDesign(k = k, test.type = test_type, alpha = alpha, beta = beta, timing = timing,
             sfu = sfu_info$func, sfupar = sfu_info$param,
             sfl = sfl_info$func, sflpar = sfl_info$param)
}, error = function(e) { design_error <<- e$message; NULL })
if (is.null(design_primary)) { exit_with_error(paste("Erreur gsDesign (Primaire):", design_error), details = capture.output(traceback())) }

# --- Calcul des Bornes Inférieures Séquentielles pour le Guardrail ---
message("Calcul des bornes Guardrail...")
guardrail_bounds_z <- rep(NA_real_, k)
tryCatch({
    # Get cumulative alpha spent for guardrail at each stage
    guardrail_alpha_spent_cumulative <- sfg_info$func(t = timing, alpha = alpha_guardrail, param = sfg_info$param)
    message(paste("Guardrail alpha cumulé dépensé:", paste(round(guardrail_alpha_spent_cumulative, 4), collapse=", ")))
    # Convert cumulative alpha spent to one-sided Z-scores (lower bound)
    guardrail_bounds_z <- qnorm(guardrail_alpha_spent_cumulative)
    message(paste("Guardrail bornes Z:", paste(round(guardrail_bounds_z, 4), collapse=", ")))
}, error = function(e) {
     warning(paste("Erreur calcul bornes guardrail:", e$message))
     # guardrail_bounds_z reste un vecteur de NA
})

# --- Calcul des Z-scores Observés ---
# Primaire
z_primary_result <- calculate_z_score(params$visitors_a, params$conversions_a, params$visitors_b, params$conversions_b)
message(paste("Z Primaire:", z_primary_result$message))
# Secondaire (si données fournies)
z_secondary_result <- list(z = NA_real_, message = "Données secondaires non fournies.")
required_sec_keys <- c("visitors_a_secondary", "conversions_a_secondary", "visitors_b_secondary", "conversions_b_secondary")
# **Important**: Secondary Z calculation now uses potentially different visitor counts if provided
# If secondary visitor counts are *not* provided, fall back to primary visitor counts for rate calculation.
visitors_a_sec <- params$visitors_a_secondary %||% params$visitors_a
visitors_b_sec <- params$visitors_b_secondary %||% params$visitors_b
conversions_a_sec <- params$conversions_a_secondary
conversions_b_sec <- params$conversions_b_secondary

if (!is.null(conversions_a_sec) && !is.null(conversions_b_sec)) { # Check if secondary conversions were provided
     z_secondary_result <- calculate_z_score(visitors_a_sec, conversions_a_sec, visitors_b_sec, conversions_b_sec)
     message(paste("Z Secondaire:", z_secondary_result$message))
} else {
     message("Z Secondaire: Non calculé (conversions secondaires manquantes).")
}


# --- Préparation de la Sortie JSON ---
results <- list(
    error = FALSE,
    message = "Calcul terminé.",
    observedZ_primary = if (!is.na(z_primary_result$z)) round(z_primary_result$z, 5) else NULL,
    observedZ_primary_message = z_primary_result$message,
    observedZ_secondary = if (!is.na(z_secondary_result$z)) round(z_secondary_result$z, 5) else NULL,
    observedZ_secondary_message = z_secondary_result$message,
    parameters = list(
        k = k, alpha = alpha, beta = beta, power = power, testType = test_type, timing = timing,
        sfu = sfu_info$name, sfuParam = sfu_info$param,
        sfl = sfl_info$name %||% "None", sflParam = sfl_info$param, # Use the potentially updated SFL info
        alpha_guardrail = alpha_guardrail, sfg = sfg_info$name, sfgParam = sfg_info$param
    ),
    boundaries_primary = list(), # Renamed for clarity
    guardrailBounds = lapply(guardrail_bounds_z, function(z) if(is.na(z)) NULL else round(z, 5)) # Return guardrail bounds as a simple array or list of numbers/nulls
)

# Remplir les bornes primaires
for (i in seq_len(k)) {
    eff_z <- NA_real_; fut_z <- NA_real_; info_frac <- NA_real_; alpha_cum <- NA_real_; beta_cum <- NA_real_;
    info_frac <- get_numeric_or_na(design_primary$n.I[[i]])
    if (!is.null(design_primary$upper) && length(design_primary$upper$bound) >= i) { eff_z <- get_numeric_or_na(design_primary$upper$bound[[i]]); }
    if (!is.null(design_primary$upper) && length(design_primary$upper$spend) >= i) { alpha_cum <- get_numeric_or_na(design_primary$upper$spend[[i]]); }
    if (!is.null(design_primary$lower) && length(design_primary$lower$bound) >= i) { fut_z <- get_numeric_or_na(design_primary$lower$bound[[i]]); }
    if (!is.null(design_primary$lower) && length(design_primary$lower$spend) >= i) { beta_cum <- get_numeric_or_na(design_primary$lower$spend[[i]]); }
    results$boundaries_primary[[i]] <- list( stage = i, infoFraction = info_frac, efficacyZ = eff_z, futilityZ = fut_z, alphaSpentCumulative = alpha_cum, betaSpentCumulative = beta_cum )
}

# --- Imprimer le JSON sur stdout et Quitter Proprement ---
cat(toJSON(results, pretty = FALSE, auto_unbox = TRUE, na = "null"))
quit(save = "no", status = 0, runLast = FALSE)

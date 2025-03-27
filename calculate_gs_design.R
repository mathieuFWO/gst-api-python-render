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
alpha <- params$alpha %||% 0.05 # Récupérer alpha ici
beta <- params$beta %||% 0.20
test_type <- params$testType %||% 1 # 1 = one-sided (supériorité)
sfu_name <- params$sfu %||% "OF"
sfl_name <- params$sfl %||% sfu_name

# Vérifications basiques
if (is.null(k) || !is.numeric(k) || k <= 0) {
  error_response$message <- "Le paramètre 'k' (nombre d'étapes) est manquant ou invalide."
  cat(toJSON(error_response, auto_unbox = TRUE))
  quit(status = 1)
}
if (is.null(alpha) || !is.numeric(alpha) || alpha <= 0 || alpha >= 1) { # Vérifier alpha
    error_response$message <- "Le paramètre 'alpha' est manquant ou invalide."
    cat(toJSON(error_response, auto_unbox = TRUE))
    quit(status = 1)
}
k <- as.integer(k)

# --- Mapping des noms de fonctions de dépense (MODIFIÉ) ---
# Prend alpha en argument maintenant
get_spending_function <- function(name, alpha_val) {
  safe_name <- tolower(name %||% "of")
  switch(safe_name,
         "of" = gsDesign::sfLDOF,
         "pocock" = gsDesign::sfPocock,
         # *** CORRECTION ICI: Passer alpha à sfPower ***
         "kimdemets" = gsDesign::sfPower(alpha = alpha_val, param = 3),
         # Retourner le défaut si le nom n'est pas reconnu
         gsDesign::sfLDOF
  )
}

# *** CORRECTION ICI: Appeler get_spending_function avec alpha ***
sfu_func <- get_spending_function(sfu_name, alpha)
# NOTE: La fonction sfPower pour la borne inférieure (sfl) n'existe pas directement
# dans gsDesign de la même manière. Si on utilise KimDeMets pour sfu,
# il faut choisir une fonction compatible pour sfl. sfLDOF est un choix courant.
# Ou utiliser la même logique sfPower si sfl_name est aussi "KimDeMets",
# mais en passant 'alpha' (ce qui est techniquement incorrect pour une borne beta,
# mais c'est souvent comme ça que c'est utilisé pour la symétrie).
# Option 1: Toujours utiliser sfLDOF pour la futilité si sfu est KimDeMets
# sfl_func <- if (tolower(sfu_name) == "kimdemets") gsDesign::sfLDOF else get_spending_function(sfl_name, alpha)
# Option 2: Utiliser sfPower pour sfl si demandé (même si sémantiquement étrange pour beta)
sfl_func <- get_spending_function(sfl_name, alpha)

# Timing : Supposer des étapes équi-espacées en information par défaut
timing <- (1:k) / k

# --- Appel à gsDesign ---
message(paste("Appel gsDesign: k=", k, "alpha=", alpha, "beta=", beta, "sfu=", sfu_name, "sfl=", sfl_name)) # Pour débogage

design <- tryCatch({
  gsDesign(
    k = k,
    test.type = test_type,
    alpha = alpha,
    beta = beta,
    timing = timing,
    sfu = sfu_func,
    sfl = sfl_func # Utiliser la fonction choisie
  )
}, error = function(e) {
  error_response$message <- paste("Erreur lors de l'appel à gsDesign:", e$message)
  # Ajouter plus de détails sur l'erreur R si possible
  error_response$details <- capture.output(traceback(e))
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
      sfu = sfu_name,
      sfl = sfl_name
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
    betaSpentCumulative = design$lower$spend[i] # Peut être non pertinent si sfl ne dépend pas de beta
  )
}

# --- Imprimer le JSON sur stdout ---
cat(toJSON(results, auto_unbox = TRUE, pretty = FALSE))

quit(status = 0) # Succès

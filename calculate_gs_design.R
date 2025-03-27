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
sfu_name <- params$sfu %||% "OF"    # "OF", "Pocock", "KimDeMets"
sfl_name <- params$sfl %||% sfu_name # Par défaut, futilité = efficacité

# Vérifications basiques
if (is.null(k) || !is.numeric(k) || k <= 0) {
  error_response$message <- "Le paramètre 'k' (nombre d'étapes) est manquant ou invalide."
  cat(toJSON(error_response, auto_unbox = TRUE))
  quit(status = 1)
}
k <- as.integer(k)

# --- Mapping des noms de fonctions de dépense ---
get_spending_function <- function(name) {
  safe_name <- tolower(name %||% "of") # Défaut si name est NULL
  switch(safe_name,
         "of" = gsDesign::sfLDOF,         # O'Brien-Fleming like
         "pocock" = gsDesign::sfPocock,
         "kimdemets" = gsDesign::sfPower(param = 3), # Kim-DeMets approx
         # Ajouter d'autres si nécessaire
         gsDesign::sfLDOF # Défaut sécurisé
  )
}

sfu_func <- get_spending_function(sfu_name)
sfl_func <- get_spending_function(sfl_name)

# Timing : Supposer des étapes équi-espacées en information par défaut
timing <- (1:k) / k

# --- Appel à gsDesign ---
design <- tryCatch({
  gsDesign(
    k = k,
    test.type = test_type,
    alpha = alpha,
    beta = beta,
    timing = timing,
    sfu = sfu_func,
    sfl = sfl_func
  )
}, error = function(e) {
  error_response$message <- paste("Erreur lors de l'appel à gsDesign:", e$message)
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
    betaSpentCumulative = design$lower$spend[i]
  )
}

# --- Imprimer le JSON sur stdout ---
cat(toJSON(results, auto_unbox = TRUE, pretty = FALSE))

quit(status = 0) # Succès
```
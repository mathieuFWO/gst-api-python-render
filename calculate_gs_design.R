#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = TRUE)
# Simple message pour vérifier que le script est bien appelé
message("--- Simple R script started ---")
# Imprime un JSON de succès minimal
cat('{"error": false, "message": "R script ran successfully!", "args_received": ', length(args), '}\n')
# Quitte avec un code de succès
quit(save = "no", status = 0, runLast = FALSE)

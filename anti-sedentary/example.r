#! /usr/bin/Rscript
library('rjson')

# script is assuming JSON output always
args <- commandArgs(trailingOnly = TRUE)
input = fromJSON(args[1])

results <- list(
    a_it = 0,
    pi_it = 0
)

# output the results
cat(toJSON(results))
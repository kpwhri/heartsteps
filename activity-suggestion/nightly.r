#! /usr/bin/Rscript
library('rjson')

# script is assuming JSON output always
args <- commandArgs(trailingOnly = TRUE)
input = fromJSON(args[1])

# run script here
# this doesn't need to produce output
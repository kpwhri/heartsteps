#! /usr/bin/Rscript
library('rjson')

# script is assuming JSON output always
args <- commandArgs(trailingOnly = TRUE)
input = fromJSON(args)

#
## Required packages and source files
source("functions.R")
#require(mgcv); require(chron);

# payload = ' {
#   "userId": [ 1 ],
#   "decisionId": [ 1803312 ] ,
#   "time": [ "2018-10-12 10:10" ] ,
#   "dayStart": [ "2018-10-12 8:00" ] ,
#   "dayEnd": [ "2018-10-12 20:00" ]
# }
# '

# Pull in the Necessary CSVs
setwd("./data/")
window.time = read.csv("window_time.csv")
Sedentary.values = read.csv("sed_values.csv")
Sedentary.length = read.csv("sed_length.csv")

file_name = paste("user_",input$userId,"_antised_data.csv", sep = "")

if(file.exists(file_name)) {
  user.data = read.csv(file = file_name)
} else {
  user.data = data.frame(userid = input$userId, decisionId = input$decisionId,
                         time = input$time, dayStart = input$dayStart, dayEnd = input$dayEnd,
                         probaction = 0.0, action = 0.0)
}

# Fix the user datetime issue
user.data$time = as.POSIXct(strptime(user.data$time, "%m/%d/%y %H:%M"), tz = "Etc/GMT+6")
user.data$dayStart = as.POSIXct(strptime(user.data$dayStart, "%m/%d/%y %H:%M"), tz = "Etc/GMT+6")
user.data$dayEnd = as.POSIXct(strptime(user.data$dayEnd, "%m/%d/%y %H:%M"), tz = "Etc/GMT+6")

# setwd("../")
bucket1 = c(14,17); bucket2 = c(18,21); bucket3 = c(22,1)
buckets = list(bucket1,bucket2, bucket3)

window.time$window.utime = as.POSIXct(window.time$window.utime, tz = "GMT")

## Create a data.frame for Expected time Remaining
## Range of current hour = c(14:23,0:1)

seq.hour = c(14:23,0:1)
fraction.data = readRDS("fractiondata.RDS")
fraction.df = data.frame(fraction.data)
names(fraction.df) = c("current.hour", "mean", "var")


## Build history from existing database
current.time = as.POSIXct(strptime(input$time, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
final.time = as.POSIXct(strptime(input$dayEnd, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
beginning.time = as.POSIXct(strptime(input$dayStart, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")

library('chron')
current.day.obs = user.data$time < current.time & days(user.data$time) == days(current.time)

current.day.user.data = user.data[current.day.obs,]

## Convert to GMT
attr(current.day.user.data$time, "tzone") <- "GMT"
attr(current.time, "tzone") <- "GMT"
attr(final.time, "tzone") <- "GMT"
attr(beginning.time, "tzone") <- "GMT"

H.t = data.frame(
  old.states = current.day.user.data$state,
  old.A = current.day.user.data$action,
  old.rho = current.day.user.data$probaction,
  time.diff = as.numeric(current.time - current.day.user.data$time)
  )

time.steps = seq(1, as.numeric(final.time - beginning.time)*(60/5))
hour = (floor(time.steps/12)+14)%%24
block.steps = unlist(lapply(hour, FUN = which.block))

## Apply function
current.state = 1
current.hour = hours(current.time)
current.block = which.block(current.hour)
which.blocks = which(block.steps == current.block)
start.block = min(which.blocks); stop.block = max(which.blocks)

decision.time = (hours(current.time) - hours(beginning.time))*12 + minutes(current.time)/5
past.sedentary = (H.t$old.states == current.state)
N = c(0.0,1.8); lambda = 0.0; eta = 0.0

if( any(past.sedentary)) {
  current.run.length = t+1 - max(which(past.sedentary))
} else {
  current.run.length = 0
}

# remaining.time = length(time.steps) - (t-1)
remaining.time.in.block = stop.block - (decision.time - 1)
if(any(H.t$old.A[(max(1,decision.time-12)):(decision.time-1)] == 1)) {
  rho.t = 0
  A.t = 0
} else {
  rho.t = randomization.probability(N, current.state, remaining.time.in.block, current.run.length, current.hour, H.t, lambda, eta)
  A.t = rbinom(n = 1, size = 1, prob = rho.t)
}

results <- list(
    a_it = A.t,
    pi_it = rho.t
)

# output the results
cat(toJSON(results))

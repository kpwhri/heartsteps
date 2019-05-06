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
#   "userid": [ "1" ],
#   "decisionid": [ "dba4b6d0-3138-4fc3-a394-bac2b1a301e3" ] ,
#   "time": [ "2018-10-12 10:10:35" ] ,
#   "daystart": [ "2018-10-12 8:00" ] ,
#   "dayend": [ "2018-10-12 20:00" ] ,
#   "state": [ 1 ],
#   "steps": [ 10 ],
#   "available": [ 1 ]
# }
# '
# input = fromJSON(payload)

## INSERT SANITY CHECKS
return_default = FALSE
reasons = rep(0,0)

## CHECK 1: Datetime correct
if (any(is.na(strptime(input$time, "%Y-%m-%d %H:%M")),
        is.na(strptime(input$time, "%Y-%m-%d %H:%M")),
        is.na(strptime(input$time, "%Y-%m-%d %H:%M")))) {
  return_default = TRUE
  reasons = paste(reasons, 'Bad datetimes provided; ', sep = "")
}
## Check 2: state is 0 or 1
if(!is.element(input$state, 0:1)){
  return_default = TRUE
  reasons = paste(reasons, 'Bad state indicator provided; ', sep = "")
}

## Check 3: step count negative 
if(input$steps < 0 | !is.numeric(input$steps) ) {
  reasons = paste(reasons, 'Bad step count provided; ', sep = "")
}

## Check 4: availability is 1 or 0
if(!is.element(input$available, 0:1)){
  return_default = TRUE
  reasons = paste(reasons, 'Bad availability indicator provided; ', sep = "")
}

if(return_default) {
  results <- list(
    a_it = A.t,
    pi_it = rho.t
  )
  temp = c(as.vector(unlist(input)), reasons)
  write(x = temp, file = "errorfile.log", ncolumns = length(temp), append = TRUE)
  
} else {

  # Pull in the Necessary CSVs
  setwd("./data/")
  # window.time = read.csv("window_time.csv")
  r_min_x.table = readRDS("rminx.RDS")
  r_minus_x_plus.table = readRDS("rminusxplus.RDS")
  Sedentary.values = read.csv("sed_values.csv")
  Sedentary.length = read.csv("sed_length.csv")
  
  # If userID file exists then pull that in
  # Otherwise construct a dataframe
  file_name = paste("user_",input$userid,"_antised_data.csv", sep = "")
  
  if(file.exists(file_name)) {
    user.data = read.csv(file = file_name, header= TRUE)
  } else {
    user.data = data.frame(userid = input$userid, decisionid = input$decisionid,
                           time = input$time, daystart = input$daystart, dayend = input$dayend,
                           online_state = input$state, online_step = input$steps, available = input$available,
                           batch_state = -1, batch_step = -1, probaction = 0.0, action = 0.0, 
                           missingindicator = 0, duplicate = FALSE)
  }
  
  # Fix the user datetime issue
  if( any(is.na(strptime(user.data$time, "%Y-%m-%d %H:%M"))) ) {
    user.data$time = as.POSIXct(strptime(user.data$time, "%m/%d/%y %H:%M"), tz = "Etc/GMT+6")
    user.data$daystart = as.POSIXct(strptime(user.data$daystart, "%m/%d/%y %H:%M"), tz = "Etc/GMT+6")
    user.data$dayend = as.POSIXct(strptime(user.data$dayend, "%m/%d/%y %H:%M"), tz = "Etc/GMT+6")
  } else {
    user.data$time = as.POSIXct(strptime(user.data$time, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
    user.data$daystart = as.POSIXct(strptime(user.data$daystart, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
    user.data$dayend = as.POSIXct(strptime(user.data$dayend, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
  }
  
  # setwd("../")
  bucket1 = c(14,17); bucket2 = c(18,21); bucket3 = c(22,1)
  buckets = list(bucket1,bucket2, bucket3)
  
  # window.time$window.utime = as.POSIXct(window.time$window.utime, tz = "GMT")
  
  ## Create a data.frame for Expected time Remaining
  ## Range of current hour = c(14:23,0:1)
  
  seq.hour = c(14:23,0:1)
  fraction.data = readRDS("fractiondata.RDS")
  fraction.df = data.frame(fraction.data)
  names(fraction.df) = c("current.hour", "mean", "var")
  
  
  ## Build history from existing database
  current.time = as.POSIXct(strptime(input$time, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
  final.time = as.POSIXct(strptime(input$dayend, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
  beginning.time = as.POSIXct(strptime(input$daystart, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
  
  library('chron')
  current.day.obs = user.data$time < current.time & days(user.data$time) == days(current.time)
  
  current.day.user.data = user.data[current.day.obs,]
  
  ## Check if duplication
  if( any(is.element(user.data$time,current.time)) ) { 
    user.data$decisionid = as.numeric(user.data$decisionid)
    temp.data = data.frame(userid = input$userid, decisionid = input$decisionid,
                           time = input$time, daystart = input$daystart, dayend = input$dayend,
                           online_state = input$state, online_step = input$steps, available = input$available,
                           batch_state = -1, batch_step = -1, probaction = 0.0, action = 0.0, 
                           missingindicator = 0, duplicate = TRUE)
    
    write.csv(rbind(user.data, temp.data), file = file_name, row.names = FALSE)
    
    results <- list(
      a_it = 0,
      pi_it = 0
    )
    
  } else {
    ## Convert to GMT
    attr(current.day.user.data$time, "tzone") <- "GMT"
    attr(current.time, "tzone") <- "GMT"
    attr(final.time, "tzone") <- "GMT"
    attr(beginning.time, "tzone") <- "GMT"
    
    H.t = data.frame(
      old.states = current.day.user.data$online_state,
      old.A = current.day.user.data$action,
      old.rho = current.day.user.data$probaction,
      time.diff = as.numeric(current.time - current.day.user.data$time)
    )
    
    time.steps = seq(1, as.numeric(final.time - beginning.time)*(60/5))
    hour = (floor(time.steps/12)+14)%%24
    block.steps = unlist(lapply(hour, FUN = which.block))
    
    ## Apply function
    current.state = input$state
    current.hour = hours(current.time)
    current.block = which.block(current.hour)
    which.blocks = which(block.steps == current.block)
    start.block = min(which.blocks); stop.block = max(which.blocks)
    
    decision.time = (hours(current.time) - hours(beginning.time))*12 + minutes(current.time)/5
    past.sedentary = (H.t$old.states == current.state)
    N = c(0.0,1.8); lambda = 0.0; eta = 0.0
    
    if( any(past.sedentary)) {
      current.run.length = decision.time+1 - max(which(past.sedentary))
    } else {
      current.run.length = 0
    }
    
    # remaining.time = length(time.steps) - (t-1)
    remaining.time.in.block = stop.block - (decision.time - 1)
    if(any(H.t$old.A[H.t$time.diff< 60] == 1) | input$available == 0) {
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
    
    ## Write output to the file
    current.time = as.POSIXct(strptime(input$time, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
    final.time = as.POSIXct(strptime(input$dayend, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
    beginning.time = as.POSIXct(strptime(input$daystart, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
    
    temp.data = data.frame(userid = input$userid, decisionid = input$decisionid,
                           time = current.time, daystart = beginning.time, dayend = final.time,
                           online_state = input$state, online_step = input$steps, available = input$available, 
                           batch_state = -1, batch_step = -1, probaction = rho.t, action = A.t, 
                           missingindicator = 0, duplicate = FALSE)
    
    write.csv(rbind(user.data, temp.data), file = file_name, row.names = FALSE)
  }
}

# output the results
cat(toJSON(results))
  
  
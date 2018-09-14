rm(list = ls())
#' ---
#' title:  Nightly Udates in the bandit algorithm in HS 2.0
#' author: Peng Liao
#' date:   09.11, 2018
#' ---
#' 

library(rjson)
source("/Users/Peng/Dropbox/GitHubRepo/heartsteps/activity-suggestion/banditcode/functions.R")

# ================ Recieve and Process the input ================ 

# args <- commandArgs(trailingOnly = TRUE)[1]
# input = fromJSON(args) # this is a list

setwd("/Users/Peng/Dropbox/GitHubRepo/heartsteps/activity-suggestion/")
input <- fromJSON(file = "./banditcode/update.json")

names.array <- c("temperatureArray", "preStepsArray", "postStepsArray")
for(name in names.array){
  
  input[[name]] <- proc.array(input[[name]])
  
}

# check if the length is 5 
stopifnot(all(lapply(input[names.array], length)==5))

# temperature should be imputed by HS server
stopifnot(all(is.na(input$temperatureArray)) == FALSE)

# priorAnti, lastActivity can only be true or false
stopifnot(is.logical(input$priorAnti), is.logical(input$lastActivity))


# ================ Asscess the day's data ================ 

paths <- paste("./data/", "user", input$userID, sep="")
load(paste(paths, "/imputation.Rdata", sep=""))
load(paste(paths, "/daily.Rdata", sep="")) 
load(paste(paths, "/history.Rdata", sep="")) 
load(paste(paths, "/policy.Rdata", sep="")) 

# Expect to have 5 rows, i.e. the decision services are called 5 times
stopifnot(nrow(data.day$history) == 5)

# ================ Update the daily data ================ 

# might need to alter the action in 5th decision time 
action.index <- 5
prob.index <- 4
last.time <- 5
last.action <- data.day$history[last.time, action.index]  
if(input$lastActivity != last.action){
  
  # if inconsistent, 
  # update the action and set the prob to NA to indicate this failure
  
  data.day$history[last.time, action.index] <- input$lastActivity;
  data.day$history[last.time, prob.index] <- NA; 
  
  
}


# filling in the states and rewards (require imputation and standardization)
# Note: we do not impute the reward! 
# Note: we do not have any missing in the interaction terms (checked before)

# need to fill in: temp, presteps, reward

# Format: day, decision time, avail, prob, action, reward, 
#         interaction, temp, LOG presteps, sqrtsteps
# where interaction is given by
# c(current.dosage,  engagement.indc,  work.loc, other.loc, variation.indc)


day.history <- data.day$history
colnames(day.history) <- c("day", "decision.time", 
                           "availability", "probability", "action", "reward",
                           "dosage", "engagement", "work.location", "other.location", "variation",
                           "temperature", "logpresteps", "sqrt.totalsteps", "prepoststeps")
day.history <- data.frame(day.history)

# temperature (should have no missingness, i.e already imputed by HS server; checked before)
day.history$temperature <- input$temperatureArray

# log pre-steps (possibly missing, will impute)
day.history$logpresteps <- log(0.5 + input$preStepsArray)

if(any(is.na(day.history$logpresteps))){
  
  for(k in which(is.na(day.history$logpresteps))){
    
    # load the previous at most 7 data at the same decision time
    tmp <- data.imputation$presteps[[k]]
    
    if(all(is.na(tmp)) == FALSE){
      
      # if we have something
      # assuming length(tmp) <= 7
      day.history$logpresteps[k] <- log(0.5+mean(tmp))
      
    }
  }
}

# imputed 60 min steps 
poststep.temp <- input$postStepsArray
if(any(is.na(poststep.temp))){
  
  for(k in which(is.na(poststep.temp))){
    
    # load the previous at most 7 data at the same decision time
    tmp <- data.imputation$poststeps[[k]]
    
    if(all(is.na(tmp)) == FALSE){
      
      # if we have something
      # assuming length(tmp) <= 7
      poststep.temp[k] <- mean(tmp)
      
    }
  }
}
prestep.temp <- input$preStepsArray
if(any(is.na(prestep.temp))){
  
  for(k in which(is.na(prestep.temp))){
    
    # load the previous at most 7 data at the same decision time
    tmp <- data.imputation$presteps[[k]]
    
    if(all(is.na(tmp)) == FALSE){
      
      # if we have something
      # assuming length(tmp) <= 7
      prestep.temp[k] <- mean(tmp)
      
    }
  }
}
day.history$prepoststeps <- poststep.temp + prestep.temp


# reward (possibly missing, but no imputation)
day.history$reward <- log(0.5+input$postStepsArray)



# ================ update the history by adding the history in daily dataset ================ 

data.history <- rbind(data.history, day.history)

# ================ update the policy using the updated history ================ 

# note the continous states (temperature, logpresteps, sqrtsteps) are unstandarized
# there are potential missing data in the reward, prob
# states are all computed unless no observation for that variable so far 
# NEEEEED TO STANDADIZE DOSAGE IN THE ANALYSIS

# ================ Re-initialize the daily dataset used for next day ================

# calcualte the dosage at the end of day
dosage.index <- 7
last.time <- 5
last.dosage <- data.day$history[last.time, dosage.index]  
receive.indc <- any(input$priorAnti, input$lastActivity)
# update the dosage
current.dosage <- update.dosage(last.dosage, receive.indc)

# engagement (cannot be missing)
engagement.indc <- (input$appClick >= data.imputation$thres.appclick);
if(is.na(engagement.indc)){
  
  # app click data is missing
  avg.click <- mean(data.imputation$appclicks)
  engagement.indc <- (avg.click > data.imputation$thres.appclick)
  
}


# variation (cannot be missing) #### TO DO
variation.indc <- rep(NA, 5)

for(k in 1:5){

  
  temp <- data.history$prepoststeps[data.history$decision.time == k]
  temp <- rollapply(temp, width=7, FUN=sd, align='right', fill = NA) # rolling sd over past 7 days (including today)
  temp <- tail(temp, 1+input$studyDay) # exclude the warm-up period
  
  Y1 <- temp[length(temp)] # today's sd
  Y0 <- median(temp[1:(length(temp)-1)]) # median of the past
  variation.indc[k] <- (Y1 >= Y0)

}

# sqrt steps (can be missing) 
sqrt.steps <- sqrt(input$totalSteps)
if(is.na(sqrt.steps)){
  
  avg.steps <- mean(data.imputation$totalsteps)
  sqrt.steps <- sqrt(avg.steps)
  
}

# Re-initialize the daily dataset 

data.day <- list()
data.day$init.dosage <- current.dosage
data.day$engagement <- engagement.indc
data.day$variation <- variation.indc
data.day$sqrtsteps <- sqrt.steps 



# ================ update the imputation dataset ================ 


# applicks last 7 days (update daily)
data.imputation$appclicks <- append.array(data.imputation$appclicks, input$appClick)

# total steps last 7 days (update daily)
data.imputation$totalsteps <- append.array(data.imputation$totalsteps, input$totalSteps)

# pre steps last 7 days per decision time (update daily)
for(i in 1:5){
  
  data.imputation$presteps[[i]] <- append.array(data.imputation$presteps[[i]], input$preStepsArray[i])
  
}

# post steps for last 7 days per decision time (update daily)
for(i in 1:5){
  
  poststeps <- input$postStepsArray[i]
  data.imputation$poststeps[[i]] <- append.array(data.imputation$poststeps[[i]], poststeps)
  
  
}


# ================ Save everything ================

save(data.day, file = paste(paths, "/daily.Rdata", sep=""))
save(data.policy, file = paste(paths, "/policy.Rdata", sep=""))
save(data.history, file = paste(paths, "/history.Rdata", sep=""))
save(data.imputation, file = paste(paths, "/imputation.Rdata", sep=""))


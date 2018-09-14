rm(list = ls())

#' ---
#' title:  Action selection in the bandit algorithm in HS 2.0
#' author: Peng Liao
#' date:   09.11, 2018
#' ---
#' 

library(rjson)
source("/Users/Peng/Dropbox/GitHubRepo/heartsteps/activity-suggestion/banditcode/functions.R")
# ================ recieve the input ================ 
# args <- commandArgs(trailingOnly = TRUE)[1]
# input = fromJSON(args) # this is a list

setwd("/Users/Peng/Dropbox/GitHubRepo/heartsteps/activity-suggestion/")
input <- fromJSON(file = "./banditcode/call_5.json")


# should not be any missing
stopifnot(all(lapply(input, is.null)==FALSE))
# location in (1, 2, 3)
stopifnot(input$location %in% c(1, 2, 3))
# availability, priorAnti, lastActivity can only be true or false
stopifnot(is.logical(input$availability), is.logical(input$priorAnti), is.logical(input$lastActivity))


# ================ access the user's dataset ================  
paths <- paste("./data/", "user", input$userID, sep="")

# including daily features and dosage at the begining of the day and the current history
load(paste(paths, "/daily.Rdata", sep="")) 

# policy related
load(paste(paths, "/policy.Rdata", sep="")) 

# expect the service will be called every decision time
if(input$decisionTime > 1){
  stopifnot(input$decisionTime == max(data.day$history[, 2]) + 1)
}


# ================ create the interaction terms ================ 

# get last dosage
if(input$decisionTime == 1){
  
  last.dosage <- data.day$init.dosage
  
}else{
  
  dosage.index <- 7
  last.time <- input$decisionTime - 1
  last.dosage <- data.day$history[last.time, dosage.index]  
  
}

# whether recieve any msg since last dt to current 
# if we are at the first one, then only check since the begining of the day to the first
# lastAct should always be FALSE (we not gonna use this anyway)

receive.indc <- any(input$priorAnti, input$lastActivity)

# update the dosage
current.dosage <- update.dosage(last.dosage, receive.indc)

work.loc <- input$location == 1;
other.loc <- input$location == 0;
engagement.indc <- data.day$engagement;
variation.indc <- data.day$variation[input$decisionTime]

interaction.terms <- c(current.dosage, 
                       engagement.indc, 
                       work.loc, 
                       other.loc, 
                       variation.indc)

# we should not have any missingness here 
stopifnot(all(is.na(interaction.terms))==FALSE)

# ================ action Selection ================  
if(input$availability){
  
  ## retrieve the current policy from the user's dataset
  mu <- data.policy$mu
  Sigma <- data.policy$Sigma
  
  ## create the feature
  feat <- c(1, std.dosage(interaction.terms[1]), interaction.terms[-1]) 
  pos.mean <- c(feat %*% mu)
  pos.var <- max(0, c(t(feat) %*% Sigma %*% feat))
  
  # forming proxy of value
  gamma.mdp <- data.policy$gamma.mdp;
  Q.mat <- data.policy$Q.mat;
  margin <- gamma.mdp * Q.mat[current.dosage, 1] - gamma.mdp * Q.mat[current.dosage, 2]

  # raw prob
  pit0 <- pnorm((pos.mean-margin)/sqrt(pos.var))
  
  # clipping
  pi_max <- data.policy$pi_max;
  pi_min <- data.policy$pi_min;  
  prob =  min(c(pi_max, max(c(pi_min, pit0))))
  
  action <- (runif(1) < prob)
  
}else{
  
  prob <- 0
  action <- FALSE
  
}

# ================ Update the daily dataset ================ 

# add the current decision time
# Format: day, decision time, avail, prob, action, reward, 
#         interaction, temp, presteps, sqrtsteps, 60minsteps
# Currently unknown: temperture, log presteps and reward (log poststeps), 60minsteps
data.day$history <- rbind(data.day$history, c(input$studyDay, 
                                              input$decisionTime, 
                                              input$availability, 
                                              prob, 
                                              action, 
                                              NA, 
                                              interaction.terms, 
                                              NA, 
                                              NA, 
                                              data.day$sqrtsteps,
                                              NA)) 

# check if prior action is consistent with system (lastActivity)
# only need to check when the current decision time > 1 
if(input$decisionTime > 1){
  
  action.index <- 5
  prob.index <- 4
  
  last.time <- input$decisionTime - 1
  last.action <- data.day$history[last.time, action.index]  
  
  if(input$lastActivity != last.action){
    
    # if inconsistent, 
    # update the action and set the prob to NA to indicate this failure
    # will be used to update the value function
    data.day$history[last.time, action.index] <- input$lastActivity;
    data.day$history[last.time, prob.index] <- NA; 
    
    
  }
  
  
}

# save to the system
save(data.day, file = paste(paths, "/daily.Rdata", sep="")) 


# ================Output ================
output <- list(send = action, probability = prob)
cat(toJSON(output))



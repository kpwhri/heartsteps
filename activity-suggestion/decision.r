rm(list = ls())
server = T
#' ---
#' title:  Action selection in the bandit algorithm in HS 2.0
#' author: Peng Liao
#' date:   09.11, 2018
#' ---
#' 

library(rjson)
# ================ recieve the input ================ 

if(server){
  
  source("functions.R")
  args <- commandArgs(trailingOnly = TRUE)[1]
  input = fromJSON(args) # this is a list
  
  
}else{
  
  source("/Users/Peng/Dropbox/GitHubRepo/heartsteps/activity-suggestion/banditcode/functions.R")
  setwd("/Users/Peng/Dropbox/GitHubRepo/heartsteps/activity-suggestion/")
  input <- fromJSON(file = "./banditcode/call_6.json")
  
}


# should not be any missing
stopifnot(all(lapply(input, is.null)==FALSE))
# location in (1, 2, 3)
stopifnot(input$location %in% c(1, 2, 3))
# availability, priorAnti, lastActivity can only be true or false
stopifnot(is.logical(input$availability), is.logical(input$priorAnti), is.logical(input$lastActivity))
# for the first decision time, last Activity must be false (acc. to defintion)
if(input$decisionTime == 1){
  
  stopifnot(input$lastActivity==FALSE)
}


# ================ access the user's dataset ================  
paths <- paste("./data/", "user", input$userID, sep="")

# including daily features and dosage at the begining of the day and the current history
load(paste(paths, "/daily.Rdata", sep="")) 

# policy related
load(paste(paths, "/policy.Rdata", sep="")) 

# expect the service will be called every decision time
if(is.null(data.day$history)){
  
  # meanning we have not see the first decision time
  # check if we are getting the first one 
  
  stopifnot(input$decisionTime == 1)
  
}else{
  
  stopifnot(input$decisionTime == max(data.day$history[, 2]) + 1)

}

# expect the service will be called every day
stopifnot(input$studyDay == data.day$study.day)



# ================ create the interaction terms ================ 

# obtain the last dosage and decide if to increase
if(input$decisionTime == 1){
  
  # retrive the dosage at the fifth time yesterday
  last.dosage <- data.day$yesterdayLast.dosage
  
  # whether recieve any msg between the fifth decision time to the first decision time 
  # that is, any activitity sent at the yesterday's fifth and any anti sent between fifth to first. 
  # we infer the second one by two inputs
  receive.indc <- any(input$priorAnti, data.day$fifthToEnd.anti, data.day$fifth.act)
  
  
}else{
  
  # retrive the dosage at the last decision time
  dosage.index <- which(data.day$var.names == "dosage")
  last.time <- input$decisionTime - 1
  last.dosage <- data.day$history[last.time, dosage.index]  
  
  # whether recieve any msg between last and current decision time
  receive.indc <- any(input$priorAnti, input$lastActivity)
  
}

# update the dosage
current.dosage <- update.dosage(last.dosage, receive.indc)

# other interactions 
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
  
  # retrieve the current policy from the user's dataset
  mu <- data.policy$mu
  Sigma <- data.policy$Sigma
  gamma.mdp <- data.policy$gamma.mdp;
  Q.mat <- data.policy$Q.mat;
  pi_max <- data.policy$pi_max;
  pi_min <- data.policy$pi_min;  
  
  # create the feature (standardization ocurrs here)
  feat <- c(1, std.dosage(interaction.terms[1]), interaction.terms[-1]) 

  # posterior dist
  pos.mean <- c(feat %*% mu)
  pos.var <- max(0, c(t(feat) %*% Sigma %*% feat))
  
  # forming the margin
  margin <- gamma.mdp * Q.mat[current.dosage, 1] - gamma.mdp * Q.mat[current.dosage, 2]

  # raw prob
  pit0 <- pnorm((pos.mean-margin)/sqrt(pos.var))
  
  # clipping
  prob <- min(c(pi_max, max(c(pi_min, pit0))))
  

  
}else{
  
  prob <- 0
  
}

# take action
random.num <- runif(1)
action <- (random.num <= prob)

# ================ Update the daily dataset ================ 

# add the current decision time
# Same Format as in the initialization
data.day$history <- rbind(data.day$history, 
                          c(input$studyDay, 
                            input$decisionTime, 
                            input$availability, 
                            prob, 
                            action, 
                            NA, 
                            interaction.terms, 
                            NA, 
                            NA, 
                            data.day$sqrtsteps,
                            NA,
                            random.num)) 

# check if prior action is consistent with system (lastActivity)
# only need to check when the current decision time > 1 

if(input$decisionTime > 1){
  
  action.index <- which(data.day$var.names == "action")
  prob.index <- which(data.day$var.names == "probability")
  
  last.time <- input$decisionTime - 1
  last.action <- data.day$history[last.time, action.index]  
  
  if(input$lastActivity != last.action){
    
    # if inconsistent, 
    # update the action and set the prob to NA to indicate this failure
    # although in the nightly updates we will set prob = 0
    data.day$history[last.time, action.index] <- input$lastActivity;
    data.day$history[last.time, prob.index] <- NA; 
    
  }
  
  
}

# save to the system
save(data.day, file = paste(paths, "/daily.Rdata", sep="")) 


# ================Output ================
output <- list(send = action, probability = prob)
cat(toJSON(output))



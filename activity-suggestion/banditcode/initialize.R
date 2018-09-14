rm(list = ls())
#' ---
#' title:  Initialize the bandit algorithm in HS 2.0
#' author: Peng Liao
#' date:   09.11, 2018
#' ---
#' 

library(rjson)
source("/Users/Peng/Dropbox/GitHubRepo/heartsteps/activity-suggestion/banditcode/functions.R")

# ========  Recieve Input ========= ####

# args <- commandArgs(trailingOnly = TRUE)[1]
# input = fromJSON(args) # this is a list

setwd("/Users/Peng/Dropbox/GitHubRepo/heartsteps/activity-suggestion/")
input <- fromJSON(file = "./banditcode/start.json")


# convert NULL to NA and tranform into vector/matrix
names.array <- c("appClicksArray", "totalStepsArray")
names.matrix <- c("availMatrix", "preStepsMatrix", "postStepsMatrix")
for(name in names.array) input[[name]] <- proc.array(input[[name]])
for(name in names.matrix) input[[name]] <- proc.matrix(input[[name]])
  

# need to ensure we have app clicks data 
stopifnot(all(is.na(input$appClicksArray)) == FALSE)

# check if we have identical days' data for each variables
len.all <- NULL
for(name in names.array){
  
  len.all <- c(len.all, length(input[[name]]))
  
  
}
for(name in names.matrix){
  
  len.all <- c(len.all, nrow(input[[name]]))
  
  
}
stopifnot(all(diff(len.all) == 0))

# number of days before the study
ndays <- len.all[1]

# check if we have all five datas for the matrics
ncol.all <- NULL
for(name in names.matrix){
  
  ncol.all <- c(ncol.all, ncol(input[[name]]) - 1)
  
  
}
stopifnot(ncol.all == 5)

# assuming it is continuing
stopifnot(diff(input$availMatrix[, 1]) == 1, diff(input$preStepsMatrix[, 1])==1, diff(input$postStepsMatrix[, 1]) == 1)

# ensure availability is logicial (no missing)
stopifnot(all(c(input$availMatrix[, -1]) %in% c(0, 1)))

# ===  Initialize a Dataset for imputation and discretization === ####

## dataset used to handle future missing data and standarization
data.imputation <- list()
data.imputation$userID <- input$userID

# threshold to standarize the app click
data.imputation$thres.appclick <- mean(input$appClicksArray, na.rm=TRUE)

# applicks last 7 days (update daily)
data.imputation$appclicks <- tail(input$appClicksArray[is.na(input$appClicksArray)==FALSE], 7)

# total steps last 7 days (update daily)
data.imputation$totalsteps <- NA
if(all(is.na(input$totalStepsArray))==FALSE){
  
  data.imputation$totalsteps <- tail(input$totalStepsArray[is.na(input$totalStepsArray)==FALSE], 7)
  
}

# check we at least have some known values for pre-post step for each decision time 

# pre steps last 7 days per decision time (update daily)
data.imputation$presteps <- NULL
for(i in 1:5){
  
  temp <- input$preStepsMatrix[, 1+i] # first column is day
  
  if(all(is.na(temp))){
    
    data.imputation$presteps[[i]] <- NA
    
  }else{
    
    data.imputation$presteps[[i]] <- tail(temp[is.na(temp)==FALSE], 7)
    
  }
  
  
  
}

# 60 min steps for last 7 days per decision time (update daily)
data.imputation$poststeps <- NULL
for(i in 1:5){
  
  temp <-input$postStepsMatrix[, 1+i]
  
  if(all(is.na(temp))){
    
    data.imputation$poststeps[[i]] <- NA
    
  }else{
    
    data.imputation$poststeps[[i]] <- tail(temp[is.na(temp)==FALSE], 7)
    
  }
  
  
}


# ===== Initialize the Policy ====== ####
data.policy <- list()

# this will be used to select the action on the first day. 
# contains: posterior mean and variance, value function, pi_min and pi_max
# c(current.dosage,  (standarized)
#   engagement.indc, 
#   work.loc, 
#   other.loc, 
#   variation.indc)

data.policy$mu <- rep(0, 6)
data.policy$Sigma <- diag(1, 6)
data.policy$Q.mat <- matrix(0, 100, 2)
data.policy$pi_max <- 0.8;
data.policy$pi_min <- 0.1;
data.policy$gamma.mdp <- 0.9


# ===== Create a holder to save the entire (imputated, unstandarized) history ====== ####
names <- c("day", "decision.time", 
           "availability", "probability", "action", "reward",
           "dosage", "engagement", "work.location", "other.location", "variation",
           "temperature", "logpresteps", "sqrt.totalsteps", "prepoststeps")

data.history <- matrix(NA, nrow = 5*ndays, ncol = length(names))
colnames(data.history) <- c("day", "decision.time", 
                           "availability", "probability", "action", "reward",
                           "dosage", "engagement", "work.location", "other.location", "variation",
                           "temperature", "logpresteps", "sqrt.totalsteps", "prepoststeps")
data.history <- data.frame(data.history)

data.history$day <- -rep(ndays:1, each = 5) # negative represents before the study
data.history$decision.time <- rep(1:5, times = ndays)
data.history$availability <- c(t(input$availMatrix[, -1]))
data.history$probability <- 0;
data.history$action <- 0;
data.history$dosage <- 1;
data.history$reward <- log(0.5 + c(t(input$postStepsMatrix[, -1])))

##### the imputed 60 min steps#######
prestep.mat <- NULL # column: decision time
for(k in 1:5){
  
  temp <- input$preStepsMatrix[, k+1]
  
  if(is.na(temp[1])){
    
    temp[[1]] <- mean(temp, na.rm = TRUE)
    
  }
  
  for(i in 2:ndays){
    
    temp[i] <- mean(temp[1:i], na.rm = TRUE)
    
  }
  
  prestep.mat <- cbind(prestep.mat, temp)
  
  
}

poststep.mat <- NULL # column: decision time
for(k in 1:5){
  
  temp <- input$postStepsMatrix[, k+1]
  
  if(is.na(temp[1])){
    
    temp[[1]] <- mean(temp, na.rm = TRUE)
    
  }
  
  for(i in 2:ndays){
    
    temp[i] <- mean(temp[1:i], na.rm = TRUE)
    
  }
  
  poststep.mat <- cbind(poststep.mat, temp)
  
  
}

data.history$prepoststeps <- c(t(prestep.mat + poststep.mat))



# =====  Holder for data on the first day ==== ####
# dosage/engagement/variation/sqrt of total steps 

data.day <- list()
# dosage
data.day$init.dosage <- 1

# sqrt steps (imputed if last day is missing)
data.day$sqrtsteps <- sqrt(input$totalStepsArray[ndays]) # not in action selection
if(is.na(data.day$sqrtsteps)){
 
  if(all(is.na(input$totalStepsArray))){
    
    # all previous days have missing total steps
    data.day$sqrtsteps <- NA
    
  }else{
    
    # impute by the average of the past (at most) 7 known days' value
    data.day$sqrtsteps <- sqrt(mean(data.imputation$totalsteps))
    
  }
  
}

# app engagement (imputed if last day is missing)
data.day$engagement <- (input$appClicksArray[ndays] > data.imputation$thres.appclick)
if(is.na(data.day$engagement)){
  
  # use the last known day
  #data.day$engagement <- (tail(data.imputation$appclicks, 1) >= data.imputation$thres.appclick)
  
  # use the average, then we get true 
  data.day$engagement <- TRUE
}


# use the history to define it based on the protocol 

data.day$variation <- rep(NA, 5)
for(k in 1:5){
  
  Y1 = sd(subset(data.history, decision.time == k)$prepoststeps)
  Y0 = sd(subset(data.history, decision.time == k & day < -1)$prepoststeps) # exclude the last day
  data.day$variation[k] <- (Y1 >= Y0)
  
}






# ===== create the folder for the user and save the datasets ====== ####

paths <- paste("./data/", "user", input$userID, sep="")
dir.create(paths)

save(data.day, file = paste(paths, "/daily.Rdata", sep=""))
save(data.policy, file = paste(paths, "/policy.Rdata", sep=""))
save(data.history, file = paste(paths, "/history.Rdata", sep=""))
save(data.imputation, file = paste(paths, "/imputation.Rdata", sep=""))


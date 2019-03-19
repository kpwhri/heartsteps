rm(list = ls())
server = T
#' ---
#' title:  Initialize the bandit algorithm in HS 2.0
#' author: Peng Liao
#' date:   09.11, 2018
#' ---
#'  

library(rjson)


# ========  Recieve Input ========= ####

if(server){
  
  source("functions.R")
  load("bandit-spec.Rdata")
  args <- commandArgs(trailingOnly = TRUE)[1]
  input = fromJSON(args) # this is a list
   
}else{
  

  setwd("/Users/Peng/Dropbox/GitHubRepo/heartsteps/walking-suggestion-service/")
  source("functions.R")
  load("bandit-spec.Rdata")
  
  input <- fromJSON(file = "./test/start.json")
  
}





# check if we have all the information 
stopifnot(all(c("userID", "totalStepsArray", "preStepsMatrix", "postStepsMatrix") %in% names(input)))

# convert NULL to NA and tranform into vector/matrix
names.array <- c("totalStepsArray")
names.matrix <- c("preStepsMatrix", "postStepsMatrix")
for(name in names.array) input[[name]] <- proc.array(input[[name]])
for(name in names.matrix) input[[name]] <- proc.matrix(input[[name]])



# check if we have identical days' data for each variables
len.all <- c(sapply(names.array, function(x) length(input[[x]])), 
             sapply(names.matrix, function(x) nrow(input[[x]])))
stopifnot(all(diff(len.all) == 0))

# number of days before the study (assuing 7 days)
ndays <- as.numeric(len.all[1])
stopifnot(ndays == 7)

# check if we have all five decision times for the matrics
ncol.all <- sapply(names.matrix, function(x) ncol(input[[x]]))
stopifnot(ncol.all == 5)

# need to ensure we have, for each dt, any pre/post steps data)
stopifnot(all(apply(input$preStepsMatrix, 2, function(x) sum(is.na(x))) < ndays))
stopifnot(all(apply(input$postStepsMatrix, 2, function(x) sum(is.na(x))) < ndays))

# need to ensure we have at least one obvervation for the total steps (so that we can impute)
stopifnot(all(is.na(input$totalStepsArray)) == FALSE)

# ===  Initialize a Dataset for imputation and discretization === ####

## dataset used to handle future missing data and standarization
data.imputation <- list()
data.imputation$userID <- input$userID

# appclicks last 7 known days (update daily; to impute the missing app clicks)
data.imputation$appclicks <- NA

# total steps last 7 days (update daily)
data.imputation$totalsteps <- NA
if(all(is.na(input$totalStepsArray))==FALSE){
  
  data.imputation$totalsteps <- tail(input$totalStepsArray[is.na(input$totalStepsArray)==FALSE], 7)
  
}

# pre steps last 7 days per decision time (update daily)
data.imputation$presteps <- NULL
for(i in 1:5){
  
  temp <- input$preStepsMatrix[, i] 
  
  if(all(is.na(temp))){
    
    # checked already 
    data.imputation$presteps[[i]] <- NA
    
  }else{
    
    data.imputation$presteps[[i]] <- tail(temp[is.na(temp)==FALSE], 7)
    
  }
  
}

# post steps for last 7 days per decision time (update daily)
data.imputation$poststeps <- NULL
for(i in 1:5){
  
  temp <-input$postStepsMatrix[, i]
  
  if(all(is.na(temp))){
    
    # checked already
    data.imputation$poststeps[[i]] <- NA
    
  }else{
    
    data.imputation$poststeps[[i]] <- tail(temp[is.na(temp)==FALSE], 7)
    
  }
  
}

# ===== Initialize the Policy ====== ####
data.policy <- list()

# This contains the policy used to select the action during the day
# posterior mean and variance, value function, pi_min and pi_max
# FORMAT:
# intercept
# (standarized) current.dosage,  
# engagement.indc, 
# work.loc, 
# other.loc, 
# variation.indc

interaction.index <- bandit.spec$policy.index # include the intercept
data.policy$mu <- bandit.spec$prior.mean[interaction.index]
data.policy$Sigma <- bandit.spec$prior.var[interaction.index, interaction.index]
data.policy$pi_min <- bandit.spec$pi_min;
data.policy$pi_max <- bandit.spec$pi_max;
data.policy$gamma.mdp <- bandit.spec$gamma.mdp;
data.policy$Q.mat <- bandit.spec$init.Q.mat


# ===== Create a holder to save the entire (imputated and unstandarized) history ====== ####

var.names <- c("day", "decision.time", 
           "availability", "probability", "action", "reward",
           "dosage", "engagement", "work.location", "other.location", "variation",
           "temperature", "logpresteps", "sqrt.totalsteps", "prepoststeps", "deliever", "appclick" ,"random.number")

data.history <- matrix(NA, nrow = 5*ndays, ncol = length(var.names))
colnames(data.history) <- var.names
data.history <- data.frame(data.history)

# just fill in the variables might be used later (avail, action, reward, cts variables)
data.history$day <- -rep(ndays:1, each = 5) # negative represents before the study
data.history$decision.time <- rep(1:5, times = ndays)
data.history$availability <- NA
data.history$probability <- NA;
data.history$action <- NA;
data.history$dosage <- NA;
data.history$reward <- NA
data.history$temperature <- NA

# the imputed pre and post steps using cumulative averages
# if the first one is missing, then use the total average
prestep.mat <- NULL # column: decision time
poststep.mat <- NULL # column: decision time
for(k in 1:5){
  
  prestep.mat <- cbind(prestep.mat, warmup.imput(input$preStepsMatrix[, k]))
  poststep.mat <- cbind(poststep.mat, warmup.imput(input$postStepsMatrix[, k]))
}
data.history$prepoststeps <- c(t(prestep.mat + poststep.mat))
data.history$logpresteps <- log(0.5 + c(t(prestep.mat)))

# imputed total steps
data.history$sqrt.totalsteps <- rep(c(NA, sqrt(warmup.imput(input$totalStepsArray)[1:(ndays-1)])), each = 5)


# =====  Data Holder for the first day ==== ####
# study day / dosage on the first decision time / engagement indicator yesterday / 
# historical variation measure / sqrt of total steps yesterday 

data.day <- list()

# study day
data.day$study.day <- 1

# dosage related
data.day$yesterdayLast.dosage <-  0 # dosage at the fifth decision yesterday prior to treatment
data.day$fifthToEnd.anti <- FALSE # indicator of whether there is anti-sed msg sent between 5th to the end of yesterday
data.day$fifth.act <- FALSE # indicator of whether there is activity msg sent at fifth decision time yesterday

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

# app engagement (initialize to be TRUE)
data.day$engagement <- TRUE

# use the history to define it based on the protocol 
data.day$variation <- rep(NA, 5)
for(k in 1:5){
  
  Y1 = sd(subset(data.history, decision.time == k)$prepoststeps)
  Y0 = sd(subset(data.history, decision.time == k & day < -1)$prepoststeps) # exclude the last day
  data.day$variation[k] <- (Y1 >= Y0)
  
}


# keep the names to ensure the format is same
data.day$var.names <- var.names



# ====== log file for saving the error ===== # 

error.log <- NULL

# ===== create the folder for the user and save the datasets ====== ####

if(dir.exists("./data") == FALSE){
  
  dir.create("./data")

}

paths <- paste("./data/", "user", input$userID, sep="")
dir.create(paths, showWarnings = FALSE)

save(data.day, file = paste(paths, "/daily.Rdata", sep=""))
save(data.policy, file = paste(paths, "/policy.Rdata", sep=""))
save(data.history, file = paste(paths, "/history.Rdata", sep=""))
save(data.imputation, file = paste(paths, "/imputation.Rdata", sep=""))
save(error.log, file = paste(paths, "/error.Rdata", sep=""))

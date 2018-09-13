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


# trans into matrix and vector and convert NULL to NA

names.array <- c("appClicksArray", "totalStepsArray")
names.matrix <- c("availMatrix", "preStepsMatrix", "postStepsMatrix")
for(name in names.array){
  
  input[[name]] <- proc.array(input[[name]])
  
}
for(name in names.matrix){
  
  input[[name]] <- proc.matrix(input[[name]])
  
}

# need to ensure we have app clicks data #### ASSUMPTION 
stopifnot(all(is.na(input$appClicksArray)) == FALSE)


# ===  Initialize a Dataset for imputation and standarization=== ####

## dataset used to handle future missing data and standarization
data.imputation <- list()
data.imputation$userID <- input$userID

# threshold to standarize the app click
data.imputation$thres.appclick <- mean(input$appClicksArray, na.rm=TRUE)

# applicks last 7 days (update daily)
data.imputation$appclicks <- input$appClicksArray[is.na(input$appClicksArray)==FALSE]

# total steps last 7 days (update daily)
data.imputation$totalsteps <- NA
if(all(is.na(input$totalStepsArray))==FALSE){
  
  data.imputation$totalsteps <- input$totalStepsArray[is.na(input$totalStepsArray)==FALSE]
  
}

# pre steps last 7 days per decision time (update daily)
data.imputation$presteps <- NULL
for(i in 1:5){
  
  temp <- input$preStepsMatrix[, 1+i]
  
  if(all(is.na(temp))){
    
    data.imputation$presteps[[i]] <- NA
    
  }else{
    
    data.imputation$presteps[[i]] <- temp[is.na(temp)==FALSE]
    
  }
  
  
  
}

# 60 min steps for last 7 days per decision time (update daily)
data.imputation$prepoststeps <- NULL
for(i in 1:5){
  
  temp <- input$preStepsMatrix[, 1+i] + input$postStepsMatrix[, 1+i]
  
  if(all(is.na(temp))){
    
    data.imputation$prepoststeps[[i]] <- NA
    
  }else{
    
    data.imputation$prepoststeps[[i]] <- temp[is.na(temp)==FALSE]
    
  }
  
  
}


# ===== Initialize the Policy ====== ####
data.policy <- list()

# this will be used to select the action on the first day. 
# contains: posterior mean and variance, value function, pi_min and pi_max

# mu <- rep(0, 6)
# Sigma <- diag(1, 6)
# 
# feat <- c(1, interaction.terms)
# stopifnot(all(is.na(feat))==FALSE)
# 
# pos.mean <- c(feat %*% mu)
# pos.var <- max(0, c(t(feat) %*% Sigma %*% feat))
# margin <- 0;
# 
# pi_max <- 0.8;
# pi_min <- 0.1;  
# 
# pit0 <- pnorm((pos.mean-margin)/sqrt(pos.var))
# prob =  min(c(pi_max, max(c(pi_min, pit0))))



# ===== Create a holder to save the entire (imputated) history ====== ####
data.history <- NULL

# make the same format
# inlcude the availability 

# =====  Holder for data on the first day ==== ####
# dosage/engagement/variation/sqrt of total steps 

data.day <- list()
data.day$init.dosage <- 1
data.day$engagement <- TRUE
data.day$variation <- c(TRUE, FALSE, TRUE, FALSE, TRUE)

######## Still need to standarize it
data.day$sqrtsteps <- sqrt(input$totalStepsArray[7])
if(is.na(input$totalStepsArray[7])){
 
  if(all(is.na(input$totalStepsArray[-7]))){
    
    data.day$sqrtsteps <- NA
    
  }else{
    
    data.day$sqrtsteps <- sqrt(mean(input$totalStepsArray[-7], na.rm = TRUE))
    
  }
  
}




# ===== create the folder for the user and save the datasets ====== ####

paths <- paste("./data/", "user", input$userID, sep="")
dir.create(paths)

save(data.day, file = paste(paths, "/daily.Rdata", sep=""))
save(data.policy, file = paste(paths, "/policy.Rdata", sep=""))
save(data.history, file = paste(paths, "/history.Rdata", sep=""))
save(data.imputation, file = paste(paths, "/imputation.Rdata", sep=""))


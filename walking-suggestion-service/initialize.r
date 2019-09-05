rm(list = ls())
server = T
localtest = T
options(warn=-1)
#' ---
#' title:  Initialize the bandit algorithm in HS 2.0
#' author: Peng Liao
#' date:   2019-08
#' version: removing work + change default prob
#' ---
#'  

library(rjson)
library(fda, warn.conflicts=FALSE, quietly =T)


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
  
  if(localtest){
    
    args <- commandArgs(trailingOnly = TRUE)[1]
    input = fromJSON(file = args)
    
  }else{
    
   
  
    # input <- fromJSON(file = "./test/start_mash.json")
    # input <- fromJSON(file = "/Users/Peng/Dropbox/GitHubRepo/data/init.json")
    # input <- fromJSON(file = "/Users/Peng/Dropbox/GitHubRepo/data/10118/user10118_request history_init.json")
    # input <- fromJSON(file = "./test/start.json")
    input <- fromJSON(file = "/Users/Peng/Dropbox/GitHubRepo/test/start.json")
    
  }
  
  
  
}

# ===== create the folder for the user and save the datasets ====== ####

if("userID" %in% names(input)){
  
  if(dir.exists("./data") == FALSE){
  
  dir.create("./data")
  
  }
  

  paths <- paste("./data/", "user", input$userID, sep="")
  dir.create(paths, showWarnings = FALSE)
  dir.create(paste0(paths, "/request_history"), showWarnings = FALSE)

  request <- toJSON(input)
  write(request, file= paste(paths, "/request_history/init.json",sep="")) # save the request


}else{
  
  stop("User ID is missing")
  
}





  
tryCatch({
  
# ========  Format of Input Checking ========= ####
 
# processing input: convert NULL to NA and tranform into vector/matrix
for(k in 1:length(input)){
    
    if(grepl("Array", names(input)[k])){
      
      input[[k]] <- proc.array(input[[k]])
    }
    
    if(grepl("Matrix", names(input)[k])){
      
      # check if the length matches
      temp <- input[[k]]
      stopifnot(all(diff(unlist(lapply(temp, function(l) length(l[[1]])))) == 0))
      input[[k]] <- proc.matrix(input[[k]])
      
    }
    
}

# check if we have all the information 
stopifnot(all(c("userID", "date", "DelieverMatrix", "PriorAntiMatrix", 
                "totalStepsArray", "preStepsMatrix", "postStepsMatrix") %in% names(input)))

# check if we have identical days' data for step count data
len.all.step <- c(sapply(c("totalStepsArray"), function(x) length(input[[x]])), 
             sapply(c("preStepsMatrix", "postStepsMatrix"), function(x) nrow(input[[x]])))
stopifnot(all(diff(len.all.step) == 0))

# check if we have identical days' data for anti-and walking message
len.all.msg <- sapply(c("DelieverMatrix", "PriorAntiMatrix"), function(x) nrow(input[[x]]))
stopifnot(all(diff(len.all.msg) == 0))

# expect 7 days of using and installing the app
ndays <- as.numeric(len.all.step[1])
gap.days <- as.numeric(len.all.msg[1])
# stopifnot(ndays - 7 + 1 == gap.days)

# check if we have all five decision times for the step matrices and walking
ncol.all <- sapply(c("preStepsMatrix", "postStepsMatrix", "DelieverMatrix"), function(x) ncol(input[[x]]))
stopifnot(ncol.all == 5)

# check if we have 6 records for the priorAnti matrix
ncol.all.anti <- ncol(input$PriorAntiMatrix)
stopifnot(ncol.all.anti == 6)


# ========  Step Count Data Quality Checking =========####

data.quality <- list()

data.quality$presteps <- data.frame(-(ndays:1), input$preStepsMatrix)
colnames(data.quality$presteps) <- c("day", "ts1", "ts2", "ts3", "ts4", "ts5")


data.quality$poststeps <- data.frame(-(ndays:1), input$postStepsMatrix)
colnames(data.quality$poststeps) <- c("day", "ts1", "ts2", "ts3", "ts4", "ts5")

data.quality$totalsteps <- data.frame(-(ndays:1), input$totalStepsArray)
colnames(data.quality$totalsteps) <- c("day", "steps")


# # need to ensure we have, for each dt, any pre/post steps data)
# stopifnot(all(apply(input$preStepsMatrix, 2, function(x) sum(is.na(x))) < ndays))
# stopifnot(all(apply(input$postStepsMatrix, 2, function(x) sum(is.na(x))) < ndays))
# # need to ensure we have at least one obvervation for the total steps (so that we can impute)
# stopifnot(all(is.na(input$totalStepsArray)) == FALSE)



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
data.imputation$presteps <- list()
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
data.imputation$poststeps <- list()
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
# other.loc, 
# variation.indc

data.policy$mu.beta <- bandit.spec$mu2
data.policy$Sigma.beta <- bandit.spec$Sigma2
data.policy$pi_min <- bandit.spec$pi_min;
data.policy$pi_max <- bandit.spec$pi_max;
data.policy$gamma <- bandit.spec$gamma;
data.policy$eta.fn <- function(x) 0

# ===== Create a holder to save the entire (imputated and unstandarized) history ====== ####

var.names <- c("day", "decision.time", 
           "availability", "probability", "action", "reward",
           "dosage", "engagement", "other.location", "variation",
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
last.dsg <- 0
for(k in 1:gap.days){
  
  if(k == 1){
    
    last.dsg <- compute.dosage.day(last.dsg, 
                                   yes.fifthToEnd.anti = F, 
                                   yes.last.walk = F, 
                                   anti = input$PriorAntiMatrix[k, 1:5], 
                                   walk = input$DelieverMatrix[k, 1:4])  
    
  }else{
    
    
    last.dsg <- compute.dosage.day(last.dsg, 
                                   yes.fifthToEnd.anti = input$PriorAntiMatrix[k-1, 6], 
                                   yes.last.walk = input$DelieverMatrix[k-1, 5], 
                                   anti = input$PriorAntiMatrix[k, 1:5], 
                                   walk = input$DelieverMatrix[k, 1:4])  
    
  }
  
  
}
data.day$yesterdayLast.dosage <-  last.dsg # dosage at the fifth decision yesterday prior to treatment
data.day$fifthToEnd.anti <- isTRUE(input$PriorAntiMatrix[gap.days, 6]) # indicator of whether there is anti-sed msg sent between 5th to the end of yesterday
data.day$fifth.act <- isTRUE(input$DelieverMatrix[gap.days, 5]) # indicator of whether there is activity msg sent at fifth decision time yesterday

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
  
  if(is.na(Y1 >= Y0)){
    
    # no step count available for this decision time
    data.day$variation[k] <- FALSE
    
  }else{
   
    data.day$variation[k]<- (Y1 >= Y0) 
  }
   
  
}


# keep the names to ensure the format is same
data.day$var.names <- var.names

######## dataset for calculating dosage
data.dosage <- list()
data.dosage$init <- data.day$yesterdayLast.dosage
data.dosage$dataset <- data.frame(day = 1, timeslot = 1, 
                                  walk = isTRUE(input$DelieverMatrix[gap.days, 5]), 
                                  anti1 = isTRUE(input$PriorAntiMatrix[gap.days, 6]), anti2 = NA)
  

###### dataset to save all decision

data.decision <- data.frame(day = 0, timeslot = 0, action = 0, prob = 0, random.number = 0)
colnames(data.decision) <- c("day", "timeslot", "action", "prob", "random.number")
data.decision <- data.decision[data.decision$day > 0, ]



# save
save(data.decision, file = paste(paths, "/decision.Rdata", sep=""))
save(data.day, file = paste(paths, "/daily.Rdata", sep=""))
save(data.policy, file = paste(paths, "/policy.Rdata", sep=""))
save(data.history, file = paste(paths, "/history.Rdata", sep=""))
save(data.imputation, file = paste(paths, "/imputation.Rdata", sep=""))
save(data.dosage, file = paste(paths, "/dosage.Rdata", sep=""))
save(data.quality, file = paste(paths, "/quality.Rdata", sep=""))

# log file  
cat(paste("Initialization:", "Success"), file =  paste(paths, "/log", sep=""))

}, 
error = function(e) {
  
  if(file.exists(paste(paths, "/log", sep=""))){
    
    cat(paste("\nInitialization:", e), file =  paste(paths, "/log", sep=""), append = TRUE)
    
  }else{
    
    cat(paste("Initialization:", e), file =  paste(paths, "/log", sep=""))
    
  }
  stop("Error in the initialization occurs. Check the input")
  })


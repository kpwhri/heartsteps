rm(list = ls())
server = T
#' ---
#' title:  Nightly Udates in the bandit algorithm in HS 2.0
#' author: Peng Liao
#' date:   09.11, 2018
#' ---
#' 

library(rjson)
library(zoo, warn.conflicts=FALSE)
# ================ Recieve and Process the input ================ 

if(server){
  
  source("functions.R")
  load("bandit-spec.Rdata")
  args <- commandArgs(trailingOnly = TRUE)[1]
  input = fromJSON(args) # this is a list
  
  
}else{
  
  setwd("/Users/Peng/Dropbox/GitHubRepo/heartsteps/activity-suggestion/")
  source("functions.R")
  load("bandit-spec.Rdata")
  input <- fromJSON(file = "./test/test-run/update_2.json")
  
}

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

# check if we're dealing with the same day
stopifnot(data.day$study.day == input$studyDay)


# ================ update the history by adding the history in daily dataset ================ 

# might need to alter the action in 5th decision time 
action.index <- which(data.day$var.names == "action")
prob.index <- which(data.day$var.names == "probability")
last.time <- 5
last.action <- data.day$history[last.time, action.index]  
if(input$lastActivity != last.action){
  
  # if inconsistent, 
  # update the action and set the prob to NA to indicate this failure
  
  data.day$history[last.time, action.index] <- input$lastActivity;
  data.day$history[last.time, prob.index] <- NA; 
  
  
}

# filling in the states and rewards (require imputation and standardization)
day.history <- data.day$history
colnames(day.history) <- data.day$var.names
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

# prepost steps
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

# updatee the history 
data.history <- rbind(data.history, day.history)

# ================ Update the policy using the updated history ================ 
# A batch version update

# 1. Standarization (using the whole dataset)
#    (dosage, temperature, logpresteps, sqrtsteps) requires standarize

std.history <- data.history
std.history$dosage <- sapply(data.history$dosage, std.dosage)
std.history$temperature <- winsor(data.history$temperature, beta = 3, range = c(-15.6, 36.1))
std.history$logpresteps <- winsor.upp(data.history$logpresteps, beta = 3, range = c(log(0.5), 8.60))
std.history$sqrt.totalsteps <- winsor(data.history$sqrt.totalsteps, beta = 3, range = c(0, 209))

# modify the NA prob (due to inconsistency). 
# Note the action is whether it is delievered
index.set <- is.na(std.history$probability)
std.history$probability[index.set] <- ifelse(std.history$action[index.set] == 1, 1, 0)



# 2. Posterior for all parameters (Hierarchy, action-centered). 
train.dat <- subset(std.history,day > 0, select = -c(random.number, prepoststeps))

# missing can only be in reward; other will be imputed
stopifnot(sum(is.na(subset(train.dat, select = -reward))) == 0)

# available, completed cases
index.set <- (train.dat$availability * (is.na(train.dat$reward) == FALSE)) == 1

# posterior update if there is available, non-missing reward case
if(sum(index.set) > 0){
  
  # restrict to the available, non-missing reward
  # batch version of posterior calculation
  wm <- posterior.cal(train.dat[index.set, ], 
                      mu0 = bandit.spec$prior.mean, Sigma0 = bandit.spec$prior.var, sigma = bandit.spec$sigma,
                      int.names = c("dosage", "engagement", "work.location", "other.location", "variation"),
                      nonint.names = c("temperature", "logpresteps", "sqrt.totalsteps"))
  
  # update the policy
  data.policy$mu <- wm$mu
  data.policy$Sigma <- wm$Sigma
  
}

# 3. Margin update
if(bandit.spec$weight.vec[input$studyDay] > 0){
  
  # MDP update: transition, reward function
  
  ## txt effect
  
  train.dat <- subset(std.history, day > 0, select = -c(random.number, prepoststeps))
  
  # missing can only be in reward; other will be imputed
  stopifnot(sum(is.na(subset(train.dat, select = -reward))) == 0)
  
  # available, completed cases
  index.set <- (train.dat$availability * (is.na(train.dat$reward) == FALSE)) == 1
  
  # posterior update if there is available, non-missing reward case
  if(sum(index.set) > 0){
    
    # restrict to the available, non-missing reward
    # batch version of posterior calculation
    wm <- posterior.cal(train.dat[index.set, ], 
                        mu0 = bandit.spec$prior.mean.txt, Sigma0 = bandit.spec$prior.var.txt, sigma = bandit.spec$sigma.txt,
                        int.names = c("dosage"),
                        nonint.names = c("temperature", "logpresteps", "sqrt.totalsteps", "engagement", "work.location", "other.location", "variation"))
    
    theta.txt <- wm$mu
    
  }else{
    
    theta.txt <- tail(bandit.spec$prior.mean.txt, 2)
    
  }
  
  
  
  ### available baseline
  
  train.dat <- subset(std.history, select = c(availability, action, dosage, reward))
  
  # missing can only be in reward; other will be imputed
  stopifnot(sum(is.na(subset(train.dat, select = -reward))) == 0)
  
  # available, no treatment, completed cases
  index.set <- (train.dat$availability * (train.dat$action == 0) * (is.na(train.dat$reward) == FALSE)) == 1
  
  if(sum(index.set) > 0){
    
    
    wm = posterior.cal.mar (train.dat[index.set,], 
                            mu0 = bandit.spec$prior.mean.base, 
                            Sigma0 = bandit.spec$prior.var.base, 
                            sigma = bandit.spec$sigma.base.avail)
    
    theta.base = wm$mu
    
  }else{
    
    theta.base <- bandit.spec$prior.mean.base
  }
  
  ### unavailable baseline
  
  # UN-available (no treatment) completed cases
  stopifnot(all(train.dat$action[train.dat$availability == F] == 0))
  index.set <- ((train.dat$availability == F) * (is.na(train.dat$reward) == FALSE)) == 1
  
  if(sum(index.set) > 0){
    
    
    wm = posterior.cal.mar (train.dat[index.set,], 
                            mu0 = bandit.spec$prior.mean.unavail, 
                            Sigma0 = bandit.spec$prior.var.unavail, 
                            sigma = bandit.spec$sigma.unavail)
    
    theta.unavail = wm$mu
    
  }else{
    
    theta.unavail <- bandit.spec$prior.mean.unavail
  }
  
  ### estimated reward function
  feat.val = function(x) c(1, std.dosage(x))
  rwrd.est = function(x, i, a) c(ifelse(i==1, sum(feat.val(x) * theta.base) + a*sum(feat.val(x) * theta.txt), 
                                        sum(feat.val(x) * theta.unavail)))
  
  ## trainsition model for availability
  prob_avail <- mean(data.history$availability)
  
  # get the estimated value function
  Q.est = Cal.Q(rwrd.est, prob_avail, bandit.spec$gamma.mdp, bandit.spec$alpha0, bandit.spec$alpha1)
  
  # weighted average between initial
  weight <- bandit.spec$weight.vec[input$studyDay]
  Q.int <- bandit.spec$init.Q.mat
  Q.mat <- (1-weight) * Q.int + weight* Q.est
  
  # update the policy data
  data.policy$Q.mat <- Q.mat
  
}

# ================ Initialize the daily dataset used for next day ================

# dosage related
dosage.index <- which(data.day$var.names == "dosage")
action.index <- which(data.day$var.names == "action")

yesterdayLast.dosage <- data.day$history[5, dosage.index]  
fifth.act <- input$lastActivity
fifthToEnd.anti <- input$priorAnti 

# engagement (cannot be missing)
engagement.indc <- (input$appClick >= data.imputation$thres.appclick);
if(is.na(engagement.indc)){
  
  # app click data is missing
  avg.click <- mean(data.imputation$appclicks)
  engagement.indc <- (avg.click > data.imputation$thres.appclick)
  
}


# variation (cannot be missing) 
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

data.day$study.day <- input$studyDay + 1 # next day
data.day$engagement <- engagement.indc # engage indic used next day
data.day$variation <- variation.indc # variation measures for each decision next day
data.day$sqrtsteps <- sqrt.steps # sqrt of steps used next day
data.day$yesterdayLast.dosage <-  yesterdayLast.dosage # dosage at the fifth decision yesterday prior to treatment
data.day$fifthToEnd.anti <- fifthToEnd.anti # indicator of whether there is anti-sed msg sent between 5th to the end of yesterday
data.day$fifth.act <- fifth.act # indicator of whether there is activity msg sent at fifth decision time yesterday
data.day$var.names <- colnames(data.history)


# ================ Update the imputation dataset ================ 

# applicks last 7 days
data.imputation$appclicks <- append.array(data.imputation$appclicks, input$appClick)

# total steps last 7 days
data.imputation$totalsteps <- append.array(data.imputation$totalsteps, input$totalSteps)

# pre and post steps last 7 days per decision time
for(i in 1:5){
  
  data.imputation$presteps[[i]] <- append.array(data.imputation$presteps[[i]], input$preStepsArray[i])
  data.imputation$poststeps[[i]] <- append.array(data.imputation$poststeps[[i]], input$postStepsArray[i])
  
}



# ================ Save everything ================

save(data.day, file = paste(paths, "/daily.Rdata", sep=""))
save(data.policy, file = paste(paths, "/policy.Rdata", sep=""))
save(data.history, file = paste(paths, "/history.Rdata", sep=""))
save(data.imputation, file = paste(paths, "/imputation.Rdata", sep=""))


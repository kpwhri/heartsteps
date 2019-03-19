rm(list = ls())
server = F
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
  
  setwd("/Users/Peng/Dropbox/GitHubRepo/heartsteps/walking-suggestion-service/")
  source("functions.R")
  load("bandit-spec.Rdata")
  input <- fromJSON(file = "./test/update_2.json")
  
}


# ================ Asscess the day's data ================ 
paths <- paste("./data/", "user", input$userID, sep="")
load(paste(paths, "/imputation.Rdata", sep=""))
load(paste(paths, "/daily.Rdata", sep="")) 
load(paste(paths, "/history.Rdata", sep="")) 
load(paste(paths, "/policy.Rdata", sep="")) 

# ================= Condition checking ===================

condition1 = function(){
  
  # check if we have all the information 
  stopifnot(all(c("userID", "studyDay", "priorAnti", "lastActivity",
                  "temperatureArray", "appClick", "totalSteps", 
                  "preStepsArray", "postStepsArray", 
                  "availabilityArray",
                  "priorAntiArray",
                  "lastActivityArray",
                  "locationArray") %in% names(input)))
  
  
  # check if the length is 5 
  stopifnot(all(lapply(input[c("temperatureArray", "preStepsArray", "postStepsArray", 
                               "availabilityArray", "priorAntiArray", "lastActivityArray", "locationArray")], length)==5))
  
  # temperature should be imputed by HS server
  stopifnot(all(is.na(proc.array(input$temperatureArray)) == FALSE))
  
  # priorAnti, lastActivity, availability can only be true or false
  stopifnot(is.logical(input$priorAnti), is.logical(input$lastActivity), is.logical(input$availabilityArray), is.logical(input$lastActivityArray), is.logical(input$priorAntiArray))
  
  # nightly service needs to be called every day (dosage, bla bla bla)
  stopifnot(data.day$study.day == input$studyDay)
}

if(is.null(try(condition1(), silent = T))){
  
  # =============== Process input ===============
  
  # convert NULL to NA
  names.array <- c("temperatureArray", "preStepsArray", "postStepsArray", 
                   "availabilityArray", "priorAntiArray", "lastActivityArray", "locationArray")
  for(name in names.array){
    input[[name]] <- proc.array(input[[name]])
  }
  
  # total steps null to NA
  input$totalSteps <- ifelse(is.null(input$totalSteps), NA, input$totalSteps)
  
  
  # =============== Impute missed decision time and dosage ============= 
  
  # Expect to have 5 rows, i.e. the decision services are called 5 times
  skip.indicator <- ifelse(is.null(data.day$history), TRUE, nrow(data.day$history) < 5)
  if(skip.indicator){
    
    miss.dt <- which((1:5 %in% data.day$history[, 2]) == F)
    
    # write the error file
    load(paste(paths, "/error.Rdata", sep="")) 
    err.file <- paste("Decision times skipped during the day: ", paste(miss.dt, collapse = ", " ))
    error.log <- rbind(error.log, c(input$studyDay, "Nightly Update", err.file))
    save(error.log, file = paste(paths, "/error.Rdata", sep="")) 
    
    
    
    # fill in the missing decision time and re-order 
    for(kk in miss.dt){
      
      # other interactions 
      current.dosage <- NA
      if(input$locationArray[kk] %in% c(0, 1, 2)){
        
        work.loc <- input$locationArray[kk] == 1;
        other.loc <- input$locationArray[kk] == 0;
        
      }else{
        
        work.loc <- other.loc <- NA
        
      }
      
      engagement.indc <- data.day$engagement;
      variation.indc <- data.day$variation[kk]
      
      interaction.terms <- c(current.dosage, 
                             engagement.indc, 
                             work.loc, 
                             other.loc, 
                             variation.indc)
      prob <- 0
      action <- 0
      random.num <- NA
      
      # add the current decision time
      # Same Format as in the initialization
      data.day$history <- rbind(data.day$history, 
                                c(input$studyDay, 
                                  kk, 
                                  input$availabilityArray[kk], 
                                  prob, 
                                  action, 
                                  NA, 
                                  interaction.terms, 
                                  NA, 
                                  NA, 
                                  data.day$sqrtsteps,
                                  NA,
                                  NA,
                                  NA,
                                  random.num)) 
      
    }
    data.day$history <- data.day$history[order(data.day$history[, 2]),]
    
    # dosage redefined
    dosage.recal <- c()
    for(kk in 1:5){
      
      
      # obtain the last dosage and decide if to increase
      if(kk == 1){
        
        # retrive the dosage at the fifth time yesterday
        last.dosage <- data.day$yesterdayLast.dosage
        
        # whether recieve any msg between the fifth decision time to the first decision time 
        # that is, any activitity sent at the yesterday's fifth and any anti sent between fifth to first. 
        # we infer the second one by two inputs
        receive.indc <- any(input$priorAntiArray[1], data.day$fifthToEnd.anti, data.day$fifth.act)
        
        
      }else{
        
        # retrive the dosage at the last decision time
        # dosage.index <- which(data.day$var.names == "dosage")
        # last.time <- input$decisionTime - 1
        # last.dosage <- data.day$history[last.time, dosage.index]  
        
        last.dosage <- dosage.recal[kk-1]
        # whether recieve any msg between last and current decision time
        receive.indc <- any(input$priorAntiArray[kk], input$lastActivityArray[kk])
        
      }
      
      # update the dosage
      dosage.recal <- c(dosage.recal, update.dosage(last.dosage, receive.indc))
      
      
    }
    
    dosage.index <- which(data.day$var.names == "dosage")
    data.day$history[, dosage.index] <- dosage.recal
    
    
    
  }
  
  
  
  
  # ================ update the history by adding the (imputed) daily dataset  ================ 
  
  # deliever indicator
  data.day$deliever <- c()
  for(kk in 1:4){
    
    data.day$deliever <- c(data.day$deliever, input$lastActivityArray[kk+1])
  }
  data.day$deliever <- as.numeric(c(data.day$deliever, input$lastActivity))
  
  # filling in the states and rewards (require imputation and standardization)
  day.history <- data.day$history
  colnames(day.history) <- data.day$var.names
  day.history <- data.frame(day.history)
  
  # deliever indiactor
  day.history$deliever <- data.day$deliever
  
  # today's app click (impute if missing)
  
  if(is.na(input$appClick)){
    
    avg.click <- mean(data.imputation$appclicks)
    day.history$appclick <- avg.click
    
  }else{
    
    day.history$appclick <- input$appClick
    
  }
  
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
  
  # update the history 
  data.history <- rbind(data.history, day.history)
  
  # ================ Update the policy using the updated history ================ 
  
  # 1. Create the training dataset: winsoration, standarization (using the whole dataset)
  #    (dosage, temperature, logpresteps, sqrtsteps) requires standarize. And adjust the mismatch
  
  
  train.dat <- data.history
  train.dat$dosage <- sapply(data.history$dosage, std.dosage)
  train.dat$temperature <- winsor(data.history$temperature, beta = 3, range = c(-15.6, 36.1))
  train.dat$logpresteps <- winsor.upp(data.history$logpresteps, beta = 3, range = c(log(0.5), 8.60), min.val = log(0.5))
  daily.steps <- data.history$sqrt.totalsteps[data.history$decision.time==1]
  train.dat$sqrt.totalsteps <- rep(winsor(daily.steps, beta = 3, range = c(0, 209)), each = 5)
  
  
  
  # remove the prestudy data
  train.dat <- subset(train.dat, day > 0)
  
  # modify the mistmach case
  index.set <- (train.dat$deliever != train.dat$action)
  train.dat$action <- train.dat$deliever
  train.dat$probability[index.set] <- ifelse(train.dat$action[index.set] == 1, 1, 0)
  
  # select the needed column for the analysis 
  train.dat <- subset(train.dat, select = -c(random.number, prepoststeps, appclick, deliever))
  
  # remmove missing reward or NA location
  train.dat <- train.dat[complete.cases(train.dat), ]
  
  
  # 2. Posterior for all parameters (Hierarchy, action-centered). 
  
  # available cases
  index.set <- (train.dat$availability == 1)
  
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
    
    # # MDP update: transition, reward function
    # 
    # ## txt effect
    # 
    # 
    # # missing can only be in reward; other will be imputed
    # stopifnot(sum(is.na(subset(train.dat, select = -reward))) == 0)
    # 
    # # available, completed cases
    # index.set <- (train.dat$availability * (is.na(train.dat$reward) == FALSE)) == 1
    # 
    # # posterior update if there is available, non-missing reward case
    # if(sum(index.set) > 0){
    #   
    #   # restrict to the available, non-missing reward
    #   # batch version of posterior calculation
    #   wm <- posterior.cal(train.dat[index.set, ], 
    #                       mu0 = bandit.spec$prior.mean.txt, Sigma0 = bandit.spec$prior.var.txt, sigma = bandit.spec$sigma.txt,
    #                       int.names = c("dosage"),
    #                       nonint.names = c("temperature", "logpresteps", "sqrt.totalsteps", "engagement", "work.location", "other.location", "variation"))
    #   
    #   theta.txt <- wm$mu
    #   
    # }else{
    #   
    #   theta.txt <- tail(bandit.spec$prior.mean.txt, 2)
    #   
    # }
    # 
    # 
    # 
    # ### available baseline
    # train.dat <- subset(std.history, day > 0, select = c(availability, action, dosage, reward))
    # 
    # # missing can only be in reward; other will be imputed
    # stopifnot(sum(is.na(subset(train.dat, select = -reward))) == 0)
    # 
    # # available, no treatment, completed cases
    # index.set <- (train.dat$availability * (train.dat$action == 0) * (is.na(train.dat$reward) == FALSE)) == 1
    # 
    # if(sum(index.set) > 0){
    #   
    #   
    #   wm = posterior.cal.mar (train.dat[index.set,], 
    #                           mu0 = bandit.spec$prior.mean.base, 
    #                           Sigma0 = bandit.spec$prior.var.base, 
    #                           sigma = bandit.spec$sigma.base.avail)
    #   
    #   theta.base = wm$mu
    #   
    # }else{
    #   
    #   theta.base <- bandit.spec$prior.mean.base
    # }
    # 
    # ### unavailable baseline
    # 
    # # UN-available (no treatment) completed cases
    # stopifnot(all(train.dat$action[train.dat$availability == F] == 0))
    # index.set <- ((train.dat$availability == F) * (is.na(train.dat$reward) == FALSE)) == 1
    # 
    # if(sum(index.set) > 0){
    #   
    #   
    #   wm = posterior.cal.mar (train.dat[index.set,], 
    #                           mu0 = bandit.spec$prior.mean.unavail, 
    #                           Sigma0 = bandit.spec$prior.var.unavail, 
    #                           sigma = bandit.spec$sigma.unavail)
    #   
    #   theta.unavail = wm$mu
    #   
    # }else{
    #   
    #   theta.unavail <- bandit.spec$prior.mean.unavail
    # }
    # 
    # ### estimated reward function
    # feat.val = function(x) c(1, std.dosage(x))
    # rwrd.est = function(x, i, a) c(ifelse(i==1, sum(feat.val(x) * theta.base) + a*sum(feat.val(x) * theta.txt), 
    #                                       sum(feat.val(x) * theta.unavail)))
    # 
    # ## trainsition model for availability
    # prob_avail <- mean(data.history$availability, na.rm = TRUE)
    # 
    # # get the estimated value function
    # Q.est = Cal.Q(rwrd.est, prob_avail, bandit.spec$gamma.mdp, bandit.spec$alpha0, bandit.spec$alpha1)
    # 
    # # weighted average between initial
    # weight <- bandit.spec$weight.vec[input$studyDay]
    # Q.int <- bandit.spec$init.Q.mat
    # Q.mat <- (1-weight) * Q.int + weight* Q.est
    # 
    # # update the policy data
    # data.policy$Q.mat <- Q.mat
    
  }
  
  # ================ Initialize the daily dataset used for next day ================
  
  # dosage related
  dosage.index <- which(data.day$var.names == "dosage")
  action.index <- which(data.day$var.names == "action")
  
  yesterdayLast.dosage <- data.day$history[5, dosage.index]  
  fifth.act <- input$lastActivity
  fifthToEnd.anti <- input$priorAnti 
  
  # engagement
  today.click <- day.history$appclick[1];
  daily.click <- subset(data.history, day > 0 & decision.time == 1)$appclick;
  threshold <- as.numeric(quantile(daily.click, probs = 0.4))
  engagement.indc <- (today.click >= threshold)
  
  # variation
  variation.indc <- rep(NA, 5)
  for(k in 1:5){
    
    
    temp <- data.history$prepoststeps[data.history$decision.time == k]
    temp <- rollapply(temp, width=7, FUN=sd, align='right', fill = NA) # rolling sd over past 7 days (including today)
    temp <- tail(temp, 1+input$studyDay) # the first one corresponds to the sd calculated in the first week with no app
    
    Y1 <- temp[length(temp)] # today's sd
    Y0 <- median(temp[1:(length(temp)-1)]) # median of the past
    variation.indc[k] <- (Y1 >= Y0)
    
  }
  
  # sqrt steps 
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
  data.imputation$appclicks <- append.array(data.imputation$appclicks, 
                                            input$appClick)
  
  # total steps last 7 days
  data.imputation$totalsteps <- append.array(data.imputation$totalsteps, 
                                             input$totalSteps)
  
  # pre and post steps last 7 days per decision time
  for(i in 1:5){
    
    data.imputation$presteps[[i]] <- append.array(data.imputation$presteps[[i]], 
                                                  input$preStepsArray[i])
    data.imputation$poststeps[[i]] <- append.array(data.imputation$poststeps[[i]], 
                                                   input$postStepsArray[i])
    
  }
  
  
  
  # ================ Save everything ================
  
  save(data.day, file = paste(paths, "/daily.Rdata", sep=""))
  save(data.policy, file = paste(paths, "/policy.Rdata", sep=""))
  save(data.history, file = paste(paths, "/history.Rdata", sep=""))
  save(data.imputation, file = paste(paths, "/imputation.Rdata", sep=""))
  
  
  
}else{
  
  # error log 
  load(paste(paths, "/error.Rdata", sep="")) 
  err.file <- "Previous nightly updates are skipped or something wrong with the input"
  error.log <- rbind(error.log, c(input$studyDay, "Nightly Update", err.file))
  save(error.log, file = paste(paths, "/error.Rdata", sep="")) 
  
  stop("Previous nightly updates are skipped or something wrong with the input")
}



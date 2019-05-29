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
  
  setwd("/Users/Peng/Dropbox/GitHubRepo/heartsteps/walking-suggestion-service/")
  source("functions.R")
  load("bandit-spec.Rdata")
  # input <- fromJSON(file = "./test/update_3.json")
  input <- fromJSON(file = "./test/nick/nightly_2.json")
  
}

# save the input


# ================ Asscess the day's data ================ 

tryCatch(expr = {

  stopifnot("userID" %in% names(input))  
  paths <- paste("./data/", "user", input$userID, sep="")

  request <- toJSON(input)
  write(request, file = paste(paths, "/request history/", "nightly_", input$studyDay, ".json",sep="")) # save the request

  load(paste(paths, "/imputation.Rdata", sep=""))
  load(paste(paths, "/daily.Rdata", sep="")) 
  load(paste(paths, "/history.Rdata", sep="")) 
  load(paste(paths, "/policy.Rdata", sep="")) 
  load(paste(paths, "/dosage.Rdata", sep="")) 
  load(paste(paths, "/decision.Rdata", sep="")) 

  }, error = function(err) {
  
    stop("Initiliazation has not done for the user or user ID is missing")
  
})



# ================= Condition checking ===================

check  = tryCatch(expr = {
  


  stopifnot(all(c("userID", "studyDay", "lastActivity",
                  "temperatureArray", "appClick", "totalSteps", 
                  "preStepsArray", "postStepsArray", 
                  "availabilityArray",
                  "priorAntiArray",
                  "lastActivityArray",
                  "locationArray") %in% names(input)));
  
  # check the size 
  stopifnot(all(lapply(input[c("temperatureArray", "preStepsArray", "postStepsArray", 
                               "availabilityArray", "lastActivityArray", "locationArray")], length)==5))
  stopifnot(length(input["priorAntiArray"]$priorAntiArray) == 6);
  
  # temperature should be imputed by HS server
  stopifnot(all(is.na(proc.array(input$temperatureArray)) == FALSE))
  
  # priorAntiArray, lastActivity, availability can only be true or false
  stopifnot(all(c(is.na(input$lastActivity), 
                  is.na(input$availabilityArray), 
                  is.na(input$lastActivityArray), 
                  is.na(input$priorAntiArray)) == F))
  
  stopifnot(is.logical(input$lastActivity), 
            is.logical(input$availabilityArray), 
            is.logical(input$lastActivityArray), 
            is.logical(input$priorAntiArray))
  
  # location can only be (0, 1, 2)
  stopifnot(all(input$locationArray %in% c(0, 1, 2)))
  
  
  
}, error = function(err){
  
  cat(paste("\nNightly:", "Day =", input$studyDay, 
            "update rejected", "Error:", err$message), file =  paste(paths, "/log", sep=""), append = TRUE)
  
  stop("The inputs to the nightly update has error")
  
  
  
})

## impute dosage dataset using today's input
if(is.null(check)){
  
  
  tmp.data <- data.dosage$dataset
  
  # check if 1st decision time skipped
  if(is.na(tmp.data$anti2[tmp.data$day == input$studyDay & tmp.data$timeslot == 1])){
    
    tmp.data$anti2[tmp.data$day == input$studyDay & tmp.data$timeslot == 1] <- input$priorAntiArray[1]
  }
  
  # check if today's 2-5thdecision time being skipped
  if(all((2:5 %in% tmp.data$timeslot[tmp.data$day == input$studyDay])) == F){
    
     temp <- data.frame(day = rep(input$studyDay, 4), 
                     timeslot = 2:5, 
                     walk = input$lastActivityArray[2:5],
                     anti1 = input$priorAntiArray[2:5],
                     anti2 = rep(0, 4))
     
    index <- which(2:5 %in% tmp.data$timeslot[tmp.data$day == input$studyDay] == F)
    
     data.dosage$dataset <- rbind(data.dosage$dataset, temp[index,])
     data.dosage$dataset <- data.dosage$dataset[order(data.dosage$dataset$day, data.dosage$dataset$timeslot), ]
     
  }
  
  
  # =============== Process input ===============
  
  # convert NULL to NA
  names.array <- c("temperatureArray", "preStepsArray", "postStepsArray", 
                   "availabilityArray", "priorAntiArray", "lastActivityArray", "locationArray")
  for(name in names.array){
    input[[name]] <- proc.array(input[[name]])
  }
  
  # total steps null to NA
  input$totalSteps <- ifelse(is.null(input$totalSteps), NA, input$totalSteps)
  
  
  # =============== Create the day history ============= 
  
  # imputed dosage dataset
  temp <- data.dosage$dataset;
  for(d in 1:input$studyDay){
    
    for(k in 1:5){
      
      if(k == 1){
        
        # previous n.u occurs, 1st decision time skipped and n.p does not occur ever
        if(is.na(temp$anti2[temp$day == d & temp$timeslot == 1])){
          
          temp$anti2[temp$day == d & temp$timeslot == 1] <- 0 # need to change
          
        }
        
      }
      if(nrow(subset(temp, day == d & timeslot == k)) == 0) {
        
        # if the n.p does not occur and decision time is not reached
        
        temp <- rbind(temp, c(d, k, 0,  0,  0)) # need to change
      }
    }

  }
  
  temp <- temp[order(temp$day, temp$timeslot), ]
  event <- (temp$walk + temp$anti1 + temp$anti2 > 1);
  
  # calculate the dosage
  tmp.dat <- data.frame(day = -1, timeslot = 5, dosage = data.dosage$init)
  x <- data.dosage$init; 
  for(j in 1:length(event)) {
    
    x <- update.dosage(x, increase = event[j])
    tmp.dat <- rbind(tmp.dat, c(temp$day[j], temp$timeslot[j], x))
  }
  
  
    
  
        
  
    # day history (need to change variantion or app later)
    day.history <- NULL
    for(kk in 1:5){
      
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
      if(is.null(data.decision) == TRUE){
        
        # since the initialization, nothing occurs 
        
        prob <- 0
        action <- 0
        random.num <- NA
      
        
      }else{
        
        if(nrow(subset(data.decision, day == input$studyDay & timeslot == kk)) == 0){
          
          # decision does not occur
          prob <- 0
          action <- 0
          random.num <- NA
          
        }else{
          
          prob <- as.numeric(subset(data.decision, day == input$studyDay & timeslot == kk)$prob)
          action <- as.numeric(subset(data.decision, day == input$studyDay & timeslot == kk)$action)
          random.num <- as.numeric(subset(data.decision, day == input$studyDay & timeslot == kk)$random.number)
          
          
        }
        
      }
      
      
      
      # add the current decision time
      # Same Format as in the initialization
      day.history <- rbind(day.history,
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
    day.history <- data.frame(day.history[order(day.history[, 2]),])
    colnames(day.history) <- data.day$var.names
    
    # dosage redefined
    dosage.index <- which(data.day$var.names == "dosage")
    day.history[, dosage.index] <- subset(tmp.dat, day == input$studyDay)$dosage
    
    
    
  
  
  
  
  # ================ update the history by adding the (imputed) daily dataset  ================ 
  
  # deliever indicator
  deliever <- c()
  for(kk in 1:4){
    
    deliever <- c(deliever, input$lastActivityArray[kk+1])
    
  }
  deliever <- as.numeric(c(deliever, input$lastActivity))
  
  # filling in the states and rewards (require imputation and standardization)
  
  # deliever indiactor
  day.history$deliever <- deliever
  
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
  
  
  # save training data
  #train.dat$user <- input$userID
  #save(train.dat, file = paste(paths, "/train.Rdata", sep=""))
  
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
  # data.day$yesterdayLast.dosage <-  yesterdayLast.dosage # dosage at the fifth decision yesterday prior to treatment
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
  
  
  # update the dosage dataset (add the instance for the first decision time next day)
  
  data.dosage$dataset <- rbind(data.dosage$dataset, 
                               c(input$studyDay+1, 1, walk = input$lastActivity, anti1 = input$priorAntiArray[6], NA))
 
  # ================ Save everything ================
  
  save(data.dosage, file = paste(paths, "/dosage.Rdata", sep=""))
  save(data.day, file = paste(paths, "/daily.Rdata", sep=""))
  save(data.policy, file = paste(paths, "/policy.Rdata", sep=""))
  save(data.history, file = paste(paths, "/history.Rdata", sep=""))
  save(data.imputation, file = paste(paths, "/imputation.Rdata", sep=""))
  
  
  cat(paste("\nNightly:", "Day =", input$studyDay, "Success"), file =  paste(paths, "/log", sep=""), append = TRUE) 
}
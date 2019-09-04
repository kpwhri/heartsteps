rm(list = ls())
server = T
localtest = F
options(warn=-1)
#' ---
#' title:  Nightly Udates in the bandit algorithm in HS 2.0
#' author: Peng Liao
#' date:   2019-08
#' version: removing work + change default prob
#' ---
#' 

library(rjson)
library(methods)
library(zoo, warn.conflicts=FALSE, quietly = T)
library(fda, warn.conflicts=FALSE, quietly =T)

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
  
  if(localtest){
    
    args <- commandArgs(trailingOnly = TRUE)[1]
    input = fromJSON(file = args)
    
  }else{
    
    
    # input <- fromJSON(file = "/Users/Peng/Desktop/walking/user10006/request_history/nightly_1.json")
    # input <- fromJSON(file = "/Users/Peng/Dropbox/GitHubRepo/test/update_7.json")
    # input <- fromJSON(file = "/Users/Peng/Dropbox/GitHubRepo/data/nickreid/nightly_6.json")
    # input <- fromJSON(file = "/Users/Peng/Dropbox/GitHubRepo/data/10118/user10118_request history_nightly_1.json")
    # input <- fromJSON(file = "/Users/Peng/Dropbox/GitHubRepo/data/nightly_3.json")
    # input <- fromJSON(file = "/Users/Peng/Dropbox/GitHubRepo/data/pedja/usertest-pedja_request_history_nightly_10.json")
    input <- fromJSON(file = "/Users/Peng/Dropbox/GitHubRepo/heartsteps/walking-suggestion-service/data/user10110/request_history/nightly_34.json")
    
    
  }
  
}


# ================ Asscess the day's data ================ 

tryCatch(expr = {

  stopifnot("userID" %in% names(input))  
  paths <- paste("./data/", "user", input$userID, sep="")

  request <- toJSON(input)
  write(request, file = paste(paths, "/request_history/", "nightly_", input$studyDay, ".json",sep="")) # save the request

  load(paste(paths, "/imputation.Rdata", sep=""))
  load(paste(paths, "/daily.Rdata", sep="")) 
  load(paste(paths, "/history.Rdata", sep="")) 
  load(paste(paths, "/policy.Rdata", sep="")) 
  load(paste(paths, "/dosage.Rdata", sep="")) 
  load(paste(paths, "/decision.Rdata", sep="")) 
  load(paste(paths, "/quality.Rdata", sep="")) 

  }, 
  error = function(err) {
  
    stop("Initiliazation has not done for the user or user ID is missing")
  
})



# ================= Condition checking ===================

check  = tryCatch(expr = {
  


  stopifnot(all(c("userID", "studyDay", "lastActivity",
                  "temperatureArray", "appClick", "totalSteps", 
                  "preStepsArray", "postStepsArray", 
                  "availabilityArray",
                  "priorAntiArray",
                  "lastActivityArray", "actionArray", "probArray",
                  "locationArray") %in% names(input)));
  
  # check the size 
  stopifnot(all(lapply(input[c("temperatureArray", "preStepsArray", "postStepsArray", "actionArray", "probArray",
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
  
  
  
}, 
                  error = function(err){
  
  cat(paste("\nNightly:", "Day =", input$studyDay, 
            "update rejected", "Error:", err$message), file =  paste(paths, "/log", sep=""), append = TRUE)
  
  stop("The inputs to the nightly update has error")
  
  
  
})

## impute dosage dataset using today's input
if(is.null(check)){
  
  # =============== Process input ===============
  
  # convert NULL to NA
  names.array <- c("temperatureArray", "preStepsArray", "postStepsArray", 
                   "availabilityArray", "priorAntiArray", "lastActivityArray", "locationArray",
                   "actionArray", "probArray")
  
  for(name in names.array){
    input[[name]] <- proc.array(input[[name]])
  }
  
  # total steps null to NA
  input$totalSteps <- ifelse(is.null(input$totalSteps), NA, input$totalSteps)
  
  

  # =============== Impute dosage for the missing decision times for today ===============
  
  # check if 1st decision time skipped
  if(nrow(subset(data.dosage$dataset, day == input$studyDay & timeslot == 1)) == 0){
    
    # skipped and previous nightly update does not occur
    data.dosage$dataset <- rbind(data.dosage$dataset, c(input$studyDay, 1, NA, NA, input$priorAntiArray[1]))
    
  }else{
    
    if(is.na(data.dosage$dataset$anti2[data.dosage$dataset$day == input$studyDay & data.dosage$dataset$timeslot == 1])){
      
      # if skipped, then fill in the anti2
      data.dosage$dataset$anti2[data.dosage$dataset$day == input$studyDay & data.dosage$dataset$timeslot == 1] <- input$priorAntiArray[1]
      
    }
    
  }
  # check if there is any 2-5thdecision time being skipped today
  if(all((2:5 %in% data.dosage$dataset$timeslot[data.dosage$dataset$day == input$studyDay])) == F){
    
     temp <- data.frame(day = rep(input$studyDay, 4), 
                     timeslot = 2:5, 
                     walk = input$lastActivityArray[2:5],
                     anti1 = input$priorAntiArray[2:5],
                     anti2 = rep(0, 4))
     
    index <- which(2:5 %in% data.dosage$dataset$timeslot[data.dosage$dataset$day == input$studyDay] == F)
    
     data.dosage$dataset <- rbind(data.dosage$dataset, temp[index,])
     
     
  }
  
  data.dosage$dataset <- data.dosage$dataset[order(data.dosage$dataset$day, data.dosage$dataset$timeslot), ]
  
  # =============== Add the decision time for reinitialization ===============
  if(nrow(subset(data.decision, day == input$studyDay)) < 5){
    
    index <- c(1:5)[!(1:5 %in% subset(data.decision, day == input$studyDay)$timeslot)]
    
    for(k in index){
      
      if(!is.na(input$probArray[k]) & !is.na(input$actionArray[k])){
        
        data.decision <- rbind(data.decision, c(input$studyDay, k, input$actionArray[k], input$probArray[k], NA))
        
      }
    }
    
    colnames(data.decision) <- c("day", "timeslot", "action", "prob", "random.number")
    data.decision <- data.decision[order(data.decision$day, data.decision$timeslot), ]
    
  }
  
  
  
 
  
  
  # =============== Remove work location (once) =============
  data.day$var.names <- data.day$var.names[!(data.day$var.names %in% "work.location")]
  data.history <- data.history[!(colnames(data.history)%in% "work.location")]
  
  # =============== Create the day history ============= 
  
  # imputed dosage dataset for all days
  temp <- data.dosage$dataset
  for(d in 1:input$studyDay){
    
    for(k in 1:5){
      
      if(nrow(subset(temp, day == d & timeslot == k)) == 0){
        
        temp <- rbind(temp, c(d, k, NA, NA, 0)) # anti2 is always 2 for 2-5 decision time
        
      }
      
    }
  }
  temp <- temp[order(temp$day, temp$timeslot), ]
  temp[is.na(temp)] <- 0 # NA means nothing we can do
  
  # calculate the dosage
  event <- (temp$walk + temp$anti1 + temp$anti2 > 0);
  dosage.mat <- data.frame(day = -1, timeslot = 5, dosage = data.dosage$init)
  x <- data.dosage$init;
  for(j in 1:length(event)) {

    x <- update.dosage(x, increase = event[j])
    dosage.mat <- rbind(dosage.mat, c(temp$day[j], temp$timeslot[j], x))
  }
  
  
    
    # day history (need to change variantion or app later)
    day.history <- NULL
    for(kk in 1:5){
      
      # other interactions 
      current.dosage <- dosage.mat$dosage[which(dosage.mat$day == input$studyDay & dosage.mat$timeslot == kk)]
      other.loc <- input$locationArray[kk] == 0;
      
      engagement.indc <- data.day$engagement;
      variation.indc <- data.day$variation[kk]
      
      interaction.terms <- c(current.dosage, 
                             engagement.indc, 
                             other.loc, 
                             variation.indc)
      
      # get the probability and action
      
      if(is.null(data.decision) == TRUE){
        
        # since the initialization, nothing occurs 
        
        prob <- 0
        action <- 0
        random.num <- NA
      
        
      }else{
        
        if(nrow(subset(data.decision, day == input$studyDay & timeslot == kk)) == 0){
          
          # decision does not occur 
          # NOTE: this step never occurs if prob and action are set to non-null for the imputed decision time
          
          prob <- 0
          action <- 0
          random.num <- NA
          
        }else{
          
          if(nrow(subset(data.decision, day == input$studyDay & timeslot == kk)) == 1){
            
            # only one request
            
            prob <- as.numeric(subset(data.decision, day == input$studyDay & timeslot == kk)$prob)
            action <- as.numeric(subset(data.decision, day == input$studyDay & timeslot == kk)$action)
            random.num <- as.numeric(subset(data.decision, day == input$studyDay & timeslot == kk)$random.number)
          
          }else{
            
            
            # multiple requests (take the last one for right now -- this should not happen)
            
            ind <- nrow(subset(data.decision, day == input$studyDay & timeslot == kk))
            prob <- as.numeric(subset(data.decision, day == input$studyDay & timeslot == kk)$prob)[ind]
            action <- as.numeric(subset(data.decision, day == input$studyDay & timeslot == kk)$action)[ind]
            random.num <- as.numeric(subset(data.decision, day == input$studyDay & timeslot == kk)$random.number)[ind]
          
          
          
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
    }
    day.history <- data.frame(day.history[order(day.history[, 2]),])
    colnames(day.history) <- data.day$var.names
    
    
    
  
  
  
  
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
        
      }else{
        
        # no data available for this time slot at all
        day.history$logpresteps[k] <- log(0.5)
        
        
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
        
      }else{
        
        # no data available for this time slot at all
        poststep.temp[k] <- 0
        
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
        
      }else{
        
        # no data available for this time slot at all
        
        prestep.temp[k] <- 0
        
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
  train.dat$temperature <- winsor(data.history$temperature, beta = 3, range = c(-15.6, 36.1))
  train.dat$logpresteps <- winsor.upp(data.history$logpresteps, beta = 3, range = c(log(0.5), 8.60), min.val = log(0.5))
  daily.steps <- data.history$sqrt.totalsteps[data.history$decision.time==1] # yesterday's step, starting from the first day of using Fibit
  train.dat$sqrt.totalsteps <- rep(winsor(daily.steps, beta = 3, range = c(0, 209)), each = 5)
  
  # remove the prestudy data
  train.dat <- subset(train.dat, day > 0)
  
  # modify the mistmach case
  index.set <- (train.dat$deliever != train.dat$action)
  train.dat$action <- train.dat$deliever
  train.dat$probability[index.set] <- ifelse(train.dat$action[index.set] == 1, 1, 0)
  
  # select the needed column for the analysis 
  train.dat <- subset(train.dat, select = -c(random.number, prepoststeps, appclick, deliever))
  
  # remmove missing reward
  train.dat <- train.dat[complete.cases(train.dat), ]
  
  
  
  # 2. Posterior for all parameters (Hierarchy, action-centered). 
  wm.txt <- txt.eff.update(train.dat, 
                      mu1 = bandit.spec$mu1, Sigma1 = bandit.spec$Sigma1,
                      mu2 = bandit.spec$mu2, Sigma2 = bandit.spec$Sigma2, sigma = bandit.spec$sigma,
                      int.names = c("dosage", "engagement", "other.location", "variation"),
                      nonint.names = c("temperature", "logpresteps", "sqrt.totalsteps"))
  data.policy$mu.beta <- wm.txt$mean
  data.policy$Sigma.beta <- wm.txt$var
  
  # 3. Margin update
  if(bandit.spec$weight.est > 0){
    
    alpha0 <- unavail.update(train.dat, mu0 = bandit.spec$mu0, Sigma0 = bandit.spec$Sigma0, sigma = bandit.spec$sigma, 
                             int.names = c("dosage", "engagement", "other.location", "variation"),
                             nonint.names = c("temperature", "logpresteps", "sqrt.totalsteps"))$mean
    
    alpha1 <- main.eff.update(train.dat, mu1 = bandit.spec$mu1, Sigma1 = bandit.spec$Sigma1, sigma = bandit.spec$sigma, 
                    int.names = c("dosage", "engagement", "other.location", "variation"),
                    nonint.names = c("temperature", "logpresteps", "sqrt.totalsteps"))$mean
    
    alpha2 <- wm.txt$mean
    
    data.policy$eta.fn <- eta.update (train.dat, alpha0, alpha1, alpha2, 
                            int.names = c("dosage", "engagement", "other.location", "variation"),
                            nonint.names = c("temperature", "logpresteps", "sqrt.totalsteps"))
    
    
     
  }
  
  # ================ Initialize the daily dataset used for next day ================
  

  # engagement
  today.click <- day.history$appclick[1];
  daily.click <- subset(data.history, day > 0 & decision.time == 1)$appclick;
  threshold <- as.numeric(quantile(daily.click, probs = 0.4))
  engagement.indc <- (today.click > threshold)
  
  # variation
  variation.indc <- rep(NA, 5)
  for(k in 1:5){
    
    
    temp <- data.history$prepoststeps[data.history$decision.time == k]
    temp <- rollapply(temp, width=7, FUN=sd, align='right', fill = NA) # rolling sd over past 7 days (including today)
    temp <- temp[is.na(temp) == F] # missing days and the first 7 days 
    
    
    Y1 <- temp[length(temp)] # today's sd
    Y0 <- median(temp)
    variation.indc[k] <- (Y1 > Y0)
    
    
    
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
  # if that instance has not created
  if(nrow(subset(data.dosage$dataset, day == input$studyDay + 1 & timeslot == 1)) == 0){
    
    data.dosage$dataset <- rbind(data.dosage$dataset, 
                                 c(input$studyDay+1, 1, walk = input$lastActivity, anti1 = input$priorAntiArray[6], NA))
    
  }else{
    
    data.dosage$dataset$walk[data.dosage$dataset$day == (input$studyDay+1) & data.dosage$dataset$timeslot == 1] <- input$lastActivity
    data.dosage$dataset$anti1[data.dosage$dataset$day == (input$studyDay+1) & data.dosage$dataset$timeslot == 1] <- input$priorAntiArray[6]
    
  }
  
  
  # update the data quality dataset
  data.quality$presteps <- rbind(data.quality$presteps, c(input$studyDay, input$preStepsArray))
  data.quality$poststeps <- rbind(data.quality$poststeps, c(input$studyDay, input$postStepsArray))
  data.quality$totalsteps <- rbind(data.quality$totalsteps, c(input$studyDay, input$totalSteps))
  
  # ================ Save everything ================
  save.try <- try(expr = {save(data.decision, file = paste(paths, "/decision.Rdata", sep=""))
    save(data.dosage, file = paste(paths, "/dosage.Rdata", sep=""))
    save(data.day, file = paste(paths, "/daily.Rdata", sep=""))
    save(data.policy, file = paste(paths, "/policy.Rdata", sep=""))
    save(data.history, file = paste(paths, "/history.Rdata", sep=""))
    save(data.imputation, file = paste(paths, "/imputation.Rdata", sep=""))
    if(nrow(train.dat) > 0){
      
      train <- data.frame(id = input$userID, train.dat);
      save(train, file = paste(paths, "/train.Rdata", sep="")) # For pooling
      
    }
    
    
  }, silent = T)
  
  kk <- 1
  max.try <- 3
  while(is(save.try,"try-error") & kk <= max.try){
    
    kk <- kk + 1
    save.try <- try(expr = {save(data.decision, file = paste(paths, "/decision.Rdata", sep=""))
      save(data.dosage, file = paste(paths, "/dosage.Rdata", sep=""))
      save(data.day, file = paste(paths, "/daily.Rdata", sep=""))
      save(data.policy, file = paste(paths, "/policy.Rdata", sep=""))
      save(data.history, file = paste(paths, "/history.Rdata", sep=""))
      save(data.imputation, file = paste(paths, "/imputation.Rdata", sep=""))
      if(nrow(train.dat) > 0){
        
        train <- data.frame(id = input$userID, train.dat);
        save(train, file = paste(paths, "/train.Rdata", sep="")) # For pooling
        
      }
      
    }, silent = T)
    
    
  }
  
  if(is(save.try,"try-error")){
    
    cat(paste("\nNightly:", "Day =", input$studyDay, "Fail to save after", max.try, "attemps", save.try), file =  paste(paths, "/log", sep=""), append = TRUE) 
    
  }else{
    
    cat(paste0("\nNightly: ", "Day = ", input$studyDay, " Success", "[", kk, "]"), file =  paste(paths, "/log", sep=""), append = TRUE) 
    
  }
  

  
  
  
  
  
}




rm(list = ls())
server = T
localtest = T
#' ---
#' title:  Action selection in the bandit algorithm in HS 2.0
#' author: Peng Liao
#' date:   2019-05
#' ---
#' 

library(rjson)
library(fda, warn.conflicts=FALSE, quietly =T)
# ================ recieve the input ================ 

if(server){
  
  source("functions.R")
  load("bandit-spec.Rdata")
  args <- commandArgs(trailingOnly = TRUE)[1]
  input = fromJSON(args) # this is a list
  
  
}else{
  
  setwd("/Users/Peng/Dropbox/GitHubRepo/heartsteps/walking-suggestion-service")
  source("functions.R")
  load("bandit-spec.Rdata")
  
  
  if(localtest){
    
    args <- commandArgs(trailingOnly = TRUE)[1]
    input = fromJSON(file = args)
  
  }else{
    
    
    input <- fromJSON(file = "./test/call_8_1.json")
    # input <- fromJSON(file = filename)
    
  }
  
}

# ================ access the user's dataset ================  
tryCatch(
  expr = {

  stopifnot("userID" %in% names(input))  
  paths <- paste("./data/", "user", input$userID, sep="")

  request <- toJSON(input)
  write(request, file = paste(paths, "/request history/", "decision_", input$studyDay, "_", input$decisionTime, ".json",sep="")) # save the request

  # including daily features and dosage at the begining of the day and the current history
  load(paste(paths, "/daily.Rdata", sep="")) 

  # policy related
  load(paste(paths, "/policy.Rdata", sep="")) 
  
  # dosage 
  load(paste(paths, "/dosage.Rdata", sep=""))
  
  # decision 
  load(paste(paths, "/decision.Rdata", sep="")) 
  
  }, 
  error = function(err) {
  
  cat(paste("\nDecision:", err), file =  paste(paths, "/log", sep=""))
  
    stop("Initiliazation has not done for the user")
  
})

# ================ Condition Checking + action selection ================
# check current input (if fails, then MRT)
output <- tryCatch(
  expr = {
    stopifnot((c("userID", 
                 "studyDay", 
                 "decisionTime", 
                 "availability", 
                 "priorAnti", 
                 "lastActivity", 
                 "location") %in% names(input)))
    
    stopifnot(all(lapply(input, is.null)==FALSE) 
              & input$location %in% c(0, 1, 2) 
              & is.logical(input$availability) 
              & is.logical(input$priorAnti)
              & is.logical(input$lastActivity))
    
    stopifnot(input$decisionTime %in% c(1:5))
    stopifnot(input$studyDay %in% c(1:1000))
    
    },
  error = function(err){
    
  cat(paste("\nDecision:", "Day =", input$studyDay, "Slot =", input$decisionTime, 
            "micro-randomize", "Error:", err$message), file =  paste(paths, "/log", sep=""), append = TRUE)
    
  type <- -1
  if(is.logical(input$availability)){
    
    prob <- ifelse(input$availability, 0.25, 0)
    
  }else{
    
    prob <- 0
    
  }
  
  random.num <- runif(1)
  action <- (random.num <= prob);
  
  if(all(c("studyDay", "decisionTime") %in% names(input))){
    
    data.decision <- rbind(data.decision, c(input$studyDay, input$decisionTime, action, prob, random.num))
    data.decision <- data.frame(data.decision)
    colnames(data.decision) <- c("day", "timeslot", "action", "prob", "random.number")
    
    # save to the system
    save(data.decision, file = paste(paths, "/decision.Rdata", sep=""))
    
  }
  
  output <- list(send = action, probability = prob, type = type)
  
  return(output)
    })


# if current input is fine, then use bandit if dosage is well defined
if(is.null(output)){
  
  output <- tryCatch(
    expr ={
  
      # update the dosage 
      if(input$decisionTime == 1){

        if(nrow(subset(data.dosage$dataset, day == input$studyDay & timeslot == input$decisionTime)) == 0){
          
          # nightly update on day d-1 does not occur
          
          data.dosage$dataset <- rbind(data.dosage$dataset, c(input$studyDay, input$decisionTime, NA, NA, input$priorAnti))
          
        }else{
          
          index <- which(data.dosage$dataset$day == input$studyDay & data.dosage$dataset$timeslot == 1)
          data.dosage$dataset$anti2[index] <- input$priorAnti;
          
        }
        
      }else{

        data.dosage$dataset <- rbind(data.dosage$dataset, c(input$studyDay, input$decisionTime, input$lastActivity, input$priorAnti, FALSE))
        

      }
      # save to the system
      save(data.dosage, file = paste(paths, "/dosage.Rdata", sep=""));
      
      # calculate the dosage
      if((input$studyDay-1) * 5 + input$decisionTime == nrow(data.dosage$dataset) & all(is.na(data.dosage$dataset) == F)){
        
        # no missing decision time
        
        temp <- data.dosage$dataset
        temp <- temp[order(temp$day, temp$timeslot), ]
        event <- (temp$walk + temp$anti1 + temp$anti2 > 0);
        x <- data.dosage$init;
        for(j in 1:length(event)) x <- update.dosage(x, increase = event[j])
        current.dosage <- x
        
      }else{
        
        # imputed dosage dataset for all days
        temp <- data.dosage$dataset
        temp <- temp[order(temp$day, temp$timeslot), ]
        
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
        
        current.dosage <- subset(dosage.mat, day == input$studyDay & timeslot == input$decisionTime)$dosage
        
        
      }
      
      
     
  
      # ================ create the interaction terms ================ 
      
      # other interactions 
      work.loc <- input$location == 1;
      other.loc <- input$location == 0;
      engagement.indc <- data.day$engagement;
      variation.indc <- data.day$variation[input$decisionTime]
      
      # interaction.terms <- c(current.dosage, engagement.indc, 
      #                        work.loc, other.loc, variation.indc)
      # 
      
      # ================ action Selection ================  
      if(input$availability){
        
        # retrieve the current policy from the user's dataset
        mu <- data.policy$mu.beta
        Sigma <- data.policy$Sigma.beta
        gamma <- data.policy$gamma;
        eta <- data.policy$eta.fn;
        pi_max <- data.policy$pi_max;
        pi_min <- data.policy$pi_min;  
        
        # create the feature (standardization ocurrs here)
        feat <- c(1, std.dosage(current.dosage), engagement.indc, work.loc, other.loc, variation.indc) 
        
        # posterior dist
        pos.mean <- c(feat %*% mu)
        pos.var <- max(0, c(t(feat) %*% Sigma %*% feat))
        
        # forming the margin
        margin <- gamma/(1-gamma) * eta(current.dosage)
        
        # raw prob
        pit0 <- pnorm((pos.mean-margin)/sqrt(pos.var))
        
        # clipping
        prob <- min(c(pi_max, max(c(pi_min, pit0))))
        
        # output type (1: bandit, 0: MRT)
        type <- 1
        
        # MRT period
        
        if(input$studyDay < 8){
          
          prob <- 0.25
          type <- 0
          
        }
        
      }else{
        
        # output type (1: bandit, 0: MRT)
        type <- 1
        
        # MRT period
        
        if(input$studyDay < 8){
          
          type <- 0
          
        }
        
        prob <- 0
        
      }
  
      # take action
      random.num <- runif(1)
      action <- (random.num <= prob)
      
      
      
      # save the decision 
      data.decision <- rbind(data.decision, c(input$studyDay, input$decisionTime, action, prob, random.num))
      data.decision <- data.frame(data.decision)
      colnames(data.decision) <- c("day", "timeslot", "action", "prob", "random.number")
      
      # save to the system
      save(data.decision, file = paste(paths, "/decision.Rdata", sep=""))
      
      
      cat(paste("\nDecision:", "Day =", input$studyDay, "Slot =", input$decisionTime, "Success"), file =  paste(paths, "/log", sep=""), append = TRUE) 
      list(send = action, probability = prob, type = type);
      
  
  }, 
    error = function(err){
    
    cat(paste("\nDecision:", "Day =", input$studyDay, "Slot =", input$decisionTime, "micro-randomize", "Error:", err$message), file =  paste(paths, "/log", sep=""), append = TRUE)
    
    type <- -1
    if(is.logical(input$availability)){
    
    prob <- ifelse(input$availability, 0.25, 0)
    
    }else{
    
    prob <- 0
    
    }
    
    random.num <- runif(1)
    action <- (random.num <= prob);
    
    # save the decision 
    
    data.decision <- rbind(data.decision, c(input$studyDay, input$decisionTime, action, prob, random.num))
    data.decision <- data.frame(data.decision)
    colnames(data.decision) <- c("day", "timeslot", "action", "prob", "random.number")
    
    
   # save to the system
    save(data.decision, file = paste(paths, "/decision.Rdata", sep=""))
  
    
    
    output <- list(send = action, probability = prob, type = type)
    return(output)
  
    
    
    
  })
  
}

# ================Output ================

cat(toJSON(output))



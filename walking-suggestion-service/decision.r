rm(list = ls())
server = F
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
  
  setwd("/Users/Peng/Dropbox/GitHubRepo/heartsteps/walking-suggestion-service")
  source("functions.R")
  input <- fromJSON(file = "./test/call_1_5.json")

  
}



# ================ access the user's dataset ================  
tryCatch(expr = {

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
  }, error = function(err) {
  
  cat(paste("Decision:", err), file =  paste(paths, "/log", sep=""))
  
    stop("Initiliazation has not done for the user")
  
})



# ================ Condition Checking + action selection ================
# check current input (if fails, then MRT)
output <- tryCatch(expr = {
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
    },  error = function(err){
    
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
  
  output <- list(send = action, probability = prob, type = type)
  return(output)
    })

# if current input is fine, then use bandit if dosage is well defined
if(is.null(output)){
  
  output <- tryCatch(expr ={
  
      # check if there is any skipped times and update the dosage set
      
      if(input$decisionTime == 1){

        x <- (input$studyDay-1) * 5 + input$decisionTime # expected number of rows in dosage data
        if(x != nrow(data.dosage$dataset)) stop("previous decision time or nightly update is not complete")
        index <- which(data.dosage$dataset$day == input$studyDay & data.dosage$dataset$timeslot == 1)
        data.dosage$dataset$anti2[index] <- input$priorAnti;
        
      }else{

        x <- (input$studyDay-1) * 5 + input$decisionTime - 1 # expected number of rows in dosage data
        if(x != nrow(data.dosage$dataset)) stop("previous decision time or nightly update is not complete")
        
        data.dosage$dataset <- rbind(data.dosage$dataset, c(input$studyDay, input$decisionTime, input$lastActivity, input$priorAnti, FALSE))
        

      }
      
      # calculate the dosage
      temp <- data.dosage$dataset
      temp <- temp[order(temp$day, temp$timeslot), ]
      event <- (temp$walk + temp$anti1 + temp$anti2 > 1);
      x <- data.dosage$init;
      for(j in 1:length(event)) x <- update.dosage(x, increase = event[j])
      current.dosage <- x
      
      
     
  
  # ================ create the interaction terms ================ 
  
  # other interactions 
  work.loc <- input$location == 1;
  other.loc <- input$location == 0;
  engagement.indc <- data.day$engagement;
  variation.indc <- data.day$variation[input$decisionTime]
  
  interaction.terms <- c(current.dosage, engagement.indc, 
                         work.loc, other.loc, variation.indc)
  
  
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
  save(data.dosage, file = paste(paths, "/dosage.Rdata", sep=""));
  save(data.decision, file = paste(paths, "/decision.Rdata", sep=""))
  
  
  cat(paste("\nDecision:", "Day =", input$studyDay, "Slot =", input$decisionTime, "Success"), file =  paste(paths, "/log", sep=""), append = TRUE) 
  list(send = action, probability = prob, type = type);
  
  }, error = function(err){
    
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
    
    
    
     if(input$decisionTime == 1){
        
       if(length(subset(data.dosage$dataset, day == input$studyDay & timeslot == 1)) > 0){
         
        index <- (data.dosage$dataset$day == input$studyDay & data.dosage$dataset$timeslot == 1)
        data.dosage$dataset$anti2[index] <- input$priorAnti;
         
       }else{
         
         # previous nightly update does not occur
         
         #data.dosage$dataset <- rbind(data.dosage$dataset, c(input$studyDay, input$decisionTime, input$lastActivity, ))
         
       }
        
      }else{

      
        data.dosage$dataset <- rbind(data.dosage$dataset, c(input$studyDay, input$decisionTime, input$lastActivity, input$priorAnti, FALSE))
        

      }     
    
   # save to the system
    save(data.dosage, file = paste(paths, "/dosage.Rdata", sep=""));
    save(data.decision, file = paste(paths, "/decision.Rdata", sep=""))
  
    
    
    output <- list(send = action, probability = prob, type = type)
    return(output)
  
    
    
    
  })
  
}

# ================Output ================
cat(toJSON(output))



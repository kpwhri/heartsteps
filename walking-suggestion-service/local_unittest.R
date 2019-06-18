# 
# loc <- "/Users/Peng/Dropbox/GitHubRepo/test/"
# filename <- paste0(loc, "start", ".json")
# system(paste("Rscript initialize.r", filename))
# 
# 
# x <- paste0("call_", 2, "_", 1)
# filename <- paste0(loc, x, ".json")
# temp <- fromJSON(file = filename)
# 
# 
# x <- paste0("update_", 2)
# filename <- paste0(loc, x ,".json")
# temp2 <- fromJSON(file = filename)
# 
# 
# for(d in 1:20){
# 
# 
# 
# 
#   for(k in 1:5){
# 
# 
#     temp$studyDay <- d
#     temp$decisionTime <- k
#     write(toJSON(temp), file = paste0(loc, paste0("call_", d, "_", k), ".json"))
# 
#   }
# 
# 
#   temp2$studyDay <- d
#   temp2$totalSteps <- round(abs(rnorm(1, mean= 10000, sd = 3000)))
#   
#   temp2$probArray <- runif(5, min = 0, max = 1);
#   temp2$actionArray <- (runif(5) < temp2$probArray)
#   
#   write(toJSON(temp2), file = paste0(loc, paste0("update_", d), ".json"))
# 
# 
#   # system(paste("Rscript nightly.r", filename))
# 
# 
# }



setwd("/Users/Peng/Dropbox/GitHubRepo/heartsteps/walking-suggestion-service/")

loc <- "./test/"
filename <- paste0(loc, "start", ".json")
system(paste("Rscript initialize.r", filename))

for(d in 1:15){
  
  for(k in 1:5){
    
    if(runif(1) < 0.5){
      
      x <- paste0("call_", d, "_", k)
      filename <- paste0(loc, x, ".json")
      system(paste("Rscript decision.r", filename))
      print(c(d, k))
    }else{
      
      next
    }
    
    
  }
  
  if(runif(1) < 0.5){
    
    x <- paste0("update_", d)
    filename <- paste0(loc, x, ".json")
    system(paste("Rscript nightly.r", filename))
    print(d)
  }else{
    
    next
    
  }
  
  
}



# testing Pedja
loc <- "/Users/Peng/Dropbox/GitHubRepo/data/pedja/"
filename <- paste0(loc, "usertest-pedja_request_history_init", ".json")
system(paste("Rscript initialize.r", filename))


for(d in c(1, 3, 4)){
  
  filename <- paste0(loc, "usertest-pedja_request_history_nightly_",d , ".json")
  system(paste("Rscript nightly.r", filename))
  
  
}


filename <- paste0(loc, "usertest-pedja_request_history_decision_",10,"_", 2,  ".json")
system(paste("Rscript decision.r", filename))

filename <- paste0(loc, "usertest-pedja_request_history_decision_",10,"_", 3,  ".json")
system(paste("Rscript decision.r", filename))


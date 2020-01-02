#! /usr/bin/Rscript
## Required packages and source files
#"test-nickreid","test-pedja"
#participants = c("10339","10259","10194","10360","10269","10234","10365","10352","10336","10304")
library(lubridate)


return_immediately<-function(id){
    tryCatch({
      print(id)
    
       
       
       tempfile = paste("data/user", id, "_pooled_params/temp_policy.Rdata", sep = "")
       oldfile= paste("data/user", id, "_pooled_params/policy.Rdata", sep = "")
       
       load(oldfile)
       #print('loaded old')
       load(tempfile)
       data.policy$mu.beta = dataset$mu
       
       A = matrix(nrow=5,ncol=5,byrow=TRUE)
       A[1,] = dataset$sigma0
       A[2,] = dataset$sigma1
       A[3,] = dataset$sigma2
       A[4,] = dataset$sigma3
       A[5,] = dataset$sigma4
       #colnames(temp) <- NULL
       data.policy$Sigma.beta = A
       save(data.policy, file = oldfile)
       #print('set new')

  
},error= function(err){
    reasons = 'savine'
    print(err)
    reasons=paste(reasons, err, sep = "")
    temp = c(reasons)
    write(x = temp, file = "errorfile_pooled_time.txt", ncolumns = length(temp), append = TRUE)


    
}

)
     
    
    #if(inherits(possibleError, "error")) next
    
}
call_all<-function(){
    someusers <- read.csv(file = 'data/join_dates.csv')
  
    someusers$join_date = lubridate::mdy(someusers$join_date)
    print(someusers)
    start = lubridate::mdy('12/2/2019')
    print(start)
    participants<-c()
    count=0
    for (i in 1:dim(someusers)[1]) {
      if(someusers$join_date[i]>=start & count<20){
      
        participants<-append(participants,someusers$user_id[i])
        count=count+1
        
      }
      
    }
    print(participants)
    for (id in participants) {
       return_immediately(id)
    }
    return("")
}
results<-call_all()
#return_immediately()



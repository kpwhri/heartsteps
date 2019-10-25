#! /usr/bin/Rscript
## Required packages and source files
#"test-nickreid","test-pedja"
#'10237':0,'10271':1,'10041':2,'10355':3,'10062':4,'10374':5,'10215':6,'10313':7,'10395':8,'10152':9,
participants = c("10339","10259","10194","10360","10269","10234","10365","10352","10336","10304")


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
    write(x = temp, file = "errorfile_pooled.txt", ncolumns = length(temp), append = TRUE)


    
}

)
     
    
    #if(inherits(possibleError, "error")) next
    
}
call_all<-function(){
    for (id in participants) {
       return_immediately(id)
    }
    return("")
}
results<-call_all()
#return_immediately()



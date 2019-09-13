#! /usr/bin/Rscript
## Required packages and source files
#"test-nickreid","test-pedja"
participants = c("test-nickreid","test-pedja")


return_immediately<-function(){
    tryCatch(
    {
       
       for (id in participants) {
           tempfile = paste("data/user", id, "_pooled_params/temp_policy.Rdata", sep = "")
           oldfile= paste("data/user", id, "_pooled_params/policy.Rdata", sep = "")
       
       load(oldfile)
       print('loaded old')
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
       print('set new')
       }
       return("")
    },error= function(err){
        reasons = 'savine'
        print(err)
        reasons=paste(reasons, err, sep = "")
        temp = c(reasons)
        write(x = temp, file = "errorfile_pooled.txt", ncolumns = length(temp), append = TRUE)
       
        return("")
        
    }
    
    )
}

results<-return_immediately()


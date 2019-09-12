#! /usr/bin/Rscript
## Required packages and source files

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
       data.policy$sigma.beta = dataset$sigma
       save(data.policy, file = oldfile)
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


#! /usr/bin/Rscript
## Required packages and source files
#"test-nickreid","test-pedja"
participants = c("10032","10006","10157","10075","10142","10055","10101","test-pedja")


return_immediately<-function(){
    tryCatch(
    {
       
       for (id in participants) {
           tempfile = paste("data/user", id, "_pooled_params/policy.Rdata", sep = "")
          
       
       
       #print('loaded old')
       load(tempfile)
       mu_beta = data.policy$mu.beta
       
    
       write.csv(mu_beta, paste("data/user", id, "_pooled_params/mu_beta.csv", sep = ""))
       #print('set new')
       }
       return("")
    },error= function(err){

        print(err)
        return(err)
    }
    
    )
}

results<-return_immediately()


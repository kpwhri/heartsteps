#! /usr/bin/Rscript
## Required packages and source files

participants = c("10110")


return_immediately<-function(){
    tryCatch(
    {
       
       for (id in participants) {
           tempfile_name = paste("data/user", id, "_pooling_params/temp_policy.Rdata", sep = "")
           oldfile= paste("data/user", id, "_pooling_params/policy.Rdata", sep = "")
       
       load(oldfile)
       load(tempfile)
       data.policy$mu.beta = dataset$mu
       data.policy$sigma.beta = dataset$sigma
       save(data.policy, file = oldfile)
       }
       return("")
    },error= function(err){
        
        reasons=paste(reasons, err, sep = "")
        temp = c(as.vector(unlist(input)), reasons)
        write(x = temp, file = "data/errorfile_merge.txt", ncolumns = length(temp), append = TRUE)
       
        return("")
        
    }
    
    )
}

results<-return_immediately()


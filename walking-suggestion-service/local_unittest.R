loc <- "./test/"
filename <- paste0(loc, "start", ".json")
system(paste("Rscript initialize.r", filename))

for(d in 1:2){
  
  for(k in 1:5){
    
    x <- paste0("call_", d, "_", k)
    filename <- paste0(loc, x, ".json")
    system(paste("Rscript decision.r", filename))
    
    
  }
  
  x <- paste0("update_", d)
  filename <- paste0(loc, x, ".json")
  system(paste("Rscript nightly.r", filename))
  
  
}


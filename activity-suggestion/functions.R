proc.array <- function(list) {
  
  unlist(lapply(list, function(x) ifelse(is.null(x), NA, x)))
  
}

proc.matrix <- function(list) {
  
  fn = function(x) {
    x[sapply(x, is.null)] <- NA
    return(x)
  }
  temp <- lapply(list, function(l) lapply(l, fn))
  do.call(rbind, lapply(temp, unlist))
}


update.dosage = function(x, increase=TRUE){
  
  max(1, min(x + ifelse(increase, 2, -1), 100))
  
}

append.array = function(x, y){
  
  # if (x, y) are both NA, then return NA
  # if x is NA and y is not, then return y
  # if x is not NA and y is NA, then remain the same
  # otherwise (x, y both no NA), append and truncate at 7 elements. 
  
  if(is.na(y)){
    
    return(x)
    
  }else{
    
    if(all(is.na(x))){
      
      return(y)
      
    }else{
      
      return(tail(c(x, y), 7))
      
      
    }
    
  }
  
}


std.dosage = function(x) (x-1)/100
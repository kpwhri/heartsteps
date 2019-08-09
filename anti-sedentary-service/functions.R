exp.time.rem.in.state <- function(remaining.time, current.state, current.run.length, max.val = 100) {
  ## Computes the expected remaining time in Sedendatry 
  ## or Not Sedentary state
  ## Within each bucket
  
  temp = Sedentary.length[Sedentary.values == current.state 
                          & Sedentary.length > current.run.length
                          & Sedentary.length < max.val] - current.run.length
  r_min_x.temp = remaining.time * (temp > remaining.time) + temp * (temp <= remaining.time)
  r_minus_x_plus.temp = (remaining.time - temp)* ((remaining.time - temp) > 0)
  return(list("r_min_x.mean" = mean(r_min_x.temp), 
              "r_min_x.var" = var(r_min_x.temp),
              "r_minus_x_plus.mean" = mean(r_minus_x_plus.temp), 
              "r_minus_x_plus.var" = var(r_minus_x_plus.temp),
              "r_min_x.r_minus_x_plus.cov" = cov(r_min_x.temp, r_minus_x_plus.temp)
  ))
}

fraction.time.in.state <- function(current.hour, buckets) {
  ## Computes fraction of time in Sedentary 
  ## or Not Sedentary for remainder of study at the 
  ## hour level

  current.block = which.block(current.hour)
  
  if(current.hour > 24) {stop("Hour outside normal range")}
  if(current.block != 3) {
    remaining.data = window.time[hours(window.time$window.utime) >= current.hour
                                 & hours(window.time$window.utime) <= buckets[[current.block]][2], ] 
  } else {
    remaining.data = window.time[hours(window.time$window.utime) >= current.hour
                                 | hours(window.time$window.utime) <= buckets[[current.block]][2], ] 
  }
  temp = aggregate(sedentary.width ~ user + study.day, 
                   data = remaining.data,
                   FUN = function(x) mean(x == TRUE))
  
  return(list("mean" = mean(temp[,3]), "var" = var(temp[,3])))
}

full.remainder.fn <- function(remaining.time, current.state, current.run.length, current.hour, eta,r_min_x.table,r_minus_x_plus.table,fraction.df) {
  ## Combines exp. and fraction. functions to 
  ## Produce estimate of expectation and standard 
  ## deviation e(i,r) and sd(i,r).  Use these with
  ## eta to compute remainder function.
  
  # remaining.temp = exp.time.rem.in.state(remaining.time, current.state, current.run.length)
  r_min_x.mean = r_min_x.table[remaining.time, current.run.length+1]
  r_minus_x_plus.mean = r_minus_x_plus.table[remaining.time, current.run.length+1]
  fraction.temp = fraction.df[fraction.df$current.hour == current.hour,]
  
  complete.mean = (current.state==TRUE)*r_min_x.mean +
    r_minus_x_plus.mean * fraction.temp$mean     
  return(complete.mean)
}


weighted.history <- function(current.state, time.diff, old.states, lambda, old.A, old.rho) {
  ## Take the history and spit out 
  ## the weighted version according to lambda
  
  sum (( lambda^time.diff * old.A + (1-lambda^time.diff) * old.rho ) * (old.states == current.state))
  
}

randomization.probability <- function(N, current.state, remaining.time, current.run.length, current.hour, H.t, lambda, eta,r_min_x.table,r_minus_x_plus.table,fraction.df, max.prob = 0.995, min.prob = 0.005) {
  ## Randomization probabilifty function 
  ## depending on weighted history and full.remainder.fn.
  
  if (current.state == FALSE) {
    return(0) 
  } else {
    temp = (N[current.state+1] - weighted.history(current.state, H.t$time.diff, H.t$old.states, lambda, H.t$old.A, H.t$old.rho))/
             full.remainder.fn(remaining.time, current.state, current.run.length, current.hour, eta,r_min_x.table,r_minus_x_plus.table,fraction.df)
    return(min(max(temp,min.prob),max.prob))
  }
  
}  

which.block <- function(current.hour,buckets) {
  if( is.numeric(current.hour) & !is.na(current.hour)) {
    if( (current.hour >= buckets[[1]][1]) & (current.hour <= buckets[[1]][2])) {
      return(1)
    } else if ( (current.hour >= buckets[[2]][1]) & (current.hour <= buckets[[2]][2]) ) {
      return(2)
    } else if ( (current.hour >= buckets[[3]][1]) | (current.hour <= buckets[[3]][2]) ) {
      return(3)
    } else { 
      return(0) 
    }
  } else {
    # BAD VALUES GET BLOCK OF -1 
    return(-1)
  }
}

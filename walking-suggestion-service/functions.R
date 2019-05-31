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




disc.dosage <- 0.8


update.dosage = function(x, increase=TRUE){
  
  #max(1, min(x + ifelse(increase, 2, -1), 100))  #discrete
  
  disc.dosage * x  + ifelse(increase, 1, 0) #cts
  
  
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

warmup.imput = function(x){
  
  old <- x
  new <- old;
  for(d in 2:length(x)){
    
    if(is.na(new[d])){
      
      if(all(is.na(old[1:(d-1)]))==FALSE){
        
        new[d] <- mean(old[1:(d-1)], na.rm = T)    
      }
      
    }
    
  }
  
  # if entire vector is missing then use 0. 
  
  new[is.na(new)] <- ifelse(all(is.na(old)), 0, mean(old, na.rm = TRUE))
  
  return(new)
}

std.dosage = function(x) {
  
  # (x-1)/(100-1) # discrete
  
  x * (1-disc.dosage)
  
}

winsor.fn = function (x, beta=3, range = c(1, 10)){
  
  stopifnot(all(is.na(x)==FALSE))
  # compute the winsor scores
  # beta is the threshold parameter
  # range is the pre-specified min and max (if null, then just replacing the outliers)
  
  # standarize by median and mad (med abs dev)
  med <- median(x)
  sd <- mad(x)
  y <- (x-med)/sd
  
  # threshold
  y[ y > beta ] <- beta
  y[ y < - beta ] <- -beta
  
  # re-scale
  z <- med + y * sd
  
  # scale based on min and max if range is supplied
  if(is.null(range) == FALSE){
    
    min = range[1]
    max = range[2]
    z <- (z-min)/(max - min)
    
  }
  
  
  return(z)
  
}

winsor = function (x, beta=3, range = c(1, 10)){
  

  x[is.na(x) == FALSE] <- winsor.fn(x[is.na(x) == FALSE], beta, range)
  return(x)

  
}


winsor.upp = function (x, beta=3, range = c(1, 10), min.val){
  
  stopifnot(all(is.na(x)==FALSE))
  # compute the winsor scores
  # beta is the threshold parameter
  # range is the pre-specified min and max (if null, then just replacing the outliers)
  
  
  # let the minimal untouched
  x.copy <- x
  index <- which(x > min.val)
  
  #
  x <- x[index]
  
  # standarize by median and mad (med abs dev)
  med <- median(x)
  sd <- mad(x)
  y <- (x-med)/sd
  
  # threshold
  y[ y > beta ] <- beta
  
  # re-scale
  z <- med + y * sd
  
  # 
  x.copy[index] <- z
  z <- x.copy;
  
  # scale based on min and max if range is supplied
  if(is.null(range) == FALSE){
    
    min = range[1]
    max = range[2]
    z <- (z-min)/(max - min)
    
  }
  
  
  return(z)
  
}

posterior.cal = function(train.dat, mu0, Sigma0, sigma, int.names, nonint.names){
  
  # hirachcial action-centering posterior update
  
  stopifnot(all(complete.cases(train.dat)))
  
  interactions <- as.matrix(train.dat[, int.names])
  maineffects <- as.matrix(cbind(train.dat[, nonint.names], train.dat[, int.names]))
  
  probs <- train.dat$probability
  actions <- train.dat$action
  rewards <- train.dat$reward
  
  X1 <- cbind(1, maineffects)
  X2 <- probs * cbind(1, interactions)
  X3 <- (actions-probs) * cbind(1, interactions) 
  X <- cbind(X1, X2, X3)
  Y <- rewards
  
  
  # prior info
  inv.Sigma0 <- solve(Sigma0)
  sigma.sq <- sigma^2
  
  # posterior
  mu <- c(solve(t(X) %*% X +  sigma.sq * inv.Sigma0, t(X) %*% Y + sigma.sq * inv.Sigma0 %*% mu0))  
  Sigma <- sigma.sq * solve(t(X) %*% X +  sigma.sq * inv.Sigma0)
  
  # the poster mean and varnace for the interaction terms (intercept included)
  interaction.index <- tail(1:ncol(X), ncol(X3)) # include the intercept
  
  # return the posterio in the policy
  list(mu = mu[interaction.index], 
       Sigma = Sigma[interaction.index, interaction.index])

  
}

posterior.cal.mar = function(train.dat, mu0, Sigma0, sigma){
  
  # posterior calculation for marginal reward model
  
  X <- cbind(1, train.dat$dosage)
  Y <- train.dat$reward
  
  # prior info
  inv.Sigma0 <- solve(Sigma0)
  sigma.sq <- sigma^2
  
  # posterior
  mu <- c(solve(t(X) %*% X +  sigma.sq * inv.Sigma0, t(X) %*% Y + sigma.sq * inv.Sigma0 %*% mu0))  
  Sigma <- sigma.sq * solve(t(X) %*% X +  sigma.sq * inv.Sigma0)
  
  
  list(mu = mu, Sigma = Sigma)
  
}

Cal.Q = function(r.fn, prob, gamma, alpha0, alpha1){
  
  # calculate the value function
  
  max.dosage <- 100
  irs <- 2;
  drs <- 1;
  prob_as <- 0.25

  
  tran = function(x.next, x, a){
    
    # as <- as.numeric(runif(1) < prob_as)
    # max(1, min(x + ifelse((as+a)>0, 1, -1), 10))
    
    if(a==1){
      
      # a = 1
      
      if(x+irs <= max.dosage){
        
        ifelse(x.next == x+irs, 1, 0)
        
      }else{
        
        ifelse(x.next == max.dosage, 1, 0)
      }
      
    }else{
      
      # a = 0
      
      if(x+irs <= max.dosage){
        
        if(x-drs >= 1){
          
          (x.next == x+irs) * prob_as + (x.next == x-drs) * (1-prob_as)
          
        }else{
          
          (x.next == x+irs) * prob_as + (x.next == 1) * (1-prob_as)
          
        }  
        
        
      }else{
        
        (x.next == max.dosage) * prob_as +  (x.next == x-drs) * (1-prob_as)
      }
      
      
    }
    
  }
  
  prob.mat0 = t(sapply(1:max.dosage, function(x) sapply(1:max.dosage, function(y) tran(y, x, 0))))
  prob.mat1 = t(sapply(1:max.dosage, function(x) sapply(1:max.dosage, function(y) tran(y, x, 1))))
  
  
  TQ.op = function(Q.vec, Q.mat){
    
    VQ <- apply(Q.mat, 1, max);
    
    temp0 <- M0 + gamma * prob.mat0 %*% (prob * VQ + (1-prob) * Q.vec)
    temp1 <- M1 + gamma * prob.mat1 %*% (prob * VQ + (1-prob) * Q.vec)
    temp2 <- M_unavai + (temp0 - M0)
    
    TQ.mat <- cbind(temp0, temp1)
    TQ.vec <- temp2
    
    list(TQ.mat=TQ.mat, TQ.vec=TQ.vec)
  }
  
  TQ.op.adv = function(Q.vec, Q.mat){
    
    
    VQ <- apply(Q.mat, 1, max);
    
    temp0 <- M0 + gamma * prob.mat0 %*% (prob * VQ + (1-prob) * Q.vec)
    temp1 <- M1 + gamma * prob.mat1 %*% (prob * VQ + (1-prob) * Q.vec)
    temp2 <- M_unavai + (temp0 - M0)
    
    TQ.mat <- cbind(temp0, temp1) - alpha.mat * (VQ - Q.mat)
    TQ.vec <- temp2
    
    list(TQ.mat = TQ.mat , TQ.vec = TQ.vec)
  }
  
  compute.Q = function(op){
    
    Q.vec <- rep(0, max.dosage)
    Q.mat <- matrix(0, max.dosage, 2) 
    kk <- 0
    TQ = op(Q.vec, Q.mat)
    thres <- max(abs(TQ$TQ.mat - Q.mat), abs(TQ$TQ.vec - Q.vec))
    
    while(thres > thres.val){
      
      Q.vec <- TQ$TQ.vec
      Q.mat <- TQ$TQ.mat;
      
      TQ = op(Q.vec, Q.mat)
      thres <- max(abs(TQ$TQ.mat - Q.mat), abs(TQ$TQ.vec - Q.vec))
      
      kk <- kk + 1
      #cat(kk, thres, "\n")
      
    }
    
    return(Q.mat)
    
  }
  
  
  
  thres.val = 1e-4;
  # iter.max=1e7;
  
  # compute Q
  M_unavai <- sapply(1:max.dosage, function(x) c(r.fn(x, i = 0, a = 0)))
  M0 <- sapply(1:max.dosage, function(x) c(r.fn(x, i = 1, a = 0)))
  M1 <- sapply(1:max.dosage, function(x) c(r.fn(x, i = 1, a = 1)))
  
  
  alpha.mat <- matrix(0, nrow=max.dosage, ncol = 2)
  alpha.mat[, 1] <- alpha0
  alpha.mat[, 2] <- alpha1
  
  Q.opt <- compute.Q(TQ.op.adv)
  Q.til <- Q.opt - cbind(M0, M1)
  
  return(Q.til/gamma)
}



compute.dosage.day = function(last.dsg, yes.fifthToEnd.anti, yes.last.walk, anti, walk){
  
  # last.dsg = the dosage at yesterday's fifth decision time
  # fifthToEnd.anti
  # last.walk
  
  x <- update.dosage(last.dsg, increase= any(yes.fifthToEnd.anti, yes.last.walk, anti[1]))
  for(k in 2:5){
    
    
    x <- update.dosage(x, increase= any(walk[k-1], anti[k]))
    
  }
  
  return(x)
  
}




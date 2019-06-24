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

disc.dosage <- 0.95

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
  sd <- max(mad(x), 1e-10)
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


txt.eff.update = function(train.dat, mu1, Sigma1, mu2, Sigma2, sigma, int.names, nonint.names){
  
  # hirachcial action-centering posterior update
  
  stopifnot(all(complete.cases(train.dat)))
  
  temp.dat <- train.dat[train.dat$availability == 1, ]
  
  if(nrow(temp.dat) == 0){
    
    list(mean =  mu2, 
         var = Sigma2)
    
  }else{
    
    
    temp.dat$dosage <- sapply(temp.dat$dosage, std.dosage);
    
    interactions <- as.matrix(temp.dat[, int.names])
    maineffects <- as.matrix(cbind(temp.dat[, nonint.names], temp.dat[, int.names]))
    
    probs <- temp.dat$probability
    actions <- temp.dat$action
    rewards <- temp.dat$reward
    
    X1 <- cbind(1, maineffects)
    X2 <- probs * cbind(1, interactions)
    X3 <- (actions-probs) * cbind(1, interactions) 
    X <- cbind(X1, X2, X3)
    Y <- rewards
    
    
    # prior info
    
    mu.tmp <- c(mu1, mu2, mu2)
    Sigma.tmp <- as.matrix(bdiag(Sigma1, Sigma2, Sigma2))
    
    inv.Sigma.tmp <- solve(Sigma.tmp)
    sigma.sq <- sigma^2
    
    # posterior
    mu <- c(solve(t(X) %*% X +  sigma.sq * inv.Sigma.tmp, t(X) %*% Y + sigma.sq * inv.Sigma.tmp %*% mu.tmp))  
    Sigma <- sigma.sq * solve(t(X) %*% X +  sigma.sq * inv.Sigma.tmp)
    
    # index
    interaction.index <- tail(1:nrow(Sigma), length(mu2))
    
    # return the posterio in the policy
    list(mean = mu[interaction.index], 
         var = Sigma[interaction.index, interaction.index])
    
  }
  
  
  
  
}


main.eff.update = function(train.dat, mu1, Sigma1, sigma, int.names, nonint.names){
  
  # hirachcial action-centering posterior update
  
  stopifnot(all(complete.cases(train.dat)))
  
  temp.dat <- train.dat[train.dat$availability == 1 & train.dat$action == 0, ]
  
  if(nrow(temp.dat) == 0){
    
    list(mean =  mu1, 
         var = Sigma1)
    
  }else{
    
    
    temp.dat$dosage <- sapply(temp.dat$dosage, std.dosage);
    maineffects <- as.matrix(cbind(temp.dat[, nonint.names], temp.dat[, int.names]))
    rewards <- temp.dat$reward
    
    X <- cbind(1, maineffects)
    Y <- rewards
    
    
    # prior info
    
    mu.tmp <- mu1
    Sigma.tmp <- Sigma1
    
    inv.Sigma.tmp <- solve(Sigma.tmp)
    sigma.sq <- sigma^2
    
    # posterior
    mu <- c(solve(t(X) %*% X +  sigma.sq * inv.Sigma.tmp, t(X) %*% Y + sigma.sq * inv.Sigma.tmp %*% mu.tmp))  
    Sigma <- sigma.sq * solve(t(X) %*% X +  sigma.sq * inv.Sigma.tmp)
    
    
    # return the posterio in the policy
    list(mean = mu, 
         var = Sigma)
    
  }
  
  
  
  
}

unavail.update = function(train.dat, mu0, Sigma0, sigma, int.names, nonint.names){
  
  # hirachcial action-centering posterior update
  
  stopifnot(all(complete.cases(train.dat)))
  
  temp.dat <- train.dat[train.dat$availability == 0, ]
  
  if(nrow(temp.dat) == 0){
    
    list(mean =  mu0, 
         var = Sigma0)
    
  }else{
    
    
    temp.dat$dosage <- sapply(temp.dat$dosage, std.dosage);
    maineffects <- as.matrix(cbind(temp.dat[, nonint.names], temp.dat[, int.names]))
    rewards <- temp.dat$reward
    
    X <- cbind(1, maineffects)
    Y <- rewards
    
    
    # prior info
    
    mu.tmp <- mu0
    Sigma.tmp <- Sigma0
    
    inv.Sigma.tmp <- solve(Sigma.tmp)
    sigma.sq <- sigma^2
    
    # posterior
    mu <- c(solve(t(X) %*% X +  sigma.sq * inv.Sigma.tmp, t(X) %*% Y + sigma.sq * inv.Sigma.tmp %*% mu.tmp))  
    Sigma <- sigma.sq * solve(t(X) %*% X +  sigma.sq * inv.Sigma.tmp)
    
    
    # return the posterio in the policy
    list(mean = mu, 
         var = Sigma)
    
  }
  
  
  
  
}

eta.update = function(train.dat, alpha0, alpha1, alpha2, 
                        int.names = c("dosage", "engagement", "work.location", "other.location", "variation"),
                        nonint.names = c("temperature", "logpresteps", "sqrt.totalsteps")){
  
  # alpha0 <- gen.param$mu0
  # alpha1 <- gen.param$mu1
  # alpha2 <- gen.param$mu2
  
  # apply(train.dat, 1, function(z) z[int.names])
  
  # [1] "steps.yesterday.sqrt" "jbsteps30pre.log"    
  # [3] "loc.is.other"         "temperature"         
  # [5] "loc.is.work"          "window7.steps60.sd"  
  
  
  if(nrow(train.dat) < 10){
    
    return(bandit.spec$eta.init)
    
  }else{
    
    
    p.avail <- mean(train.dat$avail)
    X.null <- seq(0, 1/(1-0.950), by = 0.1)
    Z.trn <- train.dat[c(nonint.names, int.names[-1])]
    
    
    feat0 = function(z, x) c(1, z[1:length(nonint.names)], std.dosage(x), tail(z, length(int.names)-1))
    feat1 = function(z, x) c(1, z[1:length(nonint.names)], std.dosage(x), tail(z, length(int.names)-1))
    feat2 = function(z, x) c(1, std.dosage(x), tail(z, length(int.names)-1))
    
    # F0 <- t(sapply(X.null, function(x) apply(apply(Z.trn, 1, function(z) input$feat0(z, x)), 1, mean)))
    # F1 <- t(sapply(X.null, function(x) apply(apply(Z.trn, 1, function(z) input$feat1(z, x)), 1, mean)))
    # F2 <- t(sapply(X.null, function(x) apply(apply(Z.trn, 1, function(z) input$feat2(z, x)), 1, mean)))
    
    F.all <- t(sapply(X.null, function(x) apply(apply(Z.trn, 1, function(z) c(feat0(z, x), feat1(z, x), feat2(z, x))), 1, mean)))
    index0 <- 1:length(alpha0)
    index1 <- length(alpha0)+1 : length(alpha1)
    index2 <- tail(1:ncol(F.all), length(alpha2))
    F0 <- F.all[, index0]
    F1 <- F.all[, index1]
    F2 <- F.all[, index2]
    
    
    r0.vec = c(F0 %*% alpha0)
    r1.vec = c(F1 %*% alpha1)
    r2.vec = r1.vec + c(F2 %*% alpha2) 
    
    bsb <- create.bspline.basis (range=c(0, 1/(1-0.950)), nbasis=50, norder = 4)
    psi = function(x) c(eval.basis(x, bsb))
    
    psi.mat <- t(sapply(X.null, function(x) psi(x)))
    inv.cov <- solve(t(psi.mat) %*% psi.mat)
    
    psi.mat.irs = t(sapply(X.null, function(x) psi(0.950 * x + 1)))
    psi.mat.drs = t(sapply(X.null, function(x) psi(0.950 * x)))
    psi.mat.bar <- bandit.spec$p.sed * psi.mat.irs  + (1-bandit.spec$p.sed) * psi.mat.drs
    
    
    kmax <- 100;
    kk <- 1
    
    theta1 = rep(0, length(psi(0)));
    theta0 = rep(0, length(psi(0)));
    theta.bar = theta1 * p.avail + (1-p.avail) * theta0
    
    Y1.0 <- r1.vec + bandit.spec$gamma * psi.mat.bar %*% theta.bar
    Y1.1 <- r2.vec + bandit.spec$gamma * psi.mat.irs %*% theta.bar
    index <- (Y1.1 - Y1.0 > 0)
    Y1 <- Y1.0
    Y1[index] <- Y1.1[index]
    Y0 <- r0.vec + bandit.spec$gamma * psi.mat.bar %*% theta.bar
    delta <- max(abs(Y1 - psi.mat%*% theta1), abs(Y0 - psi.mat %*% theta0))
    
    
    delta.thres <- 1e-2;
    while(kk < kmax & delta > delta.thres){
      
      # new theta
      theta1 <- inv.cov %*% t(psi.mat) %*% Y1
      theta0 <- inv.cov %*% t(psi.mat) %*% Y0
      
      theta.bar = theta1 * p.avail + (1-p.avail) * theta0
      
      # Bellman operator
      Y1.0 <- r1.vec + bandit.spec$gamma * psi.mat.bar %*% theta.bar
      Y1.1 <- r2.vec + bandit.spec$gamma * psi.mat.irs %*% theta.bar
      index <- (Y1.1 - Y1.0 > 0)
      Y1 <- Y1.0
      Y1[index] <- Y1.1[index]
      Y0 <- r0.vec + bandit.spec$gamma * psi.mat.bar %*% theta.bar
      
      delta <- max(abs(Y1 - psi.mat%*% theta1), abs(Y0 - psi.mat %*% theta0))
      kk <- kk + 1
      
      # cat(kk, delta, "\n")
    }
    
    if(kk == kmax){
      
      warning("Not Converge")
      
    }
    
    
    eta.fn = function(x) {
      
      eta.hat <- c((1-bandit.spec$p.sed)* t(theta.bar)%*%(psi(disc.dosage*x)-psi(disc.dosage*x+1)) * (1-bandit.spec$gamma))
      
      # return(eta.hat)
      return(bandit.spec$weight.est * eta.hat + (1-bandit.spec$weight.est) * bandit.spec$eta.init(x))
      
      
    }
    
    
    
    return(eta.fn)
    
    
    
  }
  
  
  
  
  
  
}



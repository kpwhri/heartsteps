
import sys

import pickle
import pandas as pd
import numpy as np
import time
import os
import torch
import warnings
import gpytorch
from gpytorch.kernels import Kernel
from gpytorch.lazy import MatmulLazyTensor, RootLazyTensor
from gpytorch.constraints import constraints

def get_users(users,userstwo):
        
        xx,yy = np.meshgrid(users,userstwo,sparse=True)
        #.99999999999
        return (xx==yy).astype('float')

def get_first_mat(sigma_theta,data,baseline_indices):
    new_data = data[:,[baseline_indices]].reshape((data.shape[0],data.shape[1]))

    new_data_two = data[:,[baseline_indices]].reshape((data.shape[0],data.shape[1]))
    result = np.dot(new_data,sigma_theta)

    results = np.dot(result,new_data_two.T)
    return results

def inv_softplus(val):

    return np.log(np.exp(val)-1)

def get_sigma_u(u1,u2,rho):
    off_diagaonal_term = u1**.5*u2**.5*(rho-1)
    return np.array([[u1,off_diagaonal_term],[off_diagaonal_term,u2]])

def get_sigma_u_soft(u1,u2,rho):
    off_diagaonal_term = inv_softplus(u1**.5*u2**.5*(rho-1))
    return np.array([[inv_softplus(u1),off_diagaonal_term],[off_diagaonal_term,inv_softplus(u2)]])


class MyKernel(Kernel):
  
    
    def __init__(self, num_dimensions,user_mat, first_mat,gparams, variance_prior=None, offset_prior=None, active_dims=None):
        super(MyKernel, self).__init__(active_dims=active_dims)
        self.user_mat = user_mat
        self.first_mat = first_mat
       
        self.psi_dim_one = gparams.psi_indices[0]
        self.psi_dim_two = gparams.psi_indices[1]
        self.psi_indices =gparams.psi_indices
        #print(self.psi_dim_one)
        #print(self.psi_dim_two)
        
        self.init_u1 = gparams.sigma_u[0][0]
        #init_u1 = gparams.u1
        
        self.init_u2 = gparams.sigma_u[1][1]
        #init_u2 = gparams.u2
        
        #self.register_parameter(name="u1", parameter=torch.nn.Parameter(init_u1*torch.tensor(1.0)))
        self.register_parameter(name="raw_u1", parameter=torch.nn.Parameter(self.init_u1*torch.tensor(1.0)))
        
        #self.register_parameter(name="u2", parameter=torch.nn.Parameter(init_u2*torch.tensor(1.0)))
        self.register_parameter(name="raw_u2", parameter=torch.nn.Parameter(self.init_u2*torch.tensor(1.0)))
        t =gparams.sigma_u[0][0]**.5 * gparams.sigma_u[1][1]**.5
        self.r = (gparams.sigma_u[0][1]+t)/t
        #r = gparams.rho_term
        #self.register_parameter(name="rho", parameter=torch.nn.Parameter(r*torch.tensor(1.0)))
        self.register_parameter(name="raw_rho", parameter=torch.nn.Parameter(self.r*torch.tensor(1.0)))
        
        
        #initial_value=init_u2*torch.tensor(1.0)
        #initial_value=init_u1*torch.tensor(1.0)
        self.register_constraint("raw_u1",constraint= constraints.Positive(initial_value=self.init_u1*torch.tensor(1.0)))
        #initial_value=init_u2*torch.tensor(1.0)
        self.register_constraint("raw_u2",constraint= constraints.Positive(initial_value=self.init_u2*torch.tensor(1.0)
))
        
        self.register_constraint("raw_rho",constraint= constraints.Interval(0.0,2.0))
        # print(self.rho)
        #print(self.u1)
        #print(self.u2)
    #self.register_prior("u1_prior", gpytorch.priors.SmoothedBoxPrior(a=0,b=3,sigma=.5), "u1")
    #self.register_prior("u2_prior", gpytorch.priors.SmoothedBoxPrior(a=0,b=3,sigma=.5), "u2")
    #self.register_prior("rho_prior", gpytorch.priors.SmoothedBoxPrior(a=0,b=2,sigma=.5), "rho")
    
    
    
    @property
    def u2(self):
        if self.raw_u2<0.0001:
            return self.init_u2+.1
        return self.raw_u2
        return self.raw_u2_constraint.transform(self.raw_u2)
    
    @u2.setter
    def u2(self, value):
        self._set_u2(value)
    
    def _set_u2(self, value):
        if not torch.is_tensor(value):
            value = torch.as_tensor(value).to(self.raw_u2)
        self.initialize(raw_u2=self.raw_u2_constraint.inverse_transform(value))

    @property
    def u1(self):
        #print('called function one')
        #print(self.raw_u1)
        #print(self.raw_u1_constraint.transform(self.raw_u1))
        if self.raw_u1<0.0001:
            return self.init_u1+.1
        return self.raw_u1
        
        return self.raw_u1_constraint.transform(self.raw_u1)
    
    @u1.setter
    def u1(self, value):
        print('called function two')
        print(value)
        self._set_u1(value)
    
    def _set_u1(self, value):
        print('called function three')
        print(value)
        if not torch.is_tensor(value):
            value = torch.as_tensor(value).to(self.raw_u1)
            #self.raw_u1_constraint.inverse_transform(value)
        self.initialize(raw_u1=self.raw_u1_constraint.inverse_transform(value))
        print(self.raw_u1)

    @property
    def rho(self):
        if self.raw_rho<0.0001:
            return self.r+.1
        return self.raw_rho
        return self.raw_rho_constraint.transform(self.raw_rho)
    
    @rho.setter
    def rho(self, value):
        self._set_rho(value)
    
    def _set_rho(self, value):
        if not torch.is_tensor(value):
            value = torch.as_tensor(value).to(self.raw_rho)
        self.initialize(raw_rho=self.raw_rho_constraint.inverse_transform(value))


    
    
    
    def forward(self, x1, x2, batch_dims=None, **params):
        
        #us = torch.cat([self.u1, self.u2], 0) # us is a vector of size 2
        #print(x1[0,:,0:2].size())
        # print(x1.size())
        #print(us.size())
        #x1_ =torch.stack((x1[:,self.psi_dim_one],x1[:,self.psi_dim_two]),dim=1)
        x1_ = torch.stack([x1[:,i] for  i in self.psi_indices],dim=1)
        #x1_ =    torch.stack((x1[:,self.psi_dim_one],x1[:,self.psi_dim_two]),dim=1)
        #x2_ =torch.stack((x2[:,self.psi_dim_one],x2[:,self.psi_dim_two]),dim=1)
        x2_ =    torch.stack([x2[:,i] for  i in self.psi_indices],dim=1)
        #print(x1_)
        #print(x2_)
        #u2_= self.u2
        #u1_ =self.u1
        #print(self.u1)
        #print(x1_)
        #print(x2_)
        if batch_dims == (0, 2):
            print('batch bims here')
        #pass
        #print(x1_.size())
        
        #x1_ = x1_.view(x1_.size(0), x1_.size(1), -1, 1)
        #x1_ = x1_.permute(0, 2, 1, 3).contiguous()
        #x1_ = x1_.view(-1, x1_.size(-2), x1_.size(-1))
        
        
        #x2_ = x2_.view(x2_.size(0), x2_.size(1), -1, 1)
        #x2_ = x2_.permute(0, 2, 1, 3).contiguous()
        #x2_ = x2_.view(-1, x2_.size(-2), x2_.size(-1))
        #print(x1_.size())
        #print(x2_.size())
        #prod = MatmulLazyTensor(x1_, x2_.transpose(1, 0))
        
        prod = MatmulLazyTensor(x1_[:,0:1], x2_[:,0:1].transpose(-1, -2))
        
        
        #.expand(1,100,100)
        tone = prod * (self.u1)
        
        
        prod = MatmulLazyTensor(x1_[:,1:2], x2_[:,1:2].transpose(-1, -2))
        
        ttwo = prod * (self.u2)
        
        
        diagone = MatmulLazyTensor(x1_[:,0:1], x2_[:,1:2].transpose(-1, -2))
        
        
        diagtwo = MatmulLazyTensor(x1_[:,1:2], x2_[:,0:1].transpose(-1, -2))
        
        tthree = (diagone+diagtwo)*((self.rho-1)*(self.u1)**.5*(self.u2)**.5)
        
        
        
        random_effects = tone+ttwo+tthree
        
        #print(random_effects.evaluate())
        
        #print(random_effects)
        
        #print(random_effects.size())
        #print(self.user_mat.size())
        final = random_effects*self.user_mat
        
        #print(final.evaluate())
        #noise_term = (self.noise**2)*self.noise_mat
        #print(type(noise_term))
        #print(noise_term)
        #prod = MatmulLazyTensor(x1_, x2_.transpose(-1, -2))
        #prod = MatmulLazyTensor(prod,noise_term)
        #prod = prod*self.user_mat
        
        #final  = final + noise_term
        
        #final = torch.stack((tone,ttwo,tone,ttwo),dim=0)
        #print('one')
        #print(random_effects.evaluate())
        #print('two')
        #print(final.evaluate())
        #print(MatmulLazyTensor(random_effects,2*torch.eye(100)).evaluate())
        
        #n = self.first_mat
        #+noise_term
        
        
        final = final+self.first_mat
        #print(final.evaluate())
        return final




class GPRegressionModel(gpytorch.models.ExactGP):
    def __init__(self, train_x, train_y, likelihood,user_mat,first_mat,gparams):
        super(GPRegressionModel, self).__init__(train_x, train_y, likelihood)
        
        # SKI requires a grid size hyperparameter. This util can help with that
        # We're setting Kronecker structure to False because we're using an additive structure decomposition
        #grid_size = gpytorch.utils.grid.choose_grid_size(train_x, kronecker_structure=False)
        
        self.mean_module = gpytorch.means.ZeroMean()
        #self.mean_module.constant.requires_grad=False
        self.covar_module =  MyKernel(len(gparams.baseline_indices),user_mat,first_mat,gparams)
    
    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)









def run(X,users,y,global_params):
    #initial_u1,initial_u2,initial_rho,initial_noise,baseline_indices,psi_indices,user_index
    torch.manual_seed(111)
    #np.random.seed(111)
    user_mat= get_users(users,users)
    #print(user_mat.shape)
    #print(X.shape)
    #print(global_params.baseline_indices)
    first_mat = get_first_mat(np.eye(len(global_params.baseline_indices)),X,global_params.baseline_indices)
    #print(first_mat.shape)
    with gpytorch.settings.fast_computations(log_prob=False, solves=False):
        
        test_constraint = constraints.Positive(initial_value=global_params.sigma_u[0][0]*torch.tensor(1.0))
        #print('upper bound {}'.format(test_constraint.upper_bound))
        likelihood = gpytorch.likelihoods.GaussianLikelihood()
        likelihood.noise_covar.initialize(noise=(global_params.noise_term)*torch.ones(1))
    #print('going on')
    #print((global_params.noise_term)*torch.ones(X.shape[0]))
    # likelihood = gpytorch.likelihoods.FixedNoiseGaussianLikelihood(noise=(1.0)*torch.ones(X.shape[0]), learn_additional_noise=True)
    #print('like worked')
        X = torch.from_numpy(np.array(X)).float()
        y = torch.from_numpy(y).float()
    #print(X.size())
        first_mat = torch.from_numpy(first_mat).float()
        user_mat = torch.from_numpy(user_mat).float()
    
        model = GPRegressionModel(X, y, likelihood,user_mat,first_mat,global_params)
        #print('first one {}'.format(model.covar_module.u1.item()))
        model.train()
        likelihood.train()
        sigma_u=None
        cov=None
        noise=None
    
        optimizer = torch.optim.Adam([
                                  {'params': model.parameters()},  # Includes GaussianLikelihood parameters
                                  ], lr=global_params.lr)
                                  
        mll = gpytorch.mlls.ExactMarginalLogLikelihood(likelihood, model)
        #def train(num_iter):
        num_iter=10
        with gpytorch.settings.use_toeplitz(False):
            for i in range(num_iter):
                try:
                   
                    optimizer.zero_grad()
                    output = model(X)
                #print(type(output))
                    loss = -mll(output, y)
                    loss.backward()
                    
                    #print('Iter %d/%d - Loss: %.3f' % (i + 1, num_iter, loss.item()))
                    optimizer.step()
                    #print(get_sigma_u(model.covar_module.u1.item(),model.covar_module.u2.item(),model.covar_module.rho.item()))
                    #print(test_constraint.transform(model.covar_module.u1.item()*torch.tensor(1.0)))
    
                    sigma_temp = get_sigma_u(model.covar_module.u1.item(),model.covar_module.u2.item(),model.covar_module.rho.item())
                    ##print('linalg {}'.format(np.linalg.eig(sigma_temp)))
                    
                    #print(sigma_temp)
                    eigs = np.linalg.eig(sigma_temp)
                    f_preds = model(X)
                    f_covar = f_preds.covariance_matrix
                    covtemp = f_covar.detach().numpy()
                    #print('noise two {}'.format(likelihood.second_noise_covar.noise.item()))
                    #print('noise two {}'.format(likelihood.noise_covar.noise))
                    if np.isreal(sigma_temp).all() and not np.isnan(covtemp).all() and eigs[0][0]>0.0005 and eigs[0][1]>0.0005:
                        
                        sigma_u = sigma_temp
                        cov=covtemp
                        #print(np.isreal( covtemp))
                        #print(cov)
                        noise = likelihood.noise_covar.noise.item()
                    #noise = likelihood.second_noise_covar.noise.item()+1.0
                            #**.5
                    else:
                        #print(eigs)
                        break

                except Exception as e:
                    print(e)
                    print('here')
                    break
        one_test = True
        if i<2:
            one_test=False
            likelihood = gpytorch.likelihoods.GaussianLikelihood()
        #likelihood = gpytorch.likelihoods.FixedNoiseGaussianLikelihood(noise=(1.0)*torch.ones(X.shape[0]), learn_additional_noise=True)

            likelihood.noise_covar.initialize(noise=(global_params.noise_term)*torch.ones(1))
        
            model = GPRegressionModel(X, y, likelihood,user_mat,first_mat,global_params)
            print('1 test')
        #t =global_params.sigma_u[0][0]**.5 * global_params.sigma_u[1][1]**.5
        #r = (global_params.sigma_u[0][1]+t)/t
        
        #model.covar_module.u1 =global_params.sigma_u[0][0]*torch.tensor(1.0)
        ##print('ok 1')
        #model.covar_module.u2 =global_params.sigma_u[1][1]*torch.tensor(1.0)
        #model.covar_module.rho =r*torch.tensor(1.0)
        ##print('ok 1')
        ##print(model.covar_module.u1.item())
        ##print(model.covar_module.u2.item())
        ##print(model.covar_module.rho.item())
            sigma_u = get_sigma_u(model.covar_module.u1.item(),model.covar_module.u2.item(),model.covar_module.rho.item())
        ##print('ok 2')
            noise =global_params.noise_term
        ##print('ok 3')
        #model.eval()
        #likelihood.eval()
        ##print('ok 4')
            f_preds = model(X)
        ##print('ok 5')
            f_covar = f_preds.covariance_matrix
        #print('ok 6')
        #print(f_covar)
            cov = f_covar.detach().numpy()
#print('ok 7')
        ##print('ok 6')
        ##print(cov.shape)

#train(50)
#model.eval()
# likelihood.eval()
#observed_pred = likelihood(model(X))
    #print('o')
    #print(likelihood(model(X)))
    #print(likelihood(model(X)).mean.numpy())

    #print('cov')
    #print(cov)
    if one_test:
        sigma_u = get_sigma_u(model.covar_module.u1.item(),model.covar_module.u2.item(),model.covar_module.rho.item())
    return {'sigma_u':sigma_u,'cov':cov,'noise':noise,'like':0,'iters':i}



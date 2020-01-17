
import sys
from datetime import date
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
import pooling_params_time as gtp
import simple_bandits
import R_to_python_functions_time as rpy
softplus = torch.functional.F.softplus

#from LBFGS import FullBatchLBFGS

def get_users_new(users,userstwo):
    to_return = []
    for i in range(len(users)):
        temp = []
        for j in range(len(userstwo)):
            #if users[i]==userstwo[j]:
            temp.append(int(users[i]==userstwo[j]))
        to_return.append(temp)
    return to_return


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

def dist(one,two):
    return np.exp(-(one-two)**2/4.6**2)

def get_distance(days):
    to_return = []
    for i in range(len(days)):
        temp = []
        
        temp=[dist(days[i],days[j]) for j in range(len(days))]
        to_return.append(temp)
    return np.array(to_return)

def inv_softplus(val):
    
    return np.log(np.exp(val)-1)

def get_sigma_u(u1,u2,rho):
    off_diagaonal_term = u1**.5*u2**.5*(rho-1)
    return np.array([[u1,off_diagaonal_term],[off_diagaonal_term,u2]])

def get_sigma_v(s1,s3):
    return np.diag([s1,s3])

def get_sigma_u_soft(u1,u2,rho):
    off_diagaonal_term = inv_softplus(u1**.5*u2**.5*(rho-1))
    return np.array([[inv_softplus(u1),off_diagaonal_term],[off_diagaonal_term,inv_softplus(u2)]])


class MyKernel(Kernel):
    
    
    def __init__(self, num_dimensions,user_mat, first_mat,time_mat,gparams, variance_prior=None, offset_prior=None, active_dims=None):
        super(MyKernel, self).__init__(active_dims=active_dims)
        self.user_mat = user_mat
        self.first_mat = first_mat
        self.time_mat = time_mat
        #self.action_indices = [8,13]
        self.action_indices=[7]
        self.psi_dim_one = gparams.psi_indices[0]
        self.psi_dim_two = gparams.psi_indices[1]
        self.psi_indices =gparams.psi_indices
        #print(self.psi_indices)
        self.g_indices = [i for i in range(8)]
        self.g_indices = [i for i in range(7)]
        
        self.action_indices_one = [i for i in range(8,8+5)]
        self.action_indices_two = [i for i in range(8+5,18)]

        self.action_indices_one = [i for i in range(7,7+4)]
        
        
        self.init_u1 = gparams.sigma_u[0][0]
        
        
        self.init_u2 = gparams.sigma_u[1][1]
        
        self.init_s1 = gparams.sigma_v[0][0]
        
        
        self.init_s3 = gparams.sigma_v[1][1]
        
   
        
        self.register_parameter(name="raw_u1", parameter=torch.nn.Parameter(1.0*torch.tensor(1.0)))
        #self.register_parameter(name="test", parameter=torch.nn.Parameter(1.0*torch.tensor(1.0)))
        
        
        self.register_parameter(name="raw_u2", parameter=torch.nn.Parameter(1.0*torch.tensor(1.0)))
        t =gparams.sigma_u[0][0]**.5 * gparams.sigma_u[1][1]**.5
        self.r = (gparams.sigma_u[0][1]+t)/t
        
        self.register_parameter(name="raw_rho", parameter=torch.nn.Parameter(1.0*torch.tensor(1.0)))
        
        
        self.register_constraint("raw_u1",constraint= constraints.Positive())
        
        self.register_constraint("raw_u2",constraint= constraints.Positive())
            
        self.register_constraint("raw_rho",constraint= constraints.Interval(0.0,2.0))
        
        self.register_parameter(name="raw_s1", parameter=torch.nn.Parameter(1.0*torch.tensor(1.0)))
     
        self.register_constraint("raw_s1",constraint= constraints.Positive())
        
        self.register_parameter(name="raw_s3", parameter=torch.nn.Parameter(1.0*torch.tensor(1.0)))
    
        self.register_constraint("raw_s3",constraint= constraints.Positive())
        
                
        
        self.u1 = self.init_u1
        self.u2 = self.init_u2
        self.rho = self.r
        #print(self.rho)
        self.s1 = self.init_s1
   
        self.s3 = self.init_s3
    
  
    def forward(self, x1, x2, batch_dims=None, **params):
        #action_vector = torch.stack([torch.Tensor(x1)[:,i] for  i in [self.action_indices_one]],dim=1)\
        #+torch.stack([torch.Tensor(x1)[:,i] for  i in [self.action_indices_two]],dim=1)

        action_vector = torch.stack([torch.Tensor(x1)[:,i] for  i in [self.action_indices_one]],dim=1)

    
    
        baseline_vector =torch.stack([torch.Tensor(x1)[:,i] for  i in [self.g_indices]],dim=1)
        #print(action_vector)
        fake_vector_one = torch.cat((baseline_vector.squeeze(),action_vector.squeeze()),1)

        #action_vector = torch.stack([torch.Tensor(x2)[:,i] for  i in [self.action_indices_one]],dim=1)\
        #+torch.stack([torch.Tensor(x2)[:,i] for  i in [self.action_indices_two]],dim=1)
        action_vector = torch.stack([torch.Tensor(x2)[:,i] for  i in [self.action_indices_one]],dim=1)

    
        baseline_vector =torch.stack([torch.Tensor(x2)[:,i] for  i in [self.g_indices]],dim=1)
        fake_vector_two = torch.cat((baseline_vector.squeeze(),action_vector.squeeze()),1)
    #x1=[]
    

    #fake_vector_one[:,i]
        x1_ = torch.stack([ fake_vector_one[:,i] for  i in self.psi_indices],dim=1)
        
        x2_ =    torch.stack([fake_vector_two[:,i] for  i in self.psi_indices],dim=1)
        
        #print(x1_)
        
        if batch_dims == (0, 2):
            print('batch bims here')
        
        prod = MatmulLazyTensor(x1_[:,0:1], x2_[:,0:1].transpose(-1, -2))
        
        
        
        tone = prod * (self.u1)
        #print('here 1')
        
        prod = MatmulLazyTensor(x1_[:,1:2], x2_[:,1:2].transpose(-1, -2))
        
        ttwo = prod * (self.u2)
        #print('here 2')
        
        diagone = MatmulLazyTensor(x1_[:,0:1], x2_[:,1:2].transpose(-1, -2))
        
        
        diagtwo = MatmulLazyTensor(x1_[:,1:2], x2_[:,0:1].transpose(-1, -2))
        
        tthree = (diagone+diagtwo)*((self.rho-1)*(self.u1)**.5*(self.u2)**.5)
        #print('here 3')
        
        
        random_effects = tone+ttwo+tthree
        #print(random_effects)
        
        final = random_effects*self.user_mat

        prod = MatmulLazyTensor(x1_[:,0:1], x2_[:,0:1].transpose(-1, -2))
        ttimeone = prod * (self.s1)

    
        prod = MatmulLazyTensor(x1_[:,1:2], x2_[:,1:2].transpose(-1, -2))
    
        ttimetwo = prod * (self.s3)
        
        
        time_effects = ttimeone+ttimetwo
        time_effects = time_effects*self.time_mat
        final = final + time_effects
        
        final = final+self.first_mat
        
        return final

    @property
    def s1(self):
        return self.raw_s1_constraint.transform(self.raw_s1)
    
    @s1.setter
    def s1(self, value):
        self._set_s1(value)
    
    def _set_s1(self, value):
        if not torch.is_tensor(value):
            value = torch.as_tensor(value).to(self.raw_s1)
        self.initialize(raw_s1=self.raw_s1_constraint.inverse_transform(value))
    
    
 
    @property
    def s3(self):
        return self.raw_s3_constraint.transform(self.raw_s3)
    
    @s3.setter
    def s3(self, value):
        self._set_s3(value)
    
    def _set_s3(self, value):
        if not torch.is_tensor(value):
            value = torch.as_tensor(value).to(self.raw_s3)
        self.initialize(raw_s3=self.raw_s3_constraint.inverse_transform(value))
    
    
    @property
    def u2(self):
        
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
        return self.raw_u1_constraint.transform(self.raw_u1)
    
    
    
    @u1.setter
    def u1(self, value):
        
        self._set_u1(value)
    
    def _set_u1(self, value):
        
        if not torch.is_tensor(value):
            value = torch.as_tensor(value).to(self.raw_u1)
        self.initialize(raw_u1=self.raw_u1_constraint.inverse_transform(value))
    
    
    @property
    def rho(self):
        
        return self.raw_rho_constraint.transform(self.raw_rho)
    
    @rho.setter
    def rho(self, value):
        self._set_rho(value)
    
    def _set_rho(self, value):
        if not torch.is_tensor(value):
            value = torch.as_tensor(value).to(self.raw_rho)
        self.initialize(raw_rho=self.raw_rho_constraint.inverse_transform(value))
    
    
    
    
    
    



class GPRegressionModel(gpytorch.models.ExactGP):
    def __init__(self, train_x, train_y, likelihood,user_mat,first_mat,time_mat,gparams):
        super(GPRegressionModel, self).__init__(train_x, train_y, likelihood)
        
        
        
        self.mean_module = gpytorch.means.ZeroMean()
  
        self.covar_module =  MyKernel(len(gparams.baseline_indices),user_mat,first_mat,time_mat,gparams)
    
    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)


def simple_random_effects(X):
    ##just for trial
    to_return =[]
    for i in range(len(X)):
        feat_vec = X[i]
        r_one = feat_vec[0]
        r_two = feat_vec[8]+feat_vec[8+5]
        to_return.append([r_one,r_two])
    return np.array(to_return)


def real_run(X,users,ycentered,y,days,global_params):
    
    #_lbfgs
        hyper = get_hyper(np.array(X),users,np.array(ycentered),days,global_params)
        print('got hyper')
        global_params.sigma_u =hyper['sigma_u']
        global_params.sigma_v =hyper['sigma_v']
        global_params.noise_term = hyper['noise']
        

        with open('data/pooled_time_hyper/pooled_init_time_params.pkl','wb') as f:
            pickle.dump({'sigma_u':hyper['sigma_u'],'sigma_v':hyper['sigma_v'],'noise_term':hyper['noise']},f)
        global_params.sigma_u =hyper['sigma_u']
        global_params.sigma_v =hyper['sigma_v']
        global_params.noise_term = hyper['noise']
   
    
        random_effects = simple_random_effects(X)
        #print(random_effects[0])

        
        
        cov = simple_bandits.other_cov_time(np.array(X),global_params.sigma_theta,random_effects,global_params.sigma_u,get_users(users,users),global_params.sigma_v,get_distance(days))
        #return cov
        
        hyper['cov']=cov
        #hyper['noise']=1e10

        with open('data/pooled_time_hyper/pooled_time_init_params_{}.pkl'.format(str(date.today())),'wb') as f:
            pickle.dump({'sigma_u':hyper['sigma_u'],'sigma_v':hyper['sigma_v'],'noise_term':hyper['noise'],'cov':hyper['cov'],'iters':hyper['iters'],'gp':global_params.psi_indices},f)
        inv_term = simple_bandits.get_inv_term(hyper['cov'],np.array(X).shape[0],hyper['noise'])
        global_params.update_params(hyper)
            #with open('../../data_to_test.pkl','wb') as f:
            #pickle.dump({'X':X,'y':y,'users':users,'gp':global_params},f)
#print(global_params.sigma_u)
        global_params.inv_term=inv_term
        ##uncentered y
        to_return = {i:simple_bandits.calculate_posterior_faster_time(global_params,\
                                                             i,rpy.get_current_day(i),\
                                                             np.array(X), users,days,np.array(y) ) for i in set(users)}
        print('worked')
        return to_return



def get_hyper(X,users,y,days,global_params):
    torch.manual_seed(10)


    user_mat= get_users(users,users)
   
    time_mat =get_distance(days)
    print(X.shape)
    first_mat = get_first_mat(global_params.sigma_theta,X,global_params.baseline_indices)

    print('first mat')
    print(first_mat.shape)
    print(time_mat.shape)
    print(user_mat.shape)

    X = torch.from_numpy(np.array(X)).float()

    y = torch.from_numpy(y).float()
  
    first_mat = torch.from_numpy(first_mat).float()
    user_mat = torch.from_numpy(user_mat).float()
    time_mat = torch.from_numpy(time_mat).float()

    likelihood = gpytorch.likelihoods.GaussianLikelihood()
    #(global_params.noise_term)
    likelihood.noise_covar.initialize(noise=(global_params.noise_term)*torch.ones(1))
    model = GPRegressionModel(X, y, likelihood,user_mat,first_mat,time_mat,global_params)
        

    sigma_u=None
    cov=None
    noise=None
    model.train()
    likelihood.train()
    optimizer = torch.optim.Adam([
                                      {'params': model.parameters()},  # Includes GaussianLikelihood parameters
                                      ], lr=0.1)
                                      #global_params.lr
    mll = gpytorch.mlls.ExactMarginalLogLikelihood(likelihood, model)

    num_iter=40
#print(X)
    losses = []
    Failure=False
    one_test=True
    with gpytorch.settings.use_toeplitz(True):
            for i in range(num_iter):
                try:
                    #print(i)
                    optimizer.zero_grad()
                    #print(X.size())
                    output = model(X)
                    #print('here 5')
                    loss = -mll(output, y)
                    #print('here 6')
                    #print('here 5')
                    loss.backward()
                    losses.append(loss.item())
                    print('Iter %d/%d - Loss: %.3f like: %.3f' % (i + 1, i, loss.item(),likelihood.noise_covar.noise.item()))
                                                  
                    optimizer.step()
                    
                    #print(model.covar_module.u1.item())
                                                  
                    sigma_temp = get_sigma_u(model.covar_module.u1.item(),model.covar_module.u2.item(),model.covar_module.rho.item())
                    sigma_vtemp = get_sigma_v(model.covar_module.s1.item(),model.covar_module.s3.item())
                    eigs = np.linalg.eig(sigma_temp)
                    #print(sigma_vtemp)
                    #print(eigs)
                    f_preds = model(X)
                    f_covar = f_preds.covariance_matrix
                    covtemp = f_covar.detach().numpy()
                    #print(eigs)
                    #and eigs[0][0]>0.0001 and eigs[0][1]>0.0001
                    if np.isreal(sigma_temp).all() and not np.isnan(covtemp).all() and \
                        np.isreal(sigma_vtemp).all():
                                                          
                        sigma_u = sigma_temp
                        sigma_v=sigma_vtemp
                        cov=covtemp
                                                                  
                        noise = likelihood.noise_covar.noise.item()
                                                                      
                    else:
                        print('oops')
                        break
                                                                              
                except Exception as e:
                    print(e)
                    Failure=True
                    with open('data/error_within_gpy_time.txt','w+') as f:
                        f.write('{}'.format(e))
                        f.write('\n')
                    print(e)
                                                                              
                one_test = False
                if i<2:
                    one_test=True
                  

    if one_test or Failure:
                print('here')
                sigma_u = get_sigma_u(model.covar_module.u1.item(),model.covar_module.u2.item(),model.covar_module.rho.item())
                sigma_v =get_sigma_v(model.covar_module.s1.item(),model.covar_module.s3.item())

                f_preds = model(X)
                f_covar = f_preds.covariance_matrix
                covtemp = f_covar.detach().numpy()
                cov=covtemp
                noise = likelihood.noise_covar.noise.item()

    return {'sigma_u':sigma_u,'cov':cov,'noise':noise,'like':0,'iters':i,'sigma_v':sigma_v}














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
import pooling_params as gtp
import simple_bandits



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
        self.action_indices = [8,13]
        self.psi_dim_one = gparams.psi_indices[0]
        self.psi_dim_two = gparams.psi_indices[1]
        self.psi_indices =gparams.psi_indices
        print(self.psi_indices)
        self.g_indices = [i for i in range(8)]
        self.action_indices_one = [i for i in range(8,8+5)]
        self.action_indices_two = [i for i in range(8+5,18)]
        self.init_u1 = gparams.sigma_u[0][0]
        
        
        self.init_u2 = gparams.sigma_u[1][1]
        
        
        
        self.register_parameter(name="raw_u1", parameter=torch.nn.Parameter(1.0*torch.tensor(1.0)))
        self.register_parameter(name="test", parameter=torch.nn.Parameter(1.0*torch.tensor(1.0)))
        
        
        self.register_parameter(name="raw_u2", parameter=torch.nn.Parameter(1.0*torch.tensor(1.0)))
        t =gparams.sigma_u[0][0]**.5 * gparams.sigma_u[1][1]**.5
        self.r = (gparams.sigma_u[0][1]+t)/t
        
        self.register_parameter(name="raw_rho", parameter=torch.nn.Parameter(1.0*torch.tensor(1.0)))
        
        
        self.register_constraint("raw_u1",constraint= constraints.Positive())
        
        self.register_constraint("raw_u2",constraint= constraints.Positive())
            
        self.register_constraint("raw_rho",constraint= constraints.Interval(0.0,2.0))
        self.u1 = self.init_u1
        self.u2 = self.init_u2
        self.rho = self.r
      
    #self.test = 1.0
    
                                                                           #self.u2=1
                                                                           #self.init_u2;
                                                                           #self.u1=1
        #self.init_u1;
        #self.rho=1
    #self.r;
    def forward(self, x1, x2, batch_dims=None, **params):
        action_vector = torch.stack([torch.Tensor(x1)[:,i] for  i in [self.action_indices_one]],dim=1)\
+torch.stack([torch.Tensor(x1)[:,i] for  i in [self.action_indices_two]],dim=1)
#combine into new feature vector
#print('one')
        baseline_vector =torch.stack([torch.Tensor(x1)[:,i] for  i in [self.g_indices]],dim=1)
        #print('two')
        #print(baseline_vector.size())
        #print(action_vector.size())
        fake_vector_one = torch.cat((baseline_vector.squeeze(),action_vector.squeeze()),1)
#x1=[]  print()
#print('three')
        action_vector = torch.stack([torch.Tensor(x2)[:,i] for  i in [self.action_indices_one]],dim=1)\
+torch.stack([torch.Tensor(x2)[:,i] for  i in [self.action_indices_two]],dim=1)
    #combine into new feature vector
        baseline_vector =torch.stack([torch.Tensor(x2)[:,i] for  i in [self.g_indices]],dim=1)
        fake_vector_two = torch.cat((baseline_vector.squeeze(),action_vector.squeeze()),1)
    #x1=[]
    

    #fake_vector_one[:,i]
        x1_ = torch.stack([ fake_vector_one[:,i] for  i in self.psi_indices],dim=1)
        
        x2_ =    torch.stack([fake_vector_two[:,i] for  i in self.psi_indices],dim=1)
        #print(x1_.shape)
        #print(x2_.shape)
        #print(x2_[:4,:])
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
        #temp = prod*self.test
        #temp = temp*self.user_mat
        #print('here 4')
        
        
        final = final+self.first_mat
        
        return final


    
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
    def __init__(self, train_x, train_y, likelihood,user_mat,first_mat,gparams):
        super(GPRegressionModel, self).__init__(train_x, train_y, likelihood)
        
        
        
        self.mean_module = gpytorch.means.ZeroMean()
        #self.mean_module =gpytorch.means.ConstantMean()
        #self.mean_module.requires_grad=True
        #self.mean_module.constant.requires_grad=False
        self.covar_module =  MyKernel(len(gparams.baseline_indices),user_mat,first_mat,gparams)
    
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


def real_run(X,users,ycentered,y,global_params):
    
        
        hyper = get_hyper(np.array(X),users,np.array(ycentered),global_params)
        with open('data/ran_new_model_two.txt','w+') as f:
                f.write('{}'.format('ran'))
                f.write('\n')
        with open('data/pooled_hyper/pooled_init_params.pkl','wb') as f:
            pickle.dump({'sigma_u':hyper['sigma_u'],'noise_term':hyper['noise']},f)
                #hyper['sigma_u']=np.array([[.09,.008],[.008,.001]])
        global_params.sigma_u =hyper['sigma_u']
        #cov = simple_bandits.get_covar_simple(np.array(X),users,global_params)
        #random_effects = np.array(X)[:,global_params.psi_indices]
        random_effects = simple_random_effects(X)
        print(random_effects[0])

        
        
        cov = simple_bandits.other_cov_notime(np.array(X),global_params.sigma_theta,random_effects,global_params.sigma_u,get_users(users,users))
        hyper['cov2']=hyper['cov']
        hyper['cov']=cov
        #hyper['noise']=1e10
      
        with open('data/pooled_hyper/pooled_init_params_{}.pkl'.format(str(date.today())),'wb') as f:
            pickle.dump({'sigma_u':hyper['sigma_u'],'noise_term':hyper['noise'],'cov2':hyper['cov2'],'cov':hyper['cov'],'iters':hyper['iters'],'gp':global_params.psi_indices},f)
        inv_term = simple_bandits.get_inv_term(hyper['cov'],np.array(X).shape[0],hyper['noise'])
        global_params.update_params(hyper)
            #with open('../../data_to_test.pkl','wb') as f:
            #pickle.dump({'X':X,'y':y,'users':users,'gp':global_params},f)
#print(global_params.sigma_u)
        global_params.inv_term=inv_term
        ##uncentered y
        to_return = {i:simple_bandits.calculate_posterior_faster(global_params,\
                                                             i,0,\
                                                             np.array(X), users,np.array(y) ) for i in set(users)}

        return to_return



def get_hyper(X,users,y,global_params):
    torch.manual_seed(10)

    #print('here 2')
    #torch.manual_seed(111)
    
    user_mat= get_users(users,users)
    #print(global_params.baseline_indices)
    #print(X.shape)
    #np.eye(len(global_params.baseline_indices))
    first_mat = get_first_mat(global_params.sigma_theta,X,global_params.baseline_indices)
    #print('here 3')
    #print(user_mat)
    #print(users)
    #print(first_mat.shape)
    #print(X[0])
    #with open('data/X_peek.pkl','wb') as f:
    #pickle.dump(X,f)

        #gpytorch.settings.fast_computations(log_prob=False, solves=False):
        
       

        
#X=X[:10,]
#y=y[:10]
    #first_mat=first_mat[0:10,:10]
#user_mat=user_mat[0:10,:10]

    X = torch.from_numpy(np.array(X)).float()
#X =torch.from_numpy(np.array([i*np.ones(18) for i in range(10)])).float()
    y = torch.from_numpy(y).float()
    #y = torch.from_numpy(np.array([10 for i in range(1000)]+[100 for i in range(554)])).float()
        #print(y)
    first_mat = torch.from_numpy(first_mat).float()
    user_mat = torch.from_numpy(user_mat).float()
#user_mat = torch.from_numpy(np.ones((10,10))).float()
#first_mat = torch.from_numpy(np.ones((10,10))).float()
# print(X.shape)
#print(user_mat.shape)
#print(y.shape)
#print(first_mat.shape)
    likelihood = gpytorch.likelihoods.GaussianLikelihood()
    #(global_params.noise_term)
    likelihood.noise_covar.initialize(noise=(global_params.noise_term)*torch.ones(1))
    model = GPRegressionModel(X, y, likelihood,user_mat,first_mat,global_params)
        

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

    num_iter=15
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
                    #print('Iter %d/%d - Loss: %.3f like: %.3f' % (i + 1, i, loss.item(),likelihood.noise_covar.noise.item()))
                                                  
                    optimizer.step()
                    #print(model.covar_module.u1.item())
                                                  
                    sigma_temp = get_sigma_u(model.covar_module.u1.item(),model.covar_module.u2.item(),model.covar_module.rho.item())
                    
                    eigs = np.linalg.eig(sigma_temp)
                    print(sigma_temp)
                    print(eigs)
                    f_preds = model(X)
                    f_covar = f_preds.covariance_matrix
                    covtemp = f_covar.detach().numpy()
                    #print(eigs)
                    #and eigs[0][0]>0.0001 and eigs[0][1]>0.0001
                    if np.isreal(sigma_temp).all() and not np.isnan(covtemp).all() :
                                                          
                        sigma_u = sigma_temp
                        cov=covtemp
                                                                  
                        noise = likelihood.noise_covar.noise.item()
                                                                      
                    else:
                        print('oops')
                        break
                                                                              
                except Exception as e:
                    Failure=True
                    with open('data/error_within_gpy.txt','w+') as f:
                        f.write('{}'.format(e))
                        f.write('\n')
                    print(e)
                                                                              
                one_test = False
                if i<2:
                    one_test=True
                  

    if one_test or Failure:
                print('here')
                sigma_u = get_sigma_u(model.covar_module.u1.item(),model.covar_module.u2.item(),model.covar_module.rho.item())
                f_preds = model(X)
                f_covar = f_preds.covariance_matrix
                covtemp = f_covar.detach().numpy()
                cov=covtemp
                noise = likelihood.noise_covar.noise.item()
    #print(sigma_u)
#print(model.covar_module.u1.item())
#print(model.covar_module.test.item())
#print(noise)
#print(cov)
    with open('data/training_losses_{}.pkl'.format(str(date.today())),'wb') as f:
        pickle.dump(losses,f)
    #print(sigma_temp.all()==sigma_u.all())
    #print(global_params.psi_indices)

    return {'sigma_u':sigma_u,'cov':cov,'noise':noise,'like':0,'iters':i}



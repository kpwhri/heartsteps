from datetime import date
import gpytorch
import pyreadr
from sklearn import preprocessing
import R_to_python_functions_time as RPY
import hyperparameter_runner_time
import json
import pickle
import sys
import os
import numpy as np
import pooling_params_time as gtp
import pandas as pd

def initialize_policy_params_TS(standardize=False,baseline_features=None,psi_features=None,\
                                responsivity_keys=None):
    #,'location_1','location_2','location_3'
    #'continuous_temp',
    global_p =gtp.TS_global_params(18,baseline_features=baseline_features,psi_features=psi_features, responsivity_keys= responsivity_keys)
    #personal_p = pp.TS_personal_params()
    #global_p =gtp.TS_global_params(10,context_dimension)
    
    
    
    #global_p.mu_dimension = 64
    
    global_p.kdim =18
    #194
    global_p.baseline_indices = [i for i in range(3+ len(baseline_features)+2*len(responsivity_keys))]
    
    #[i for i in range(192)]
    #[0,1,2,3,4,5,6]
    #print(global_p.baseline_indices )
    global_p.psi_indices = [0,1+len(baseline_features)]
    #[0,64]
    global_p.user_id_index =0
    
    global_p.psi_features =psi_features
    #[0,64]
    
    
    
    #global_p.update_period = update_period
    
    global_p.standardize = standardize
    global_p.lr = 0.1
    
    initial_context = [0 for i in range(global_p.theta_dim)]
    
    global_p.mus0= global_p.get_mu0(initial_context)
    #global_p.get_mu0(initial_context)
    global_p.mus1= global_p.get_mu1(global_p.num_baseline_features)
    global_p.mus2= global_p.get_mu2(global_p.num_responsivity_features)
    #np.array([.120,3.3,-.11])
    #global_p.get_mu2(global_p.num_responsivity_features)
    
    #global_p.sigmas0= global_p.get_asigma(len( personal_p.mus0[person]))
    global_p.sigmas1= global_p.get_asigma(global_p.num_baseline_features+1)
    global_p.sigmas2= global_p.get_asigma( global_p.num_responsivity_features+1)
    
    
    global_p.mu2_knot = np.array([0]+[0 for i in range(global_p.num_responsivity_features)])
    global_p.mu1_knot = np.zeros(global_p.num_baseline_features+1)
    global_p.sigma1_knot = np.eye(global_p.num_baseline_features+1)
    global_p.sigma2_knot = np.eye(global_p.num_responsivity_features+1)
    
    return global_p


def run_updates(data_path,users):
    baseline_features = ['temperature', 'logpresteps', 'sqrt.totalsteps',\
                         'dosage', 'engagement',  'other.location', 'variation']
    responsivity_features = ['dosage', 'engagement',  'other.location', 'variation']
        
    global_params = initialize_policy_params_TS(standardize=False,baseline_features=[i for i in range(len(baseline_features))],psi_features=[],responsivity_keys=[i for i in range(3,len(baseline_features))])
 
        #nusers = set(users)
    
    users, X,ycentered,y,days= RPY.combine_users(data_path,users,global_params)
    #y = np.array([ys[i]-np.dot(to_return[i],to_adjust) for i in range(len(to_return))])
    
    
    g = hyperparameter_runner_time.real_run(X,users,ycentered,y,days,global_params)
    return g





def update_params(users,g,lookup):

    try:
        for u in users:
  
        #print(data_path)
            print(g.keys())
            if u in lookup and lookup[u] in g:
                #print(u)
                datap = 'data/{}/temp_policy.Rdata'.format('user'+u+'_pooled_params')
                mu = g[lookup[u]][0]
                sigma_string = g[lookup[u]][1]
                    #with open('data/errors_pool.txt','w+') as f:
                    #f.write('{}'.format(sigma_string))
                    
                to_save = {'mu':mu}
                for i in range(len(sigma_string)):
                    to_save['sigma{}'.format(i)]=sigma_string[i]
                pyreadr.write_rdata(datap, pd.DataFrame(to_save))
                #print(sigma_string)
                #z = np.array([float(i) for i in j.split(' ') for j in sigma_string])
             

    except Exception as e:
        print(e)
        with open('data/runerrors_time_pool.txt','w+') as f:
            f.write('{}'.format(e))
            f.write('\n')
            to_return = 'Errors'
            print( to_return)
        with open('data/errors_time_pool.txt','w+') as f:
            f.write('{}'.format(e))
            f.write('\n')
            to_return = 'Errors'
            print( to_return)

if __name__=="__main__":
    np.random.seed(100)
    data_path = 'data'
    #print(os.listdir('data'))
    try:
        users = RPY.get_user_ids().keys()
        
        #users =set( ["10470","10332","10451"])
        x = run_updates(data_path,users)
        
        with open('data/test_time.pkl','wb') as f:
            pickle.dump(x,f)
        with open('data/test_time_{}.pkl'.format(str(date.today())),'wb') as f:
            pickle.dump(x,f)
        update_params(users,x,RPY.get_user_ids())
#print(users)
    except Exception as e:
        print(e)
        with open('data/errors_time_pool.txt','w+') as f:
            f.write('{}'.format(e))
            f.write('\n')
        to_return = 'Errors'
        print( to_return)

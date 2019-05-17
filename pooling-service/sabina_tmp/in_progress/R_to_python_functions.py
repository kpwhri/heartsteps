import gpytorch
import pyreadr
import pooling_params as gtp
import run_gpytorchkernel
import simple_bandits
from sklearn import preprocessing
import numpy as np
import os

def process_data(rdata,baseline_features):
    
    availabilities = []
    probabilities = []
    actions = []
    data = []
    users = []
    y = []
    users_to_ids= {}
    user_count = 0
    for k,v in result['train.dat'].iterrows():
        availabilities.append(v['availability'])
        probabilities.append(v['probability'])
        actions.append(v['action'])
        
        data.append([v[b] for b in baseline_features ])
        if v['user'] not in users_to_ids:
            user_count = user_count+1
            users_to_ids[v['user']]=user_count
        users.append(users_to_ids[v['user']])
        y.append(v['reward'])
    return {'avail':availabilities,'prob':probabilities,'reward':y,'users':users,\
        'user_lookup':users_to_ids,'data':data,'actions':actions}


def get_standard_x(X):
    return preprocessing.StandardScaler().fit_transform(X)

def get_phi(standard_x,all_dict,baseline_indices,responsivity_indices):
    ##returns users, transformed data, and transformed rewards
    to_return = []
    
    users = []
    for i in range(len(standard_x)):
        if all_dict['avail'][i]:
            raw_data = standard_x[i]
            temp = [1]
            temp.extend([raw_data[i] for i in baseline_indices])
            temp_two  = [1]
            temp_two.extend([raw_data[i] for i in responsivity_indices])
            temp.extend([all_dict['prob'][i]*d for d in temp_two])
            temp.extend([(all_dict['actions'][i]-all_dict['prob'][i])*d for d in temp_two])
            to_return.append(temp)
            users.append(all_dict['users'][i])
    to_adjust = [np.array(all_dict['reward']).mean()]+[0]*(len(to_return[0])-1)
    #to_adjust = np.ones(len(to_return[0]))
    y = np.array([all_dict['reward'][i]-np.dot(to_return[i],to_adjust) for i in range(len(to_return))])
    return np.array(to_return),y,np.array(users)







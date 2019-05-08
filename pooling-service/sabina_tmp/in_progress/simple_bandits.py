import gpflow
import numpy as np
import math

import pickle
import pandas as pd

from sklearn import preprocessing

import os
import random



def get_inv_term(cov,X_dim,noise_term):
    noise = noise_term * np.eye(X_dim)
    middle_term = np.add(cov,noise)
    #inv_term = np.linalg.inv(middle_term)
    return np.linalg.inv(middle_term)



def get_theta(dim_baseline):
    m = np.eye(dim_baseline)
    #m = np.add(m,.1)
    return m




def get_sigma_u(u1,u2,rho):
    off_diagaonal_term = u1**.5*u2**.5*(rho-1)
    return np.array([[u1,off_diagaonal_term],[off_diagaonal_term,u2]])

def get_sigma_umore(gparams):
    cov_12 = (gparams.r12-1)*(gparams.u1**.5)*(gparams.u2**.5)
    cov_13 = (gparams.r13-1)*(gparams.u1**.5)*(gparams.u3**.5)
    cov_14 = (gparams.r14-1)*(gparams.u1**.5)*(gparams.u4**.5)
    cov_23 =(gparams.r23-1)*(gparams.u2**.5)*(gparams.u3**.5)
    cov_24 =(gparams.r24-1)*(gparams.u2**.5)*(gparams.u4**.5)
    cov_34 =(gparams.r34-1)*(gparams.u3**.5)*(gparams.u4**.5)
    
    row_one = [gparams.u1,cov_12,cov_13,cov_14]
    row_two = [cov_12,gparams.u2,cov_23,cov_24]
    row_three = [cov_13,cov_23,gparams.u3,cov_34]
    row_four = [cov_14,cov_24,cov_34,gparams.u4]
    
    
    return np.array([row_one,row_two,row_three,row_four])



##make function of pZ, not too hard
def create_H(num_baseline_features,num_responsivity_features,psi_indices):
    ##for now have fixed random effects size one
    
    random_effect_one = [1]
    random_effect_two = [1]
    
    column_one = [1]
    column_one = column_one+[0]*num_baseline_features
    column_one = column_one+[0]
    column_one = column_one+[0]*num_responsivity_features
    column_one = column_one+[0]
    column_one = column_one+[0]*num_responsivity_features
    
    
    column_two = [0]
    column_two = column_two+[0]*num_baseline_features
    column_two = column_two+[int(i in psi_indices) for i in range(2*num_responsivity_features+2)]

    
    return np.transpose(np.array([column_one,column_two]))


def create_H_four(num_baseline_features,num_responsivity_features,psi_indices):
            ##for now have fixed random effects size one

    random_effect_one = [1]
    random_effect_two = [1]

    column_one = [1]
    column_one = column_one+[0]*num_baseline_features
    column_one = column_one+[0]
    column_one = column_one+[0]*num_responsivity_features
    column_one = column_one+[0]
    column_one = column_one+[0]*num_responsivity_features
    
    
    column_two = [0]
    column_two =column_two+[int(i==psi_indices[1]) for i in range(num_baseline_features)]
    column_two =column_two+[0]*(2*num_responsivity_features+2)
    
    
    column_three = [0]+[0]*num_baseline_features
    column_three = column_three+[int(i==psi_indices[0]) for i in range(num_responsivity_features+1)]
    column_three= column_three+[int(i==psi_indices[0]) for i in range(num_responsivity_features+1)]
    
    column_four = [0]+[0]*num_baseline_features
    column_four = column_four+[int(i==psi_indices[1]) for i in range(num_responsivity_features+1)]
    column_four= column_four+[int(i==psi_indices[1]) for i in range(num_responsivity_features+1)]
    
    
    return np.transpose(np.array([column_one,column_two,column_three,column_four]))






def get_M(global_params,user_id,user_study_day,history):
  
  
    day_id =user_study_day
    #print(history)
    M = [[] for i in range(history.shape[0])]

    H = create_H(global_params.num_baseline_features,global_params.num_responsivity_features,global_params.psi_indices)
    #inv_term = global_params.inv_term
    for x_old_i in range(history.shape[0]):
        x_old = history[x_old_i]
        old_user_id = x_old[global_params.user_id_index]
        old_day_id = x_old[global_params.user_day_index]
        
        ##these indices all need to be parameters
        phi = np.array([x_old[i] for i in global_params.baseline_indices])
        
        t_one = np.dot(np.transpose(phi),global_params.sigma_theta)
        #first_terms.append(t_one)
        
        temp = np.dot(H,global_params.sigma_u)
        temp = np.dot(temp,H.T)
        temp = np.dot(np.transpose(phi),temp)
        temp = float(old_user_id==user_id)*temp
        t_two = temp
        #middle_terms.append(t_two)
        temp = np.dot(H,global_params.sigma_v.reshape(2,2))
        temp = np.dot(temp,H.T)
        temp = np.dot(np.transpose(phi),temp)
        temp = rbf_custom_np(user_study_day,old_day_id)*temp
        t_three = temp
        #print(user_study_day)
        
        #last_terms.append(t_three)
        term = np.add(t_one,t_two)
        
        term = np.add(term,t_three)
        #print(term.shape)
        #print(term)
        M[x_old_i]=term

    return np.array(M)

def get_RT(y,X,sigma_theta,x_dim):
    
    to_return = [y[i]-np.dot(X[i][0:x_dim],sigma_theta) for i in range(len(X))]
    return np.array([i[0] for i in to_return])





def get_M_faster(global_params,user_id,user_study_day,history,users,sigma_u):
    
    
    day_id =user_study_day
    #print(history)
    M = [[] for i in range(history.shape[0])]
    
    H = create_H(global_params.num_baseline_features,global_params.num_responsivity_features,global_params.psi_indices)
    
    phi = history[:,global_params.baseline_indices]
    ##should be fine
    #print(global_params.sigma_theta)
    t_one = np.dot(phi,global_params.sigma_theta)
    #print(t_one.shape)
    temp = np.dot(H,global_params.sigma_u)
    #print(temp.shape)
    #print(global_params.sigma_u)
    temp = np.dot(temp,H.T)
    temp = np.dot(phi,temp)
    
    user_ids =users
    #history[:,global_params.user_id_index]

    my_days = np.ma.masked_where(user_ids==user_id, user_ids).mask.astype(float)
    
    if type(my_days)!=np.ndarray:
        my_days = np.zeros(history.shape[0])
    user_matrix = np.diag(my_days)

    t_two = np.matmul(user_matrix,temp)
  
    term = np.add(t_one,t_two)
    
    
    return term


def get_M_faster_four(global_params,user_id,user_study_day,history,users,sigma_u):
    
    
    day_id =user_study_day
    #print(history)
    M = [[] for i in range(history.shape[0])]
    
    H = create_H_four(global_params.num_baseline_features,global_params.num_responsivity_features,global_params.psi_indices)
    
    phi = history[:,global_params.baseline_indices]
    ##should be fine
    #print(global_params.sigma_theta)
    t_one = np.dot(phi,global_params.sigma_theta)
    #print(t_one.shape)
    temp = np.dot(H,sigma_u)
    #print(temp.shape)
    #print(global_params.sigma_u)
    temp = np.dot(temp,H.T)
    temp = np.dot(phi,temp)
    
    user_ids =users
    #history[:,global_params.user_id_index]
    
    my_days = np.ma.masked_where(user_ids==user_id, user_ids).mask.astype(float)
    
    if type(my_days)!=np.ndarray:
        my_days = np.zeros(history.shape[0])
    user_matrix = np.diag(my_days)

    t_two = np.matmul(user_matrix,temp)

    term = np.add(t_one,t_two)
    
    
    return term



def calculate_posterior_faster(global_params,user_id,user_study_day,X,users,y):
    H = create_H(global_params.num_baseline_features,global_params.num_responsivity_features,global_params.psi_indices)
    
    M = get_M_faster(global_params,user_id,user_study_day,X,users,global_params.sigma_u)
    ##change this to be mu_theta
    ##is it updated?  the current mu_theta?
    adjusted_rewards =get_RT(y,X,global_params.mu_theta,global_params.theta_dim)
    #print('current global cov')
    #print(global_params.cov)
    #.reshape(X.shape[0],X.shape[0])
    mu = get_middle_term(X.shape[0],global_params.cov,global_params.noise_term,M,adjusted_rewards,global_params.mu_theta,global_params.inv_term)
    #.reshape(X.shape[0],X.shape[0])
    sigma = get_post_sigma(H,global_params.cov,global_params.sigma_u.reshape(2,2),None,global_params.noise_term,M,X.shape[0],global_params.sigma_theta,global_params.inv_term)
    
    return mu[-(global_params.num_responsivity_features+1):],[j[-(global_params.num_responsivity_features+1):] for j in sigma[-(global_params.num_responsivity_features+1):]]


def calculate_posterior_current(global_params,user_id,user_study_day,X,users,y):
    sigma_u =get_sigma_umore(global_params)
    #print(sigma_u)
    H = create_H_four(global_params.num_baseline_features,global_params.num_responsivity_features,global_params.psi_indices)
    
    M = get_M_faster_four(global_params,user_id,user_study_day,X,users,sigma_u)
    ##change this to be mu_theta
    ##is it updated?  the current mu_theta?
    adjusted_rewards =get_RT(y,X,global_params.mu_theta,global_params.theta_dim)
    #print('current global cov')
    #print(global_params.cov)
    #.reshape(X.shape[0],X.shape[0])
    mu = get_middle_term(X.shape[0],global_params.cov,global_params.noise_term,M,adjusted_rewards,global_params.mu_theta,global_params.inv_term)
    #.reshape(X.shape[0],X.shape[0])
    sigma = get_post_sigma(H,global_params.cov,sigma_u,None,global_params.noise_term,M,X.shape[0],global_params.sigma_theta,global_params.inv_term)
    
    return mu[-(global_params.num_responsivity_features+1):],[j[-(global_params.num_responsivity_features+1):] for j in sigma[-(global_params.num_responsivity_features+1):]]


def calculate_posterior(global_params,user_id,user_study_day,X,y):
    H = create_H(global_params.num_baseline_features,global_params.num_responsivity_features,global_params.psi_indices)
   
    M = get_M(global_params,user_id,user_study_day,X)
    ##change this to be mu_theta
    ##is it updated?  the current mu_theta?
    adjusted_rewards =get_RT(y,X,global_params.mu_theta,global_params.theta_dim)
    #print('current global cov')
    #print(global_params.cov)
    #.reshape(X.shape[0],X.shape[0])
    mu = get_middle_term(X.shape[0],global_params.cov,global_params.noise_term,M,adjusted_rewards,global_params.mu_theta,global_params.inv_term)
    #.reshape(X.shape[0],X.shape[0])
    sigma = get_post_sigma(H,global_params.cov,global_params.sigma_u.reshape(2,2),global_params.sigma_v.reshape(2,2),global_params.noise_term,M,X.shape[0],global_params.sigma_theta)

    return mu[-(global_params.num_responsivity_features+1):],[j[-(global_params.num_responsivity_features+1):] for j in sigma[-(global_params.num_responsivity_features+1):]]




def get_middle_term(X_dim,cov,noise_term,M,adjusted_rewards,mu_theta,inv_term):
  
    middle_term = np.matmul(M.T,inv_term)
    #print(middle_term)
    #print('middles')
    #print(middle_term)
    #print(adjusted_rewards)
    middle_term = np.matmul(middle_term,adjusted_rewards)

    return np.add(mu_theta,middle_term)

def get_post_sigma(H,cov,sigma_u,sigma_v,noise_term,M,x_dim,sigma_theta,inv_term):
    #M = get_M(global_params,user_id,user_study_day,history[0])
    
    ##change this to be mu_theta
    ##is it updated?  the current mu_theta?
    #adjusted_rewards =[history[1][i]-np.dot(history[0][i][0:6],np.ones(6)) for i in range(len(history[0]))]
    
    
    
    #first_term = np.add(sigma_u,sigma_v)
    first_term = sigma_u
    #print(first_term.shape)
    #print(H.shape)
    first_term = np.dot(H,first_term)
    #print(first_term.shape)
    first_term = np.dot(first_term,H.T)
    #print(first_term)
    
    #noise = noise_term * np.eye(x_dim)
    #print(noise.shape)
    #middle_term = np.add(cov,noise)
    #print(middle_term.shape)
    middle_term = np.dot(M.T,inv_term)
    #print(middle_term.shape)
    middle_term = np.dot(middle_term,M)
    #print(middle_term.shape)
    last = np.add(sigma_theta,first_term)
    last = np.subtract(last,middle_term)
    
    return last

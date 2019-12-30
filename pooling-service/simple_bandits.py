
import numpy as np
import math

import pickle
import pandas as pd

from sklearn import preprocessing

import os
import random

def dist(x,x2):
    return math.exp(-((x-x2)**2)/1.0)

def get_distance(days):
    to_return = []
    for i in range(len(days)):
        temp = []
        
        temp=[dist(days[i],days[j]) for j in range(len(days))]
        to_return.append(temp)
    return np.array(to_return)

def get_users(users,userstwo):
    
    xx,yy = np.meshgrid(users,userstwo,sparse=True)
    #.99999999999
    return (xx==yy).astype('float')


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
    column_two =column_two+[1]+[0]*num_responsivity_features
    
    column_two =column_two+[1]+[0]*num_responsivity_features
    #column_two+[int(i in psi_indices) for i in range(2*num_responsivity_features+2)]
    #print( np.transpose(np.array([column_one,column_two])))
    
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

def get_RT(y,X,mu_theta,x_dim):
    
    to_return = [y[i]-np.dot(X[i][0:x_dim],mu_theta) for i in range(len(X))]
    return np.array([i for i in to_return])





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
    
    user_ids =np.array(users)
    #history[:,global_params.user_id_index]

    my_days = [int(user_ids[i]==user_id) for i in range(len(user_ids))]
    #print(users)
    #print(user_ids)
    #user_matrix = []
    #for i in range(history.shape[0]):
    #temp2 = []
    #for j in range(history.shape[0]):
            
            #temp2.append(1.0*int(users[i]==user_id))
            #user_matrix.append(temp2)
        #print(len(user_matrix))
#print(len(user_matrix[0]))
#print(type(users[0]))
#print(user_matrix)
#with open('data/my_um_{}.pkl'.format(user_id),'wb') as f:
#pickle.dump(user_matrix,f)
    my_days = np.ma.masked_where(user_ids==user_id, user_ids).mask.astype(float)
    
    if type(my_days)!=np.ndarray:
        my_days = np.zeros(history.shape[0])
        print('problem {}'.format(user_id))
    user_matrix = np.diag(my_days)
    #print(user_matrix.shape)
#print(user_matrix)
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
    
    #print(cov)
    H = create_H(global_params.num_baseline_features,global_params.num_responsivity_features,global_params.psi_indices)
    
    M = get_M_faster(global_params,user_id,user_study_day,X,users,global_params.sigma_u)
        #with open('data/M_Test_{}.pkl'.format(user_id),'wb') as f:
        #pickle.dump(M,f)
    ##change this to be mu_theta
    ##is it updated?  the current mu_theta?
    adjusted_rewards =get_RT(y,X,global_params.mu_theta,global_params.theta_dim)
    #print(adjusted_rewards)
    #print('current global cov')
    #print(global_params.cov)
    #.reshape(X.shape[0],X.shape[0])
    mu = get_middle_term(X.shape[0],global_params.cov,global_params.noise_term,M,adjusted_rewards,global_params.mu_theta,global_params.inv_term)
    #.reshape(X.shape[0],X.shape[0])
    sigma = get_post_sigma(H,global_params.cov,global_params.sigma_u.reshape(2,2),None,global_params.noise_term,M,X.shape[0],global_params.sigma_theta,global_params.inv_term,user_id)
    #print(mu)
    #print(user_id)
    #print(M)
    #print(sigma)
    return mu[-(global_params.num_responsivity_features+1):],[j[-(global_params.num_responsivity_features+1):] for j in sigma[-(global_params.num_responsivity_features+1):]]


def calculate_posterior_current(global_params,user_id,user_study_day,X,users,y):
    sigma_u =get_sigma_umore(global_params)
    #print(sigma_u)
    H = create_H_four(global_params.num_baseline_features,global_params.num_responsivity_features,global_params.psi_indices)
    
    M = get_M_faster_four(global_params,user_id,user_study_day,X,users,sigma_u)
    print(M.shape)
    ##change this to be mu_theta
    ##is it updated?  the current mu_theta?
    adjusted_rewards =get_RT(y,X,global_params.mu_theta,global_params.theta_dim)
    print(adjusted_rewards)
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
    adjusted_rewards=y #=get_RT(y,X,global_params.mu_theta,global_params.theta_dim)
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

def is_pos_def(x):
    return np.all(np.linalg.eigvals(x) > 0)

def other_cov_notime(data,sigma_theta,random_effects,sigma_u,user_matrix):
    #K0 <- phi.mat %*% Sigma.theta %*% t(phi.mat)
    #K1 <- (psi.mat %*% Sigma.u %*% t(psi.mat)) * id.mat
    # K2 <- (psi.mat %*% Sigma.v %*% t(psi.mat)) * rho.mat
    one = np.dot(data,sigma_theta)
    one = np.dot(one,data.T)
    #print(one[:,0])
    two = np.dot(random_effects,sigma_u)
    two = np.dot(two,random_effects.T)
    two = np.multiply(user_matrix,two)
    #print(two[:,0])
    #three = np.dot(random_effects,sigma_v)
    #three = np.dot(three,random_effects.T)
    #three = np.multiply(time,three)
    #print(three[:,0])
    return one+two


def get_covar_simple(X,users,global_params):
    matrix = []
    for i in range(X.shape[0]):
        temp = []
        for j in range(X.shape[0]):
            base_one = X[i]
            base_two = X[j]
            re_one = np.array([X[i][k] for k in global_params.psi_indices])
            re_two = np.array([X[j][k] for k in global_params.psi_indices])
            first_term = np.dot(base_one,global_params.sigma_theta)
            #print(first_term)
            first_term = np.dot(first_term,base_two)
            #print(first_term)
            second_term = int(users[i]==users[j]) * np.dot(np.dot(re_one,global_params.sigma_u),re_two)
            
            #if second_term!=0:
            #print('second')
            #print(second_term)
            final = np.add(first_term,second_term)
            temp.append(final)
        matrix.append(temp)
    return matrix



def get_post_sigma(H,cov,sigma_u,sigma_v,noise_term,M,x_dim,sigma_theta,inv_term,uid):
    #M = get_M(global_params,user_id,user_study_day,history[0])
    
    ##change this to be mu_theta
    ##is it updated?  the current mu_theta?
    #adjusted_rewards =[history[1][i]-np.dot(history[0][i][0:6],np.ones(6)) for i in range(len(history[0]))]
    
    #with open('eigs.pkl','wb') as f:
    #pickle.dump(np.linalg.eigvals(cov),f)
    #print(H)
    #print(np.linalg.eigvals(cov) )
    #first_term = np.add(sigma_u,sigma_v)
    first_term = sigma_u
    #print(first_term.shape)
    #print(H.shape)
    first_term = np.dot(H,first_term)
    #print(first_term.shape)
    first_term = np.dot(first_term,H.T)
    #print(first_term)
    #with open('../../look/first_Term_{}.pkl'.format(uid),'wb') as f:
#    pickle.dump(first_term,f)
    #noise = noise_term * np.eye(x_dim)
    #print(noise.shape)
    #middle_term = np.add(cov,noise)
    #print(middle_term.shape)
    #with open('../../look/middle_Term11_{}.pkl'.format(uid),'wb') as f:
    #    pickle.dump(M,f)
    #with open('../../look/middle_Term12_{}.pkl'.format(uid),'wb') as f:
    #    pickle.dump(inv_term,f)
    middle_term = np.dot(M.T,inv_term)
    #print(middle_term.shape)
    #with open('../../look/middle_Term1_{}.pkl'.format(uid),'wb') as f:
    #    pickle.dump(middle_term,f)
    middle_term = np.dot(middle_term,M)
        #with open('../../look/middle_Term2_{}.pkl'.format(uid),'wb') as f:
        #    pickle.dump(middle_term,f)
    #print(middle_term.shape)
    last = np.add(sigma_theta,first_term)
        #with open('../../look/last_Term_{}.pkl'.format(uid),'wb') as f:
        #    pickle.dump(last,f)
    #print(sigma_u)
    #print(sigma_theta)
    #print(is_pos_def(last))
    #print(is_pos_def(middle_term))
    #print(np.subtract(np.diagonal(last),np.diagonal(middle_term)))
    
    last = np.subtract(last,middle_term)



    return last

def get_post_sigma_time_effects(H,cov,sigma_u,sigma_v,noise_term,M,x_dim,sigma_theta,inv_term):
    
    first_term = np.add(sigma_u,sigma_v)
    
    first_term = np.dot(H,first_term)
    
    first_term = np.dot(first_term,H.T)
    
    middle_term = np.dot(M.T,inv_term)
    
    middle_term = np.dot(middle_term,M)
    
    last = np.add(sigma_theta,first_term)
    last = np.subtract(last,middle_term)
    
    return last

def get_M_time(global_params,user_id,user_study_day,history):
    
    
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

def other_cov_time(data,sigma_theta,random_effects,sigma_u,user_matrix,sigma_v,time_matrix):
    #K0 <- phi.mat %*% Sigma.theta %*% t(phi.mat)
    #K1 <- (psi.mat %*% Sigma.u %*% t(psi.mat)) * id.mat
    # K2 <- (psi.mat %*% Sigma.v %*% t(psi.mat)) * rho.mat
    one = np.dot(data,sigma_theta)
    one = np.dot(one,data.T)

    two = np.dot(random_effects,sigma_u)
    two = np.dot(two,random_effects.T)
    two = np.multiply(user_matrix,two)

    three = np.dot(random_effects,sigma_v)
    three = np.dot(three,random_effects.T)
    three = np.multiply(time_matrix,three)
   
    return one+two+three

def calculate_posterior_faster_time(global_params,user_id,user_study_day,X,users,days,y):
    sigma_u =global_params.sigma_u
    sigma_v =global_params.sigma_v
    H = create_H(global_params.num_baseline_features,global_params.num_responsivity_features,global_params.psi_indices)
    #print(H)
    
    M = get_M_faster_time(global_params,user_id,user_study_day,X,users,days,sigma_u,sigma_v)
    
    adjusted_rewards =get_RT(y,X,global_params.mu_theta,global_params.theta_dim)
    
    #print(adjusted_rewards)
    mu = get_middle_term(X.shape[0],global_params.cov,global_params.noise_term,M,adjusted_rewards,global_params.mu_theta,global_params.inv_term)
    
    #
    sigma = get_post_sigma_time_effects(H,global_params.cov,sigma_u,sigma_v,global_params.noise_term,M,X.shape[0],global_params.sigma_theta,global_params.inv_term)
    
    return mu[-(global_params.num_responsivity_features+1):],[j[-(global_params.num_responsivity_features+1):] for j in sigma[-(global_params.num_responsivity_features+1):]]


def get_M_faster_time(global_params,user_id,day_id,history,users,days,sigma_u,sigma_v):
    
    
    #print(history)
    M = [[] for i in range(history.shape[0])]
    
    H = create_H(global_params.num_baseline_features,global_params.num_responsivity_features,global_params.psi_indices)
    
    phi = history[:,global_params.baseline_indices]
    
    t_one = np.dot(phi,global_params.sigma_theta)
    
    temp = np.dot(H,global_params.sigma_u)
    
    temp = np.dot(temp,H.T)
    temp = np.dot(phi,temp)
    
    user_ids =np.array(users)
    
    
    my_days = [int(user_ids[i]==user_id) for i in range(len(user_ids))]
    
    my_days = np.ma.masked_where(user_ids==user_id, user_ids).mask.astype(float)
    
    if type(my_days)!=np.ndarray:
        my_days = np.zeros(history.shape[0])
        print('problem {}'.format(user_id))
    user_matrix = np.diag(my_days)

    t_two = np.matmul(user_matrix,temp)

    term = np.add(t_one,t_two)
    rho_diag = np.diag([dist(d,day_id) for d in days])



    temp = np.dot(H,sigma_v)
    temp = np.dot(temp,H.T)
    temp = np.dot(phi,temp)

    t_three = np.matmul(rho_diag,temp)

    ##time effects
    term = np.add(term,t_three)
    
    return term
    

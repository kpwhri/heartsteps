import gpytorch
import pyreadr
from sklearn import preprocessing
import numpy as np
import os


def get_user_ids():

    return {'10195':0,'10075':1,'10237':2,'10041':3,'10271':4,'10355':5,'10374':6,'10062':7,'10313':8,'10215':9}

def process_data(rdata,baseline_features,user_id):
    
    availabilities = []
    probabilities = []
    actions = []
    data = []
    users = []
    y = []
    #users_to_ids= {}
    
    users_to_ids = get_user_ids()
    #user_count = 0
    for k,v in rdata.iterrows():

        feat_vec = [v[b] for b in baseline_features ]
        
        if ~np.isnan(feat_vec).any(axis=0):
            availabilities.append(v['availability'])
            probabilities.append(v['probability'])
            actions.append(v['action'])
            #if v['user'] not in users_to_ids:
            # user_count = user_count+1
            #users_to_ids[v['user']]=user_count
            users.append(users_to_ids[user_id])
            y.append(v['reward'])
            data.append(feat_vec)
    return {'avail':availabilities,'prob':probabilities,'reward':y,'users':users,\
        'user_lookup':users_to_ids,'data':data,'actions':actions}


def get_standard_x(X):
    return preprocessing.StandardScaler().fit_transform(X)

def get_phi(standard_x,all_dict,baseline_indices,responsivity_indices):
    ##returns users, transformed data, and transformed rewards
    to_return = []
    
    users = []
    ys = []
    for i in range(len(standard_x)):
        if all_dict['avail'][i]:
            #print(all_dict['actions'][i]-all_dict['prob'][i])
            raw_data = standard_x[i]
            temp = [1]
            temp.extend([raw_data[i] for i in baseline_indices])
            temp_two  = [1]
            temp_two.extend([raw_data[i] for i in responsivity_indices])
            temp.extend([all_dict['prob'][i]*d for d in temp_two])
            temp.extend([(all_dict['actions'][i]-all_dict['prob'][i])*d for d in temp_two])
            to_return.append(temp)
            users.append(all_dict['users'][i])
            ys.append(all_dict['reward'][i])
    to_adjust = [np.array(all_dict['reward']).mean()]+[0]*(len(to_return[0])-1)




#print(len(to_return))
#print(len(all_dict['avail']))
    #to_adjust = np.ones(len(to_return[0]))
    #print(np.array(ys).std())
    y = np.array([ys[i]-np.dot(to_return[i],to_adjust) for i in range(len(to_return))])
    #y.tolist()
    #print(np.array(y).std())
    return to_return,y.tolist(),users

def get_one_user(data_path,user_id):
    result = pyreadr.read_r(data_path)
   
    baseline_features = ['temperature', 'logpresteps', 'sqrt.totalsteps',\
                         'dosage', 'engagement',  'other.location', 'variation']
    responsivity_features = ['dosage', 'engagement',  'other.location', 'variation']
    #print(result['train'])
    data_dict = process_data(result['train'],baseline_features,user_id)
                         
                         #standard_x = get_standard_x(data_dict['data'])
    
    #feature_vector =standard_x[~np.isnan(standard_x).any(axis=1)]
    #user_vect
   
    return data_dict



def combine_users(data_path,user_list):
    #data_path  = '../../../walking-suggestion-service/data'
    user_files = [directory for directory in os.listdir(data_path) if directory.strip('user') in user_list]
    #print()
    big_user_list = []
    big_data_list = []
    big_reward_list = []
    big_action_list = []
    big_avail_list = []
    big_prob_list = []
    
    baseline_features = ['temperature', 'logpresteps', 'sqrt.totalsteps',\
                         'dosage', 'engagement',  'other.location', 'variation']
    responsivity_features = ['dosage', 'engagement',  'other.location', 'variation']
    #print(responsivity_features)
    baseline_indices = [i for i in range(len(baseline_features))]
    responsivity_indices = [i for i in range(len(baseline_features)) if baseline_features[i] in set(responsivity_features)]
    
    
    
    
    for f in user_files:
        user_id = f.strip('user')
        #print(user_id)
        #print(f)
        #print('{}{}{}'.format(data_path,'/{}'.format(f),'/train.Rdata'))
        data =  get_one_user('{}{}{}'.format(data_path,'/{}'.format(f),'/train.Rdata'),user_id)
        #print(data)
        #x,y,user = get_phi(data['data'],data,baseline_indices,responsivity_indices)
        if user_id in get_user_ids():
            big_user_list = big_user_list+data['users']
            big_data_list = big_data_list+data['data']
            big_avail_list =big_avail_list+data['avail']
            big_action_list =big_action_list+data['actions']
            big_prob_list =big_prob_list+data['prob']
        
    
            big_reward_list = big_reward_list+data['reward']
    
    #temp_X = get_standard_x(big_data_list)
    temp_X = big_data_list
    temp_data = {'avail':big_avail_list,'actions': big_action_list,'prob':big_prob_list,\
'users':big_user_list,'reward':big_reward_list
}
    #if train:
    x,y,user =get_phi(temp_X,temp_data,baseline_indices,responsivity_indices)

    return  user, x,y




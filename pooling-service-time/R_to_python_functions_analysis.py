import pickle
from datetime import date
import gpytorch
import pyreadr
from sklearn import preprocessing
import numpy as np
import os


def get_user_ids():

    return {'10237':0,'10271':1,'10041':2,'10355':3,'10062':4,'10374':5,'10215':6,'10313':7,'10395':8,'10152':9,'10194':10,'10259':11,'10339':12,'10360':13,'10269':14,'10234':15,'10365':16,'10352':17,'10336':18,'10304':19}

def process_data(rdata,baseline_features,user_id):
    
    availabilities = []
    probabilities = []
    actions = []
    data = []
    users = []
    y = []
    day = []
    #users_to_ids= {}
    
    users_to_ids = get_user_ids()
    #user_count = 0
    for k,v in rdata.iterrows():
        #dosages = [v[b][0]   for b in baseline_features if b=='dosage' ]
        #print(dosages)
        #maxdosage = max(dosages)
        feat_vec = [v[b] if b!='dosage' else v[b]/10 for b in baseline_features ]
        
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
            day.append(v['day'])
    return {'avail':availabilities,'prob':probabilities,'reward':y,'users':users,\
        'user_lookup':users_to_ids,'data':data,'actions':actions,'days':day}


def get_standard_x(X):
    return preprocessing.StandardScaler().fit_transform(X)

def get_phi(standard_x,all_dict,baseline_indices,responsivity_indices):
    ##returns users, transformed data, and transformed rewards
    to_return = []
    actions = []
    users = []
    ys = []
    locs = []
    print('avail test')
    print(len([i for i in all_dict['avail'] if i])/len(all_dict['avail']))
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
            #print(all_dict['users'][i])
            ys.append(all_dict['reward'][i])
            locs.append(raw_data[-2])
            actions.append(all_dict['actions'][i])
    to_adjust = [np.array(all_dict['reward']).mean()]+[0]*(len(to_return[0])-1)

    return to_return,ys,ys,users,locs,actions




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
    #user_list = ["10215", "10313", "10062", "10374", "10355", "10271", "10041", "10237", "10075", "10195"]
    user_files = [directory for directory in os.listdir(data_path) if directory.strip('user') in user_list]
    #print(user_files)
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
        print(user_id)
        #print(user_id)
        #print(f)
        #print('{}{}{}'.format(data_path,'/{}'.format(f),'/train.Rdata'))
        if os.path.exists('{}{}{}'.format(data_path,'/{}'.format(f),'/train.Rdata')):
            data =  get_one_user('{}{}{}'.format(data_path,'/{}'.format(f),'/train.Rdata'),user_id)
                #print(user_id)
                #print(set(data['avail']))
 
            print(len(data['data']))
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
    #print(temp_X)
    x,y,ys,user,locs,actions =get_phi(temp_X,temp_data,baseline_indices,responsivity_indices)

    return  user, x,y,ys,locs,actions

def get_phi_days(standard_x,all_dict,baseline_indices,responsivity_indices):
   
    to_return = []
    
 
    ys = []
    locs = []
    days = []
    probs = []
    actions = []
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

            #print(all_dict['users'][i])
            ys.append(all_dict['reward'][i])
            days.append(all_dict['days'][i])
            locs.append(raw_data[-2])
            probs.append(all_dict['prob'][i])
            actions.append(all_dict['actions'][i])
    return to_return,ys,locs,days,probs,actions

def get_all_for_one_user(data_path,userid):
    baseline_features = ['temperature', 'logpresteps', 'sqrt.totalsteps',\
                         'dosage', 'engagement',  'other.location', 'variation']
    responsivity_features = ['dosage', 'engagement',  'other.location', 'variation']
                         #print(responsivity_features)
    baseline_indices = [i for i in range(len(baseline_features))]
    responsivity_indices = [i for i in range(len(baseline_features)) if baseline_features[i] in set(responsivity_features)]
                         
                         
    
    data =  get_one_user('{}{}{}'.format(data_path,'/user{}'.format(userid),'/train.Rdata'),userid)


    x,y,locs,days,probs,actions =get_phi_days(data['data'],data,baseline_indices,responsivity_indices)
    return x,y,locs,days,probs,actions

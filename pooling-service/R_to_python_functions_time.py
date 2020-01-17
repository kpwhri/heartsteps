import pickle
from datetime import date
import gpytorch
import pyreadr
from sklearn import preprocessing
import numpy as np
import os
import simple_bandits
import pandas as pd
import datetime


def get_user_ids():
    joins = join_dates()
    start = datetime.datetime.strptime('12/2/2019','%m/%d/%Y')
    users  =[k for k, v in sorted(joins.items(),\
            key=lambda item: item[1]) if v>=start]
            #print(joins)
            #print(sorted(joins.items(),\key=lambda item: item[1]))
    return {str(users[i]):i for i in range(len(users)) if i<20}

def join_dates():
    dates = pd.read_csv('data/join_dates.csv')
    print(join_dates)
    return {r['user_id']:pd.to_datetime(r['join_date']) for i,r in dates.iterrows() }

def join_dates_reversed():
    dates = pd.read_csv('data/join_dates.csv')
    lookup = get_user_ids()
    #if str(i) in lookup
    return {lookup[str(r['user_id'])]:pd.to_datetime(r['join_date']) for i,r in
            dates.iterrows()}


def get_current_day(user_id):
    
    join = join_dates_reversed()
    print(join)
    join_date = join[int(user_id)]
    current_day = (datetime.datetime.today()-join_date).days
    #current_day = (pd.to_datetime('12/8/2019')-join_date).days
    
    return current_day

def process_data(rdata,baseline_features,user_id):
    jdates = join_dates()
    availabilities = []
    probabilities = []
    actions = []
    data = []
    users = []
    y = []
    days =[]
    #users_to_ids= {}
    
    users_to_ids = get_user_ids()
    #user_count = 0
    for k,v in rdata.iterrows():
        #dosages = [v[b][0]   for b in baseline_features if b=='dosage' ]
        #print(dosages)
        #maxdosage = max(dosages)
        feat_vec = [v[b] if b!='dosage' else v[b]/20 for b in baseline_features ]
        
        if ~np.isnan(feat_vec).any(axis=0):
            #if jdates[int(user_id)]+datetime.timedelta(days=v['day'])\
            #<pd.Timestamp('2019-09-09'):
                availabilities.append(v['availability'])
                probabilities.append(v['probability'])
                actions.append(v['action'])
            #if v['user'] not in users_to_ids:
            # user_count = user_count+1
            #users_to_ids[v['user']]=user_count
                users.append(users_to_ids[user_id])
                y.append(v['reward'])
                data.append(feat_vec)
                days.append(v['day'])
    return {'avail':availabilities,'prob':probabilities,'reward':y,'users':users,\
        'user_lookup':users_to_ids,'data':data,'actions':actions,'days':days}


def get_standard_x(X):
    return preprocessing.StandardScaler().fit_transform(X)

def get_phi(standard_x,all_dict,baseline_indices,responsivity_indices,global_params):
    ##returns users, transformed data, and transformed rewards
    to_return = []
    
    users = []
    ys = []
    days = []
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
            days.append(all_dict['days'][i])

    centered_y = simple_bandits.get_RT(ys,to_return,global_params.mu_theta,18)
    
    
    return to_return,centered_y,ys,users,days

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



def combine_users(data_path,user_list,global_params):
    #data_path  = '../../../walking-suggestion-service/data'
    user_files = [directory for directory in os.listdir(data_path) if directory.strip('user') in user_list]
    big_user_list = []
    big_data_list = []
    big_reward_list = []
    big_action_list = []
    big_avail_list = []
    big_prob_list = []
    big_day_list = []
    
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
            with open('data/log_data/user_{}_{}.pkl'.format(user_id,str(date.today())),'wb') as f:
                pickle.dump(data,f)
            print(len(data['data']))
        #x,y,user = get_phi(data['data'],data,baseline_indices,responsivity_indices)
            if user_id in get_user_ids():
                big_user_list = big_user_list+data['users']
                big_data_list = big_data_list+data['data']
                big_avail_list =big_avail_list+data['avail']
                big_action_list =big_action_list+data['actions']
                big_prob_list =big_prob_list+data['prob']
        
    
                big_reward_list = big_reward_list+data['reward']
                big_day_list = big_day_list+data['days']
    
    #temp_X = get_standard_x(big_data_list)
    temp_X = big_data_list
    temp_data = {'avail':big_avail_list,'actions': big_action_list,'prob':big_prob_list,\
'users':big_user_list,'reward':big_reward_list,'days':big_day_list
}
    #if train:
    #print(temp_X)
    x,ycentered,y,user,days =get_phi(temp_X,temp_data,baseline_indices,responsivity_indices,global_params)

    return  user, x,ycentered,y,days




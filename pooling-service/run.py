import gpytorch
import pyreadr
from sklearn import preprocessing
import R_to_python_functions as RPY
import hyperparameter_runner
import json
import pickle
import sys
import os

import pandas as pd

def run_updates(data_path,users):
    
  
        #nusers = set(users)
    users,data,y = RPY.combine_users(data_path,users)
    print('got users')
    g = hyperparameter_runner.real_run(data,users,y)
    print(g)
    return g

            # with open('../data/test.pkl','wb') as f:
            # pickle.dump(x,f)


            #with open('../data/errors.pkl','wb') as f:
            #pickle.dump(e,f)
#return users

#def write_results():
def update_params(users,g,lookup):

    try:
        for u in users:
  
        #print(data_path)
            if u in lookup and lookup[u] in g:
                print(u)
                datap = 'data/{}/temp_policy.Rdata'.format('user'+u+'_pooled_params')
                mu = g[lookup[u]][0]
                sigma = g[lookup[u]][1]
        
                pyreadr.write_rdata(datap, pd.DataFrame({'mu':mu,'sigma':sigma}))
    except Exception as e:
        print(e)
        with open('data/errors_pool.txt','w+') as f:
            f.write('{}'.format(e))
            f.write('\n')
            to_return = 'Errors'
            print( to_return)

if __name__=="__main__":
    user_string = sys.argv[1]
    to_return =  user_string
    print(user_string)
    data_path = 'data'
    print(os.listdir('data'))
    try:
        #users = json.loads(users)
        #print(user_string)
        
        users = set([i for i in user_string.split(',')])
        print(users)
        x = run_updates(data_path,users)
        
        with open('data/test.pkl','wb') as f:
            pickle.dump(x,f)
        update_params(users,x,RPY.get_user_ids())
        print(users)
    except Exception as e:
        print(e)
        with open('data/errors_pool.txt','w+') as f:
            f.write('{}'.format(e))
            f.write('\n')
        to_return = 'Errors'
        print( to_return)

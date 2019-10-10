from datetime import date
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
    users,data, y,ynon_adjusted= RPY.combine_users(data_path,users)
    #y = np.array([ys[i]-np.dot(to_return[i],to_adjust) for i in range(len(to_return))])
    
    print('got users')
    g = hyperparameter_runner.real_run(data,users,y,ynon_adjusted)
    return g
    #try:
    #  users,data,y = RPY.combine_users(data_path,users)
    # print('got users')
    # g = hyperparameter_runner.real_run(data,users,y)
    # return g
    #except Exception as e:
       

       #with open('data/errors_pool.txt','w+') as f:
       # f.write('{}'.format(e))
       # f.write('\n')
       # to_return = 'Errors'
# print( to_return)



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
        with open('data/runerrors_pool.txt','w+') as f:
            f.write('{}'.format(e))
            f.write('\n')
            to_return = 'Errors'
            print( to_return)
        with open('data/errors_pool.txt','w+') as f:
            f.write('{}'.format(e))
            f.write('\n')
            to_return = 'Errors'
            print( to_return)

if __name__=="__main__":
    user_string = sys.argv[1]
    to_return =  user_string
    #print(user_string)
    data_path = 'data'
    #print(os.listdir('data'))
    try:
        #users = json.loads(users)
        #print(user_string)
        
        users = set([i for i in user_string.split(',')])
        with open('data/user_list_pool.pkl','wb') as f:
            pickle.dump(users,f)
        #users =set( ["10032","10006","10157","10075","10142","10055","10101","test-pedja"])
        #print(users)
        x = run_updates(data_path,users)
        
        with open('data/test.pkl','wb') as f:
            pickle.dump(x,f)
        update_params(users,x,RPY.get_user_ids())
#print(users)
    except Exception as e:
        print(e)
        with open('data/errors_pool.txt','w+') as f:
            f.write('{}'.format(e))
            f.write('\n')
        to_return = 'Errors'
        print( to_return)

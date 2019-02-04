import numpy as np
import pandas as pd
import math
import pickle 
import random


class get_history:
    
    
    
    '''
   Generates some data fairly, arbitrarly. 
    '''
    
    def __init__(self,dim_features,num_train_examples,num_users,num_test_examples=None):
        self.root =  '../../../../Volumes/dav/HeartSteps/pooling_rl_shared_data/processed/'
        
        self.dim_features =  dim_features
        self.num_train_examples =  num_train_examples
        self.num_test_examples = num_test_examples
        self.num_users = num_users
     
    
        self.states = self.state_function()
        self.actions = self.action_function()
        self.rewards = self.reward_function()
        self.users = self.make_users()
        self.day_function = self.get_all_user_study_days()
        
    def state_function(self,mean=None,std=None):
    
        if mean==None and std==None:
            mean = random.random()*10*(random.random()+3)

            
        std = 2
        return [[np.random.normal(mean,std)/100.0 for i in range(self.dim_features)] \
            for n in range(self.num_train_examples)]

    def action_function(self):
        return [int(random.random()>.6) for i in range(self.num_train_examples)]
    
    def reward_function(self):
        return [np.random.normal(150,50) for i in range(self.num_train_examples)]
    
    def make_users(self):
        return [int(random.random()*self.num_users) for i in range(self.num_train_examples)] 
    
    def get_all_user_study_days(self):
        to_return = {}
        #clumsy way of doing
        for i in range(len(self.users)):
            user = self.users[i]
            days = self.get_day_of_study(user)
          
            for di in range(len(days)):
                if self.users[di]==user:
                    to_return[di]=days[di]
                    
        return to_return
    
    def get_day_of_study(self,user_id):
        save_day_of_study  = []
        count = 0 
        for i in range(len(self.states)):
            if self.users[i]==user_id:
                count = count+1
                save_day_of_study.append(count)
            else:
                save_day_of_study.append(0)
        return save_day_of_study

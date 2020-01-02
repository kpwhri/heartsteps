
import os
import R_to_python_functions as RPY
import R_to_python_functions_time as RPYtime
from shutil import copyfile

if __name__=="__main__":
    #to_return = 'hellow'
    #os.mkdir('data/pooled_hyper')
    #copyfile('data/errors_pool.txt'.format(f),'data/pooled_hyper/errors_pool.txt')
    #return
    try:
        
        users = [f for f in os.listdir('data') if 'user' in f and (f[4:] in RPYtime.get_user_ids()) and '_pooled' not in f]
        #print(users)
        #print('to make')
        newdir = [f+'_pooled_params' for f in users ]
        to_delete = [f for f in os.listdir('data') if 'pooled_params_pooled_params' in f  ]
        for f in to_delete:
            os.rmdir('data/{}'.format(f))
        for f in newdir:
            
            #print(os.path.isdir('data/{}'.format(f)))
            if not os.path.isdir('data/{}'.format(f)):
                os.mkdir('data/{}'.format(f))
                print(f)
        for f in users:
            if 'policy.Rdata' in os.listdir('data/{}'.format(f)):
                    copyfile('data/{}/policy.Rdata'.format(f),'data/{}/policy.Rdata'.format(f+'_pooled_params'))
    except Exception as e:
        print(e)
        with open('data/errors_pool.txt','w+') as f:
            f.write('in create dirs')
            f.write('{}'.format(e))
                        #f.write('\n')
        to_return = 'Errors'
#print( to_return)
#return to_return

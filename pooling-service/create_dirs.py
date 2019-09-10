import os
from shutil import copyfile

if __name__=="__main__":
    to_return = 'hellow'
    try:
        
        users = [f for f in os.listdir('data') if 'user' in f]
        newdir = [f+'_pooled_params' for f in users if '_pooled' not in f]
        to_delete = [f for f in os.listdir('data') if 'pooled_params_pooled_params' in f  ]
            #for f in to_delete:
            #os.rmdir('data/{}'.format(f))
        for f in newdir:
        
            if not os.path.isdir('data/{}'.format(f)):
                os.mkdir('data/{}'.format(f))
            copyfile('data/{}/policy.Rdata'.format(f[:f.index('pooled')]),'data/{}'.format(f))
    except Exception as e:
        print(e)
        with open('data/errors_pool.txt','w+') as f:
            f.write('in create dirs')
            f.write('{}'.format(e))
            f.write('\n')
            to_return = 'Errors'
            print( to_return)
#return to_return

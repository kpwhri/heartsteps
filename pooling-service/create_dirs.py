import os

if __name__=="__main__":
    users = [f for f in os.listdir('data') if 'user' in f]
    newdir = [f+'_pooled_params' for f in users if '_pooled' not in f]
    to_delete = [f for f in os.listdir('data') if 'pooled_params_pooled_params' in f  ]
    for f in to_delete:
        os.rmdir('data/{}'.format(f))
    for f in newdir:
        
        if not os.path.isdir('data/{}'.format(f)):
            os.mkdir('data/{}'.format(f))

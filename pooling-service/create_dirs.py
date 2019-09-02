import os

if __name__=="__main__":
    users = [f for f in os.listdir('data') if 'user' in f]
    newdir = [f+'_pooled_params' for f in users]
    for f in newdir:
        if not os.path.isdir('data/{}'.format(f)):
            os.makedir('data/{}'.format(f))

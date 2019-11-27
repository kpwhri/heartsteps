import pickle
import random
import numpy as np


class TS_global_params:
    
    
    
    '''
    Keeps track of hyper-parameters for any TS procedure. 
    '''
    
    def __init__(self,xi=10,baseline_features=None,psi_features=None,responsivity_keys=None,uparams = None):
        try:
            with open('data/pooled_hyper/pooled_init_params.pkl','rb') as f:
                init_params = pickle.load(f)
        except:
            init_params = {'sigma_u':np.array([[1.5898, 0.0979],[ 0.0979,    0.6828]]),'noise_term':5.44}
        #5.5440
        #print(init_params)
        #init_params['noise_term']=5.44
        #init_params = {'sigma_u':np.array([[1.5898, 0.0979],[ 0.0979,    0.6828]]),'noise_term':5.44}
        self.nums = set([np.float64,int,float])
        self.pi_max = 0.8
        self.pi_min = 0.1
        self.sigma =1.15            #6**.5
        self.baseline_features=baseline_features
    
        self.responsivity_keys = responsivity_keys
        self.num_baseline_features = len(baseline_features)
        self.psi_features = psi_features
        self.num_responsivity_features = len(responsivity_keys)
    
        self.psi_indices = psi_features
       
        
        self.xi  = xi
        
        self.update_period=7
        self.gamma_mdp = .9
        self.lambda_knot = .9 
        self.prob_sedentary = .9 
        self.weight = .5
        
        self.inv_term = None
        self.to_save_params = {}
        
     
        self.theta_dim =1+self.num_baseline_features + 2*(1+self.num_responsivity_features)
        self.baseline_indices =  [i for i in range(self.theta_dim)]
        #print(self.theta_dim)
        #self.mu_theta =np.zeros(self.theta_dim)
        #self.mu_theta[0]=4.6
        
        self.mu_theta=[ 0.8231421 , 1.9493709 , 3.8116041, -0.1918933,  0.7626614 , 0.0000000, -0.9168122 , 0.0000000,0.4701715, 0.0000000, 0.0000000, 0.0000000, 0.0000000,0.4701715, 0.0000000, 0.0000000, 0.0000000,0.0000000]
            #[0.823,    1.949,    3.812,    -0.192,    0.763,    0,    -0.917,    0,
            # 0.47,    0,    0,    0,    0,
            #   0.47,    0,    0,    0,    0]
        self.sigma_theta =        np.diag([14.2413945, 13.3546165,  3.2355121 , 0.5701742, 18.9986360 , 0.2578251, 16.9993579,  7.3453086,4.9266238, 24.5584807,  4.9509419 , 0.6749049  ,0.8163259,4.9266238, 24.5584807,  4.9509419,  0.6749049 , 0.8163259])

            #np.diag([i**2 for i in [3.774,3.654,1.799,0.755,4.359,0.508,4.123,2.71,2.22,4.956,2.225,0.822,0.904,2.22,4.956,2.225,0.822,0.904]])
        
       

            #self.get_theta(self.theta_dim)
        self.lr = 1.0
   
        self.sigma_u = init_params['sigma_u']
            #np.array([[1.5898, 0.0979],[ 0.0979,    0.6828]])
      
        self.rho_term = -0.9398
      
        self.u1 =1.5898
        
        self.u2 =0.6828
        
        
        self.noise_term =init_params['noise_term']
        #5.5440
        
        self.o_noise_term =init_params['noise_term']
  
        self.cov=np.array([1])
        #self.psi = psi.psi()
        self.decision_times = 1
        self.kdim = self.theta_dim+2

        self.last_global_update_time = None
        
        self.standardize=False
        
        self.user_id_index=None
        self.user_day_index = None
        self.write_directory ='../temp'
            #'../../regal/murphy_lab/pooling/temp_EB'
        self.updated_cov = False
        self.history = None
        self.mus0 = None
        self.sigmas0 =None
        
        self.mus1 = None
        self.sigmas1 =None
        
        self.mus2 = None
        self.sigmas2 = None
        if uparams is not None:
            self.init_u_params(uparams)
    
    def init_u_params(self,uparams):
        self.u1 = uparams[0]
        self.u2 = uparams[1]
        self.u3 = uparams[2]
        self.u4 = uparams[3]
    
        self.r12 = uparams[4]
        self.r13 = uparams[5]
        self.r14 = uparams[6]
        self.r23 = uparams[7]
        self.r24 = uparams[8]
        self.r34 = uparams[9]
        
        self.init_u1 = uparams[0]
        self.init_u2 = uparams[1]
        self.init_u3 = uparams[2]
        self.init_u4 = uparams[3]
        
        self.init_r12 = uparams[4]
        self.init_r13 = uparams[5]
        self.init_r14 = uparams[6]
        self.init_r23 = uparams[7]
        self.init_r24 = uparams[8]
        self.init_r34 = uparams[9]
    
    def update_uparams(self,uparams):
        self.u1 = uparams[0]
        self.u2 = uparams[1]
        self.u3 = uparams[2]
        self.u4 = uparams[3]
        
        self.r12 = uparams[4]
        self.r13 = uparams[5]
        self.r14 = uparams[6]
        self.r23 = uparams[7]
        self.r24 = uparams[8]
        self.r34 = uparams[9]
    
    def feat0_function(self,z,x):
        
        
        temp =  [1]
        temp.extend(z)
        #print(type(x))
        if type(x) in self.nums:
        
            temp.append(x)
        else:
            temp.extend(x)
        return temp

    def feat1_function(self,z,x):
        temp =  [1]
        temp.extend(z)
        if type(x) in self.nums:
        
            temp.append(x)
        else:
            temp.extend(x)
        return temp    
        
        
    def feat2_function(self,z,x):
        temp = [1,z[0]]
        if type(x) in self.nums:
        
            temp.append(x)
        else:
            temp.extend(x)
        
        return temp
            
    def get_mu0(self,z_init):
        return [0 for i in range(len(self.feat0_function(z_init,0)))]
    
    def get_mu1(self,num_baseline_features):
        return [0 for i in range(num_baseline_features+1)]
    
    def get_mu2(self,num_responsivity_features):
        return [0 for i in range(num_responsivity_features+1)]
    
    def get_asigma(self,adim):
        return np.diag([1 for i in range(adim)])
    
    
    def comput_rho(self,sigma_u):
        t =sigma_u[0][0]**.5 * sigma_u[1][1]**.5
        r = (sigma_u[0][1]+t)/t
        return r
    
    
    def update_params(self,pdict):
        self.noise_term=pdict['noise']
        self.sigma_u = pdict['sigma_u']
        #self.sigma_v = pdict['sigma_v']
        #save rho term too
        self.rho_term = self.comput_rho(pdict['sigma_u'])
        self.cov = pdict['cov']
        self.updated_cov=True
    
    def update_params_more(self,pdict):
        self.noise_term=pdict['noise']
        
        #self.sigma_v = pdict['sigma_v']
        #save rho term too
        
        self.cov = pdict['cov']
        self.update_uparams(pdict['uparams'])
        self.updated_cov=True
    

    def get_theta(self,dim_baseline):
        m = 1*np.eye(dim_baseline)
        #m = np.add(m,.1)
        return m

    def update_cov(self,current_dts):
        cov = np.eye(current_dts)
        #cov = np.add(cov,.001)
        self.cov=cov


    def update_mus(self,pid,mu_value,which_mu):
        if which_mu==0:
            self.mus0=mu_value
        
        if which_mu==1:
            self.mus1=mu_value
        
        if which_mu==2:
            self.mus2=mu_value

    def update_sigmas(self,pid,sigma_value,which_sigma):
        if which_sigma==0:
            self.sigmas0=sigma_value
        
        if which_sigma==1:
            self.sigmas1=sigma_value

        if which_sigma==2:
            self.sigmas2=sigma_value

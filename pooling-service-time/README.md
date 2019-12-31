This service performs nightly updates to create essential parameters to be used by the bandit service. In order to do so, the services uses the pooling model. Each night the service will produce these parameter values for each participant in the pooling condition. They will be output to files in the data directory, and stored as .RData files. The bandit service can then request these values. 

The reward model is the same as for the bandit used in the walking suggestion service. Random effects are put on the intercept term only for both the baseline and treatment vectors. The features are: ``['temperature', 'logpresteps', 'sqrt.totalsteps','dosage', 'engagement',  'other.location', 'variation']`` for the baseline model and ``['dosage', 'engagement',  'other.location', 'variation']`` for the treatment effect model. 

The hyper-parameters were trained using data gathered within V2 (I'm not sure exactly how this data was collected). The exact hyper-parameters are: 

Sigma_u = ``[[1.5898, 0.0979],[ 0.0979,    0.6828]]`` sigma_squared_epsilon = ``5.44``.

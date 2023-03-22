from tools import get_postgres_connection, get_mongodb_collection, dump_table, dump_to_collection
import pandas as pd

def log(message):
    current_time = pd.Timestamp.now()
    print('{}: {}'.format(current_time, message))
    
# Dump participants_study
log('Dumping participants_study')
table_name='participants_study'
df = dump_table(table_name=table_name, columns=['id', 'name', 'baseline_period'])
dump_to_collection(df, collection_name='basic_studies')   # all collection names are plural

# Dump participants_cohort
log('Dumping participants_cohort')
table_name='participants_cohort'
df = dump_table(table_name=table_name, columns=['id', 'name', 'study_id', 'study_length'])
dump_to_collection(df, collection_name='basic_cohorts')

# Dump participants_participant
log('Dumping participants_participant')
table_name='participants_participant'
df = dump_table(table_name=table_name, columns=['heartsteps_id', 'enrollment_token', 'user_id', 'birth_year', 'cohort_id', 'study_start_date'])
dump_to_collection(df, collection_name='basic_participants', key_field='heartsteps_id')

# Prune the studies collection
log('Pruning studies collection')
study_name = 'JustWalk'
study_collection = get_mongodb_collection('basic_studies')
study_collection.delete_many({'name': {'$ne': study_name}})
study_id = study_collection.find_one({'name': study_name})['id']

# Prune the cohorts collection
log('Pruning cohorts collection')
cohort_collection = get_mongodb_collection('basic_cohorts')
cohort_collection.delete_many({'study_id': {'$ne': study_id}})
cohort_id_list = [cohort['id'] for cohort in cohort_collection.find({'study_id': study_id})]

# Prune the participants collection
log('Pruning participants collection')
participant_collection = get_mongodb_collection('basic_participants')
participant_collection.delete_many({'cohort_id': {'$nin': cohort_id_list}})
participant_id_list = [int(participant['user_id']) for participant in participant_collection.find({'cohort_id': {'$in': cohort_id_list}})]

for user_id in participant_id_list:
    log('Dumping all information for {}'.format(user_id))

    # Intervention Components
    log('  Dumping intervention_components')

    ## Levels
    log('    Dumping levels')
    df = dump_table(table_name='bout_planning_notification_level', columns=['level', 'date', 'user_id'], where_clause='user_id = {}'.format(user_id))
    dump_to_collection(df, collection_name='intervention_levels', key_field=['user_id', 'date'])
    
    ## Goals

    # # Behavior Measurements
    # log('  Dumping behavior_measurements')

    # # EMA: Psychological Measures
    # log('  Dumping ema_psychological_measures')
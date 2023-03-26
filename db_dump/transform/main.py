from operations import transform_participants, transform_daily, transform_minute_step
import ray

if __name__ == '__main__':
    # Initialize Ray
    ray.init()
    
    # Load the study, cohort, and participant collections and merge them into the participants collection
    transform_participants()
    
    # Load the daily collection
    transform_daily()

    # Load the minute_step collection
    transform_minute_step()
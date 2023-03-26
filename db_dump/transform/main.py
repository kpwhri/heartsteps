from operations import transform_participants, transform_daily, transform_minute_step, transform_minute_heart_rate
import ray

if __name__ == '__main__':
    # Initialize Ray
    ray.init()
    
    # Load the study, cohort, and participant collections and merge them into the participants collection
    transform_participants()
    
    # Load the daily collection
    transform_daily()

    # Load the minute_step collection (usually takes 50 seconds)
    transform_minute_step()

    # Load the minute_heart_rate collection (usually takes 4 minutes)
    transform_minute_heart_rate()
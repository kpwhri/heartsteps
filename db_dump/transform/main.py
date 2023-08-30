import logging
from operations import *
import ray

if __name__ == '__main__':
    # set logging level to INFO
    logging.basicConfig(level=logging.INFO)

    # Initialize Ray
    # ray.init()
    
    # Load the study, cohort, and participant collections and merge them into the participants collection
    transform_participants()
    
    # Load the daily collection
    transform_daily()

    # add 1) baseline_start_date, 2) intervention_start_date, 3) intervention_finish_date to the participants collection
    add_baseline_and_intervention_dates()

    # drop the dates after the intervention finish date
    drop_dates_after_intervention_finish_date()

    # # Load the minute_step collection (usually takes 50 seconds)
    # transform_minute_step()

    # # Load the minute_heart_rate collection (usually takes 4 minutes)
    # transform_minute_heart_rate()

    # # Copy the daily steps and heart rate aggregated data to the daily collection
    # copy_daily_steps_and_heart_rate()

    # # Load the notification collection
    # transform_survey()

    # # Select the daily EMAs
    # select_daily_ema()

    # # Widen the daily EMAs
    # widen_daily_ema()

    # # copy the daily EMAs to the daily collection
    # copy_daily_ema()
    
    # # load the bout planning notification decision data
    # transform_bout_planning_ema_decision()

    # # select the bout planning notifications
    # select_bout_planning_ema()

    # # aggregate the bout planning notification statistics
    # aggregate_bout_planning_ema()
    
    # # load the message and message receipt collections
    # transform_message()

    # # Fill out NaNs in the daily collection
    # fill_daily_nans()
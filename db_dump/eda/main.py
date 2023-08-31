# from operations import 
import ray
from operations import *

if __name__ == '__main__':
    # Initialize Ray
    # ray.init()

    # Prepare output directory
    prepare()
    filename_dict = {}

    # Draw the level heatmap
    filename_dict['levels'] = draw_level_heatmap()

    # Draw the goal heatmap
    filename_dict['goals'] = draw_goal_heatmap()
    filename_dict['goals_distribution'] = draw_goal_distribution_heatmap()

    # Draw the steps heatmap
    filename_dict['steps'] = draw_steps_heatmap()
    filename_dict['steps_distribution'] = draw_steps_distribution_heatmap()

    # Draw the wearing time heatmap
    filename_dict['wearing_time'] = draw_wearing_time_heatmap()
    filename_dict['wearing_time_sorted_bars'] = draw_wearing_time_sorted_bars()

    # Draw the survey daily ema heatmap
    filename_dict['survey_daily_ema'] = draw_survey_daily_ema_heatmap()
    filename_dict['survey_daily_ema_sorted_bars'] = draw_survey_daily_ema_sorted_bars()

    # Form the presentation
    form_the_presentation(filename_dict)
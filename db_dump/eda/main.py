# from operations import 
import ray
from operations import prepare, draw_level_heatmap, draw_goal_heatmap, form_the_presentation, draw_steps_heatmap, draw_heart_rate_hrv_heatmap, draw_wearing_time_pct_heatmap

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

    # Draw the steps heatmap
    filename_dict['steps'] = draw_steps_heatmap()

    # Draw the wearing time heatmap
    filename_dict['wearing_time_pct'] = draw_wearing_time_pct_heatmap()

    # Draw the heart rate heatmap
    filename_dict['heart_rates_hrv'] = draw_heart_rate_hrv_heatmap()

    # Form the presentation
    form_the_presentation(filename_dict)
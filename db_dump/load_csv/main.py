# from operations import 
import ray
from operations import load_csv_to_local_mongodb

if __name__ == '__main__':
    # Initialize Ray
    ray.init()

    # Load the csv files to the local mongodb
    load_csv_to_local_mongodb()
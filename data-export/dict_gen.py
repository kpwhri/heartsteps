import run
import utils
import argparse
import os
import glob
import pandas as pd

DICTIONARY_DIR = "data_dictionaries"


def generate_dictionaries(export_loc: str, hsid: str):

    # extract csvs from all runs of user
    exports = glob.glob(os.path.join(export_loc, hsid, "*.csv"))

    # parse heading
    for export in exports:
        dataframe = pd.read_csv(export)

        # Visualize Ranges
        print(dataframe.describe())

        # Create Dictionary
        dictionary = pd.DataFrame({
            'ElementName': dataframe.columns,
            'DataType': None,
            'Size': None,
            'Required': 'Required',
            'ElementDescription': None,
            'ValueRange': None,
            'Notes': None,
            'Aliases': None,
             })

        # Write Dictionary
        # Standardizes logs. exports
        export_name = "_".join(os.path.basename(export).split('.')[1:-1])

        print(f'Writing {export_name} dictionary')
        dictionary.to_csv(os.path.join(DICTIONARY_DIR, f'{export_name}.csv'), index=False)


if __name__ == "__main__":
    # arg collect
    parser = argparse.ArgumentParser(description='Generate Data Dictionaries')
    parser.add_argument('-r', '--refresh', help='run new export before generating', dest='export', action='store_true')
    parser.add_argument('hsid', help='user to use as ground truth')
    args = parser.parse_args()

    # run clean export
    config = utils.read_config()

    print(config)
    exit()

    if args.export:
        print("Running new -all export")
        run.export_all_data(config["EXPORT_DIR"], cohort='U01', exports=["all"], DEBUG=False)

    EXPORT_LOCATION = os.path.join(config["EXPORT_DIR"], 'U01')

    print(f"Exporting Data Dictionaries from user {args.hsid}")

    generate_dictionaries(EXPORT_LOCATION, hsid=args.hsid)

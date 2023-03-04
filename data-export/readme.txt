1. To run data exports, follow the steps in gcloud-setup.txt to configure a stand-alone 
vm to use as a data export server.

2. Once the server is setup, log in and run the following code to install this codebase:

git clone https://github.com/kpwhri/heartsteps.git -b data-export
pip3 install -r heartsteps/server/requirements.txt
pip3 install -r heartsteps/data-export/requirements_export.txt 

Library and output directories are specified in config.sh.

To run all exports use:
  >> source config.sh
  >> python3 run.py weekly daily minute 

To enable debug mode use:
  >> python3 run.py weekly daily minute -d

Specify any subset of available levels to only export those levels
  >> python3 run.py weekly daily

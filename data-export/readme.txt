1. To run data exports, follow the steps in gcloud-setup.txt to configure a stand-alone 
vm to use as a data export server.

2. Once the server is setup, log in and run the following code to install this codebase
into your user home directory:

>> cd ~
>> git clone https://github.com/kpwhri/heartsteps.git -b data-export
>> pip3 install -r heartsteps/server/requirements.txt
>> pip3 install -r heartsteps/data-export/requirements_export.txt 

3. The HeartSteps code directory, database credentials and output directories are specified 
in config.yaml.

To run all exports in debug mode (limits to first 2 users):
  >> cd ~/heartsteps/data-export
  >> python3 run.py weekly daily minute -d 

To run only the weekly export in debug mode (limits to first 2 users):
  >> cd ~/heartsteps/data-export
  >> python3 run.py weekly -d 

To run all exports for all users:
  >> cd ~/heartsteps/data-export
  >> python3 run.py run.py weekly daily minute

To run only the weekly export for all users:
  >> cd ~/heartsteps/data-export
  >> python3 run.py weekly 

4. For information on developing new exports see dev_guide.txt
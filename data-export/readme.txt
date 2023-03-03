Library and output directories are specified in config.sh.

To run all exports use:
  >> source config.sh
  >> python3 run.py weekly daily minute 

To enable debug mode use:
  >> python3 run.py weekly daily minute -d

Specify any subset of available levels to only export those levels
  >> python3 run.py weekly daily

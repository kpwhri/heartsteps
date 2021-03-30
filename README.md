# HeartSteps

This is the HeartSteps application, which is comprised of multiple services:
* *heartsteps-server* a Django web server
* *heartsteps-client* an Ionic hybrid mobile applicaiton
* *heartsteps-fitbit* a fitbit os application for the fitbit versa
* *walking-suggestion-service* randomizes walking-suggestions
* *anti-sedentary-service* responsible for randomizing anti-sedentary intervention
* *pooling-service* creates pooled randomizations for walking-suggestion-service

To understand the application architecture, please see the [application architecture google doc,](https://docs.google.com/document/d/1UsdR3xgVDtPpmmskc6mGsm7YJNCXJlhmE-qGk96isQw/edit?usp=sharing) which is still a work in progress.

The following outlines how to run the applications for local development, and then deploy the entire application.

## Development
We use a docker-ized workflow to make installing and running a development environment easier -- while `docker-compose up` does work, Django requires you to setup the database and an empty database is pretty boring.
```
# Create a new server database
$ docker-compose run server python manage.py migrate
# Add test data and Django admin user
$ docker-compose run server python manage.py loaddata test-data

$ docker-compose up
# Server admin at http://localhost:8080/admin
# Server dashboard at http://localhost:8080/dashboard
# Username: admin
# Password: password1234

# Angular mobile app client
# http://localhost:8100/
```

Previous code sets up the server and client, but doesn't create or load any sample participants or data. The follow code will setup two test user accounts -- one that has 2 weeks of fake data and has completed the onboarding process, and a second that is a completely new account.
```
# Adding test user accounts is a little convoluted (sorry)
# Maybe we can turn this into a Django Command?
$ docker-compose run server python manage.py shell
> from participants.tasks import reset_test_participants
> reset_test_participants()
# User: test
# Entry code: test-test
# Birth year: 2021
# User: test-new
# Entry code: test-new1
# Birth year: 2021
```

When working with the server or client, I find it useful to work in the docker container's command line directly (your utility may vary).
```
$ docker-compose run --service-ports server bash
> echo("Whoa I'm in the server")
# Run the dev server
> hocho start dev
# Run those unit-tests
> python manage.py test
# If you want to install a python package from pip
> pip install some-damn-package
> pip freeze > requirements.txt
# You need to rebuild the docker image for this to persist

$ docker-compose run --service-ports client bash
> echo("Dude, this version of Angular is 3 years old")
# Run the dev environment with hot reloading
> npm run dev
# Build the debuggable android app
> npm run build:app:android:debug
# Let's cover iOS dev somewhere else...
```

PS: Docker has a tendency to cache all sorts of things, sometimes destroying the containers is a good thing.
```
$ docker rm -f $(docker ps -aq)
```

### HeartSteps Server

```
$ docker-compose run --service-ports server bash
```
The command above will start the server environment and and give you a bash shell in the /server directory. There will be no running server until you start it.

To explain the command above a little
* docker-compose run means run a docker image defined in the docker-compose environment
* --service-ports is a flag that exposes the running image (otherwise you wouldn't see it)
* server is the name of the image
* bash is the command we want to run, which overrides the default startup command for the image

### HeartSteps Client

You would run the client like this
```
docker-compose run --service-ports client bash
```

### HeartSteps FitBit
The fitbit application is created with the [fitbit command line tools,](https://dev.fitbit.com/blog/2018-08-23-cli-tools/) and should be usable if the files are imported into [fitbit studio.](https://studio.fitbit.com)

*NOTE:* The fitbit command line doesn't work in Docker, since the command line tools require X11 (which doesn't work on a headless linux environment)

### Activity Suggestion and Anti-Sedentary Services
The activity suggestion and anti-sedentary services run Flask-based HTTP servers that run R-scripts. These R-scripts read and write to CSV file systems instead of using a database -- these CSV files will be backed-up to Google's datastorage.

The Flask webserver is responsible for validating HTTP requests, and running the R-scripts which contain business logic that randomizes participants.

Each service has an install.r script file, which runs when the Docker image is built, and is responsible for installing R-libraries used by the service.

*Running Walking Suggestion Service*
```
$ docker-compose -f docker-compose.activity-suggestions.yaml run --service-ports walking-suggestion-service
# This will start a web server running at http://localhost:5000
```


*Running Anti-Sedentary Service*
```
$ docker-compose -f docker-compose.activity-suggestions.yaml run --service-ports anti-sedentary
# This will start a web server running at http://localhost:5001
```

*Debugging Tips*
Docker creates containers and images and attempts to reuse them. This means that the install.r script isn't run often. To trigger a service to be rebuilt:
```
$ docker-compose -f docker-compose.activity-suggestions.yaml build activity-suggestion
```

### Pooling Service

To run the pooling service for development, run:

```
$ docker-compose run --service-ports pooling-service
```

This will run the pooling-service at http://localhost:5002

To copy current walking-suggestion-service data into the pooling service for development, run the copy-files command before starting the pooling-service
```
$ docker-compose run pooling-service copy-files
$ docker-compose run --service-ports pooling-service
```

To run the pooling service with the current data stored in Google Cloud Storage:
```
# NOTE: This will delete the current contents of pooling-service/data
$ docker-compose run --service-ports pooling-service-gcloud
```

## Deployment
This application is automatically tested and deployed to the google cloud by Travis-CI. See .travis-ci.yml for details of the CI/CD process.

Managing the heartsteps-server in deployment might require completing tasks like flushing the database, changing administration passwords, or other debugging tasks. **To run the *heartsteps-server* as if it was deployed to gcloud** and connected to the gcloud database, use the following command:
```
$ docker-compose run server-gcloud bash

// You will then be able to run tasks like:
/server# ./manage.py createsuperuser
/server# ./manage.py loaddata initial_data
```

## Environment Variables
Here is a list of the environment variables that are used by HeartSteps. All docker containers in this project share the same environment variables at run time and during build time on Travis-CI. None of the heartsteps docker containers use all the environment variables. Below is a list of environment variables used in the project, and how the environment variable is used.
* *GAE_PROJECT_ID* is the project ID for the google cloud project that Travis-CI deploys to.
* *HEARTSTEPS_URL* is used by the heartsteps_client to access the heartsteps_server's api endpoint.
* *HOST_NAME* is the host_name used by django on the heartsteps_server.
* *DEBUG* makes Django run in debug mode.

**This list is incomplete help!**

### HeartSteps Server Database
The heartsteps-server uses a postgres database in Google Cloud's SQL Database. To access the database, you will need a credentials file with access permisisons.

This database can be accessed directly by running:
```
$ docker-compose -f docker-compose.gcloud.yaml run --service-ports cloudsql
// The postgres server is now available at psql://heartsteps:heartsteps@localhost:5432
```

### Nightly Data Exports
The heartsteps-server exports CSV files for each participant after their nightly update once a day. These files are meant to be used to analyze the efficacy of message randomization. This data is then sync'd to a Google Storage Bucket called "heartsteps-data-exports"

You will need to have a Google Account that has permissions to access the "heartsteps-data-exports" storage bucket.

To download all the files at once (recommended), you will need to:
```
// (1) Download gcloud-utils
$ curl https://sdk.cloud.google.com | bash
// (2) Login with your google account that has access to the heartsteps-data-exports storage bucket
$ gcloud init
// (3) Make a directory to download the files to (since there a many files)
$ mkdir nightly-data
// (4) Download the files
$ gsutil -m rsync gs://heartsteps-data-exports ./nightly-data
```

*Note:* It's possible to access files individually in your web browser, [access the heartsteps-data-exports storage bucket here.](https://console.cloud.google.com/storage/browser/heartsteps-data-exports)

### Anti-Sedentary and Walking-Suggestion Service Data
Both the anti-sedentary and walking-suggestion services store data to a remote file system, which is a Google Storage Bucket. These buckets are read and written to by the services in the production environment.

The best way to access the data from these systems is to use the "copy-files" command, which will copy files from the Google Storage Bucket to your local machine.

For the anti-sedentary service, run:
```
$ docker-compose run anti-sedentary-service copy-files
// Data will be downloaded to anti-sedentary-service/data
```

For the walking-suggestion service, run:
```
$ docker-compose run walking-suggestion-service copy-files
// Data will be downloaded to walking-suggestion-service/data
```

### Context-specific Docker-compose yaml
You may create a context-specific docker-compose YAML file. If you made a YAML file, you can use it with ```-f``` option.
```
$ docker-compose -f docker-compose.nlm.yaml up
// Run docker-compose with a context-specific yaml file. Since the yaml file refers to a custom-made .env file, it would not work if you don't have 'certificate/.env-development' file.
```
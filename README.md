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

**NOTE:** See the troubleshooting section at the end of this document for quick fixes to local development issues.

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


While you are actively developing, you can use the following commands **inside** the server container:

```
$ keep_testing [app name]
```

It automatically reruns the following test command if *.py file changes.
```
$ python manage.py test [app name] --keepdb
```

### HeartSteps Client

You would run the client like this
```
docker-compose run --service-ports client bash
```

#### Debugging Client

You might want to make a user for debugging. This is how. (I'll assume you already loaded up the docker containers)

1. Create a superuser [do this in server container]

        $ python manage.py createsuperuser

2. Connect to staff dashboard (http://localhost:8080/dashboard)
    - use the id and password of a superuser that you just created in step 1.

3. Select a test cohort

4. Select "Add participant" at the top of the screen

5. Put anything as you want in those three fields. HeartSteps ID will be used as User.username (alphanumiric). Enrollment token should be "xxxx-xxxx" form. Birthyear should be normal years (such as 1980 or 2021). I recommend something with serial number. (i.e., test-01) Because you will do this again and again and you might not want to be confused. Use different prefixes for heartstep id and token, so that you can distinguish them just by looking (It will help you at some point)

Now you can log in with that ***token*** and ***birthyear*** in client (http://localhost:8100)

Then you can proceed the onboarding screens. At the "Fitbit" screen (the one with "Connect to Fitbit" button), you may pause and make the user enabled to bypass Fitbit connection.

6. Go to Django admin page. (localhost:8080/admin) You would be authenticated already, because you logged in step 2. If not, please use the id/pw used in step 1 & 2.

7. In the left section, Select Fitbit_Api > Fitbit accounts.

8. On the top right corner, hit "ADD FITBIT ACCOUNT" button. 

9. Fill random alphanumeric text in **Fitbit user**, **Access Token**, **Refresh Token**, and fill random 5 digit numbers in **Expires at** field.

10. Click + sign under FITBIT ACCOUNT USERS (Add another fitbit account user). This will make a connection with a HeartSteps user and Fitbit Account that you are creating right now.

11. Select the User you created in step 4. Technically speaking, you created a participant in step 4, and you created a User by logging in through the client app between step 5 & 6. 

Now you can go back to your client (app) screen, and click "Next", then click "Skip" in the next screen (Fitbit clockface).

Then you will reach to baseline screen.

12. Go back to Django admin page. (localhost:8080/admin). Go to AUTHENTICATION AND AUTHORIZATION > Users. Find the user you just created. Click the ID.

13. In the "Change user" page, check "Staff Status". Then click "Save".

14. Go back to client app (localhost:8100) and refresh the page. It will lead you to client home. (bypassing baseline)


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
There is a test deployment that is available at https://dev.heartsteps.net
This application is automatically tested and deployed to the google cloud by Travis-CI. 
.travis-ci.yml runs unit tests for the heartsteps-server then runs deploy-gcloud-dev.sh

**To manually deploy HeartSteps,** simply execute [deploy-gcloud-dev.sh,](./deploy-gcloud-dev.sh) which will force authorization from your current credentials directory and rebuild all required docker-images.
If you want to deploy using your own credentials or docker images, follow the instructions in deploy-gcloud-dev.sh

The deployment of this application is based on [Google Cloud's "Running Django on Google Kubernetes" documentation.](https://cloud.google.com/python/django/kubernetes-engine)
The deployment steps described in Google Cloud's documentation are roughly translated and automated in the deploy-gcloud-dev.sh script.

The primary difference in our deployment as opposed to the documentation, is we use NGINX to act as a load balancer to serve static files through a reverse proxy.
The nginx docker image only contains [a modified nginx.conf file.](./gcloud-dev-nginx.conf)
All static files are still uploaded to a Google Storage Bucket.

**Anti-Sedentary, Pooling, and Walking-Suggestion services** require a `privileged` docker environment to run a file system from a google storage bucket [(gcs-fuse.)](https://github.com/GoogleCloudPlatform/gcsfuse)
Only the Anti-Sedentary and Walking-Suggestion services are currently deployed in the [KPW deployment.](./kpwhri-deployment.yaml)

### Environment Variables
The HeartSteps server uses many different environment variables to properly configure the system.
**Our goal with evironment variables is that no settings are required to deploy HeartSteps.**
As of this time, this isn't 100% true, but we are working on it.

For each deployment there is a .env file that is reused in both the HeartSteps Server and Client to ensure both systems have matching configurations.

Below is a list of environment variables that require values to run HeartSteps.
Integration specific variables are described in the service integrations section below.

* *DEBUG* makes Django run in debug mode. Only use debug in your local environment, not on a production machine.
* *HEARTSTEPS_URL* is used by the heartsteps_client to access the heartsteps_server's api endpoint.
* *HOST_NAME* is the host_name used by django on the heartsteps_server. A comma seperated list can be used to demarkate multiple host names.

**This list is incomplete help!**

### Debugging a Deployment
It can be useful to setup kubectrl to directly access the Kubernentes cluster.
To do this you need to use the gcloud command line to setup the needed certificates.

```
# First login with your google account (you have access, right?)
$ gcloud auth login

# Set the correct gcloud project
$ gcloud config set project heartsteps-dev

# Set up kubernetes
$ gcloud container clusters get-credentials dev-cluster --region=us-central1-a

# Lets see what pods you can connect to...
$ kubectl get pods

# You'll get a long list of running pods
# let's assume one is named heartsteps-worker-123456789-abc. You can run `bash` in it by
$ kubectl exec -it heartsteps-worker-123456789-abc bash

```

### Debugging an iOS app locally

Try to do the following and you can optimize workflow by yourself. You don't have to use docker, but for the ease of setting, docker is used.

1. Run docker desktop
2. Delete platform directory (for demo)
3. Go into client container (through docker UI)
4. Build ios app

        $ ionic cordova prepare ios

5. Go to platform/ios
6. Update pod (OneSignal update) - one time thing (it’s because we deleted platform directory)

        $ cd platform/ios
        $ pod repo update
        $ pod install

7. Open platform/ios/HeartSteps.xcworkspace file. Not the project file.
8. In XCode, go to File > Workspace Settings menu and Change “Build System” to “Legacy Build System”
9. Click “HeartSteps” in the left pane (root of the tree)
10. In the right pane, change identifier: net.heartsteps.kpw -> net.heartsteps.dev
11. Change profile: Your own profile (if none, add one)
12. Remove notification capability (See the bottom in the right pane)
13. Build
14. Open client/src/pages/welcome/welcome.ts
15. Change code as you want in goToEnrollPage() (i.e., ```console.log("test");``` )
16. Build iOS app again in the docker

        $ ionic cordova prepare ios

17. Open workspace file again
18. Remove notification capability
19. Build & Run
20. See the console


### HeartSteps Server Database
The heartsteps-server uses a postgres database in Google Cloud's SQL Database. To access the database, you will need a credentials file with access permisisons.

This database can be accessed directly by running:
```
$ docker-compose -f gcloud-dev.docker-compose.yaml run --service-ports cloudsql
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

To connect to the dev server through docker you will need the development credentials in your credentials dirctory. There are two files that you need:
* .env-gcloud-dev
* gcloud-dev-service-account.json

With the credentials above you use gcloud-dev.docker-compose.yaml to connect to the database, but with your local file directory which is pretty useful for debugging.

```
$ docker-compose -f gcloud-dev.docker-compose.yaml run server bash

# Let's pretend you need to setup a new superuser
> python manage.py createsuperuser

```
## Service Integrations
HeartSteps uses multiple APIs and services to deliver a complete experience.

### Fitbit API Integration
A connection the Fitbit API is required for HeartSteps to function properly.

Authorization for a participant requires the Fitbit server publicly accessiable and connected to HeartSteps.
You will want to set Fitbit API's return URL value to `https://<your domain>/api/fitbit/authorize/process`

To enable the Fitbit API Subscription, you need to add a subscription where the endpoint is `https://<your domain>/api/fitbit/subscription`
We recommend setting a subscriber ID, as Fitbit will set the value to 1 otherwise.
You will need to set both the FITBIT_SUBSCRIBER_ID and FITBIT_SUBSCRIBER_VERIFICATION_CODE with corresponding values in your server's environment variables.

To access intra-day step counts for participants, you need to request special access from Fitbit here: https://dev.fitbit.com/build/reference/web-api/intraday-requests/
Please note this is a really long form

## Troubleshooting
This software has been known to break, here are some quick tips and commands for resetting your local environment.

Docker and Docker-Compose leave old container everywhere, often simply destroying these containers will get eveything working correctly.

```

$ docker rm -f $(docker ps -aq)

```

**Completely destroying the database** is often useful if database migrations get screwed up.
The local database is stored in a docker volume called `heartsteps_pgdata` to delete it run

```
$ docker volume rm heartsteps_pgdata
```

The heartsteps client applications store data in the browser's localstorage which can sometimes get set into the incorrect state.
A common issue is being logged in with an Authorization Token that was created for a different system.
It's good practice to delete the localstorage occasionally. 

## Github Management Rules

These rules are drafts. You can edit/suggest/improve them.

### Issues
1. Everything is managed as **issues**.
    - Bugs, new feature, server setting change, etc.
2. Most issues (except Bugs) are recommended to include the **prerequisites** (if needed) and the **completion requirements** in the form of checkbox lists.
    - Bug issue may use "Bugs" issue template, but not required.
3. As default, all issues are tagged with "needs initial review"
4. Each issues are screened with the criteria including (but not limited):
    - are the description and completion requirements detailed enough?
    - is it a bug that causes serious operational problem?
    - if it is handled now, is it possible to cause potential operational risks?
    - are all prerequisites resolved?
    - is it a long term vision?
5. After review, the issue is marked with appropriate labels. See the label list.
6. If the issue can be, and should be handled in a month, it is added to the current month's project kanban board.
7. If the issue is resolved, the following should be done
    - the issue should be closed
    - if the issue is included as a prerequisite in other issues, go and check the tickbox.
    - if the issue is included in last month's "leftover" issue, go and check the tickbox.
    - if the issue is referred in any way, go and edit it appropritately.


### Project Kanban Board: Timeline
The purposes of the Project Kanban Board are:
    - scheduling timeline (monthly project board)
    - bird's eye view on who's working on what

1. At the end of each month, a new kanban board (hereinafter, "project") is created: ***MonthName Year***
2. Each project has three columns: To do, In progress, Done
3. All new issues are triaged into "To do" column.
4. Issues in "To do" can be moved to "In progress" **only if** all of the following conditions are met:
    - the issue is assigned (unassigned issues cannot move) 
    - the assignee began to work on it (if they haven't started yet (even if they want/plan to), the issue cannot move) 
    - all prerequisites are resolved or equivalent
5. Issues in "In progress" can be moved to "Done" **only if** all of the following conditions are met:
    - the assignee thinks the issue is resolved
    - the assignee does not work on it any more
    - all completion criteria are checked or deleted
6. At the end of each month, the issues in first two columns (i.e., To do, In progress) are summarized into a new issue to be put in the next month's "To Do" column. We don't add the issue again as a separate card.

### Misc Rule
1. Github issue management is not a task assignment but a collaborative process.
2. Managing the cards/issues/projects is not Junghwan's sole authority. Anybody can comment, categorize, or edit the decision.
3. This is more than one man job. Please get involved if you find anything odd or unfinished.
4. Overdocument everything. Information is vital.



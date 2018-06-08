# HeartSteps

This is the HeartSteps application, it has two pieces:
* *heartsteps_server* a Django web server
* *heartsteps_client* an Ionic hybrid mobile applicaiton

To understand the application architecture, please see the application architecture google doc, which is still a work in progress.

The following outlines how to run the applications for local development, and then deploy the entire application.

## Development

The entire application stack can be started in development mode by running
```
$ docker-compose up
```

This will start both the client and server in development modes, so any file changes will be reloaded and shown. Unfortunately this isn't great for updating database models and more complex development tasks, which is why we recommend working on either the client or server independently in an isolated bash environment.

*Running HeartSteps Server*
```
$ docker-compose run --service-ports server bash
```
The command above will start the server environment and and give you a bash shell in the /server directory. There will be no running server until you start it.

To explain the command above a little
* docker-compose run means run a docker image defined in the docker-compose environment
* --service-ports is a flag that exposes the running image (otherwise you wouldn't see it)
* server is the name of the image
* bash is the command we want to run, which overrides the default startup command for the image

You would run the client like this
```
docker-compose run --service-ports client bash
```

## Deployment
STUB
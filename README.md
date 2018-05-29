# HeartSteps

This is the HeartSteps application, it has two pieces:
* *heartsteps_server* a Django web server
* *heartsteps_client* an Ionic hybrid mobile applicaiton

To understand the application architecture, please see the application architecture google doc, which is still a work in progress.

The following outlines how to run the applications for local development, and then deploy the entire application.

## Development

The entire application stack can be started in development mode by running
```
docker-compose up
```

### HeartSteps Server
To work with the Django application in an isolated bash environment, run:
```
docker-compose run --service-ports server bash
```

### HeartSteps Client
To work with the client application in an isolated bash environment, run:
```
docker-compose run --service-ports client bash
```

## Deployment
STUB
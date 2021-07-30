This is a Fitbit Clock Face application build for Fitbit OS 2 (or whatever they call it)

The Fitbit Clock Face downloaded from the Fitbit App Gallery by the participant.
Recorded step count, body presense, and location are incrementally sent from the clock face to the heartsteps-server.
Server side implementation can be found in the fitbit-clock-face module.

To build the fitbit clock face, you can run `npm run build` (assuming you ran `npm install`).
This will produce a app.fba file at fitbit-clock-face/build/app.fba.
The app.fba file can be uploaded to the Fitbit App Gallery

Fitbit's command line documentation recommends that you build the app using the Fitbit Simulator.
The command line run time will let you run the Fitbit Simulator on OSx or Windows
-- if you have a compatable fitbit watch, you can run code directly on your watch (which is kinda cool).
You will need to log into the command line and Fitbit Simulator with your Fitbit Account,
which doesn't currently work with docker :-(


The URL for the heartsteps-server is set in common/globals.js
-- yes, it's currently hard coded.

Fitbit OS simulator: https://dev.fitbit.com/release-notes/fitbit-os-simulator/

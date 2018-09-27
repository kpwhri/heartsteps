// Get integrationStatus setting & update text in settings
import * as messaging from "messaging";
import document from "document";
import { updateIntegrationStatus } from "./integration-status";

import { geolocation } from "geolocation";
import { locationSuccess, locationError } from "./location";

import { today as activity } from "user-activity";
import * as fs from "fs";
// import * as stepCount from "./step-count-module-easy";
// var stepCount = require("./step-count-module");
import { StepCountHandler } from "./step-count-proto.js";

// Will need to wake the companion up on occasion
// https://dev.fitbit.com/build/guides/companion/

// Update enabled/disabled flag if enrollment succeeds
messaging.peerSocket.onmessage = updateIntegrationStatus;

// Get location
geolocation.enableHighAccuracy = true;
geolocation.getCurrentPosition(locationSuccess, locationError);

// Get & save step count
// Have the timer on the companion kick this off
let stepCount = new StepCountHandler();
console.log(stepCount.currentSteps);

// stepCount.deleteFile();

console.log("First pass");
let s = stepCount.getArray();
console.log("S: " + s);
let m = stepCount.calculateElapsedSteps(s);
console.log("M: " + m);
let t = stepCount.updateArray(s);
console.log("T: " + t);
stepCount.saveFile(t);
setTimeout(console.log(" "), 10000);


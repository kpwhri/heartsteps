import * as global from "../common/globals.js";

// Get integrationStatus setting & update text in settings
import * as messaging from "messaging";
import document from "document";
import { updateIntegrationStatus } from "./integration-status";

// Check recent step count
import { today as activity } from "user-activity";
import * as fs from "fs";
import { StepCountHandler } from "./step-count.js";

// Watch attempts to notify phone of step count & location
const WAKE_INTERVAL = 5;
const MILLISECONDS_PER_MINUTE = 1000 * 60;

function sendStepMessage(recentSteps, time){
  if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    // Send the data to phone as a message
    let data = {
      key: "recentSteps",
      value: recentSteps,
      time: time
    }
    messaging.peerSocket.send(data);
  } else {
    console.log("ERROR: peerSocket not open");
  }
}

function stepCountToPhone(){
  let stepCount = new StepCountHandler();
  let oldStepData = stepCount.getData();
  console.log("original data: " + JSON.stringify(oldStepData));
  let newStepData = stepCount.updateData(oldStepData);
  console.log("updated data: " + JSON.stringify(newStepData));
  let recentSteps = stepCount.calculateElapsedSteps(newStepData);
  console.log("step count: " + recentSteps);
  stepCount.saveFile(newStepData);
  console.log("time is " + stepCount.currentTime);
  sendStepMessage(recentSteps, stepCount.currentTime);
}

// // Standard JS function - not using Companion WakeUp API
// setInterval(function() {
//   stepCountToPhone();
// }, WAKE_INTERVAL*MILLISECONDS_PER_MINUTE);

// Test purposes - run this once, 5 seconds after install
setTimeout(function(){stepCountToPhone()}, 5000);
setTimeout(function(){stepCountToPhone()}, MILLISECONDS_PER_MINUTE*3);

// Update watch message based on integration results
// Listen for enrollment message sent by phone
messaging.peerSocket.onmessage = function(evt) {
  if (evt.data.key == global.INTEGRATION_STATUS_MESSAGE) {
  // Update enabled/disabled flag if enrollment succeeds
    updateIntegrationStatus(evt.data.value);
  }
}

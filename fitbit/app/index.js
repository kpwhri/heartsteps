import { ANTI_SEDENTARY_MESSAGE, INTEGRATION_STATUS_MESSAGE,
  QUERY_STEP_MESSAGE, RECENT_STEPS } from "../common/globals.js";

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

function sendMessage(recentSteps){
  if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    // Send the data to phone as a message
    let data = {
      key: "recentSteps",
      value: recentSteps
    }
    messaging.peerSocket.send(data);
    console.log("Well, it says it sent something: " + JSON.stringify(data));
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
  sendMessage(recentSteps);
}

// Standard JS function - not using Companion WakeUp API
setInterval(function() {
  stepCountToPhone();
}, WAKE_INTERVAL*MILLISECONDS_PER_MINUTE);

setTimeout(function(){stepCountToPhone()}, 5000);

// Listen for message sent by phone
messaging.peerSocket.onmessage = function(evt) {
  if (evt.data.key == INTEGRATION_STATUS_MESSAGE) {
  // Update enabled/disabled flag if enrollment succeeds
    updateIntegrationStatus(evt.data.value);
  }
}

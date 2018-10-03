import { ANTI_SEDENTARY_MESSAGE, INTEGRATION_STATUS_MESSAGE, QUERY_STEP_MESSAGE }
  from "../common/globals.js";

// Get integrationStatus setting & update text in settings
import * as messaging from "messaging";
import document from "document";
import { updateIntegrationStatus } from "./integration-status";

// Check recent step count
import { today as activity } from "user-activity";
import * as fs from "fs";
import { StepCountHandler } from "./step-count.js";

messaging.peerSocket.onmessage = function(evt) {
  if (evt.data.key == INTEGRATION_STATUS_MESSAGE) {
  // Update enabled/disabled flag if enrollment succeeds
    updateIntegrationStatus(evt.data.value);
  } else if (evt.data.key == QUERY_STEP_MESSAGE) {
    // Get & save step count
    let stepCount = new StepCountHandler();
    let oldStepData = stepCount.getData();
    console.log("original data: " + JSON.stringify(oldStepData));
    let newStepData = stepCount.updateData(oldStepData);
    console.log("updated data: " + JSON.stringify(newStepData));
    let recentSteps = stepCount.calculateElapsedSteps(newStepData);
    console.log("step count: " + recentSteps);
    stepCount.saveFile(newStepData);
    // Tell phone to kick off anti-sedentary message if steps below a threshold
    // if (recentSteps < X) {
    //     if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    //       messaging.peerSocket.send(ANTI_SEDENTARY_MESSAGE);
    //     }
    // }
  }
}

let stepCount = new StepCountHandler();
let oldStepData = stepCount.getData();
console.log("original data: " + JSON.stringify(oldStepData));
let newStepData = stepCount.updateData(oldStepData);
console.log("updated data: " + JSON.stringify(newStepData));
let recentSteps = stepCount.calculateElapsedSteps(newStepData);
console.log("step count: " + recentSteps);
stepCount.saveFile(newStepData);

// Get integrationStatus setting & update text in settings
import * as messaging from "messaging";
import document from "document";
import { updateIntegrationStatus } from "./integration-status";

import { geolocation } from "geolocation";
import { locationSuccess, locationError } from "./location";

import { today as activity } from "user-activity";
import * as fs from "fs";
// import { me } from "appbit";

// Will need to wake the companion up on occasion
// https://dev.fitbit.com/build/guides/companion/

// Update enabled/disabled flag if enrollment succeeds
messaging.peerSocket.onmessage = updateIntegrationStatus;

// Get location
geolocation.enableHighAccuracy = true;
geolocation.getCurrentPosition(locationSuccess, locationError);

// Get & save step count
const STEP_ARRAY_40_MINS = "step_count_40_mins";
// File contains daily total followed by the last 8 observations
//   every 5 mins over the last 40 mins.

function getStepCountArray(){
  try {
    let stepArrayAscii = fs.readFileSync(STEP_ARRAY_40_MINS, "ascii");
  } catch (err) {
    if(err == `Error: Couldn't find file: ${STEP_ARRAY_40_MINS}`) {
      let step_total = activity.adjusted.steps;
      let stepArrayAscii = `${step_total},0,0,0,0,0,0,0,0`;
    } else {
      throw err;
    }
  }
  let stepArray = stepArrayAscii.split(',').map(Number);
  return stepArray;
}

function updateStepCountArray(stepArray) {
  let new_step_total = activity.adjusted.steps;
  // Total is removed from stepArray
  let old_step_total = stepArray.shift();
  let dt = Date.now();
  if (dt.hours == 0 && dt.minutes <= 5) {
    // Start a new day
    stepArray = [new_step_total, 0,0,0,0,0,0,0]
    stepArray.push(new_step_total);
  } else {
    // Remove the oldest step count
    stepArray.shift();
    let steps_5_mins = new_step_total - old_step_total;
    stepArray.unshift(new_step_total);
    stepArray.push(steps_5_mins);
  }
  return stepArray;
}

function calcStepCountFortyMins(stepArray) {
  let count40 = stepArray.slice(1).reduce(function(a, b) {
    return a + b;
  })
  return count40;
}

function saveStepCountArray(stepArray){
  fs.writeFileSync(STEP_ARRAY_40_MINS, stepArray.toString(), "ascii");
  return stepArray.toString();
}

function clearStepCountArray(){
  try {
    fs.unlinkSync(STEP_ARRAY_40_MINS);
  } catch (err) {
    }
  }


// Have the timer on the companion kick this off
// clearStepCountArray();

console.log("First pass");
let s = getStepCountArray();
console.log("S: " + s);
let m = calcStepCountFortyMins(s);
console.log("M: " + m);
let t = updateStepCountArray(s);
console.log("T: " + t);
saveStepCountArray(t);
setTimeout(console.log(" "), 10000);


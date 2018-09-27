import { today as activity } from "user-activity";
import * as fs from "fs";

// The step count file is saved with the name referenced by
// the STEP_ARRAY_40_MINS variable.
// This contains an array of 9 integers:
//   * the current total step count for the delay
//   * the last 8 calculated step count,
//     i.e., {current step count} - {prior step count}
//  This data is refreshed every 5 minutes, so the sum of the
//     last 8 observations will be the step count over the last
//     40 minutes.

const STEP_ARRAY_FILE = "step_count_array";
const FITBIT_FILE_NOT_FOUND = `Error: Couldn't find file: ${STEP_ARRAY_FILE}`;
const N_STEP_COUNTS = 8;

export function StepCountHandler() {
  this.currentSteps = activity.adjusted.steps;
}

// Probably just for test purposes - delete step count array file
StepCountHandler.prototype.deleteFile = function() {
  try {
    fs.unlinkSync("step_count_array");
  } catch (err) {
  }
}

// ECMA 5.1 has no repeat function
String.prototype.repeat = function(times) {
   return (new Array(times + 1)).join(this);
};

// Initialize a new string of step count data if necessary
StepCountHandler.prototype.newStepString = function(stepTotal) {
  let nBlanks = "0,".repeat(N_STEP_COUNTS);
  nBlanks = nBlanks.substr(0, nBlanks.length - 1);
  return `${stepTotal},${nBlanks}`;
}

StepCountHandler.prototype.stringToArray = function(stepString) {
  return stepString.split(',').map(Number);
}

StepCountHandler.prototype.getArray = function() {
  try {
    let stepString = fs.readFileSync(STEP_ARRAY_FILE, "ascii");
  } catch (err) {
    // Fitbit's JS engine doesn't return err.code
    // but the following text is used.
    if(err == FITBIT_FILE_NOT_FOUND) {
      let stepString = this.newStepString(this.currentSteps);
    } else {
      throw err;
    }
  }
  return this.stringToArray(stepString);
}

// Calculate the sum of steps over the last 40 mins
StepCountHandler.prototype.calculateElapsedSteps = function(stepArray) {
  let elapsedSteps = stepArray.slice(1).reduce(function(a, b) {
    return a + b;
  })
  return elapsedSteps;
}

// Recompute the step count array based on current data
StepCountHandler.prototype.updateArray = function(stepArray) {
  let newStepTotal = activity.adjusted.steps;
  // Total is removed from stepArray
  let oldStepTotal = stepArray.shift();
  // Start a new day if previous step total > current step total
  if (newStepTotal < oldStepTotal) {
    stepArray = this.getArray(newStepTotal);
    stepArray.push(newStepTotal);
  } else {
    // Remove the oldest step count
    stepArray.shift();
    let stepsElapsed = newStepTotal - oldStepTotal;
    stepArray.unshift(newStepTotal);
    stepArray.push(stepsElapsed);
  }
  return stepArray;
}

// Save the new step count array
StepCountHandler.prototype.saveFile = function(stepArray) {
  fs.writeFileSync(STEP_ARRAY_FILE, stepArray.toString(), "ascii");
}

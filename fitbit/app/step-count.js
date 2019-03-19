import { today as activity } from "user-activity";
import * as fs from "fs";

// Step count file is referenced by the STEP_COUNT_FILE variable.
// This contains an array of step reading objects, each
//   {"time": timestamp in milliseconds, "steps": elapsed steps}
// Elapsed step count is number of steps in past {CUTOFF_MINS}

const STEP_COUNT_FILE = "step_count.json";
const FITBIT_FILE_NOT_FOUND = `Error: Couldn't find file: ${STEP_COUNT_FILE}`;
const CUTOFF_MINS = 40;

export class StepReading {
  constructor() {
    this.time = new Date().getTime();
    this.steps = activity.adjusted.steps;
  }
}

export class StepCountHandler {
  // Time stored as milliseconds since 1970.01.01 for easy maths
  constructor() {
    this.currentTime = new Date().getTime();
    this.currentReading = new StepReading();
  }

  deleteFile() {
    try {
      fs.unlinkSync(STEP_COUNT_FILE);
    } catch (err) {
    }
  }

  // Get data from file system and convert to JSON array
  getData() {
    let stepData;
    try {
      stepData = fs.readFileSync(STEP_COUNT_FILE, "json");
    } catch (err) {
      // Fitbit's JS engine doesn't return err.code
      // but the following text is used.
      if(err == FITBIT_FILE_NOT_FOUND) {
        stepData = '[{"time": 0, "steps": 0}]';
      } else {
        throw err;
      }
    }
    return JSON.parse(stepData);
  }

  // Calculate the maximum difference in steps in array
  // Always run this after updating the array with current data
  calculateElapsedSteps(stepData) {
    let minTime = Number.MAX_VALUE;
    let maxTime = 0;
    let firstStepCount = 0;
    let lastStepCount = 0;
    for (let reading of stepData) {
      if (reading.time < minTime) {
        minTime = reading.time;
        firstStepCount = reading.steps;
      }
      if (reading.time > maxTime) {
        maxTime = reading.time;
        lastStepCount = reading.steps;
      }
    }
    let elapsedSteps = (lastStepCount - firstStepCount);
    // elapsedSteps could be < 0 if stepCount rolls over at midnight
    if (elapsedSteps < 0) {
      elapsedSteps = 0;
    }
    return elapsedSteps;
  }

  // Drop array members with datetimes before threshold
  filterByTime(stepData, cutoffTime) {
    let filtered = [];
    for (let reading of stepData) {
      if (reading.time >= cutoffTime) {
        filtered.push(reading);
      }
    }
    return filtered;
  }

  // Append new reading and drop older data
  updateData(stepData) {
    stepData.push(this.currentReading);
    let cutoffTime = this.currentTime - (CUTOFF_MINS*60*1000);
    // Select all readings since cutoffTime
    let selectData = this.filterByTime(stepData, cutoffTime);
    return selectData;
  }

  // Save the new step count array
  saveFile(stepData) {
    fs.writeFileSync(STEP_COUNT_FILE, JSON.stringify(stepData), "json");
  }
}

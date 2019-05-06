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

  // Convert json array of elapsed steps for the day
  // into a json array of elapsed steps between readings
  calculateElapsedSteps(stepData) {
    let newStepData = [];
    let priorSteps = 0;
    if (stepData[0]) {
      priorSteps = stepData[0].steps;
    }
    let currSteps;
    let n = 0;
    for (let reading of stepData) {
      // If new count is lower, reset the count for the new day
      // Possible miss steps taken since last reading but before midnight
      if (n == 0 || stepData[n].steps < priorSteps) {
        currSteps = stepData[n].steps;
      } else {
        currSteps = stepData[n].steps - priorSteps;
      }
      priorSteps = stepData[n].steps;
      newStepData.push({"time": stepData[n].time, "steps": currSteps});
      n += 1;
    }
    return newStepData;
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

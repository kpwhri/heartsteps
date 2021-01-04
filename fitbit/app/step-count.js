import { today as activity } from "user-activity";
import * as fs from "fs";
import * as messaging from "messaging";

import { BodyPresenceSensor } from "body-presence";

const bodyPresenceSensor = new BodyPresenceSensor();
bodyPresenceSensor.start();

export class StepCounter {

  constructor() {
    this.step_count_file_name = "step_count.json"
    this.interval_minutes = 5;
    this.cutoff_minutes = 40;
  }

  update() {
    console.log("Updating Step Counter");
    let step_counts = this.loadStepCounts();
    step_counts.sort(function(a, b) {
      return b.time - a.time;
    });
    const filtered_step_counts = [];
    const cutoffTime = new Date().getTime() - this.cutoff_minutes * 60 * 1000;
    step_counts.forEach(function(count) {
      if (count.time > cutoffTime) {
        filtered_step_counts.push(count);
      }
    });
    step_counts = filtered_step_counts;
    // filter old step counts
    if(!step_counts.length) {
      step_counts.push(this.makeStepCount());
    } else {

      const last_step_count = step_counts[0];
      const timeDiff = new Date().getTime() - last_step_count.time;
      const timeBuffer = this.interval_minutes * 60 * 1000;
      if(timeDiff >= timeBuffer) {
        console.log("Add step count");
        step_counts.push(this.makeStepCount());
      }
    }

    console.log(step_counts.length);
    fs.writeFileSync(this.step_count_file_name, step_counts, "json");

    if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
      messaging.peerSocket.send({
        steps: step_counts
      });
    }
  }

  makeStepCount() {
    return {
      time: new Date().getTime(),
      stepCount: activity.adjusted.steps
    }
  }

  loadStepCounts() {
    try {
      const stepData = fs.readFileSync(this.step_count_file_name, "json");
      return stepData;
    } catch (err) {
      const data = [];
      fs.writeFileSync(this.step_count_file_name, data, "json");
      return data;
    }
  }

}

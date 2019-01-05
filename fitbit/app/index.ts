import * as global from "../common/globals.js";

// Clockface imports
import clock from "clock"; // needed to have a clock! (see line 33)
import document from "document"; // needed for I have no idea what! If you don't put this nothing works!!!
import { preferences } from "user-settings"; // needed to get the user preference 12h or 24h (see line 38)
import { zeroPad, } from "../common/globals"; // import user function zeroPad (see lines 43, 45, 46)
import { HeartRateSensor } from "heart-rate"; // import HR reading from sensor (seel line 18)
import { battery } from "power"; // import battery level (see line26)
import userActivity from "user-activity"; //adjusted types (matching the stats that you upload to fitbit.com, as opposed to local types)

// Other functionality imports
// Get integrationStatus setting & update text in settings
import * as messaging from "messaging";
// import document from "document"; // Duplicated under clockface;
// import { updateIntegrationStatus } from "./integration-status"; // No longer used;
// Check recent step count
import { today as activity } from "user-activity";
import * as fs from "fs";
import { StepCountHandler, StepReading } from "./step-count.js";

// Watch attempts to notify phone of step count & location
const WAKE_INTERVAL = 5;
const MILLISECONDS_PER_MINUTE = 1000 * 60;

// Clockface
// Update the clock every minute
clock.granularity = "seconds"; //clock is refreshing every sec. It is possible to select minutes as well
// Get a handle on the <text> elements specified in the index.gui file
const timeHandle = document.getElementById("timeLabel");
const batteryHandle = document.getElementById("batteryLabel");
const stepsHandle = document.getElementById("stepsLabel");
const heartrateHandle = document.getElementById("heartrateLabel");

// The following block read the heart rate from your watch
const hrm = new HeartRateSensor();

hrm.onreading = function() {
  heartrateHandle.text = `${hrm.heartRate}`; // the measured HR is being sent to the heartrateHandle set at line 16
}
hrm.start();

// Update the <text> element every tick with the current time
clock.ontick = (evt) => {
  const now = evt.date; // get the actual instant
  let hours = now.getHours(); // separate the actual hours from the instant "now"
  let mins = now.getMinutes(); // separate the actual minute from the instant "now"
  let secs = now.getSeconds(); // separate the actual second from the instan "now"
  if (preferences.clockDisplay === "12h") { // check from your wach settings if you use 12h or 24h visualization
    // 12h format
    hours = hours % 12 || 12;
  } else {
    // 24h format
    hours = zeroPad(hours); // when you use 24h in case hours are in one digit then I put a zero in front. i.e. 3 am -> 03
  }
  let minsZeroed = zeroPad(mins); // one digit mins get a zero in front
  let secsZeroes = zeroPad(secs); // one digit secs get a zero in front
  timeHandle.text = `${hours}:${minsZeroed}:${secsZeroes}`; // time in format hh:mm:ss is assigned in the timeHandle defined at line 13


  // Activity Values: adjusted type
  let stepsValue = (userActivity.today.adjusted["steps"] || 0); // steps value measured from fitbit is assigned to the variable stepsValue
  let stepsString = stepsValue + ' steps'; // I concatenate a the stepsValue (line above) with th string ' steps' and assign to a new variable
  stepsHandle.text = stepsString; // the string stepsString is being sent to the stepsHandle set at line 15

  // Battery Measurement
  let batteryValue = battery.chargeLevel; // measure the battery level and send it to the variable batteryValue

  // Assignment value battery
  batteryHandle.text = `Batt: ${batteryValue} %`; // the string including the batteryValue is being sent to the batteryHandle set at line 14
}

function sendStepMessage(recentSteps: Number, time: Number){
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
  let stepCount: StepCountHandler;
  stepCount = new StepCountHandler();
  let oldStepData: Array<StepReading>;
  oldStepData = stepCount.getData();
  console.log("original data: " + JSON.stringify(oldStepData));
  let newStepData: Array<StepReading>;
  newStepData = stepCount.updateData(oldStepData);
  console.log("updated data: " + JSON.stringify(newStepData));
  let recentSteps: Number;
  recentSteps = stepCount.calculateElapsedSteps(newStepData);
  console.log("step count: " + recentSteps);
  stepCount.saveFile(newStepData);
  console.log("time is " + stepCount.currentTime);
  sendStepMessage(recentSteps, stepCount.currentTime);
}

// Update watch message based on integration results
// Listen for enrollment message sent by phone
// (Not used with new clockface)
// messaging.peerSocket.onmessage = function(evt) {
//   if (evt.data.key == global.INTEGRATION_STATUS_MESSAGE) {
//   // Update enabled/disabled flag if enrollment succeeds
//     updateIntegrationStatus(evt.data.value);
//   }
// }

// // Standard JS function - not using Companion WakeUp API
setInterval(function() {
  stepCountToPhone();
}, WAKE_INTERVAL*MILLISECONDS_PER_MINUTE);

// Test purposes - run this once, 30 seconds after install
// setTimeout(function(){stepCountToPhone()}, MILLISECONDS_PER_MINUTE*0.5);

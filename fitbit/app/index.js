import document from "document";

// Get integrationStatus setting & update text in settings
import * as messaging from "messaging";

// On-body presence
import { BodyPresenceSensor } from "body-presence";

// Clock-specific imports
import * as simpleActivity from "./simple/activity";
import * as simpleClock from "./simple/clock";
import * as simpleHRM from "./simple/hrm";
import * as simpleSettings from "./simple/device-settings";

import { StepCountHandler, StepReading } from "./step-count.js";

// Watch notifies phone of step count & location
const WAKE_INTERVAL = 5;
const MILLISECONDS_PER_MINUTE = 1000 * 60;

let background = document.getElementById("background");
let dividers = document.getElementsByClassName("divider");
let txtTime = document.getElementById("txtTime");
let txtDate = document.getElementById("txtDate");
let txtHRM = document.getElementById("txtHRM");
let iconHRM = document.getElementById("iconHRM");
let imgHRM = iconHRM.getElementById("icon");
let statsCycle = document.getElementById("stats-cycle");
let statsCycleItems = statsCycle.getElementsByClassName("cycle-item");
let txtWarning = document.getElementById("txtWarning");
let lower = document.getElementById("#lower");
let pin = document.getElementById("pin");

/* --------- CLOCK ---------- */
function clockCallback(data) {
  txtTime.text = data.time;
  txtDate.text = data.date;
}
simpleClock.initialize("minutes", "heartStepsDate", clockCallback);

/* ------- ACTIVITY --------- */
function activityCallback(data) {
  statsCycleItems.forEach((item, index) => {
    let img = item.firstChild;
    let txt = img.nextSibling;
    txt.text = data[Object.keys(data)[index]].pretty;
    // Reposition the activity icon to the left of the variable length text
    img.x = txt.getBBox().x - txt.parent.getBBox().x - img.width - 7;
  });
}
simpleActivity.initialize("seconds", activityCallback);

/* -------- HRM ------------- */
function hrmCallback(data) {
  txtHRM.text = `${data.bpm}`;
  if (data.zone === "out-of-range") {
    imgHRM.href = "images/heart_open.png";
  } else {
    imgHRM.href = "images/heart_solid.png";
  }
  if (data.bpm !== "--") {
    iconHRM.animate("highlight");
  }
}
simpleHRM.initialize(hrmCallback);

/* -------- SETTINGS -------- */
function settingsCallback(data) {
  if (!data) {
    return;
  }
  if (data.integrationStatus) {
    if (data.integrationStatus == "success") {
      txtWarning.style.display = "none";
      lower.style.opacity = 1.0;
    } else {
      txtWarning.style.display = "inline";
      lower.style.opacity = 0.2;
    }
  }
  if (data.colorBackground) {
    background.style.fill = data.colorBackground;
  }
  if (data.colorDividers) {
    dividers.forEach(item => {
      item.style.fill = data.colorDividers;
    });
  }
  if (data.colorTime) {
    txtTime.style.fill = data.colorTime;
  }
  if (data.colorDate) {
    txtDate.style.fill = data.colorDate;
  }
  if (data.colorActivity) {
    statsCycleItems.forEach((item, index) => {
      let img = item.firstChild;
      let txt = img.nextSibling;
      img.style.fill = data.colorActivity;
      txt.style.fill = data.colorActivity;
    });
  }
  if (data.colorHRM) {
    txtHRM.style.fill = data.colorHRM;
  }
  if (data.colorImgHRM) {
    imgHRM.style.fill = data.colorImgHRM;
  }
}
simpleSettings.initialize(settingsCallback);

/* -- On initialization, phone should send info on whether to display -- */
/* -- help text or full stats depending on authentication status -- */

/* ------- Send step data to the phone ---------*/
function sendStepMessage(recentSteps, time){
  if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    let data = {
      key: "recentSteps",
      value: recentSteps,
      time: time
    }
    console.log(data['value']);
    console.log(data['time']);
    messaging.peerSocket.send(data);
  } else {
    console.log("ERROR: peerSocket not open");
  }
}

// Start sensor to detect if watch is being worn
let bodyPresenceSensor = new BodyPresenceSensor();
bodyPresenceSensor.start();

// Process step data and send if watch being worn
function stepCountToPhone(){
  let stepCount = new StepCountHandler();
  let oldStepData = stepCount.getData();
  // console.log("original data: " + JSON.stringify(oldStepData));
  let newStepData = stepCount.updateData(oldStepData);
  // console.log("updated data: " + JSON.stringify(newStepData));
  stepCount.saveFile(newStepData);
  let readNewStepData = stepCount.calculateElapsedSteps(newStepData);
  // console.log("new step array: " + JSON.stringify(readNewStepData));
  if (bodyPresenceSensor.present) {
    sendStepMessage(readNewStepData, stepCount.currentTime);
  }
}

setInterval(function() {
  stepCountToPhone();
}, WAKE_INTERVAL * MILLISECONDS_PER_MINUTE);

/*--- When watch receives message from phone to input pin ---*/
messaging.peerSocket.onmessage = function(evt) {
  // Output the message to the console
  let p = JSON.stringify(evt.data);
  console.log(p);
  console.log(p.replace(/\"/g, ""));
  let o = p.replace(/\"/g, "");
  pin.text = o;
}

/*--- Button for when user wants to check if pin is connected to user ---*/
pin.onclick = function(evt) {
  console.log("clicked");
  if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    let data = {
      key: "checkAuthorization"
    }
    messaging.peerSocket.send(data);
  } 
}
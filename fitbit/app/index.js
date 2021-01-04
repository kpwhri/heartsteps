import document from "document";
import * as messaging from "messaging";

// Clock-specific imports
import * as simpleClock from "./simple/clock";
import * as global from "../common/globals";

import { StepCounter } from "./step-count";

const timeElement = document.getElementById("txtTime");
const dateElement = document.getElementById("txtDate");

const statusElement = document.getElementById("status");
const pinElement = document.getElementById("pin");

simpleClock.initialize("minutes", "heartStepsDate", function(data) {
  timeElement.text = data.time;
  dateElement.text = data.date;
});

function updateState(status, pin) {
  statusElement.text = status;
  pinElement.text = pin;
}

function updateStatus(status) {
  statusElement.text = status;
}

let checkAuthorizationTimeout;
function checkAuthorization() {
  console.log("check authoriztion");
  if (checkAuthorizationTimeout) {
    clearTimeout(checkAuthorization);
    checkAuthorizationTimeout = undefined;
  }
  if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    let data = {
      key: global.CHECK_AUTH
    }
    messaging.peerSocket.send(data);
  } else {
    updateStatus("Not Connected (Retrying)");
    checkAuthorizationTimeout = setTimeout(function() {
      checkAuthorization()
    }, 1000);
  }
}

messaging.peerSocket.onmessage = function(event) {
  updateState(
    event.data.status,
    event.data.pin
  );
}

timeElement.onclick = function(evt) {
 checkAuthorization();
 sendStepCounts();
}

checkAuthorization();

const stepCounter = new StepCounter();

function sendStepCounts() {
  console.log("Send step counts");
  stepCounter.update();
  if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    let data = {
      key: global.RECENT_STEPS,
      steps: stepCounter.getStepCounts()
    }
    messaging.peerSocket.send(data);
  }
}

dateElement.onclick = function() {
  sendStepCounts();
};

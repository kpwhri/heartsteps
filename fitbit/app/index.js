import document from "document";
import * as messaging from "messaging";
import { BodyPresenceSensor } from "body-presence";

// Clock-specific imports
import * as simpleClock from "./simple/clock";
import * as global from "../common/globals"

let timeElement = document.getElementById("txtTime");
let dateElement = document.getElementById("txtDate");

const statusElement = document.getElementById("status");
const tokenElement = document.getElementById("token");

simpleClock.initialize("minutes", "heartStepsDate", function(data) {
  timeElement.text = data.time;
  dateElement.text = data.date;
});

// Start sensor to detect if watch is being worn
let bodyPresenceSensor = new BodyPresenceSensor();
bodyPresenceSensor.start();

setInterval(function() {
  if (bodyPresenceSensor.present) {
    console.log("Send steps??");
  }
}, 5 * 60 * 1000); // every 5 minutes

messaging.peerSocket.onmessage = function(event) {
  if (event.data.status) {
    dateElement.style.opacity = 0;
    statusElement.style.opacity = 1;
    statusElement.text = event.data.status;
  } else {
    dateElement.style.opacity = 1;
    statusElement.style.opacity = 0;
  }

  if (event.data.authorized) {
    tokenElement.style.opacity = 0;
  } else {
    tokenElement.style.opacity = 1;
  }

  if (event.data.pin) {
    tokenElement.text = event.data.pin;
  } else {
    tokenElement.text = "";
  }
}

timeElement.onclick = function(evt) {
  console.log("time clicked");
  if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    let data = {
      key: global.CHECK_AUTH
    }
    messaging.peerSocket.send(data);
  } 
}
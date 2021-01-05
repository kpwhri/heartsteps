import document from "document";
import * as fs from "fs";
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

class AppState {

  stateFileName = 'watch-app-state.txt';

  constructor() {
    this.load();    
  }

  update() {
    if (this.loading) {
      dateElement.style.opacity = 0;
      statusElement.style.opacity = 1;
      statusElement.text = "Loading";
    } else if (this.authorized) {
      dateElement.style.opacity = 1;
      statusElement.style.opacity = 0;
      statusElement.text = "Authorized"
    } else {
      dateElement.style.opacity = 0;
      statusElement.style.opacity = 1;
      statusElement.text = "Unauthorized"
    }

    if (this.pin) {
      pinElement.text = this.pin;
    } else {
      pinElement.text = "No Pin";
    }
  }

  getAuthorization() {
    if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
      this.loading = true;
      let data = {
        key: global.CHECK_AUTH
      }
      messaging.peerSocket.send(data);
    } else {
      this.loading = false;
    }
  }

  load() {
    try {
      const state = fs.readFileSync(this.stateFileName, "json");
      this.authorized = state.authorized;
      this.pin = state.pin;
      this.loading = false;
      this.update();
    } catch(error) {
      console.log("This is an error");
      console.log(error);
      this.authorized = false;
      this.pin = undefined;
      this.getAuthorization();
    }
  }

  save(authorized, pin) {
    const appState = {
      "authorized": authorized,
      "pin": pin
    }
    fs.writeFileSync(this.stateFileName, appState, "json");
    this.load();
  }

}

const stepCounter = new StepCounter();
const app = new AppState();

timeElement.onclick = function(evt) {
  app.getAuthorization();
  stepCounter.update();
 }

 setInterval(function() {
   stepCounter.update()
 }, 60 * 1000);

 messaging.peerSocket.addEventListener("open", function (event) {
  console.log("messaging connected");
  document.getElementById("status-icon").style.fill = "#00FF00";
  app.update();
 });

 messaging.peerSocket.addEventListener("error", function (error) {
   console.log("messaging disconnected");
   console.log(error)
   document.getElementById("status-icon").style.fill = "#FF0000";
 });

 document.getElementById("status-icon").style.fill = "#0000FF";



 messaging.peerSocket.onmessage = function(event) {
  app.save(
    event.data.authorized,
    event.data.pin
  );
}

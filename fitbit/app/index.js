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
    const statusElement = document.getElementById("status");
    if (this.loading) {
      statusElement.text = "Loading";
    } else if (this.authorized) {
      statusElement.text = "Authorized"
    } else {
      statusElement.text = "Unauthorized"
    }

    const pinElement = document.getElementById("pin");
    if (this.pin) {
      pinElement.text = this.pin;
    } else {
      pinElement.text = "No Pin";
    }
  }

  getAuthorization() {
    if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
      let data = {
        key: global.CHECK_AUTH
      }
      messaging.peerSocket.send(data);
    } else {
      console.log("Debounce get authorization");
      setTimeout(function() {
        console.log("Debounce not implemented...");
      }, 1000);
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
      this.loading = true;
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
app.update();

timeElement.onclick = function(evt) {
  app.getAuthorization();
  stepCounter.update();
 }

 setInterval(function() {
   stepCounter.update()
 }, 60 * 1000);

 messaging.peerSocket.onmessage = function(event) {
  app.save(
    event.data.authorized,
    event.data.pin
  );
}

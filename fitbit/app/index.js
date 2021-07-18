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
const statusIconElement = document.getElementById("status-icon");
const pinElement = document.getElementById("pin");

simpleClock.initialize("minutes", "heartStepsDate", function(data) {
  timeElement.text = data.time;
  dateElement.text = data.date;
});

class AppState {

  stateFileName = 'watch-app-state.txt';

  authorized = false;
  pin = false;

  status = 'Starting';
  loading = false;

  constructor() {
    this.load();    
  }

  update() {
    statusElement.text = this.status;

    if (this.loading || !this.authorized || !this.pin) {
      dateElement.style.opacity = 0;
      statusElement.style.opacity = 1;
    } else {
      dateElement.style.opacity = 1;
      statusElement.style.opacity = 0;
    }

    if (this.pin) {
      pinElement.text = this.pin;
    } else {
      pinElement.text = "No Pin";
    }
  }

  getStatus() {
    if (this.loading) {
      return 'Loading'
    }
    if (this.authorized) {
      return 'Authorized';
    }
    if (this.pin) {
      return 'Enter Pin';
    }
    return 'Missing Pin'

  }

  getAuthorization() {
    if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
      this.loading = true;
      this.status = 'Fetching authorization';
      let data = {
        key: global.CHECK_AUTH
      }
      messaging.peerSocket.send(data);
      console.log('App: Sent authrization request');
    } else {
      console.log('App: get authorization failed');
      this.loading = false;
      this.status = 'Not connected';
      this.update();
    }
  }

  load() {
    this.loading = true;
    this.update();
    try {
      const state = fs.readFileSync(this.stateFileName, "json");
      this.authorized = state.authorized;
      this.pin = state.pin;
      this.loading = false;
      this.status = this.getStatus();
      this.update();
    } catch(error) {
      console.log("This is an error");
      console.log(error);
      this.authorized = false;
      this.pin = undefined;
      this.loading = false;
      this.status = 'Loading failed'
      this.update()
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


statusIconElement.onclick = function(evt) {
  app.getAuthorization();
  stepCounter.update();
 }


 setInterval(function() {
   stepCounter.update()
 }, 60 * 1000);

 messaging.peerSocket.addEventListener("open", function (event) {
  console.log("messaging connected");
  statusIconElement.style.fill = "#00FF00";
  app.load();
 });

 messaging.peerSocket.addEventListener("error", function (error) {
   console.log("messaging disconnected");
   console.log(error)
   statusIconElement.style.fill = "#FF0000";
 });
 statusIconElement.style.fill = "#0000FF";



 messaging.peerSocket.onmessage = function(event) {
    app.save(
        event.data.authorized,
        event.data.pin
    );
    if (!event.data.pin) {
        console.log("No pin, update again");
        setTimeout(function() {
            app.getAuthorization();
        }, 30 * 1000);
    }
}

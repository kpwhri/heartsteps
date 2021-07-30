import document from "document";
import * as fs from "fs";
import * as messaging from "messaging";
import { vibration } from "haptics";

// Clock-specific imports
import * as simpleClock from "./simple/clock";
import clock from "clock";
import { today as activity } from "user-activity";

import { StepCounter } from "./step-count";

const timeElement = document.getElementById("txtTime");
const dateElement = document.getElementById("txtDate");
const statusElement = document.getElementById("status");
const pinElement = document.getElementById("pin");
const stepCountElement = document.getElementById('step-counts');

simpleClock.initialize("minutes", "heartStepsDate", function(data) {
  timeElement.text = data.time;
  dateElement.text = data.date;
});


function updateStepCount() {
  const step_count = activity.adjusted.steps;
  const step_count_formatted = step_count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  stepCountElement.text = step_count_formatted.toString() + ' steps';
}
clock.granularity = "seconds";
clock.addEventListener("tick", function(){
  updateStepCount();
});

class AppState {

  stateFileName = 'watch-app-state.txt';

  authorized = false;
  pin = false;

  connected = false;
  loading = false;

  stepCounter;

  constructor() {
    this.stepCounter = new StepCounter();
    this.load();
  }

  set_loading() {
    this.loading = true;
    this.update();
  }

  set_not_loading() {
    this.loading = false;
    this.update();
  }

  set_connected() {
    this.connected = true;
    this.update();
  }

  set_disconnected() {
    this.disconnected = true;
    this.update();
  }

  update() {
    dateElement.style.opacity = 0;
    statusElement.style.opacity = 1;

    if (!this.connected) {
      statusElement.text = 'Not Connected';
    } else if (this.loading) {
      statusElement.text = 'Loading';
    } else if (!this.pin) {
      statusElement.text = 'No Pin';
    } else if (!this.authorized) {
      statusElement.text = 'Enter Pin: ' + this.pin;
    } else {
      statusElement.text = '';

      dateElement.style.opacity = 1;
      statusElement.style.opacity = 0;
    }

  }

  requestStatus() {
    if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
      this.set_loading();
      try {
        messaging.peerSocket.send({

        });
        this.log('Sent authrization request');
      } catch(error) {
        this.set_not_loading();
        this.set_disconnected();
      }
    } else {
      this.set_disconnected();
    }
  }

  load() {
    this.set_loading();
    try {
      const state = fs.readFileSync(this.stateFileName, "json");

      this.authorized = state.authorized;
      this.pin = state.pin;      

      this.set_not_loading();
    } catch(error) {
      this.authorized = false;
      this.pin = undefined;

      this.requestStatus();
    }
  }

  refresh() {
    this.requestStatus();
    this.stepCounter.update();
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

const app = new AppState();

document.getElementById('#refresh').addEventListener('click', function() {
  app.refresh();
  vibration.start('bump');
  setTimeout(function() {
    vibration.stop();
  }, 500);
});

 messaging.peerSocket.addEventListener("open", function (event) {
  app.set_connected();
  app.refresh();
 });

 messaging.peerSocket.addEventListener("error", function (error) {
  app.set_disconnected();
 });

messaging.peerSocket.onmessage = function(event) {
  app.set_not_loading();
  app.save(
    event.data.authorized,
    event.data.pin
  );

  if (!event.data.pin) {
    app.requestStatus();
  }
}

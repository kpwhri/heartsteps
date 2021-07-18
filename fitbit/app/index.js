import document from "document";
import * as fs from "fs";
import * as messaging from "messaging";

// Clock-specific imports
import * as simpleClock from "./simple/clock";
import * as global from "../common/globals";
import clock from "clock";
import { today as activity } from "user-activity";

import { StepCounter } from "./step-count";

const timeElement = document.getElementById("txtTime");
const dateElement = document.getElementById("txtDate");
const statusElement = document.getElementById("status");
const pinElement = document.getElementById("pin");
const stepCountElement = document.getElementById('step-counts');

const statusIconActiveElement = document.getElementById("status-icon-active");
const statusIconConnectedElement = document.getElementById("status-icon-connected");
const statusIconErrorElement = document.getElementById("status-icon-error");

simpleClock.initialize("minutes", "heartStepsDate", function(data) {
  timeElement.text = data.time;
  dateElement.text = data.date;
});


function updateStepCount() {
  const step_count = activity.adjusted.steps;
  stepCountElement.text = step_count + ' steps';
}
clock.granularity = "seconds";
clock.addEventListener("tick", function(){
  updateStepCount();
});

class AppState {

  stateFileName = 'watch-app-state.txt';

  authorized = false;
  pin = false;

  status = 'Starting';
  loading = false;
  error = false;

  logs = [];

  stepCounter;

  constructor() {
    this.stepCounter = new StepCounter();
    this.load();
  }

  log(message, status="log") {
    const now = 123;
    console.log('App:' + message + '(' + status + ':' + now + ')');
  }

  log_error(message) {
    this.log(message, 'error');
  }

  set_status(message) {
    this.status = message;
    this.update();
  }

  set_error(message) {
    this.error = true;
    this.set_status(message);
  }

  clear_error() {
    this.error = false;
    this.set_status();
  }

  show_loading(message) {
    this.loading = true;
    this.set_status(message);
  }

  stop_loading() {
    this.loading = false;
    this.set_status();
  }

  update() {
    if (!this.status && !this.pin) {
      this.status = 'No Pin';
    }
    if (!this.status && !this.authorized) {
      this.status = 'Enter Pin';
    }
    statusElement.text = this.status;

    if (this.status) {
      dateElement.style.opacity = 0;
      statusElement.style.opacity = 1;
    } else {
      dateElement.style.opacity = 1;
      statusElement.style.opacity = 0;
    }
    this.updatePin();
    this.updateStatusIcon();
  }

  updatePin() {
    if (this.authorized || !this.pin) {
      pinElement.style.opacity = 0;
      stepCountElement.style.opacity = 1;
    } else {
      pinElement.text = this.pin;
      pinElement.style.opacity = 1;
      stepCountElement.style.opacity = 0;
    }
  }

  updateStatusIcon() {
    if(this.loading) {
      statusIconActiveElement.style.opacity = 1;
      statusIconConnectedElement.style.opacity = 0;
      statusIconErrorElement.style.opacity = 0;
    } else if(this.error || !this.authorized) {
      statusIconActiveElement.style.opacity = 0;
      statusIconConnectedElement.style.opacity = 0;
      statusIconErrorElement.style.opacity = 1;
    } else {
      statusIconActiveElement.style.opacity = 0;
      statusIconConnectedElement.style.opacity = 1;
      statusIconErrorElement.style.opacity = 0;
    }
  }

  updateStatus() {
    this.show_loading('Updating');
    if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
      try {
        messaging.peerSocket.send({
          key: global.CHECK_AUTH
        });
        this.log('Sent authrization request');
      } catch(error) {
        this.log_error(error);
        this.set_error('Update failed');
      }
    } else {
      this.log_error('Get authorization failed, peer socket not open');
      this.set_error('No connection');
      this.retryUpdate();
    }
  }

  retryUpdate() {
    const app = this;
    setTimeout(function() {
      app.updateStatus();
    }, 5 * 1000);
  }

  load() {
    this.show_loading('Loading app');
    try {
      const state = fs.readFileSync(this.stateFileName, "json");

      this.authorized = state.authorized;
      this.pin = state.pin;      

      this.stop_loading();
    } catch(error) {
      this.log_error(error);

      this.authorized = false;
      this.pin = undefined;

      this.updateStatus();
    }
  }

  refresh() {
    this.updateStatus();
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

document.getElementsByClassName('status-icon').map((element, index) => {
  element.addEventListener("click", function() {
    app.refresh();
  });
});

 messaging.peerSocket.addEventListener("open", function (event) {
  app.log("peer socket open");
  app.clear_error();
 });

 messaging.peerSocket.addEventListener("error", function (error) {
   app.log_error("peer socket error " + error);
   app.set_error('No connection');
 });

messaging.peerSocket.onmessage = function(event) {
  app.log('peer socket sent data')
  app.save(
    event.data.authorized,
    event.data.pin
  );
  if (!event.data.pin) {
    app.log("No pin update again");
    app.getAuthorization();
  }
}

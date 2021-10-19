import document from "document";
import * as fs from "fs";
import * as messaging from "messaging";
import { vibration } from "haptics";

import { preferences } from "user-settings";
import { zeroPad } from "./simple/utils";
import { daysLong, months } from "./simple/locales/en.js";
import clock from "clock";
import { today as activity } from "user-activity";

import { StepCounter } from "./step-count";

const timeElement = document.getElementById("clock");
const dayElement = document.getElementById("txtDay");
const dateElement = document.getElementById("txtDate");
const statusElement = document.getElementById("status");
const pinElement = document.getElementById("pin");
const stepCountElement = document.getElementById('step-counts');

function updateClock(date) {
  let hours = date.getHours();
  if (preferences.clockDisplay === "12h") {
    // 12h format
    hours = hours % 12 || 12;
  }
  timeElement.text = zeroPad(hours) + ":" + zeroPad(date.getMinutes());
}

function updateDate(today) {
  const dayNameLong = daysLong[today.getDay()];
  dayElement.text = dayNameLong;
  
  let dayNumber = zeroPad(today.getDate());
  let monthName = months[today.getMonth()];
  dateElement.text = monthName + " " + dayNumber

}

function updateStepCount() {
  const step_count = activity.adjusted.steps;
  const step_count_formatted = step_count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  stepCountElement.text = step_count_formatted.toString() + ' steps';
}

function updateDailyStepGoal() {
  const test_daily_step_goal = 5000;
}

clock.granularity = "seconds";
clock.addEventListener("tick", function(event){
  updateStepCount();
  if (event.date) {
    updateClock(event.date);
    updateDate(event.date);
  }
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
    this.connected = false;
    this.update();
  }

  update() {
    dateElement.style.opacity = 0;
    dayElement.style.opacity = 0;
    statusElement.style.opacity = 1;
    pinElement.style.opacity = 1;

    pinElement.text = this.pin;

    if (!this.connected) {
      statusElement.text = 'Not Connected';
    } else if (this.loading) {
      statusElement.text = 'Loading';
    } else if (!this.pin) {
      statusElement.text = 'No Pin';
    } else if (!this.authorized) {
      statusElement.text = 'Enter Pin';
    } else {
      statusElement.text = '';

      dateElement.style.opacity = 1;
      dayElement.style.opacity = 1;
      statusElement.style.opacity = 0;
      pinElement.style.opacity = 0;
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

[
  stepCountElement,
  timeElement,
  dayElement,
  dateElement,
  pinElement,
  statusElement
].map(function(element){
  element.addEventListener('click', function() {
    app.refresh();
    vibration.start('bump');
    // setTimeout(function() {
    //   vibration.stop();
    // }, 500);
  });
})

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

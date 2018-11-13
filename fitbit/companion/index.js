import { settingsStorage } from "settings";
import * as messaging from "messaging";
import * as fs from "fs";
import { me } from "companion";

// Post entryCode to server and display result
import { enrollParticipant, enrollSettingsValid, sendData }
  from "./enrollment";

// Get location
import { geolocation } from "geolocation";
import { locationSuccess, locationError } from "./location";

import * as global from "../common/globals.js";

/************************************************************
  Look for when Entry Code & Birth Year are updated in watch settings
  and send that code to the HeartSteps server for validation.
*************************************************************/
function updateEnrollStatus(evtKey){
  if (evtKey == global.ENTRY_CODE || evtKey == global.BIRTH_YEAR) {
    let entryCode = global.parseSettingsValue(settingsStorage.getItem(global.ENTRY_CODE)).toUpperCase();
    let birthYr = global.parseSettingsValue(settingsStorage.getItem(global.BIRTH_YEAR));
    let enrollValid = enrollSettingsValid(entryCode, birthYr);
    if (enrollValid == global.VALID) {
      enrollParticipant(global.parseSettingsValue(settingsStorage.getItem(global.ENTRY_CODE)),
                        global.parseSettingsValue(settingsStorage.getItem(global.BIRTH_YEAR)))
    } else {
      settingsStorage.setItem(global.INTEGRATION_STATUS_MESSAGE, enrollValid);
      sendData({
        key: global.INTEGRATION_STATUS_MESSAGE,
        value: settingsStorage.getItem(global.INTEGRATION_STATUS_MESSAGE)
      });
    }
  }
}

// Event fires when a setting is changed
// The newValue is already set in settingsStorage
settingsStorage.onchange = function(evt) {
  if (evt.key == global.ENTRY_CODE || evt.key == global.BIRTH_YEAR) {
    let enrollStatus = updateEnrollStatus(evt.key);
  }
}

// Settings were changed while the companion was not running
if (me.launchReasons.settingsChanged) {
  // Give this a try at any time, in case it's enrollment
  let enrollStatus = updateEnrollStatus(global.ENTRY_CODE);
}

/***************************************
  Send location data to the server
***************************************/
const PLACE_SOURCE = "watch";
function sendLocation(lat, long, place) {
  let token = settingsStorage.getItem(global.AUTHORIZATION_TOKEN);
  if (token) {
    const url = `${global.BASE_URL}/api/locations/`;
    let data = {"latitude": lat, "longitude": long, source: PLACE_SOURCE};
    fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`
      }
    }).then(function(response) {
      if (response.status != 201) {
        console.log("ERROR: sendLocation completed with status "+ response.status);
      }
    }).catch(error => console.error('Error in sendLocation: ', error))
  } else {
    console.log("ERROR in sendLocation: user not authenticated");
  }
}

// Get location
function getLatLong() {
  let geo = {};
  geolocation.getCurrentPosition(
    (position) => {
      sendLocation(position.coords.latitude, position.coords.longitude, PLACE_SOURCE);
    },
    (error) => {
      sendLocation(0, 0, PLACE_SOURCE);
    },
    { "enableHighAccuracy" : true }
  );
}

// Send step data to server - scaffolding
function sendSteps(lat, long, place) {
  const url = `${global.BASE_URL}/api/antised?/`;
  let data = {"steps": steps, "dtm": dtm};
  fetch(url, {
    method: "POST",
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(function(response) {
    if (response.status != 201) {
      console.log("ERROR: sendSteps completed with status "+ response.status);
    }
    console.log("sendSteps completed with status " + response.status);
  }).catch(error => console.error('Error in sendSteps: ', error))
}

// Listen for step data from the watch
// then send Step and Location data to server
messaging.peerSocket.onmessage = function(evt) {
  if (evt.data.key == global.RECENT_STEPS) {
    console.log("Send step message to server soon!");
    // Probably send location at same time
    getLatLong();
  } else {
    console.log(evt.data.key);
  }
}

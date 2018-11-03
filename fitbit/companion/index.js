import { settingsStorage } from "settings";
import * as messaging from "messaging";
import * as fs from "fs";
import { me } from "companion";
import companion from "companion";

// Post entryCode to server and display result
import { sendSettingsData, updateEntryCode } from "./entry-code";

// Get location
import { geolocation } from "geolocation";
import { locationSuccess, locationError } from "./location";

import { ANTI_SEDENTARY_MESSAGE, AUTHORIZATION_TOKEN, ENTRY_CODE, HEARTSTEPS_ID,
  INTEGRATION_STATUS_MESSAGE, QUERY_STEP_MESSAGE, RECENT_STEPS } from "../common/globals.js";

const BASE_URL = "https://heartsteps-kpwhri.appspot.com";

/************************************************************
  Look for when Entry Code is updated in watch settings
  and send that code to the HeartSteps server for validation.
*************************************************************/
// Event fires when a setting is changed
settingsStorage.onchange = function(evt) {
  updateEntryCode(evt.key, evt.newValue);
}

// Settings were changed while the companion was not running
if (me.launchReasons.settingsChanged) {
  // Send the value of the setting
  updateEntryCode(ENTRY_CODE, settingsStorage.getItem(ENTRY_CODE));
}

/***************************************
  Send location data to the server
***************************************/
const PLACE_SOURCE = "watch";
function sendLocation(lat, long, place) {
  let token = settingsStorage.getItem(AUTHORIZATION_TOKEN);
  if (token) {
    const url = `${BASE_URL}/api/locations/`;
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
  const url = `${BASE_URL}/api/antised?/`;
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
  if (evt.data.key == RECENT_STEPS) {
    console.log("Send step message to server soon!");
    getLatLong();
  } else {
    console.log(evt.data.key);
  }
}

import { settingsStorage } from "settings";
import * as messaging from "messaging";
import { me } from "companion";
import companion from "companion";

// Post entryCode to server and display result
import { sendSettingsData, updateEntryCode } from "./entry-code";

// Get location
import { geolocation } from "geolocation";
import { locationSuccess, locationError } from "./location";

import { ANTI_SEDENTARY_MESSAGE, ENTRY_CODE, INTEGRATION_STATUS_MESSAGE,
   QUERY_STEP_MESSAGE, RECENT_STEPS } from "../common/globals.js";

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
  Only allow this if user is authenticated.
  How to send the User with this?
***************************************/
const PLACE_SOURCE = "watch";
function sendLocation(lat, long, place) {
  const url = "https://heartsteps-kpwhri.appspot.com/api/locations/";
  let data = {"latitude": lat, "longitude": long, source: PLACE_SOURCE};
  fetch(url, {
    method: "POST",
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(function(response) {
    // if (response.status == 201)
    console.log("sendLocation completed with status " + response.status);
  }).catch(error => console.error('Error in sendLocation: ', error))
}

// Get location
// geolocation.enableHighAccuracy = true;
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
  const url = "https://heartsteps-kpwhri.appspot.com/api/antised?/";
  let data = {"latitude": lat, "longitude": long, source: PLACE_SOURCE};
  fetch(url, {
    method: "POST",
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(function(response) {
    // if (response.status == 201)
    console.log("sendSteps completed with status " + response.status);
  }).catch(error => console.error('Error in sendSteps: ', error))
}

// Listen for step data from the watch
// then send Step and Location data to server
messaging.peerSocket.onmessage = function(evt) {
  if (evt.data.key == RECENT_STEPS) {
    console.log("Send step message to server soon!");
    console.log("Send location to server next!");
    getLatLong();
  } else {
    console.log(evt.data.key);
  }
}

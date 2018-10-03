import { settingsStorage } from "settings";
import * as messaging from "messaging";
import { me } from "companion";

// Post entryCode to server and display result
import { sendSettingsData, updateEntryCode } from "./entry-code";

// Get location
import { geolocation } from "geolocation";
import { locationSuccess, locationError } from "./location";

import { ANTI_SEDENTARY_MESSAGE, ENTRY_CODE, INTEGRATION_STATUS_MESSAGE,
   QUERY_STEP_MESSAGE } from "../common/globals.js";

// Tell the device to check steps every 5 minutes
const WAKE_INTERVAL = 5;

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

/*****************************************************************
  Tell the device to query watch for step count every X minutes.
  Only allow this if user is authenticated.
*****************************************************************/
const MILLISECONDS_PER_MINUTE = 1000 * 60;
me.wakeInterval = WAKE_INTERVAL * MILLISECONDS_PER_MINUTE;

if (me.launchReasons.wokenUp) {
  // The companion started due to a periodic timer
  console.log("Started due to wake interval!");
  if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    messaging.peerSocket.send(QUERY_STEP_MESSAGE);
    // Send location
  } else {
    // Close the companion and wait to be awoken
    console.log("No peerSocket connection");
    me.yield();
  }
}

/***************************************
  Send location data to the server
  Only allow this if user is authenticated.
  The lat/long look weird - check the projection
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
    console.log("Succeeded with status " + response.status);
  }).catch(error => console.error('Error in sendLocation: ', error))
}

// Get location
geolocation.enableHighAccuracy = true;
geolocation.getCurrentPosition(locationSuccess, locationError);
